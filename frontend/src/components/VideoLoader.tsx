import React, { useState } from 'react';
import {
  ArrowRight,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Languages,
  ExternalLink,
  RotateCcw
} from 'lucide-react';
import { api } from '../services/api';
import type { LoadVideoResponse } from '../types';

const Youtube = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M2.5 7.1C2.3 8.3 2.2 9.5 2.2 12c0 2.5.1 3.7.3 4.9.2 1.3 1.1 2.4 2.4 2.6 1.4.2 4.5.3 7.1.3s5.7-.1 7.1-.3c1.3-.2 2.2-1.3 2.4-2.6.2-1.2.3-2.4.3-4.9 0-2.5-.1-3.7-.3-4.9-.2-1.3-1.1-2.4-2.4-2.6-1.4-.2-4.5-.3-7.1-.3s-5.7.1-7.1.3c-1.3.2-2.2 1.3-2.4 2.6z" />
    <path d="m10 8 6 4-6 4z" />
  </svg>
);

interface VideoLoaderProps {
  loadedVideo: LoadVideoResponse | null;
  isLoading: boolean;
  onVideoLoaded: (videoData: LoadVideoResponse, url: string) => void;
  onResetVideo: () => void;
  lastUrl: string;
}

export const VideoLoader: React.FC<VideoLoaderProps> = ({
  loadedVideo,
  isLoading,
  onVideoLoaded,
  onResetVideo,
  lastUrl,
}) => {
  const [url, setUrl] = useState(lastUrl || '');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const trimmed = url.trim();
    if (!trimmed) {
      setError('Please enter a YouTube video URL.');
      return;
    }

    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
    if (!youtubeRegex.test(trimmed)) {
      setError('Please enter a valid YouTube video URL (e.g., https://www.youtube.com/watch?v=...)');
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await api.loadVideo(trimmed);
      if (!res.success) {
        throw new Error(res.error || 'Failed to extract video information or transcript.');
      }
      onVideoLoaded(res, trimmed);
    } catch (err: any) {
      setError(err.message || 'Could not load video. Please verify the URL and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto my-6 animate-in fade-in duration-300">
      {/* If no video is loaded yet, show the URL input bar */}
      {!loadedVideo && (
        <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6 sm:p-8">
          <div className="text-center mb-6">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 tracking-tight mb-2">
              Step 2: Enter YouTube Video
            </h2>
            <p className="text-sm text-gray-500">
              Fetch metadata, chapters, and transcript once — then run any processing mode.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative flex items-center w-full h-16 rounded-2xl bg-gray-50/70 border border-gray-200 hover:border-gray-300 focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20 transition-all overflow-hidden">
              <div className="pl-5 text-red-600">
                <Youtube className="w-6 h-6" />
              </div>
              <input
                id="youtube-url-input"
                type="url"
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value);
                  if (error) setError(null);
                }}
                disabled={isSubmitting || isLoading}
                placeholder="Paste YouTube video URL here (e.g. https://www.youtube.com/watch?v=...)"
                className="w-full h-full bg-transparent border-none outline-none px-4 text-gray-800 placeholder:text-gray-400 text-sm sm:text-base"
              />
              <button
                id="load-video-button"
                type="submit"
                disabled={isSubmitting || isLoading || !url.trim()}
                className="h-12 mr-2 px-6 bg-primary hover:bg-primaryHover text-white rounded-xl font-medium text-sm flex items-center justify-center gap-2 transition-all shadow-xs active:scale-98 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Loading...</span>
                  </>
                ) : (
                  <>
                    <span>Load Video</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>

            {error && (
              <div className="p-3.5 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}
          </form>
        </div>
      )}

      {/* If a video is already loaded, show the Loaded Video Summary Card */}
      {loadedVideo && loadedVideo.video && (
        <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-5 sm:p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 flex-1 min-w-0">
            <div className="relative group shrink-0">
              <img
                src={loadedVideo.video.thumbnail}
                alt={loadedVideo.video.title}
                className="w-full sm:w-48 aspect-video object-cover rounded-2xl shadow-xs border border-gray-100"
              />
              <span className="absolute bottom-2 right-2 px-2 py-0.5 rounded bg-black/80 text-white text-[10px] font-mono">
                {loadedVideo.has_chapters ? `${loadedVideo.total_chapters} chapters` : 'No chapters'}
              </span>
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-700 border border-emerald-200">
                  <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                  Ready
                </span>
                {loadedVideo.transcript_language && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium bg-gray-100 text-gray-700">
                    <Languages className="w-3 h-3 text-gray-500" />
                    {loadedVideo.transcript_language}
                  </span>
                )}
                <span className="text-[11px] text-gray-500 font-mono">
                  {loadedVideo.transcript_char_count?.toLocaleString()} chars
                </span>
              </div>

              <h2 className="text-base sm:text-lg font-bold text-gray-900 leading-snug truncate">
                {loadedVideo.video.title}
              </h2>

              <div className="flex items-center gap-3 mt-1.5 text-xs text-gray-500">
                <span>{loadedVideo.video.channel || 'YouTube'}</span>
                <span>&bull;</span>
                <a
                  href={lastUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="text-primary hover:underline flex items-center gap-1 font-medium"
                >
                  <span>Watch on YouTube</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          </div>

          {/* Reset / Change Video Button */}
          <button
            type="button"
            onClick={onResetVideo}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 transition-all cursor-pointer self-end md:self-center shrink-0"
            title="Load another YouTube video"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Change Video</span>
          </button>
        </div>
      )}
    </div>
  );
};
