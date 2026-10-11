import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  Loader2,
  RefreshCcw,
  ArrowLeft,
  FileQuestion,
  Zap,
  BookOpen,
  Presentation,
  Layers,
} from 'lucide-react';
import { Header } from './Header';
import { QuickSummaryView } from './QuickSummaryView';
import { DetailedNotesView } from './DetailedNotesView';
import { SlidesGallery } from './SlidesGallery';
import { SlidePreviewModal } from './SlidePreviewModal';
import { NotesViewer } from './NotesViewer';
import { LoadingState } from './LoadingState';
import { Actions } from './Actions';
import { ChatbotDrawer } from './ChatbotDrawer';
import { api } from '../services/api';
import { jobStorage } from '../services/jobStorage';
import type {
  GenerateNotesResponse,
  VideoMetadata,
  ChapterItem,
  VideoSlidesResponse,
  LoadVideoResponse,
  ProcessingMode,
  QuickSummaryResponse,
  DetailedNotesResponse,
  BackendHealthStatus,
} from '../types';

interface ResultsPageProps {
  selectedProvider: string;
  selectedModel: string;
  isCustomModel: boolean;
  customModel: string;
  apiKey: string;
  onNavigateToConfig: () => void;
  onResetSession?: () => void;
  // Shared in-memory state passed from App
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

const MODE_CONFIGS: Record<
  ProcessingMode,
  { label: string; badgeColor: string; icon: React.ComponentType<{ className?: string }> }
> = {
  summary: {
    label: 'Quick Summary',
    badgeColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    icon: Zap,
  },
  detailed: {
    label: 'Detailed Notes',
    badgeColor: 'bg-blue-50 text-blue-700 border-blue-200',
    icon: BookOpen,
  },
  chapter_slides: {
    label: 'Chapter-End Slides',
    badgeColor: 'bg-purple-50 text-purple-700 border-purple-200',
    icon: Presentation,
  },
  unique_slides: {
    label: 'Advanced Unique Slides',
    badgeColor: 'bg-amber-50 text-amber-700 border-amber-200',
    icon: Zap,
  },
  complete_notes: {
    label: 'Complete AI Notes',
    badgeColor: 'bg-rose-50 text-rose-700 border-rose-200',
    icon: Layers,
  },
};

export const ResultsPage: React.FC<ResultsPageProps> = ({
  selectedProvider,
  selectedModel,
  isCustomModel,
  customModel,
  apiKey,
  onNavigateToConfig,
  loadedVideo,
  setLoadedVideo,
  lastUrl,
  setLastUrl,
  summaryData,
  setSummaryData,
  detailedData,
  setDetailedData,
  slidesData,
  setSlidesData,
  completeNotesData,
  setCompleteNotesData,
  backendStatus,
  backendBaseUrl,
  backendDetails,
  onResetSession,
  onRetryHealthCheck,
}) => {
  const { jobId } = useParams<{ jobId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const activeModeParam = (searchParams.get('mode') as ProcessingMode) || 'complete_notes';
  const [activeMode, setActiveMode] = useState<ProcessingMode>(activeModeParam);

  // Status & error state
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState<boolean>(false);

  // Streaming state for Complete Notes
  const [statusMessage, setStatusMessage] = useState<string>('Analyzing video & transcript...');
  const [currentChapterNum, setCurrentChapterNum] = useState<number | undefined>(undefined);
  const [totalChapters, setTotalChapters] = useState<number | undefined>(undefined);
  const [currentChapterTitle, setCurrentChapterTitle] = useState<string | undefined>(undefined);
  const [progressiveVideo, setProgressiveVideo] = useState<VideoMetadata | null>(null);
  const [progressiveOverview, setProgressiveOverview] = useState<string>('');
  const [progressiveChapters, setProgressiveChapters] = useState<ChapterItem[]>([]);
  const [progressiveRevision, setProgressiveRevision] = useState<string>('');

  // Modals & Chatbot drawer state
  const [activeSlideChapterId, setActiveSlideChapterId] = useState<string | null>(null);
  const [isChatOpen, setIsChatOpen] = useState<boolean>(false);

  // Prevent multiple executions on mount
  const hasTriggeredRef = useRef<boolean>(false);

  const getEffectiveModel = (): string => {
    if (isCustomModel) return customModel.trim();
    return selectedModel.trim();
  };

  const effectiveModel = getEffectiveModel();
  const currentVideoId = jobId || loadedVideo?.video_id;

  // Sync mode from search param
  useEffect(() => {
    if (activeModeParam && activeModeParam !== activeMode) {
      setActiveMode(activeModeParam);
    }
  }, [activeModeParam]);

  // Execute processing for a specific mode
  const executeProcessing = useCallback(
    async (modeToRun: ProcessingMode, videoToUse: LoadVideoResponse, urlToUse: string) => {
      setIsLoading(true);
      setError(null);
      const vidId = videoToUse.video_id;

      try {
        if (modeToRun === 'summary') {
          const res = await api.generateQuickSummary({
            video_id: vidId,
            youtube_url: urlToUse,
            provider: selectedProvider,
            model: effectiveModel,
            api_key: apiKey.trim(),
          });
          if (!res.success) throw new Error(res.error || 'Quick summary generation failed.');
          setSummaryData(res);
          jobStorage.updateResult(vidId, 'summary', res);
        } else if (modeToRun === 'detailed') {
          const res = await api.generateDetailedNotes({
            video_id: vidId,
            youtube_url: urlToUse,
            provider: selectedProvider,
            model: effectiveModel,
            api_key: apiKey.trim(),
          });
          if (!res.success) throw new Error(res.error || 'Detailed notes generation failed.');
          setDetailedData(res);
          jobStorage.updateResult(vidId, 'detailed', res);
        } else if (modeToRun === 'chapter_slides') {
          const res = await api.extractSlides({
            video_id: vidId,
            youtube_url: urlToUse,
            chapters: videoToUse.chapters,
          });
          if (res.status === 'failed' && res.error) throw new Error(res.error);
          setSlidesData(res);
          jobStorage.updateResult(vidId, 'chapter_slides', res);
        } else if (modeToRun === 'complete_notes') {
          setStatusMessage('Analyzing video & transcript...');
          setCurrentChapterNum(undefined);
          setTotalChapters(undefined);
          setCurrentChapterTitle(undefined);
          setProgressiveVideo(null);
          setProgressiveOverview('');
          setProgressiveChapters([]);
          setProgressiveRevision('');
          setCompleteNotesData(null);

          const payload = {
            youtube_url: urlToUse,
            provider: selectedProvider,
            model: effectiveModel,
            api_key: apiKey.trim(),
          };

          try {
            const result = await api.generateNotesStream(payload, (event) => {
              if (event.type === 'status' && event.message) {
                setStatusMessage(event.message);
              } else if (event.type === 'metadata') {
                if (event.video) setProgressiveVideo(event.video);
                if (event.total_chapters) setTotalChapters(event.total_chapters);
              } else if (event.type === 'overview') {
                if (event.overview_content) setProgressiveOverview(event.overview_content);
              } else if (event.type === 'chapter_start') {
                if (event.message) setStatusMessage(event.message);
                if (event.chapter_num !== undefined) setCurrentChapterNum(event.chapter_num);
                if (event.total !== undefined) setTotalChapters(event.total);
                if (event.title) setCurrentChapterTitle(event.title);
              } else if (event.type === 'chapter_complete') {
                if (event.chapter) {
                  setProgressiveChapters((prev) => {
                    const updated = [...prev];
                    const idx = event.index ?? updated.length;
                    updated[idx] = event.chapter;
                    return updated;
                  });
                }
              } else if (event.type === 'revision') {
                if (event.revision_content) setProgressiveRevision(event.revision_content);
              }
            });

            setCompleteNotesData(result);
            jobStorage.updateResult(vidId, 'complete_notes', result);

            // Extract slides in background if not already available
            if (result.success && result.video?.id) {
              api.getSlides(result.video.id).then((existingSlides) => {
                if (existingSlides && existingSlides.status === 'completed') {
                  setSlidesData(existingSlides);
                  jobStorage.updateResult(vidId, 'chapter_slides', existingSlides);
                } else {
                  api
                    .extractSlides({
                      video_id: result.video!.id,
                      youtube_url: urlToUse,
                      chapters: result.video!.chapters || result.chapters,
                    })
                    .then((sRes) => {
                      setSlidesData(sRes);
                      jobStorage.updateResult(vidId, 'chapter_slides', sRes);
                    })
                    .catch(() => {});
                }
              });
            }
          } catch (streamErr) {
            console.warn('SSE stream failed, falling back to standard endpoint...', streamErr);
            const fallbackResult = await api.generateNotes(payload);
            setCompleteNotesData(fallbackResult);
            jobStorage.updateResult(vidId, 'complete_notes', fallbackResult);
          }
        }
      } catch (err: any) {
        console.error(`Error running mode ${modeToRun}:`, err);
        setError(err.message || 'Operation failed. Please try again.');
      } finally {
        setIsLoading(false);
      }
    },
    [
      selectedProvider,
      effectiveModel,
      apiKey,
      setSummaryData,
      setDetailedData,
      setSlidesData,
      setCompleteNotesData,
    ]
  );

  // Initial Load / Refresh Recovery Lifecycle
  useEffect(() => {
    if (!jobId) {
      setNotFound(true);
      return;
    }

    const initPage = async () => {
      // 1. Check in-memory state or localStorage
      let currentVideo = loadedVideo;
      let currentUrl = lastUrl;

      const stored = jobStorage.getJob(jobId);
      if (stored) {
        if (!currentVideo) {
          currentVideo = stored.videoData;
          setLoadedVideo(stored.videoData);
        }
        if (!currentUrl) {
          currentUrl = stored.url;
          setLastUrl(stored.url);
        }
        if (stored.summaryData && !summaryData) setSummaryData(stored.summaryData);
        if (stored.detailedData && !detailedData) setDetailedData(stored.detailedData);
        if (stored.slidesData && !slidesData) setSlidesData(stored.slidesData);
        if (stored.completeNotesData && !completeNotesData) setCompleteNotesData(stored.completeNotesData);
      }

      // 2. If video metadata still absent, fetch from backend job cache
      if (!currentVideo) {
        try {
          const backendVideo = await api.getVideoJob(jobId);
          if (backendVideo && backendVideo.success) {
            currentVideo = backendVideo;
            currentUrl = `https://www.youtube.com/watch?v=${jobId}`;
            setLoadedVideo(backendVideo);
            setLastUrl(currentUrl);

            // Persist base job session
            jobStorage.saveJob({
              jobId: jobId,
              url: currentUrl,
              videoData: backendVideo,
              selectedMode: activeMode,
              summaryData: summaryData || stored?.summaryData,
              detailedData: detailedData || stored?.detailedData,
              slidesData: slidesData || stored?.slidesData,
              completeNotesData: completeNotesData || stored?.completeNotesData,
              lastUpdated: Date.now(),
            });
          } else {
            setNotFound(true);
            return;
          }
        } catch {
          setNotFound(true);
          return;
        }
      }

      // 3. For Chapter-End Slides mode, also check backend slides cache
      if (activeMode === 'chapter_slides' && (!slidesData || slidesData.status !== 'completed')) {
        try {
          const existingSlides = await api.getSlides(jobId);
          if (existingSlides && existingSlides.status === 'completed') {
            setSlidesData(existingSlides);
            jobStorage.updateResult(jobId, 'chapter_slides', existingSlides);
            return; // Already completed, no need to execute
          }
        } catch {
          // Continue to execution if not found
        }
      }

      // 4. Check if the active mode is already completed
      const isAlreadyCompleted =
        (activeMode === 'summary' && (summaryData?.success || stored?.summaryData?.success)) ||
        (activeMode === 'detailed' && (detailedData?.success || stored?.detailedData?.success)) ||
        (activeMode === 'chapter_slides' && (slidesData?.status === 'completed' || stored?.slidesData?.status === 'completed')) ||
        (activeMode === 'complete_notes' && (completeNotesData?.success || stored?.completeNotesData?.success));

      if (isAlreadyCompleted) {
        // Output already exists, do NOT generate twice
        return;
      }

      // 5. If not yet generated and hasn't triggered yet, run processing
      if (!hasTriggeredRef.current && currentVideo) {
        hasTriggeredRef.current = true;
        executeProcessing(activeMode, currentVideo, currentUrl);
      }
    };

    initPage();
  }, [
    jobId,
    activeMode,
    executeProcessing,
    loadedVideo,
    lastUrl,
    summaryData,
    detailedData,
    slidesData,
    completeNotesData,
    setLoadedVideo,
    setLastUrl,
    setSummaryData,
    setDetailedData,
    setSlidesData,
    setCompleteNotesData,
  ]);

  const handleRetry = () => {
    if (loadedVideo) {
      executeProcessing(activeMode, loadedVideo, lastUrl);
    }
  };

  const handleBackToProcessing = () => {
    navigate('/video');
  };

  // Determine current markdown content for Actions toolbar
  const getActiveMarkdownContent = (): { content: string; title: string } | null => {
    if (activeMode === 'complete_notes' && completeNotesData?.success && completeNotesData.notes) {
      return {
        content: completeNotesData.notes.content,
        title: completeNotesData.notes.title || loadedVideo?.video?.title || 'NoteTube Notes',
      };
    }
    if (activeMode === 'detailed' && detailedData?.success) {
      return {
        content: detailedData.markdown_content,
        title: detailedData.title || loadedVideo?.video?.title || 'Detailed Notes',
      };
    }
    if (activeMode === 'summary' && summaryData?.success) {
      return {
        content: summaryData.markdown_content || summaryData.summary,
        title: summaryData.title || loadedVideo?.video?.title || 'Quick Summary',
      };
    }
    return null;
  };

  const activeMarkdown = getActiveMarkdownContent();
  const isProgressiveActive =
    isLoading &&
    activeMode === 'complete_notes' &&
    (Boolean(progressiveOverview) || progressiveChapters.length > 0);

  const modeConfig = MODE_CONFIGS[activeMode] || MODE_CONFIGS.complete_notes;
  const videoTitle =
    loadedVideo?.video?.title || completeNotesData?.video?.title || 'Video Processing Results';

  // State: Job Not Found or Session Expired
  if (notFound) {
    return (
      <div className="min-h-screen flex flex-col font-sans bg-gray-50/50 text-gray-900">
        <Header
          currentPage="results"
          onBackToProcessing={handleBackToProcessing}
          onNavigateToConfig={onNavigateToConfig}
          onResetSession={onResetSession}
          providerName={selectedProvider}
          modelName={effectiveModel}
          hasVideoLoaded={false}
          backendStatus={backendStatus}
          backendBaseUrl={backendBaseUrl}
          backendDetails={backendDetails}
          onRetryHealthCheck={onRetryHealthCheck}
        />
        <main className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-white rounded-3xl p-8 border border-gray-100 shadow-sm text-center animate-in fade-in">
            <div className="w-14 h-14 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto mb-4 border border-amber-100">
              <FileQuestion className="w-7 h-7" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Processing Job Not Found</h3>
            <p className="text-xs text-gray-500 leading-relaxed mb-6">
              The requested video session was not found in active memory or durable cache. Please
              return to the processing dashboard to paste a YouTube video URL.
            </p>
            <button
              type="button"
              onClick={handleBackToProcessing}
              className="w-full py-2.5 px-4 bg-primary hover:bg-primaryHover text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer shadow-xs"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Processing Dashboard</span>
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col font-sans bg-gradient-to-b from-gray-50/60 via-white to-gray-50/40 text-gray-900">
      {/* Page B Compact Header with Back Button, Video Title, Mode Label, Model, and Chatbot */}
      <Header
        currentPage="results"
        onBackToProcessing={handleBackToProcessing}
        onNavigateToConfig={onNavigateToConfig}
        onResetSession={onResetSession}
        providerName={selectedProvider}
        modelName={effectiveModel}
        isChatOpen={isChatOpen}
        onToggleChat={() => setIsChatOpen(!isChatOpen)}
        hasVideoLoaded={Boolean(currentVideoId)}
        videoTitle={videoTitle}
        modeLabel={modeConfig.label}
        modeBadgeColor={modeConfig.badgeColor}
        backendStatus={backendStatus}
        backendBaseUrl={backendBaseUrl}
        backendDetails={backendDetails}
        onRetryHealthCheck={onRetryHealthCheck}
      />

      {/* Main Results Layout */}
      <div className="flex-1 flex flex-row relative overflow-x-hidden">
        {/* Results Viewer Area (Shrinks gracefully with margin on desktop when chatbot is open) */}
        <main
          className={`flex-1 transition-all duration-300 px-4 pb-40 max-w-6xl mx-auto w-full ${
            isChatOpen ? 'lg:mr-[420px]' : ''
          }`}
        >
          {/* Processing Error Banner with Retry */}
          {error && (
            <div className="w-full max-w-4xl mx-auto my-6 p-5 bg-red-50/90 border border-red-200 text-red-800 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xs animate-in fade-in">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-sm text-red-900 mb-0.5">Processing Failed</h4>
                  <p className="text-xs text-red-700 leading-relaxed">{error}</p>
                </div>
              </div>
              <button
                type="button"
                onClick={handleRetry}
                disabled={isLoading}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-semibold transition-all cursor-pointer shadow-xs shrink-0 disabled:opacity-50"
              >
                <RefreshCcw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                <span>Retry Processing</span>
              </button>
            </div>
          )}

          {/* Loading State for Complete AI Notes (Streaming) */}
          {isLoading && activeMode === 'complete_notes' && (
            <div className="my-8">
              <LoadingState
                statusMessage={statusMessage}
                currentChapter={currentChapterNum}
                totalChapters={totalChapters}
                currentChapterTitle={currentChapterTitle}
                isInline={isProgressiveActive}
              />
            </div>
          )}

          {/* Loading State for Other Modes (Summary, Detailed, Chapter Slides) */}
          {isLoading && activeMode !== 'complete_notes' && (
            <div className="my-16 flex flex-col items-center justify-center text-center p-8 bg-white rounded-3xl border border-gray-100 shadow-xs max-w-lg mx-auto animate-in fade-in">
              <div className="w-14 h-14 rounded-2xl bg-primary/10 text-primary flex items-center justify-center mb-4">
                <Loader2 className="w-7 h-7 animate-spin text-primary" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-1">
                Generating {modeConfig.label}...
              </h3>
              <p className="text-xs text-gray-500 max-w-sm leading-relaxed mb-4">
                Processing video transcript using {selectedProvider.toUpperCase()} ({effectiveModel}).
              </p>
              <div className="w-48 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div className="w-full h-full bg-primary animate-pulse" />
              </div>
            </div>
          )}

          {/* OUTPUT VIEWERS (Rendered according to active mode) */}
          <div className="w-full mt-4">
            {/* Mode 1: Quick Summary */}
            {activeMode === 'summary' && summaryData && (
              <QuickSummaryView data={summaryData} videoTitle={videoTitle} />
            )}

            {/* Mode 2: Detailed Notes */}
            {activeMode === 'detailed' && detailedData && (
              <DetailedNotesView
                data={detailedData}
                videoTitle={videoTitle}
                onOpenSlide={(chapterId) => setActiveSlideChapterId(chapterId)}
              />
            )}

            {/* Mode 3: Chapter-End Slides */}
            {activeMode === 'chapter_slides' && (
              <div className="w-full max-w-5xl mx-auto my-6 bg-white rounded-3xl border border-gray-100 shadow-sm p-6 sm:p-8 animate-in fade-in">
                <SlidesGallery
                  slidesData={slidesData}
                  isLoading={isLoading && activeMode === 'chapter_slides'}
                  videoId={currentVideoId}
                  videoTitle={videoTitle}
                  onOpenSlide={(chapterId) => setActiveSlideChapterId(chapterId)}
                  onRetryExtract={handleRetry}
                  getSlideImageUrl={api.getSlideImageUrl}
                  getDownloadPptUrl={api.getDownloadPptUrl}
                />
              </div>
            )}

            {/* Mode 5: Complete AI Notes (Streaming / Completed) */}
            {activeMode === 'complete_notes' &&
              (completeNotesData?.success || isProgressiveActive) && (
                <div className="animate-in fade-in duration-300">
                  <NotesViewer
                    notes={
                      completeNotesData?.notes || {
                        title: progressiveVideo?.title || videoTitle || 'Study Notes',
                        content: '',
                      }
                    }
                    provider={completeNotesData?.provider || selectedProvider}
                    model={completeNotesData?.model || effectiveModel}
                    fallbackUsed={completeNotesData?.fallback_used}
                    transcriptLanguage={
                      completeNotesData?.transcript_language || loadedVideo?.transcript_language
                    }
                    transcriptGenerated={
                      completeNotesData?.transcript_generated || loadedVideo?.transcript_generated
                    }
                    videoId={currentVideoId}
                    videoTitle={
                      completeNotesData?.video?.title || progressiveVideo?.title || videoTitle
                    }
                    overviewContent={completeNotesData?.overview_content || progressiveOverview}
                    chapters={
                      completeNotesData?.chapters && completeNotesData.chapters.length > 0
                        ? completeNotesData.chapters
                        : progressiveChapters
                    }
                    revisionContent={completeNotesData?.revision_content || progressiveRevision}
                    slidesData={slidesData}
                    isExtractingSlides={false}
                    onRetryExtractSlides={handleRetry}
                    activeSlideChapterId={activeSlideChapterId}
                    onOpenSlide={(chapterId) => setActiveSlideChapterId(chapterId)}
                    onCloseSlideModal={() => setActiveSlideChapterId(null)}
                  />
                </div>
              )}
          </div>
        </main>

        {/* Transcript RAG Chatbot Panel (Right Drawer) */}
        {currentVideoId && (
          <ChatbotDrawer
            isOpen={isChatOpen}
            onClose={() => setIsChatOpen(false)}
            videoId={currentVideoId}
            videoTitle={videoTitle}
            provider={selectedProvider}
            model={effectiveModel}
            apiKey={apiKey.trim()}
          />
        )}

        {/* Slide Preview Modal for Fullscreen Slide Inspection */}
        {slidesData && slidesData.slides && slidesData.slides.length > 0 && activeSlideChapterId && (
          <SlidePreviewModal
            slides={slidesData.slides}
            activeChapterId={activeSlideChapterId}
            videoId={currentVideoId}
            onClose={() => setActiveSlideChapterId(null)}
            onSelectChapter={(id) => setActiveSlideChapterId(id)}
            getSlideImageUrl={api.getSlideImageUrl}
          />
        )}

        {/* Floating Actions Toolbar (Copy, Markdown, PDF, Retry, New) */}
        {activeMarkdown && (
          <Actions
            markdownContent={activeMarkdown.content}
            title={activeMarkdown.title}
            onRegenerate={handleRetry}
            onNew={handleBackToProcessing}
            isRetrying={isLoading}
            isChatOpen={isChatOpen}
          />
        )}
      </div>
    </div>
  );
};
