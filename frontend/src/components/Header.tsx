import React from 'react';
import { BookOpen, Cpu, Settings2, Sparkles, ArrowLeft, RotateCcw } from 'lucide-react';
import geminiChatbotSvg from '../assets/gemini-chatbot.svg';
import type { BackendHealthStatus } from '../types';

interface HeaderProps {
  currentPage?: 'config' | 'workspace' | 'results';
  onNavigateToConfig?: () => void;
  onNavigateToWorkspace?: () => void;
  onResetSession?: () => void;
  providerName?: string;
  modelName?: string;
  isChatOpen?: boolean;
  onToggleChat?: () => void;
  hasVideoLoaded?: boolean;
  // Compact Results Header Props (Page B)
  videoTitle?: string;
  modeLabel?: string;
  modeBadgeColor?: string;
  onBackToProcessing?: () => void;
  // Backend Health Status Props
  backendStatus?: BackendHealthStatus;
  backendBaseUrl?: string;
  backendDetails?: string;
  onRetryHealthCheck?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentPage = 'config',
  onNavigateToConfig,
  onNavigateToWorkspace,
  onResetSession,
  providerName,
  modelName,
  isChatOpen,
  onToggleChat,
  hasVideoLoaded = false,
  videoTitle,
  modeLabel,
  modeBadgeColor = 'bg-primary/10 text-primary border-primary/20',
  onBackToProcessing,
  backendStatus,
  backendBaseUrl = 'http://127.0.0.1:8000',
  backendDetails,
  onRetryHealthCheck,
}) => {
  return (
    <header className="w-full bg-white/90 backdrop-blur-md border-b border-gray-100 sticky top-0 z-40 transition-all">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between gap-3 sm:gap-4">
        {/* Left Section */}
        {currentPage === 'results' ? (
          /* PAGE B: Compact Header Left Controls */
          <div className="flex items-center gap-2.5 sm:gap-3 min-w-0 flex-1">
            {onBackToProcessing && (
              <button
                type="button"
                onClick={onBackToProcessing}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-gray-700 hover:text-gray-900 bg-gray-100 hover:bg-gray-200/80 transition-all cursor-pointer shrink-0 shadow-2xs"
                title="Back to Processing Dashboard"
              >
                <ArrowLeft className="w-4 h-4 text-gray-600" />
                <span className="hidden sm:inline">Back to Processing</span>
                <span className="sm:hidden">Back</span>
              </button>
            )}

            <div className="w-px h-6 bg-gray-200 hidden sm:block shrink-0" />

            {/* Video Title and Mode Badge */}
            <div className="flex items-center gap-2 min-w-0 flex-1">
              {modeLabel && (
                <span
                  className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border shrink-0 ${modeBadgeColor}`}
                >
                  {modeLabel}
                </span>
              )}
              {videoTitle && (
                <span
                  className="font-bold text-sm text-gray-900 truncate max-w-[180px] sm:max-w-xs md:max-w-md"
                  title={videoTitle}
                >
                  {videoTitle}
                </span>
              )}
            </div>
          </div>
        ) : (
          /* PAGE A / CONFIG: Standard NoteTube Brand */
          <div
            className="flex items-center gap-3 cursor-pointer select-none"
            onClick={onNavigateToWorkspace}
          >
            <div className="bg-primary/10 p-2 rounded-xl text-primary flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-primary" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 via-primary to-indigo-600">
                  NoteTube
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">
                  v2.0
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Right Section: Config Badge, Edit Settings, and Chatbot Launcher */}
        <div className="flex items-center gap-2 sm:gap-3 shrink-0">
          {/* Backend Status Indicator */}
          {backendStatus === 'online' && (
            <div
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-emerald-50 border border-emerald-200/80 text-[11px] font-medium text-emerald-700 shadow-2xs select-none"
              title={`Backend is connected and healthy (${backendBaseUrl})`}
            >
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="font-semibold hidden sm:inline">Backend</span>
              <span className="font-semibold">Online</span>
            </div>
          )}

          {backendStatus === 'offline' && (
            <button
              type="button"
              onClick={onRetryHealthCheck}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-rose-50 hover:bg-rose-100/80 border border-rose-200 text-[11px] font-medium text-rose-700 shadow-2xs transition-all cursor-pointer"
              title={`Backend is offline (${backendBaseUrl}). Click to retry.`}
            >
              <span className="inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
              <span className="font-semibold">Backend Offline</span>
              <span className="text-[10px] underline ml-0.5 opacity-80">Retry</span>
            </button>
          )}

          {backendStatus === 'timeout' && (
            <button
              type="button"
              onClick={onRetryHealthCheck}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-amber-50 hover:bg-amber-100/80 border border-amber-200 text-[11px] font-medium text-amber-700 shadow-2xs transition-all cursor-pointer"
              title={`Backend health check timed out (${backendBaseUrl}). Click to retry.`}
            >
              <span className="inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
              <span className="font-semibold">Connection Timeout</span>
              <span className="text-[10px] underline ml-0.5 opacity-80">Retry</span>
            </button>
          )}

          {backendStatus === 'error' && (
            <button
              type="button"
              onClick={onRetryHealthCheck}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-red-50 hover:bg-red-100/80 border border-red-200 text-[11px] font-medium text-red-700 shadow-2xs transition-all cursor-pointer"
              title={`Backend error: ${backendDetails || 'Unexpected response'}. Click to retry.`}
            >
              <span className="inline-flex rounded-full h-2 w-2 bg-red-500"></span>
              <span className="font-semibold">Backend Error</span>
              <span className="text-[10px] underline ml-0.5 opacity-80">Retry</span>
            </button>
          )}

          {backendStatus === 'checking' && (
            <div
              className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-amber-50 border border-amber-200 text-[11px] font-medium text-amber-700 shadow-2xs select-none"
              title="Checking backend connection..."
            >
              <span className="inline-flex rounded-full h-2 w-2 bg-amber-400 animate-pulse"></span>
              <span>Connecting...</span>
            </div>
          )}

          {/* Active Model Indicator */}
          {providerName && currentPage !== 'config' && (
            <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gray-50 border border-gray-200/70 text-xs text-gray-700">
              <Cpu className="w-3.5 h-3.5 text-primary" />
              <span className="font-semibold text-gray-900 capitalize">{providerName}</span>
              <span className="text-gray-300">/</span>
              <span className="font-mono text-gray-600 max-w-[120px] truncate" title={modelName}>
                {modelName || 'default'}
              </span>
            </div>
          )}

          {/* Edit Model Configuration Button */}
          {currentPage !== 'config' && onNavigateToConfig && (
            <button
              type="button"
              onClick={onNavigateToConfig}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium text-gray-600 hover:text-gray-900 bg-gray-100/80 hover:bg-gray-200/70 transition-all cursor-pointer"
              title="Change AI model or provider configuration"
            >
              <Settings2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Change Model</span>
            </button>
          )}

          {/* Reset Session Option (Fresh Session) */}
          {onResetSession && (
            <button
              type="button"
              onClick={onResetSession}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-medium text-gray-500 hover:text-rose-600 hover:bg-rose-50 transition-all cursor-pointer"
              title="Start a fresh session"
            >
              <RotateCcw className="w-3 h-3" />
              <span className="hidden lg:inline text-[11px]">New Session</span>
            </button>
          )}

          {/* RAG Chatbot Button with Uploaded Animated SVG Logo */}
          {onToggleChat && (currentPage === 'workspace' || currentPage === 'results') && (
            <button
              type="button"
              onClick={onToggleChat}
              disabled={!hasVideoLoaded}
              aria-label="Ask about this video"
              title={hasVideoLoaded ? "Ask about this video" : "Load a video first to ask questions"}
              className={`flex items-center gap-2 px-3 sm:px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer shadow-xs active:scale-95 ${
                isChatOpen
                  ? 'bg-primary text-white shadow-primary/20 ring-2 ring-primary/30'
                  : hasVideoLoaded
                  ? 'bg-gradient-to-r from-primary to-indigo-600 hover:from-primaryHover hover:to-indigo-700 text-white shadow-sm'
                  : 'bg-gray-100 text-gray-400 cursor-not-allowed opacity-60'
              }`}
            >
              <img
                src={geminiChatbotSvg}
                alt="AI Chatbot"
                className="w-5 h-5 shrink-0 object-contain drop-shadow-2xs"
              />
              <span className="hidden sm:inline">Ask about this video</span>
              <span className="text-[10px] bg-white/20 px-1.5 py-0.5 rounded font-mono">
                RAG
              </span>
            </button>
          )}

          {currentPage === 'config' && (
            <div className="text-xs font-medium text-gray-500 hidden sm:flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-primary" />
              <span>Step 1: Configure AI Model</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

