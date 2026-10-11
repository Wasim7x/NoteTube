import React, { useEffect, useCallback, useState } from 'react';
import {
  X,
  ChevronLeft,
  ChevronRight,
  Clock,
  ExternalLink,
  Film,
  AlertTriangle,
  RefreshCw,
  ImageOff
} from 'lucide-react';
import type { ChapterSlideItem } from '../types';

interface SlidePreviewModalProps {
  slides: ChapterSlideItem[];
  activeChapterId: string | null;
  videoId?: string;
  onClose: () => void;
  onSelectChapter: (chapterId: string) => void;
  getSlideImageUrl: (videoId: string, chapterId: string) => string;
}

export const SlidePreviewModal: React.FC<SlidePreviewModalProps> = ({
  slides,
  activeChapterId,
  videoId,
  onClose,
  onSelectChapter,
  getSlideImageUrl,
}) => {
  const [imgLoadError, setImgLoadError] = useState(false);

  // Resilient chapter index matching: supports chapter_id, ch_*, index numbers, and fallback
  const matchedIndex = slides.findIndex((s) => {
    if (!activeChapterId) return false;
    if (s.chapter_id === activeChapterId) return true;
    if (s.chapter_id === `ch_${activeChapterId}`) return true;
    if (activeChapterId.startsWith('ch_') && s.chapter_id === activeChapterId.replace('ch_', '')) return true;
    if (String(s.chapter_index) === String(activeChapterId)) return true;
    if (activeChapterId.includes(`_${s.chapter_index}`) || activeChapterId.includes(`-${s.chapter_index}`)) return true;
    return false;
  });

  const currentIndex = matchedIndex >= 0 ? matchedIndex : 0;
  const currentSlide = slides.length > 0 ? slides[currentIndex] : null;

  // Reset load error when slide changes
  useEffect(() => {
    setImgLoadError(false);
  }, [currentSlide?.chapter_id]);

  const handlePrev = useCallback(() => {
    if (currentIndex > 0) {
      onSelectChapter(slides[currentIndex - 1].chapter_id);
    }
  }, [currentIndex, slides, onSelectChapter]);

  const handleNext = useCallback(() => {
    if (currentIndex < slides.length - 1) {
      onSelectChapter(slides[currentIndex + 1].chapter_id);
    }
  }, [currentIndex, slides, onSelectChapter]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'ArrowLeft') {
        handlePrev();
      } else if (e.key === 'ArrowRight') {
        handleNext();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handlePrev, handleNext, onClose]);

  if (!currentSlide || !videoId) {
    return null;
  }

  const imageUrl = getSlideImageUrl(videoId, currentSlide.chapter_id);
  const isFailed = currentSlide.status === 'failed' || imgLoadError;

  const youtubeUrl = `https://www.youtube.com/watch?v=${videoId}&t=${Math.floor(
    currentSlide.start_time
  )}s`;

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-md animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-5xl bg-gray-900 border border-gray-800 rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800 bg-gray-900/90 text-white">
          <div className="flex items-center gap-3 min-w-0 pr-4">
            <span className="px-3 py-1 bg-primary text-white rounded-full text-xs font-bold tracking-wide shrink-0">
              Chapter {currentSlide.chapter_index}
            </span>
            <h3 className="text-base sm:text-lg font-bold text-gray-100 truncate">
              {currentSlide.title}
            </h3>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <span className="text-xs text-gray-400 font-mono hidden sm:inline">
              Slide {currentIndex + 1} of {slides.length}
            </span>
            <button
              onClick={onClose}
              aria-label="Close slide preview"
              className="p-1.5 rounded-full text-gray-400 hover:text-white hover:bg-gray-800 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Main Visual Display */}
        <div className="relative flex-1 bg-black flex items-center justify-center overflow-hidden min-h-[320px] sm:min-h-[460px]">
          {isFailed ? (
            <div className="flex flex-col items-center justify-center p-8 text-center text-gray-400 max-w-md">
              <div className="w-14 h-14 rounded-2xl bg-amber-500/10 text-amber-400 flex items-center justify-center mb-4">
                {imgLoadError ? <ImageOff className="w-7 h-7" /> : <AlertTriangle className="w-7 h-7" />}
              </div>
              <h4 className="text-lg font-semibold text-gray-200 mb-2">
                {imgLoadError ? 'Image Frame Not Available' : 'Frame Extraction Failed'}
              </h4>
              <p className="text-sm text-gray-400 leading-relaxed mb-4">
                {currentSlide.error ||
                  (imgLoadError
                    ? 'The image asset could not be loaded from storage or was not yet rendered.'
                    : 'The video stream could not be decoded at this chapter timestamp.')}
              </p>
              {imgLoadError && (
                <button
                  onClick={() => setImgLoadError(false)}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-xs font-semibold text-gray-200 transition-colors cursor-pointer"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Retry Image Load</span>
                </button>
              )}
            </div>
          ) : (
            <img
              src={imageUrl}
              alt={`Slide for ${currentSlide.title}`}
              onError={() => setImgLoadError(true)}
              className="w-full h-full max-h-[65vh] object-contain select-none transition-opacity duration-200"
            />
          )}

          {/* Previous / Next Arrow Overlays */}
          {currentIndex > 0 && (
            <button
              onClick={handlePrev}
              aria-label="Previous slide"
              className="absolute left-4 top-1/2 -translate-y-1/2 p-2.5 rounded-full bg-black/60 hover:bg-black/85 text-white/90 hover:text-white border border-white/10 transition-all cursor-pointer backdrop-blur-sm hover:scale-105"
            >
              <ChevronLeft className="w-6 h-6" />
            </button>
          )}

          {currentIndex < slides.length - 1 && (
            <button
              onClick={handleNext}
              aria-label="Next slide"
              className="absolute right-4 top-1/2 -translate-y-1/2 p-2.5 rounded-full bg-black/60 hover:bg-black/85 text-white/90 hover:text-white border border-white/10 transition-all cursor-pointer backdrop-blur-sm hover:scale-105"
            >
              <ChevronRight className="w-6 h-6" />
            </button>
          )}
        </div>

        {/* Footer Info Bar */}
        <div className="px-6 py-4 bg-gray-900 border-t border-gray-800 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex flex-wrap items-center gap-3 sm:gap-5 text-gray-300">
            <div className="flex items-center gap-1.5 text-gray-300">
              <Clock className="w-4 h-4 text-primary" />
              <span>Chapter: <strong>{currentSlide.timestamp_str}</strong></span>
            </div>

            <div className="flex items-center gap-1.5 text-indigo-300 bg-indigo-950/60 px-2.5 py-1 rounded-lg border border-indigo-800/50">
              <Film className="w-3.5 h-3.5 text-indigo-400" />
              <span>
                Slide extracted at <strong>{currentSlide.extraction_timestamp_str}</strong> (5s before chapter end)
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <a
              href={youtubeUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-red-400 hover:text-red-300 hover:underline font-medium"
            >
              <span>Watch on YouTube</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
