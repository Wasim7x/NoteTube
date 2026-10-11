import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';
import { Header } from './Header';
import { VideoLoader } from './VideoLoader';
import { ModeSelector } from './ModeSelector';
import { ComingSoonView } from './ComingSoonView';
import { ChatbotDrawer } from './ChatbotDrawer';
import { jobStorage } from '../services/jobStorage';
import type {
  LoadVideoResponse,
  ProcessingMode,
  QuickSummaryResponse,
  DetailedNotesResponse,
  VideoSlidesResponse,
  GenerateNotesResponse,
  BackendHealthStatus,
} from '../types';

interface DashboardPageProps {
  selectedProvider: string;
  selectedModel: string;
  isCustomModel: boolean;
  customModel: string;
  apiKey: string;
  onNavigateToConfig: () => void;
  onResetSession?: () => void;
  loadedVideo: LoadVideoResponse | null;
  setLoadedVideo: React.Dispatch<React.SetStateAction<LoadVideoResponse | null>>;
  lastUrl: string;
  setLastUrl: React.Dispatch<React.SetStateAction<string>>;
  summaryData: QuickSummaryResponse | null;
  setSummaryData: React.Dispatch<React.SetStateAction<QuickSummaryResponse | null>>;
  detailedData: DetailedNotesResponse | null;
  setDetailedData: React.Dispatch<React.SetStateAction<DetailedNotesResponse | null>>;
  slidesData: VideoSlidesResponse | null;
  setSlidesData: React.Dispatch<React.SetStateAction<VideoSlidesResponse | null>>;
  completeNotesData: GenerateNotesResponse | null;
  setCompleteNotesData: React.Dispatch<React.SetStateAction<GenerateNotesResponse | null>>;
  backendStatus?: BackendHealthStatus;
  backendBaseUrl?: string;
  backendDetails?: string;
  onRetryHealthCheck?: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  selectedProvider,
  selectedModel,
  isCustomModel,
  customModel,
  apiKey,
  onNavigateToConfig,
  onResetSession,
  loadedVideo,
  setLoadedVideo,
  lastUrl,
  setLastUrl,
  summaryData,
  detailedData,
  slidesData,
  completeNotesData,
  setSummaryData,
  setDetailedData,
  setSlidesData,
  setCompleteNotesData,
  backendStatus,
  backendBaseUrl = 'http://127.0.0.1:8000',
  backendDetails,
  onRetryHealthCheck,
}) => {
  const navigate = useNavigate();
  const [selectedMode, setSelectedMode] = useState<ProcessingMode>('complete_notes');
  const [isChatOpen, setIsChatOpen] = useState<boolean>(false);
  const [comingSoonActive, setComingSoonActive] = useState<boolean>(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const getEffectiveModel = (): string => {
    if (isCustomModel) return customModel.trim();
    return selectedModel.trim();
  };

  const effectiveModel = getEffectiveModel();

  const handleVideoLoaded = (videoData: LoadVideoResponse, url: string) => {
    setLoadedVideo(videoData);
    setLastUrl(url);
    setValidationError(null);
    setComingSoonActive(false);

    // Save base job session to storage
    jobStorage.saveJob({
      jobId: videoData.video_id,
      url: url,
      videoData: videoData,
      selectedMode: selectedMode,
      summaryData: null,
      detailedData: null,
      slidesData: null,
      completeNotesData: null,
      lastUpdated: Date.now(),
    });

    // Reset previous outputs for new video
    setSummaryData(null);
    setDetailedData(null);
    setSlidesData(null);
    setCompleteNotesData(null);
  };

  const handleResetVideo = () => {
    setLoadedVideo(null);
    setLastUrl('');
    setValidationError(null);
    setComingSoonActive(false);
    setIsChatOpen(false);
    setSummaryData(null);
    setDetailedData(null);
    setSlidesData(null);
    setCompleteNotesData(null);
  };

  const handleSelectMode = (mode: ProcessingMode) => {
    setSelectedMode(mode);
    setValidationError(null);
    if (mode === 'unique_slides') {
      setComingSoonActive(true);
    } else {
      setComingSoonActive(false);
    }
  };

  const handleRunMode = (mode: ProcessingMode) => {
    if (!loadedVideo) {
      setValidationError('Please load a YouTube video first.');
      return;
    }

    // Mode 4: Advanced Unique Slides — Coming Soon (Do NOT run backend)
    if (mode === 'unique_slides') {
      setSelectedMode('unique_slides');
      setComingSoonActive(true);
      return;
    }

    setComingSoonActive(false);
    setValidationError(null);

    // Update current mode in storage
    const existing = jobStorage.getJob(loadedVideo.video_id);
    if (existing) {
      existing.selectedMode = mode;
      jobStorage.saveJob(existing);
    }

    // Navigate to dedicated results page (Page B)
    navigate(`/results/${encodeURIComponent(loadedVideo.video_id)}?mode=${mode}`);
  };

  // Status mapping for ModeSelector cards
  const modeStatusMap = {
    summary: { completed: Boolean(summaryData?.success) },
    detailed: { completed: Boolean(detailedData?.success) },
    chapter_slides: { completed: Boolean(slidesData?.status === 'completed') },
    unique_slides: { completed: false },
    complete_notes: { completed: Boolean(completeNotesData?.success) },
  };

  return (
    <div className="min-h-screen flex flex-col font-sans bg-gradient-to-b from-gray-50/60 via-white to-gray-50/40 text-gray-900">
      {/* Top Header */}
      <Header
        currentPage="workspace"
        onNavigateToConfig={onNavigateToConfig}
        onResetSession={onResetSession}
        providerName={selectedProvider}
        modelName={effectiveModel}
        isChatOpen={isChatOpen}
        onToggleChat={() => setIsChatOpen(!isChatOpen)}
        hasVideoLoaded={Boolean(loadedVideo?.video_id)}
        backendStatus={backendStatus}
        backendBaseUrl={backendBaseUrl}
        backendDetails={backendDetails}
        onRetryHealthCheck={onRetryHealthCheck}
      />

      {/* Main Dashboard Area */}
      <div className="flex-1 flex flex-row relative overflow-x-hidden">
        <main
          className={`flex-1 transition-all duration-300 px-4 pb-20 max-w-6xl mx-auto w-full ${
            isChatOpen ? 'lg:mr-[420px]' : ''
          }`}
        >
          {/* Health Status Warning Banner */}
          {backendStatus === 'offline' && (
            <div className="w-full max-w-4xl mx-auto my-4 p-4 bg-amber-50 border border-amber-200 text-amber-800 rounded-2xl flex items-center justify-between gap-3 shadow-2xs animate-in fade-in">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-amber-600 shrink-0" />
                <span className="text-xs font-medium">
                  <strong>Backend Offline:</strong> Unable to connect to the NoteTube FastAPI server at <code className="bg-amber-100/80 px-1 py-0.5 rounded font-mono">{backendBaseUrl}</code>. Please verify the backend is running.
                </span>
              </div>
              {onRetryHealthCheck && (
                <button
                  type="button"
                  onClick={onRetryHealthCheck}
                  className="px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-xs font-semibold shrink-0 transition-all cursor-pointer shadow-2xs"
                >
                  Retry Connection
                </button>
              )}
            </div>
          )}

          {backendStatus === 'timeout' && (
            <div className="w-full max-w-4xl mx-auto my-4 p-4 bg-amber-50 border border-amber-200 text-amber-800 rounded-2xl flex items-center justify-between gap-3 shadow-2xs animate-in fade-in">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-amber-600 shrink-0" />
                <span className="text-xs font-medium">
                  <strong>Connection Timeout:</strong> Health check request to NoteTube FastAPI server at <code className="bg-amber-100/80 px-1 py-0.5 rounded font-mono">{backendBaseUrl}</code> timed out.
                </span>
              </div>
              {onRetryHealthCheck && (
                <button
                  type="button"
                  onClick={onRetryHealthCheck}
                  className="px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-xs font-semibold shrink-0 transition-all cursor-pointer shadow-2xs"
                >
                  Retry Connection
                </button>
              )}
            </div>
          )}

          {backendStatus === 'error' && (
            <div className="w-full max-w-4xl mx-auto my-4 p-4 bg-red-50 border border-red-200 text-red-800 rounded-2xl flex items-center justify-between gap-3 shadow-2xs animate-in fade-in">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
                <span className="text-xs font-medium">
                  <strong>Backend Error:</strong> NoteTube server responded with an error{backendDetails ? `: ${backendDetails}` : '.'}
                </span>
              </div>
              {onRetryHealthCheck && (
                <button
                  type="button"
                  onClick={onRetryHealthCheck}
                  className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-semibold shrink-0 transition-all cursor-pointer shadow-2xs"
                >
                  Retry Connection
                </button>
              )}
            </div>
          )}

          {/* Step 2: YouTube Video Input or Loaded Video Summary Card */}
          <VideoLoader
            loadedVideo={loadedVideo}
            isLoading={false}
            onVideoLoaded={handleVideoLoaded}
            onResetVideo={handleResetVideo}
            lastUrl={lastUrl}
          />

          {/* Validation Error Banner */}
          {validationError && (
            <div className="w-full max-w-4xl mx-auto my-4 p-4 bg-red-50 border border-red-200 text-red-800 rounded-2xl flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
              <span className="text-xs font-medium">{validationError}</span>
            </div>
          )}

          {/* When Video is Loaded: Display the Five Processing Mode Cards */}
          {loadedVideo && (
            <>
              <ModeSelector
                selectedMode={selectedMode}
                onSelectMode={handleSelectMode}
                onRunMode={handleRunMode}
                isProcessing={false}
                modeStatus={modeStatusMap}
              />

              {/* Mode 4 Coming Soon Preview (Only if selected) */}
              {comingSoonActive && (
                <div className="mt-4 animate-in fade-in duration-300">
                  <ComingSoonView />
                </div>
              )}
            </>
          )}
        </main>

        {/* RAG-Based Transcript Chatbot Panel */}
        {loadedVideo && (
          <ChatbotDrawer
            isOpen={isChatOpen}
            onClose={() => setIsChatOpen(false)}
            videoId={loadedVideo.video_id}
            videoTitle={loadedVideo.video?.title || 'Loaded Video'}
            provider={selectedProvider}
            model={effectiveModel}
            apiKey={apiKey.trim()}
          />
        )}
      </div>
    </div>
  );
};
