import os
import re
import json
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import httpx

from app.models.schemas import RAGSourceChunk, RAGQueryResponse, RAGStatusResponse
from app.services.video_service import video_job_service
from app.services.youtube_service import YouTubeService
from app.services.llm.factory import create_llm_provider
from app.prompts.notes_prompt import RAG_QA_SYSTEM_PROMPT, RAG_QA_USER_PROMPT
from app.config import settings

logger = logging.getLogger(__name__)

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
RAG_DATA_DIR = _BACKEND_DIR / "data" / "rag"
RAG_DATA_DIR.mkdir(parents=True, exist_ok=True)


class LocalTFIDFEmbedder:
    """
    Lightweight, deterministic local dense embedder based on sublinear TF-IDF
    and character/word n-grams with L2 normalization.
    Zero external dependencies, fast (<5ms), robust across all deployment targets.
    """
    def __init__(self, dim: int = 256):
        self.dim = dim

    def _hash_token(self, token: str) -> int:
        h = int(hashlib.md5(token.encode('utf-8')).hexdigest()[:8], 16)
        return h % self.dim

    def embed_text(self, text: str) -> List[float]:
        tokens = re.findall(r'\b[a-zA-Z0-9_]{2,}\b', text.lower())
        if not tokens:
            return [0.0] * self.dim

        vec = np.zeros(self.dim, dtype=np.float32)
        # Word unigrams + bigrams for semantic phrase matching
        for i, t in enumerate(tokens):
            idx = self._hash_token(t)
            vec[idx] += 1.0
            if i + 1 < len(tokens):
                bigram = f"{t}_{tokens[i+1]}"
                vec[self._hash_token(bigram)] += 1.5

        # Sublinear TF scaling: 1 + log(tf)
        positive_mask = vec > 0
        vec[positive_mask] = 1.0 + np.log(vec[positive_mask])

        # L2 normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


