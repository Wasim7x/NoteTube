import React, { useState } from 'react';
import { ArrowRight } from 'lucide-react';

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

interface UrlInputProps {
  onSubmit: (url: string) => void;
  isLoading: boolean;
  children?: React.ReactNode;
  hasApiKey: boolean;
  onMissingApiKey: () => void;
}

export const UrlInput: React.FC<UrlInputProps> = ({
  onSubmit,
  isLoading,
  children,
  hasApiKey,
  onMissingApiKey,
}) => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!url.trim()) {
      setError('Please enter a YouTube video URL.');
      return;
    }

    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
    if (!youtubeRegex.test(url.trim())) {
      setError('Please enter a valid YouTube video URL (e.g. https://www.youtube.com/watch?v=...)');
      return;
    }

    if (!hasApiKey) {
      onMissingApiKey();
      return;
    }

    onSubmit(url.trim());
  };

  return (
    <div className="w-full max-w-2xl mx-auto mt-12 px-4">
      <div className="text-center mb-8">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-3 tracking-tight">
          Turn any video into <span className="text-primary">structured notes.</span>
        </h1>
        <p className="text-base md:text-lg text-gray-500">
          Extract transcript &bull; Select any AI model &bull; Generate rich study notes
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Dynamic Model Configuration Section */}
        {children}

        {/* YouTube URL input */}
        <div className="relative">
          <div className="relative flex items-center w-full h-16 rounded-2xl bg-white shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100 hover:border-gray-200 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all overflow-hidden focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary">
            <div className="pl-5 text-red-600">
              <Youtube className="w-6 h-6" />
            </div>
            <input
              id="youtube-url-input"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isLoading}
              placeholder="Paste YouTube video URL here..."
              className="w-full h-full bg-transparent border-none outline-none px-4 text-gray-800 placeholder:text-gray-400 text-base"
            />
            <button
              id="generate-notes-button"
              type="submit"
              disabled={isLoading}
              className="h-12 mr-2 px-6 bg-primary hover:bg-primaryHover text-white rounded-xl font-medium flex items-center justify-center gap-2 transition-all shadow-sm hover:shadow active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed cursor-pointer"
            >
              <span className="hidden sm:inline">Generate Notes</span>
              <span className="sm:hidden">Generate</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          {error && (
            <p className="mt-2 text-sm text-red-500 font-medium px-2">
              {error}
            </p>
          )}
        </div>
      </form>
    </div>
  );
};
