import sys
import time
from app.services.youtube_service import youtube_service
from app.services.transcript_service import transcript_service
from app.services.chapter_service import chapter_service
from app.services.llm.ollama import OllamaProvider
from app.services.summarization_service import SummarizationService
from app.services.slide_service import slide_service

TARGET_URL = "https://www.youtube.com/watch?v=SahaDGzN-Bk&list=PLEneLIDJFpcA&index=6"

def main():
    print("=" * 70)
    print(f"Testing NoteTube Pipeline with Ollama on Target Video:\n{TARGET_URL}")
    print("=" * 70)

    # 1. Video ID extraction
    video_id = youtube_service.extract_video_id(TARGET_URL)
    print(f"1. Extracted Video ID: {video_id}")
    assert video_id == "SahaDGzN-Bk", f"Expected SahaDGzN-Bk, got {video_id}"

    # 2. Metadata fetch
    print("\n2. Fetching YouTube Video Metadata...")
    meta = youtube_service.get_video_metadata(TARGET_URL)
    print(f"   Title   : {meta.title}")
    print(f"   Duration: {meta.duration}s ({youtube_service.format_duration(meta.duration)})")
    print(f"   Thumb   : {meta.thumbnail}")

    # 3. Transcript fetch
    print("\n3. Fetching Transcript...")
    t0 = time.time()
    transcript = transcript_service.get_transcript(video_id)
    t_fetch = time.time() - t0
    trans_text = str(transcript)
    print(f"   Fetched in {t_fetch:.2f}s")
    print(f"   Language: {transcript.language} ({transcript.language_code})")
    print(f"   Is Generated: {transcript.is_generated}")
    print(f"   Length: {len(trans_text)} characters, {len(transcript.segments)} segments")

    # 4. Chapters detection
    print("\n4. Detecting / Generating Chapters...")
    provider = OllamaProvider(model="qwen3:1.7b")
    chapters = chapter_service.detect_or_generate_chapters(
        metadata=meta,
        transcript=transcript,
        llm_provider=provider
    )
    print(f"   Detected {len(chapters)} chapters:")
    for idx, ch in enumerate(chapters):
        print(f"   [{idx+1:02d}] {ch.timestamp_str} - {ch.title} ({ch.duration_str}) [id={ch.chapter_id}]")

    # 5. Test Ollama Summarization on Overview
    print("\n5. Testing Ollama 'qwen3:1.7b' generation on Video Overview...")
    summarizer = SummarizationService(provider=provider)
    duration_str = youtube_service.format_duration(meta.duration)
    overview_context = f"Video Title: {meta.title}\nDescription: {meta.description or ''}\n\nKey Excerpt:\n{trans_text[:2500]}"
    t0 = time.time()
    overview_res = summarizer.generate_video_overview(
        title=meta.title,
        duration_str=duration_str,
        context=overview_context
    )
    t_overview = time.time() - t0
    print(f"   Generated Overview in {t_overview:.2f}s:")
    print("   " + "-" * 50)
    print("   " + "\n   ".join(overview_res.strip().splitlines()[:10]))
    print("   ...")

    # 6. Test Slide Service extraction on the detected chapters
    print("\n6. Testing Slide Service frame extraction & PPT generation on detected chapters...")
    t0 = time.time()
    slides_result = slide_service.extract_slides(
        video_id=video_id,
        youtube_url=TARGET_URL,
        chapters=chapters
    )
    t_slides = time.time() - t0
    print(f"   Extracted {len(slides_result.slides)} slides in {t_slides:.2f}s!")
    print(f"   Status     : {slides_result.status}")
    print(f"   PPT Url    : {slides_result.ppt_download_url}")
    print(f"   Total Slides: {slides_result.total_chapters}")
    for s in slides_result.slides:
        print(f"   - Slide #{s.slide_index}: '{s.title}' at {s.timestamp_str} (extracted at {s.extraction_timestamp_str}) -> {s.image_url}")

    print("\n" + "=" * 70)
    print("ALL CHECKS PASSED FOR SahaDGzN-Bk WITH OLLAMA & SLIDES PIPELINE!")
    print("=" * 70)

if __name__ == "__main__":
    main()
