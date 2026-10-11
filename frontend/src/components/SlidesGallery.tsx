import React, { useState } from 'react';
import {
  Presentation,
  FileDown,
  Clock,
  Film,
  AlertCircle,
  CheckCircle2,
  Loader2,
  Maximize2,
  RefreshCw,
  Info
} from 'lucide-react';
import type { VideoSlidesResponse } from '../types';

interface SlidesGalleryProps {
  slidesData: VideoSlidesResponse | null;
  isLoading: boolean;
  videoId?: string;
  videoTitle?: string;
  onOpenSlide: (chapterId: string) => void;
  onRetryExtract?: () => void;
  getSlideImageUrl: (videoId: string, chapterId: string) => string;
  getDownloadPptUrl: (videoId: string) => string;
}

export const SlidesGallery: React.FC<SlidesGalleryProps> = ({
  slidesData,
  isLoading,
  videoId,
  videoTitle,
  onOpenSlide,
  onRetryExtract,
  getSlideImageUrl,
  getDownloadPptUrl,
}) => {
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const handleDownloadPpt = async () => {
    if (!videoId) return;
    setIsDownloading(true);
    setDownloadError(null);

    try {
      const url = getDownloadPptUrl(videoId);
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to download presentation (status ${response.status})`);
      }

      const blob = await response.blob();
      const disposition = response.headers.get('content-disposition');
      let filename = `${(videoTitle || 'NoteTube').replace(/[^a-zA-Z0-9_-]/g, '_')}_chapter_slides.pptx`;
      
      if (disposition && disposition.includes('filename=')) {
        const match = disposition.match(/filename="?([^"]+)"?/);
        if (match && match[1]) {
          filename = match[1];
        }
      }

      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err: any) {
      console.error('PPT download error:', err);
      setDownloadError(err.message || 'Could not download PowerPoint presentation.');
    } finally {
      setIsDownloading(false);
    }
  };

  const slides = slidesData?.slides || [];
  const status = slidesData?.status;
  const hasChapters = slidesData?.has_chapters !== false;
  const extractedCount = slidesData?.extracted_slides || 0;
  const totalCount = slidesData?.total_chapters || slides.length;

  return (
    <section id="chapter-slides-section" className="w-full bg-white rounded-3xl shadow-sm border border-gray-100 p-6 md:p-10 mb-8 scroll-mt-20">
      {/* Top Header & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-gray-100">
        <div className="flex items-start sm:items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center shrink-0">
            <Presentation className="w-5 h-5" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-xl font-bold text-gray-900 leading-tight">
                Chapter Slides &amp; Presentation
              </h2>
              {slides.length > 0 && (
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
                  {extractedCount} / {totalCount} Slides (16:9 Widescreen)
                </span>
              )}
            </div>
            <p className="text-xs text-gray-500 mt-0.5">
              Visual slide frames extracted 5 seconds before chapter ends, ready to preview &amp; export as PowerPoint
            </p>
          </div>
        </div>

        {/* Action Button: Download PPT */}
        <div className="flex items-center gap-2.5 shrink-0">
          {onRetryExtract && status === 'failed' && (
            <button
              onClick={onRetryExtract}
              disabled={isLoading}
              className="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl border border-gray-200 text-gray-700 hover:text-gray-900 hover:bg-gray-50 text-xs font-semibold transition-all cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Retry Extraction</span>
            </button>
          )}

          <button
            onClick={handleDownloadPpt}
            disabled={isDownloading || isLoading || extractedCount === 0 || !hasChapters}
            className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-xs transition-all shadow-sm cursor-pointer ${
              extractedCount > 0 && !isDownloading
                ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-100 active:scale-[0.98]'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200'
            }`}
          >
            {isDownloading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>Downloading PPT...</span>
              </>
            ) : (
              <>
                <FileDown className="w-4 h-4" />
                <span>Download PPT (.pptx)</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Download Error Banner if any */}
      {downloadError && (
        <div className="mt-4 p-3 bg-red-50 text-red-700 border border-red-200 rounded-xl text-xs flex items-center justify-between">
          <span>{downloadError}</span>
          <button onClick={() => setDownloadError(null)} className="underline ml-2">Dismiss</button>
        </div>
      )}

      {/* State A: Loading / Extracting */}
      {isLoading && (
        <div className="py-12 flex flex-col items-center justify-center text-center">
          <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-3">
            <Loader2 className="w-6 h-6 animate-spin" />
          </div>
          <h4 className="text-sm font-bold text-gray-800 mb-1">
            Extracting Chapter Slide Frames...
          </h4>
          <p className="text-xs text-gray-500 max-w-sm">
            Accessing video stream to capture high-resolution frames 5 seconds before each chapter ends.
          </p>
        </div>
      )}

      {/* State B: No Chapters Available */}
      {!isLoading && !hasChapters && (
        <div className="my-6 p-6 bg-amber-50/70 border border-amber-200 rounded-2xl flex items-start gap-3 text-amber-900">
          <Info className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-bold mb-1">No Chapter Markers Found in Video</h4>
            <p className="text-xs text-amber-800 leading-relaxed">
              This YouTube video does not contain official chapter timestamps or description timestamps.
              Chapter slides and PowerPoint presentation export require chapter markers to extract representative slides.
            </p>
          </div>
        </div>
      )}

      {/* State C: Extraction Failed */}
      {!isLoading && status === 'failed' && extractedCount === 0 && (
        <div className="my-6 p-6 bg-red-50/70 border border-red-200 rounded-2xl flex items-start gap-3 text-red-900">
          <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-bold mb-1">Slide Extraction Failed</h4>
            <p className="text-xs text-red-800 leading-relaxed">
              {slidesData?.message ||
                'The video stream could not be accessed or downloaded for frame extraction. Please try again.'}
            </p>
          </div>
        </div>
      )}

      {/* State D: Slides Gallery Grid */}
      {!isLoading && slides.length > 0 && (
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {slides.map((slide) => {
            const isCompleted = slide.status === 'completed';
            const imgUrl = videoId ? getSlideImageUrl(videoId, slide.chapter_id) : '';

            return (
              <div
                key={slide.chapter_id}
                className={`group relative bg-gray-50/60 rounded-2xl border border-gray-200 overflow-hidden transition-all duration-200 hover:shadow-md hover:border-indigo-300 flex flex-col ${
                  isCompleted ? 'cursor-pointer' : 'opacity-85'
                }`}
                onClick={() => {
                  if (isCompleted) {
                    onOpenSlide(slide.chapter_id);
                  }
                }}
              >
                {/* Thumbnail Image Container */}
                <div className="relative aspect-video bg-gray-900 flex items-center justify-center overflow-hidden">
                  {isCompleted ? (
                    <>
                      <img
                        src={imgUrl}
                        alt={`Slide preview for ${slide.title}`}
                        loading="lazy"
                        onError={(e) => {
                          e.currentTarget.style.display = 'none';
                        }}
                        className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                      />
                      {/* Hover Overlay Button */}
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 text-white">
                        <span className="px-3 py-1.5 rounded-xl bg-white/20 backdrop-blur-md text-xs font-semibold flex items-center gap-1.5 border border-white/20 shadow-sm">
                          <Maximize2 className="w-3.5 h-3.5" />
                          <span>View Slide</span>
                        </span>
                      </div>
                    </>
                  ) : (
                    <div className="flex flex-col items-center justify-center p-4 text-center text-gray-400">
                      <AlertCircle className="w-6 h-6 text-amber-500 mb-1" />
                      <span className="text-[11px] font-medium text-gray-300">Extraction Failed</span>
                    </div>
                  )}

                  {/* Chapter Badge Overlay */}
                  <div className="absolute top-2.5 left-2.5">
                    <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-black/75 text-white backdrop-blur-md border border-white/10 shadow-sm">
                      Chapter {slide.chapter_index}
                    </span>
                  </div>

                  {/* Slide Status Badge */}
                  <div className="absolute top-2.5 right-2.5">
                    {isCompleted ? (
                      <span className="p-1 rounded-full bg-emerald-500/90 text-white shadow-sm" title="Slide Ready">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                      </span>
                    ) : (
                      <span className="p-1 rounded-full bg-amber-500/90 text-white shadow-sm" title="Failed to extract">
                        <AlertCircle className="w-3.5 h-3.5" />
                      </span>
                    )}
                  </div>
                </div>

                {/* Card Details */}
                <div className="p-4 flex-1 flex flex-col justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-gray-900 line-clamp-2 leading-snug group-hover:text-indigo-600 transition-colors">
                      {slide.title}
                    </h3>

                    <div className="mt-2.5 flex flex-wrap items-center gap-2 text-[11px] text-gray-500">
                      <span className="flex items-center gap-1 text-gray-600">
                        <Clock className="w-3 h-3 text-gray-400" />
                        <span>{slide.timestamp_str}</span>
                      </span>
                      <span className="text-gray-300">&bull;</span>
                      <span className="flex items-center gap-1 text-indigo-600 font-medium bg-indigo-50 px-1.5 py-0.5 rounded border border-indigo-100">
                        <Film className="w-3 h-3" />
                        <span>Frame at {slide.extraction_timestamp_str}</span>
                      </span>
                    </div>
                  </div>

                  {/* Action Link */}
                  {isCompleted && (
                    <div className="mt-3 pt-2.5 border-t border-gray-100 flex items-center justify-between text-xs text-indigo-600 font-semibold group-hover:underline">
                      <span>Click to preview</span>
                      <span>&rarr;</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
};