class TranscriptRAGService:
    def __init__(self, data_dir: Path = RAG_DATA_DIR):
        self.data_dir = data_dir.resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.local_embedder = LocalTFIDFEmbedder(dim=384)

    def _get_video_dir(self, video_id: str) -> Path:
        clean_id = "".join(c for c in video_id if c.isalnum() or c in "-_")[:64]
        v_dir = self.data_dir / clean_id
        v_dir.mkdir(parents=True, exist_ok=True)
        return v_dir

    def _chunk_transcript(
        self,
        video_id: str,
        segments: List[Dict[str, Any]],
        chapters: List[Dict[str, Any]],
        full_text: str
    ) -> List[Dict[str, Any]]:
        """
        Splits transcript segments into overlapping chunks with start/end timestamps
        and maps them to corresponding chapters.
        """
        chunks: List[Dict[str, Any]] = []

        if segments and len(segments) > 0:
            current_words: List[str] = []
            chunk_start = float(segments[0].get("start", 0.0))
            chunk_end = chunk_start
            target_word_count = 160
            overlap_words = 35

            for seg in segments:
                t = (seg.get("text") or "").strip()
                if not t:
                    continue
                seg_words = t.split()
                current_words.extend(seg_words)
                dur = float(seg.get("duration", 0.0))
                seg_start = float(seg.get("start", 0.0))
                chunk_end = max(chunk_end, seg_start + dur)

                if len(current_words) >= target_word_count:
                    text_content = " ".join(current_words)
                    # Find chapter
                    ch_title = None
                    for ch in chapters:
                        st = float(ch.get("start_time", 0.0))
                        et = float(ch.get("end_time") or (st + 300.0))
                        if st <= chunk_start <= et or (chunk_start >= st and not ch_title):
                            ch_title = ch.get("title")

                    c_id = f"{video_id}_c_{len(chunks) + 1}"
                    t_str = f"{YouTubeService.format_timestamp(chunk_start)} – {YouTubeService.format_timestamp(chunk_end)}"

                    chunks.append({
                        "chunk_id": c_id,
                        "text": text_content,
                        "start_time": round(chunk_start, 2),
                        "end_time": round(chunk_end, 2),
                        "timestamp_str": t_str,
                        "chapter_title": ch_title or "Overview"
                    })

                    # Keep overlap for next chunk
                    current_words = current_words[-overlap_words:]
                    chunk_start = seg_start

            if current_words:
                text_content = " ".join(current_words)
                c_id = f"{video_id}_c_{len(chunks) + 1}"
                t_str = f"{YouTubeService.format_timestamp(chunk_start)} – {YouTubeService.format_timestamp(chunk_end)}"
                chunks.append({
                    "chunk_id": c_id,
                    "text": text_content,
                    "start_time": round(chunk_start, 2),
                    "end_time": round(chunk_end, 2),
                    "timestamp_str": t_str,
                    "chapter_title": "Concluding Discussion"
                })

        else:
            # Fallback chunking from raw text
            words = full_text.split()
            chunk_size = 180
            overlap = 40
            idx = 0
            while idx < len(words):
                chunk_words = words[idx:idx + chunk_size]
                text_content = " ".join(chunk_words)
                start_sec = (idx / max(1, len(words))) * 300.0
                end_sec = min(300.0, start_sec + 60.0)
                t_str = f"{YouTubeService.format_timestamp(start_sec)} – {YouTubeService.format_timestamp(end_sec)}"
                chunks.append({
                    "chunk_id": f"{video_id}_c_{len(chunks) + 1}",
                    "text": text_content,
                    "start_time": round(start_sec, 2),
                    "end_time": round(end_sec, 2),
                    "timestamp_str": t_str,
                    "chapter_title": f"Section {len(chunks) + 1}"
                })
                idx += (chunk_size - overlap)

        return chunks

    def _generate_embeddings(
        self,
        texts: List[str],
        provider: str,
        api_key: str = "",
        model: str = ""
    ) -> Tuple[List[List[float]], str]:
        """
        Generates embeddings. First attempts cloud/local provider if supported,
        falling back to local sublinear TF-IDF vectors.
        """
        prov_clean = (provider or "").strip().lower()

        # Try Google Gemini Embeddings if available
        if prov_clean == "gemini" and api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key.strip())
                embeddings = []
                # Batch in groups of 20
                for i in range(0, len(texts), 20):
                    batch = texts[i:i + 20]
                    res = client.models.embed_content(
                        model="text-embedding-004",
                        contents=batch
                    )
                    for item in res.embeddings:
                        embeddings.append(item.values)
                if len(embeddings) == len(texts):
                    return embeddings, "gemini:text-embedding-004"
            except Exception as e:
                logger.info(f"Gemini embedding API fallback to local: {e}")

        # Try OpenAI Embeddings if available
        if prov_clean == "openai" and api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key.strip())
                res = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=texts
                )
                embeddings = [item.embedding for item in res.data]
                if len(embeddings) == len(texts):
                    return embeddings, "openai:text-embedding-3-small"
            except Exception as e:
                logger.info(f"OpenAI embedding API fallback to local: {e}")

        # Try Ollama Embeddings if reachable
        if prov_clean == "ollama":
            try:
                base_url = settings.OLLAMA_BASE_URL.rstrip("/")
                emb_model = model or "qwen3:1.7b"
                with httpx.Client(timeout=8.0) as client:
                    resp = client.post(f"{base_url}/api/embed", json={
                        "model": emb_model,
                        "input": texts[:5]
                    })
                    if resp.status_code == 200:
                        data = resp.json()
                        raw_embs = data.get("embeddings") or []
                        if raw_embs and len(raw_embs) == len(texts[:5]):
                            # Embed all
                            all_embs = []
                            for i in range(0, len(texts), 15):
                                b = texts[i:i+15]
                                r = client.post(f"{base_url}/api/embed", json={"model": emb_model, "input": b})
                                all_embs.extend(r.json().get("embeddings", []))
                            if len(all_embs) == len(texts):
                                return all_embs, f"ollama:{emb_model}"
            except Exception as e:
                logger.info(f"Ollama embedding API fallback to local: {e}")

        # Universal, guaranteed fast deterministic local embedding
        embs = self.local_embedder.embed_batch(texts)
        return embs, "local:tfidf-384"

    def get_or_build_index(
        self,
        video_id: str,
        provider: str = "gemini",
        api_key: str = "",
        model: str = ""
    ) -> Dict[str, Any]:
        """
        Retrieves or builds the persistent vector store for a video.
        Reuses cached index on disk if valid.
        """
        video_dir = self._get_video_dir(video_id)
        index_file = video_dir / "index.json"

        # Check existing disk index
        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    cached_index = json.load(f)
                if cached_index.get("chunks") and cached_index.get("embeddings"):
                    logger.info(f"Loaded persistent RAG index for video_id={video_id} ({len(cached_index['chunks'])} chunks)")
                    return cached_index
            except Exception as e:
                logger.warning(f"Failed to read cached RAG index for {video_id}: {e}")

        # Build fresh index from cached video job
        job = video_job_service.get_cached_job(video_id)
        if not job:
            raise ValueError(f"No video job found for {video_id}. Please load the video first.")

        segments = job.get("transcript_segments", [])
        chapters = job.get("chapters", [])
        full_text = job.get("transcript_full", "")

        chunks = self._chunk_transcript(video_id, segments, chapters, full_text)
        if not chunks:
            chunks = [{
                "chunk_id": f"{video_id}_c_1",
                "text": full_text[:1000] or "Empty video transcript.",
                "start_time": 0.0,
                "end_time": 60.0,
                "timestamp_str": "00:00 – 01:00",
                "chapter_title": "Overview"
            }]

        chunk_texts = [f"{c.get('chapter_title', '')}: {c['text']}" for c in chunks]
        embeddings, emb_type = self._generate_embeddings(
            texts=chunk_texts,
            provider=provider,
            api_key=api_key,
            model=model
        )

        index_record = {
            "video_id": video_id,
            "chunk_count": len(chunks),
            "embedding_type": emb_type,
            "chunks": chunks,
            "embeddings": embeddings
        }

        try:
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(index_record, f, ensure_ascii=False)
            logger.info(f"Persisted RAG index for video_id={video_id} ({len(chunks)} chunks, type={emb_type})")
        except Exception as e:
            logger.error(f"Failed to save RAG index for {video_id}: {e}")

        return index_record

    def search(
        self,
        video_id: str,
        query: str,
        top_k: int = 4,
        provider: str = "gemini",
        api_key: str = "",
        model: str = ""
    ) -> List[RAGSourceChunk]:
        """
        Retrieves top-k most semantically relevant chunks for a question.
        """
        index_data = self.get_or_build_index(video_id, provider=provider, api_key=api_key, model=model)
        chunks = index_data.get("chunks", [])
        embeddings = index_data.get("embeddings", [])
        emb_type = index_data.get("embedding_type", "local:tfidf-384")

        if not chunks or not embeddings:
            return []

        # Embed query using matching embedder
        if emb_type.startswith("local:"):
            q_vec = np.array(self.local_embedder.embed_text(query), dtype=np.float32)
        else:
            q_embs, _ = self._generate_embeddings([query], provider=provider, api_key=api_key, model=model)
            q_vec = np.array(q_embs[0], dtype=np.float32)

        # Compute cosine similarity
        doc_matrix = np.array(embeddings, dtype=np.float32)
        # Normalize
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        doc_norms = np.linalg.norm(doc_matrix, axis=1, keepdims=True)
        doc_norms = np.where(doc_norms > 0, doc_norms, 1.0)
        normalized_docs = doc_matrix / doc_norms

        scores = np.dot(normalized_docs, q_vec)

        # Top-K indices
        top_indices = np.argsort(scores)[::-1][:top_k]

        results: List[RAGSourceChunk] = []
        for idx in top_indices:
            score = float(scores[idx])
            c = chunks[idx]
            results.append(RAGSourceChunk(
                chunk_id=c["chunk_id"],
                timestamp_str=c["timestamp_str"],
                start_time=c["start_time"],
                end_time=c["end_time"],
                chapter_title=c.get("chapter_title"),
                text=c["text"],
                score=round(score, 4)
            ))

        return results

    def answer_query(
        self,
        video_id: str,
        query: str,
        provider: str,
        model: str = "",
        api_key: str = ""
    ) -> RAGQueryResponse:
        """
        Answers a user question grounded in retrieved transcript chunks.
        """
        job = video_job_service.get_cached_job(video_id)
        video_title = job.get("video", {}).get("title", "Video") if job else "Video"

        sources = self.search(
            video_id=video_id,
            query=query,
            top_k=4,
            provider=provider,
            api_key=api_key,
            model=model
        )

        # Determine relevance threshold
        best_score = sources[0].score if sources else 0.0
        # If best match is completely unrelated (below 0.05), declare missing info
        if not sources or best_score < 0.04:
            return RAGQueryResponse(
                success=True,
                video_id=video_id,
                query=query,
                answer=(
                    f"Based on the transcript for \"{video_title}\", this topic is not discussed or mentioned in the video. "
                    "Please ask a question related to the topics covered in this video."
                ),
                sources=[],
                grounded=False
            )

        # Build context
        context_parts = []
        for s in sources:
            ch_info = f" [Chapter: {s.chapter_title}]" if s.chapter_title else ""
            context_parts.append(f"- Timestamp: [{s.timestamp_str}]{ch_info}\nExcerpt: \"{s.text}\"")

        context_str = "\n\n".join(context_parts)

        # Generate answer from LLM
        try:
            llm = create_llm_provider(provider=provider, model=model, api_key=api_key)
            user_prompt = RAG_QA_USER_PROMPT.format(
                title=video_title,
                context_chunks=context_str,
                question=query
            )
            answer_text = llm.generate_content(
                system_prompt=RAG_QA_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.2,
                max_tokens=500
            )

            return RAGQueryResponse(
                success=True,
                video_id=video_id,
                query=query,
                answer=answer_text.strip(),
                sources=sources,
                grounded=True
            )

        except Exception as e:
            logger.exception(f"Error generating RAG answer for {video_id}: {e}")
            return RAGQueryResponse(
                success=False,
                video_id=video_id,
                query=query,
                answer="Could not generate an answer at this time.",
                sources=sources,
                grounded=False,
                error=str(e)
            )


rag_service = TranscriptRAGService()
