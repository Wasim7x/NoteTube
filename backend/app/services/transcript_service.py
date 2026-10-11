import logging
from typing import Optional, List, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    YouTubeTranscriptApiException,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    NotTranslatable,
    TranslationLanguageNotAvailable,
)
from app.models.transcript import NormalizedTranscript
from app.utils.text_processing import clean_text

logger = logging.getLogger(__name__)

class TranscriptService:
    @staticmethod
    def _calculate_priority_score(t: Any) -> tuple:
        """
        Calculates a deterministic priority score for transcript selection.
        Strategy:
        1. Manually created transcripts over auto-generated.
        2. English direct tracks preferred if present, but any native language is supported.
        3. Directly fetchable track.
        4. Deterministic tie-breaker.
        """
        is_manual = not getattr(t, "is_generated", True)
        manual_score = 100 if is_manual else 50

        lang_code = (getattr(t, "language_code", "") or "").lower()
        if lang_code == "en":
            lang_score = 30
        elif lang_code.startswith("en-"):
            lang_score = 25
        else:
            lang_score = 10

        fetchable_score = 20
        total_score = manual_score + lang_score + fetchable_score

        # Tuple for sorting: higher total_score, higher manual_score, higher lang_score, then alphabetical lang_code
        return (total_score, manual_score, lang_score, lang_code)

    def list_transcripts(self, video_id: str) -> List[Any]:
        """
        Discovers all available transcript tracks for a video without assuming language.
        Returns empty list if captions are disabled, unavailable, or on failure.
        """
        api = YouTubeTranscriptApi()
        try:
            transcript_list = api.list(video_id)
            return list(transcript_list)
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            logger.info(f"No YouTube transcript/captions available | video_id={video_id} | reason={type(e).__name__}")
            return []
        except VideoUnavailable as e:
            logger.warning(f"Video unavailable for transcript lookup | video_id={video_id} | reason={e}")
            return []
        except Exception as e:
            logger.warning(f"Transcript discovery encountered error | video_id={video_id} | error={e}")
            return []

    def get_transcript(
        self,
        video_id: str,
        target_language: Optional[str] = None
    ) -> Optional[NormalizedTranscript]:
        """
        Discovers, selects, and extracts the optimal transcript for a video.
        - Automatically discovers available tracks.
        - Selects manually created or auto-generated based on deterministic priority.
        - Works across any native language (English, Hindi, Spanish, etc.) without requiring English.
        - Only attempts translation if supported and available; never fails on missing translation.
        - Gracefully returns None if no transcript is available so caller can engage fallback.
        """
        logger.info(f"Transcript discovery started | video_id={video_id}")
        available_tracks = self.list_transcripts(video_id)

        if not available_tracks:
            logger.info(f"No YouTube transcript/captions available | video_id={video_id}")
            logger.info("Continuing with fallback processing")
            return None

        # Log diagnostic information about discovered transcripts
        logger.info(f"Available transcripts ({len(available_tracks)}):")
        for t in available_tracks:
            logger.info(
                f"- language={getattr(t, 'language', 'unknown')} | "
                f"language_code={getattr(t, 'language_code', 'unknown')} | "
                f"generated={getattr(t, 'is_generated', False)} | "
                f"translatable={getattr(t, 'is_translatable', False)}"
            )

        # Sort tracks deterministically based on priority
        sorted_candidates = sorted(available_tracks, key=self._calculate_priority_score, reverse=True)

        selected_track = None
        fetched_data = None

        # Attempt fetching the best candidate, falling back through candidates if needed
        for candidate in sorted_candidates:
            cand_lang = getattr(candidate, "language", "unknown")
            cand_code = getattr(candidate, "language_code", "unknown")
            cand_gen = getattr(candidate, "is_generated", False)

            logger.info(
                f"Selected transcript:\n"
                f"language={cand_lang}\n"
                f"language_code={cand_code}\n"
                f"generated={cand_gen}"
            )

            try:
                fetched_data = candidate.fetch()
                selected_track = candidate
                logger.info("Transcript extraction successful")
                break
            except Exception as fetch_err:
                logger.warning(
                    f"Failed to fetch transcript candidate {cand_code} ({cand_lang}): {fetch_err}. "
                    "Trying next available transcript..."
                )

        if not selected_track or fetched_data is None:
            logger.info(f"No YouTube transcript could be fetched | video_id={video_id}")
            logger.info("Continuing with fallback processing")
            return None

        # Optional translation handling (only if target_language requested and genuinely supported)
        final_track = selected_track
        if target_language:
            norm_target = target_language.lower().strip()
            curr_code = getattr(selected_track, "language_code", "").lower()

            if curr_code != norm_target and not curr_code.startswith(f"{norm_target}-"):
                is_translatable = getattr(selected_track, "is_translatable", False)
                translation_languages = getattr(selected_track, "translation_languages", [])
                supported_codes = {
                    getattr(tl, "language_code", "").lower()
                    for tl in translation_languages
                }

                if is_translatable and norm_target in supported_codes:
                    try:
                        translated_track = selected_track.translate(target_language)
                        trans_data = translated_track.fetch()
                        fetched_data = trans_data
                        final_track = translated_track
                        logger.info(f"Translated transcript to {target_language} successfully")
                    except Exception as trans_err:
                        logger.warning(
                            f"Translation to {target_language} failed: {trans_err}. "
                            "Using original transcript language."
                        )
                else:
                    logger.info(
                        f"Translation to {target_language} is not available or supported for {curr_code}. "
                        "Using original transcript language."
                    )

        # Normalize transcript data and preserve timestamps
        segments: List[Dict[str, Any]] = []
        raw_text_parts: List[str] = []

        for item in fetched_data:
            if isinstance(item, dict):
                text_val = item.get("text", "")
                start_val = float(item.get("start", 0.0))
                duration_val = float(item.get("duration", 0.0))
            else:
                text_val = getattr(item, "text", "")
                start_val = float(getattr(item, "start", 0.0))
                duration_val = float(getattr(item, "duration", 0.0))

            segments.append({
                "text": text_val,
                "start": start_val,
                "duration": duration_val
            })
            if text_val:
                raw_text_parts.append(text_val)

        joined_text = " ".join(raw_text_parts)
        cleaned_text = clean_text(joined_text)

        return NormalizedTranscript(
            text=cleaned_text,
            language=getattr(final_track, "language", "Unknown"),
            language_code=getattr(final_track, "language_code", "unknown"),
            is_generated=bool(getattr(final_track, "is_generated", False)),
            source="youtube",
            segments=segments
        )

transcript_service = TranscriptService()
