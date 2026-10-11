import React, { useState, useEffect, useCallback, useRef } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { Header } from './components/Header';
import { ModelConfigPage } from './components/ModelConfigPage';
import { DashboardPage } from './components/DashboardPage';
import { ResultsPage } from './components/ResultsPage';
import { api } from './services/api';
import { jobStorage } from './services/jobStorage';
import type {
  ProviderInfo,
  LoadVideoResponse,
  QuickSummaryResponse,
  DetailedNotesResponse,
  VideoSlidesResponse,
  GenerateNotesResponse,
  BackendHealthState,
} from './types';

interface ProtectedRouteProps {
  isValidated: boolean;
  children: React.ReactNode;
}

function ProtectedRoute({ isValidated, children }: ProtectedRouteProps) {
  if (!isValidated) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}

function AppRoutes() {
  const navigate = useNavigate();

  // -------------------------------------------------------------
  // Backend Health & Connectivity State
  // -------------------------------------------------------------
  const [backendHealth, setBackendHealth] = useState<BackendHealthState>({
    status: 'checking',
    message: 'Checking backend connection...',
    url: api.getBaseUrl(),
  });

  const isCheckingRef = useRef<boolean>(false);

  const checkHealthStatus = useCallback(async () => {
    if (isCheckingRef.current) return;
    isCheckingRef.current = true;
    try {
      const res = await api.checkHealth();
      setBackendHealth(res);
    } catch {
      setBackendHealth({
        status: 'offline',
        message: 'Backend Offline',
        details: `Unable to connect to NoteTube FastAPI server at ${api.getBaseUrl()}.`,
        url: api.getBaseUrl(),
        lastChecked: Date.now(),
      });
    } finally {
      isCheckingRef.current = false;
    }
  }, []);

  // Poll backend health gently (30s) and on window focus
  useEffect(() => {
    let isMounted = true;

    const executeCheck = async () => {
      if (!isMounted) return;
      await checkHealthStatus();
    };

    executeCheck();

    const interval = setInterval(() => {
      if (isMounted) checkHealthStatus();
    }, 30000);

    const onFocus = () => {
      if (isMounted) checkHealthStatus();
    };
    window.addEventListener('focus', onFocus);

    return () => {
      isMounted = false;
      clearInterval(interval);
      window.removeEventListener('focus', onFocus);
    };
  }, [checkHealthStatus]);

  // -------------------------------------------------------------
  // LLM Configuration & Session Validation State
  // -------------------------------------------------------------
  // A fresh session starts with false so root URL displays Page 1 (LLM Configuration).
  // Within an active browser tab, sessionStorage preserves validated state across refreshes.
  const [isConfigValidated, setIsConfigValidated] = useState<boolean>(() => {
    try {
      return sessionStorage.getItem('notetube_session_validated') === 'true';
    } catch {
      return false;
    }
  });

  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>(() => {
    try {
      const savedConfig = localStorage.getItem('notetube_model_config');
      if (savedConfig) {
        const parsed = JSON.parse(savedConfig);
        if (parsed.provider) return parsed.provider;
      }
    } catch {}
    return 'ollama';
  });

  const [selectedModel, setSelectedModel] = useState<string>(() => {
    try {
      const savedConfig = localStorage.getItem('notetube_model_config');
      if (savedConfig) {
        const parsed = JSON.parse(savedConfig);
        if (parsed.model) return parsed.model;
      }
    } catch {}
    return 'qwen3:1.7b';
  });

  const [isCustomModel, setIsCustomModel] = useState<boolean>(() => {
    try {
      const savedConfig = localStorage.getItem('notetube_model_config');
      if (savedConfig) {
        const parsed = JSON.parse(savedConfig);
        if (parsed.isCustomModel !== undefined) return parsed.isCustomModel;
      }
    } catch {}
    return false;
  });

  const [customModel, setCustomModel] = useState<string>(() => {
    try {
      const savedConfig = localStorage.getItem('notetube_model_config');
      if (savedConfig) {
        const parsed = JSON.parse(savedConfig);
        if (parsed.customModel) return parsed.customModel;
      }
    } catch {}
    return '';
  });

  const [apiKey, setApiKey] = useState<string>(() => {
    try {
      return sessionStorage.getItem('notetube_session_api_key') || '';
    } catch {
      return '';
    }
  });

  // Persist non-sensitive configuration only (do NOT store API secrets in localStorage)
  useEffect(() => {
    try {
      localStorage.setItem(
        'notetube_model_config',
        JSON.stringify({
          provider: selectedProvider,
          model: selectedModel,
          isCustomModel,
          customModel,
        })
      );
    } catch {}
  }, [selectedProvider, selectedModel, isCustomModel, customModel]);

  // Persist API key only in tab-scoped sessionStorage
  useEffect(() => {
    try {
      if (apiKey) {
        sessionStorage.setItem('notetube_session_api_key', apiKey);
      } else {
        sessionStorage.removeItem('notetube_session_api_key');
      }
    } catch {}
  }, [apiKey]);

  // -------------------------------------------------------------
  // Video & Processing Results State
  // -------------------------------------------------------------
  const [loadedVideo, setLoadedVideo] = useState<LoadVideoResponse | null>(null);
  const [lastUrl, setLastUrl] = useState<string>('');

  const [summaryData, setSummaryData] = useState<QuickSummaryResponse | null>(null);
  const [detailedData, setDetailedData] = useState<DetailedNotesResponse | null>(null);
  const [slidesData, setSlidesData] = useState<VideoSlidesResponse | null>(null);
  const [completeNotesData, setCompleteNotesData] = useState<GenerateNotesResponse | null>(null);

  // Restore video metadata ONLY if this specific session had loaded a video and refreshed /video
  useEffect(() => {
    try {
      const sessionVideoId = sessionStorage.getItem('notetube_session_video_id');
      if (sessionVideoId && !loadedVideo) {
        const stored = jobStorage.getJob(sessionVideoId);
        if (stored) {
          setLoadedVideo(stored.videoData);
          setLastUrl(stored.url);
          if (stored.summaryData) setSummaryData(stored.summaryData);
          if (stored.detailedData) setDetailedData(stored.detailedData);
          if (stored.slidesData) setSlidesData(stored.slidesData);
          if (stored.completeNotesData) setCompleteNotesData(stored.completeNotesData);
        }
      }
    } catch {}
  }, [loadedVideo]);

  // Track session video ID when video is loaded or changed
  const handleSetLoadedVideo: React.Dispatch<React.SetStateAction<LoadVideoResponse | null>> = (action) => {
    setLoadedVideo((prev) => {
      const next = typeof action === 'function' ? action(prev) : action;
      try {
        if (next && next.video_id) {
          sessionStorage.setItem('notetube_session_video_id', next.video_id);
        } else {
          sessionStorage.removeItem('notetube_session_video_id');
        }
      } catch {}
      return next;
    });
  };

  // Fetch supported providers on mount
  useEffect(() => {
    let isMounted = true;
    const loadProviders = async () => {
      try {
        const res = await api.getProviders();
        if (isMounted && res.providers && res.providers.length > 0) {
          setProviders(res.providers);
          const savedConfig = localStorage.getItem('notetube_model_config');
          if (!savedConfig) {
            const defaultProv = res.providers.find((p) => p.id === 'ollama') || res.providers[0];
            setSelectedProvider(defaultProv.id);
            setSelectedModel(defaultProv.default_model);
          }
        }
      } catch (err) {
        console.error('Failed to load providers:', err);
      }
    };
    loadProviders();
    return () => {
      isMounted = false;
    };
  }, []);

  const getEffectiveModel = (): string => {
    if (isCustomModel) return customModel.trim();
    return selectedModel.trim();
  };

  const activeProvider = providers.find((p) => p.id === selectedProvider);

  // Called after successful provider validation on Page 1
  const handleModelValidated = () => {
    setIsConfigValidated(true);
    try {
      sessionStorage.setItem('notetube_session_validated', 'true');
    } catch {}
    navigate('/video');
  };

  // Reset Session (Start Fresh Session)
  const handleResetSession = () => {
    setIsConfigValidated(false);
    try {
      sessionStorage.removeItem('notetube_session_validated');
      sessionStorage.removeItem('notetube_session_video_id');
    } catch {}
    setLoadedVideo(null);
    setLastUrl('');
    setSummaryData(null);
    setDetailedData(null);
    setSlidesData(null);
    setCompleteNotesData(null);
    navigate('/');
  };

  return (
    <Routes>
      {/* Route 1: Page 1 — LLM Configuration (/) */}
      <Route
        path="/"
        element={
          <div className="min-h-screen flex flex-col font-sans bg-gradient-to-b from-gray-50/60 via-white to-gray-50/40 text-gray-900">
            <Header
              currentPage="config"
              onNavigateToWorkspace={() => {
                if (isConfigValidated) navigate('/video');
                else navigate('/');
              }}
              onResetSession={handleResetSession}
              providerName={activeProvider?.name || selectedProvider}
              modelName={getEffectiveModel()}
              backendStatus={backendHealth.status}
              backendBaseUrl={backendHealth.url}
              backendDetails={backendHealth.details}
              onRetryHealthCheck={checkHealthStatus}
            />
            <main className="flex-1 w-full max-w-4xl mx-auto px-4 pb-20 animate-in fade-in duration-300">
              <ModelConfigPage
                providers={providers}
                selectedProvider={selectedProvider}
                onSelectProvider={setSelectedProvider}
                selectedModel={selectedModel}
                onSelectModel={setSelectedModel}
                isCustomModel={isCustomModel}
                setIsCustomModel={setIsCustomModel}
                customModel={customModel}
                onCustomModelChange={setCustomModel}
                apiKey={apiKey}
                onApiKeyChange={setApiKey}
                onValidated={handleModelValidated}
                isValidated={isConfigValidated}
                onContinueToDashboard={() => navigate('/video')}
                backendStatus={backendHealth.status}
                onRetryHealthCheck={checkHealthStatus}
              />
            </main>
          </div>
        }
      />

      {/* Alias for /config -> / */}
      <Route path="/config" element={<Navigate to="/" replace />} />

      {/* Route 2: Page 2 — Video Processing Dashboard (/video) */}
      <Route
        path="/video"
        element={
          <ProtectedRoute isValidated={isConfigValidated}>
            <DashboardPage
              selectedProvider={selectedProvider}
              selectedModel={selectedModel}
              isCustomModel={isCustomModel}
              customModel={customModel}
              apiKey={apiKey}
              onNavigateToConfig={() => navigate('/')}
              onResetSession={handleResetSession}
              loadedVideo={loadedVideo}
              setLoadedVideo={handleSetLoadedVideo}
              lastUrl={lastUrl}
              setLastUrl={setLastUrl}
              summaryData={summaryData}
              setSummaryData={setSummaryData}
              detailedData={detailedData}
              setDetailedData={setDetailedData}
              slidesData={slidesData}
              setSlidesData={setSlidesData}
              completeNotesData={completeNotesData}
              setCompleteNotesData={setCompleteNotesData}
              backendStatus={backendHealth.status}
              backendBaseUrl={backendHealth.url}
              backendDetails={backendHealth.details}
              onRetryHealthCheck={checkHealthStatus}
            />
          </ProtectedRoute>
        }
      />

      {/* Legacy workspace route alias */}
      <Route path="/workspace" element={<Navigate to="/video" replace />} />

      {/* Route 3: Page 3 — Results Viewer (/results/:jobId) */}
      <Route
        path="/results/:jobId"
        element={
          <ProtectedRoute isValidated={isConfigValidated}>
            <ResultsPage
              selectedProvider={selectedProvider}
              selectedModel={selectedModel}
              isCustomModel={isCustomModel}
              customModel={customModel}
              apiKey={apiKey}
              onNavigateToConfig={() => navigate('/')}
              onResetSession={handleResetSession}
              loadedVideo={loadedVideo}
              setLoadedVideo={handleSetLoadedVideo}
              lastUrl={lastUrl}
              setLastUrl={setLastUrl}
              summaryData={summaryData}
              setSummaryData={setSummaryData}
              detailedData={detailedData}
              setDetailedData={setDetailedData}
              slidesData={slidesData}
              setSlidesData={setSlidesData}
              completeNotesData={completeNotesData}
              setCompleteNotesData={setCompleteNotesData}
              backendStatus={backendHealth.status}
              backendBaseUrl={backendHealth.url}
              backendDetails={backendHealth.details}
              onRetryHealthCheck={checkHealthStatus}
            />
          </ProtectedRoute>
        }
      />

      {/* Catch-all route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;
