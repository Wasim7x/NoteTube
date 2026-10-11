import React, { useState } from 'react';
import {
  Cpu,
  Key,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Eye,
  EyeOff,
  ExternalLink
} from 'lucide-react';
import type { ProviderInfo, BackendHealthStatus } from '../types';
import { api } from '../services/api';

interface ModelConfigPageProps {
  providers: ProviderInfo[];
  selectedProvider: string;
  onSelectProvider: (providerId: string) => void;
  selectedModel: string;
  onSelectModel: (modelId: string) => void;
  isCustomModel: boolean;
  setIsCustomModel: (isCustom: boolean) => void;
  customModel: string;
  onCustomModelChange: (custom: string) => void;
  apiKey: string;
  onApiKeyChange: (key: string) => void;
  onValidated: () => void;
  isValidated?: boolean;
  onContinueToDashboard?: () => void;
  backendStatus?: BackendHealthStatus;
  onRetryHealthCheck?: () => void;
}

export const ModelConfigPage: React.FC<ModelConfigPageProps> = ({
  providers,
  selectedProvider,
  onSelectProvider,
  selectedModel,
  onSelectModel,
  isCustomModel,
  setIsCustomModel,
  customModel,
  onCustomModelChange,
  apiKey,
  onApiKeyChange,
  onValidated,
  isValidated = false,
  onContinueToDashboard,
  backendStatus,
  onRetryHealthCheck,
}) => {
  const [showApiKey, setShowApiKey] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [validationSuccess, setValidationSuccess] = useState<string | null>(null);

  const currentProvider = providers.find((p) => p.id === selectedProvider) || providers[0];
  const isLocalProvider = currentProvider?.id === 'ollama' || currentProvider?.requires_api_key === false;

  const effectiveModel = isCustomModel ? customModel.trim() : selectedModel.trim();

  const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newProviderId = e.target.value;
    onSelectProvider(newProviderId);
    setValidationError(null);
    setValidationSuccess(null);
    const newProv = providers.find((p) => p.id === newProviderId);
    if (newProv) {
      onSelectModel(newProv.default_model);
      setIsCustomModel(false);
    }
  };

  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setValidationError(null);
    setValidationSuccess(null);
    if (value === '__custom__') {
      setIsCustomModel(true);
    } else {
      setIsCustomModel(false);
      onSelectModel(value);
    }
  };

  const handleValidateAndProceed = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);
    setValidationSuccess(null);

    if (!isLocalProvider && !apiKey.trim()) {
      setValidationError(`Please enter a valid API key for ${currentProvider?.name || 'your selected provider'}.`);
      return;
    }

    if (isCustomModel && !customModel.trim()) {
      setValidationError('Please specify a custom model identifier.');
      return;
    }

    setIsValidating(true);
    try {
      const res = await api.validateProvider({
        provider: selectedProvider,
        model: effectiveModel,
        api_key: apiKey.trim()
      });

      if (res.success) {
        setValidationSuccess(res.message || 'Connection verified successfully! Proceeding...');
        setTimeout(() => {
          onValidated();
        }, 750);
      } else {
        setValidationError(res.error || res.message || 'Validation failed. Please verify your credentials or model name.');
      }
    } catch (err: any) {
      setValidationError(err.message || 'Could not connect to the backend server to validate configuration.');
    } finally {
      setIsValidating(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto mt-12 px-4 animate-in fade-in duration-300">
      {/* Hero Title */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-primary/10 text-primary text-xs font-semibold mb-4 border border-primary/15 shadow-xs">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Step 1 &bull; Model Configuration</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 tracking-tight leading-tight mb-3">
          Configure Your <span className="text-primary">AI Engine</span>
        </h1>
        <p className="text-base text-gray-500 max-w-lg mx-auto leading-relaxed">
          Select an AI model provider and verify connectivity before processing your YouTube video notes.
        </p>
      </div>

      {/* Active Session Notice if already validated */}
      {isValidated && (
        <div className="mb-6 p-4 rounded-2xl bg-emerald-50 border border-emerald-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-in fade-in">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            <div className="text-xs">
              <span className="font-bold text-emerald-900 block">AI Engine Currently Active</span>
              <span className="text-emerald-700">Model configuration is validated for this session. You can update it below or return to video processing.</span>
            </div>
          </div>
          {onContinueToDashboard && (
            <button
              type="button"
              onClick={onContinueToDashboard}
              className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 shrink-0 transition-all cursor-pointer shadow-2xs"
            >
              <span>Go to Dashboard</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      )}

      {/* Offline Alert Banner */}
      {backendStatus === 'offline' && (
        <div className="mb-6 p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-800 flex items-center justify-between gap-3 text-xs animate-in fade-in">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 text-amber-600 shrink-0" />
            <span>
              <strong>Backend Offline:</strong> NoteTube server is unreachable. Please verify FastAPI is running.
            </span>
          </div>
          {onRetryHealthCheck && (
            <button
              type="button"
              onClick={onRetryHealthCheck}
              className="px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-semibold shrink-0 transition-all cursor-pointer shadow-2xs"
            >
              Retry
            </button>
          )}
        </div>
      )}

      {/* Main Configuration Card */}
      <form onSubmit={handleValidateAndProceed} className="bg-white rounded-3xl shadow-[0_10px_35px_rgba(0,0,0,0.05)] border border-gray-100 p-6 sm:p-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-5 mb-6 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-primary/10 text-primary">
              <Cpu className="w-6 h-6" />
            </div>
            <div>
              <h2 className="font-bold text-gray-900 text-lg">AI Provider Setup</h2>
              <p className="text-xs text-gray-500">
                {isLocalProvider
                  ? 'Running locally with Ollama (100% on-device inference)'
                  : 'Cloud inference with your private API key'}
              </p>
            </div>
          </div>

          <div
            className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium self-start sm:self-auto border ${
              isLocalProvider
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : 'bg-indigo-50 text-indigo-700 border-indigo-200'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>{isLocalProvider ? 'Offline Ready' : 'Direct API Call'}</span>
          </div>
        </div>

        <div className="space-y-5">
          {/* Grid: Provider & Model */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Provider Selection */}
            <div>
              <label htmlFor="provider-select" className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
                Model Provider
              </label>
              <div className="relative">
                <select
                  id="provider-select"
                  value={selectedProvider}
                  onChange={handleProviderChange}
                  disabled={isValidating}
                  className="w-full h-12 px-3.5 bg-gray-50/70 hover:bg-gray-50 border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 rounded-xl text-sm font-semibold text-gray-800 transition-all outline-none appearance-none cursor-pointer disabled:opacity-60"
                >
                  {providers.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
                <div className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                  <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20">
                    <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Model Selection */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label htmlFor="model-select" className="block text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Model Identifier
                </label>
                {isCustomModel && (
                  <button
                    type="button"
                    onClick={() => setIsCustomModel(false)}
                    className="text-[11px] text-primary hover:underline font-medium cursor-pointer"
                  >
                    Preset models
                  </button>
                )}
              </div>

              {!isCustomModel ? (
                <div className="relative">
                  <select
                    id="model-select"
                    value={selectedModel}
                    onChange={handleModelChange}
                    disabled={isValidating}
                    className="w-full h-12 px-3.5 bg-gray-50/70 hover:bg-gray-50 border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 rounded-xl text-sm font-semibold text-gray-800 transition-all outline-none appearance-none cursor-pointer disabled:opacity-60"
                  >
                    <optgroup label={`${currentProvider?.name || 'Provider'} Models`}>
                      {currentProvider?.models.map((m) => (
                        <option key={m.id} value={m.id}>
                          {m.name} {m.is_recommended ? '★ (Recommended)' : ''}
                        </option>
                      ))}
                    </optgroup>
                    <option value="__custom__">✎ Enter custom model name...</option>
                  </select>
                  <div className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                    <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20">
                      <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
                    </svg>
                  </div>
                </div>
              ) : (
                <input
                  id="custom-model-input"
                  type="text"
                  value={customModel}
                  onChange={(e) => onCustomModelChange(e.target.value)}
                  disabled={isValidating}
                  placeholder={
                    isLocalProvider
                      ? 'e.g. qwen3:1.7b, mistral, llama3'
                      : 'e.g. gpt-4o, claude-3-7-sonnet'
                  }
                  className="w-full h-12 px-3.5 bg-gray-50/70 hover:bg-gray-50 border border-primary focus:ring-2 focus:ring-primary/20 rounded-xl text-sm font-medium text-gray-800 transition-all outline-none disabled:opacity-60"
                />
              )}
            </div>
          </div>

          {/* Local Ollama Info Banner vs Cloud API Key */}
          {isLocalProvider ? (
            <div className="p-4 bg-emerald-50/80 border border-emerald-200/90 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-emerald-900">
              <div className="flex items-center gap-3 text-xs leading-relaxed">
                <span className="relative flex h-3 w-3 shrink-0">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                </span>
                <div>
                  <strong className="font-bold">Ollama Local Mode Active:</strong>
                  <span className="text-emerald-800 ml-1">
                    No cloud API key required. Notes, summaries, and Q&amp;A run entirely on your local machine.
                  </span>
                </div>
              </div>
              <span className="text-[11px] font-mono text-emerald-800 bg-white/90 px-3 py-1.5 rounded-xl border border-emerald-200/80 shrink-0 shadow-2xs">
                http://localhost:11434
              </span>
            </div>
          ) : (
            <div>
              <div className="flex items-center justify-between mb-2">
                <label htmlFor="api-key-input" className="block text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  API Key
                </label>
                {currentProvider?.help_url && (
                  <a
                    href={currentProvider.help_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-primary hover:underline font-medium"
                  >
                    <span>Get {currentProvider.name} Key</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>

              <div className="relative flex items-center">
                <div className="absolute left-3.5 text-gray-400 pointer-events-none">
                  <Key className="w-4 h-4" />
                </div>
                <input
                  id="api-key-input"
                  type={showApiKey ? 'text' : 'password'}
                  value={apiKey}
                  onChange={(e) => {
                    onApiKeyChange(e.target.value);
                    if (validationError) setValidationError(null);
                  }}
                  disabled={isValidating}
                  placeholder={`Enter your ${currentProvider?.name || 'AI'} API key (${currentProvider?.key_placeholder || 'sk-...'})`}
                  autoComplete="off"
                  spellCheck={false}
                  className="w-full h-12 pl-10 pr-12 bg-gray-50/70 hover:bg-gray-50 border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 rounded-xl text-sm font-mono text-gray-800 transition-all outline-none disabled:opacity-60"
                />
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute right-3.5 p-1 text-gray-400 hover:text-gray-600 transition-colors focus:outline-none cursor-pointer"
                  title={showApiKey ? 'Hide Key' : 'Show Key'}
                >
                  {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
          )}

          {/* Validation Feedback Status Banners */}
          {validationError && (
            <div className="p-4 bg-red-50/90 border border-red-200 rounded-2xl flex items-start gap-3 text-red-900 text-xs animate-in fade-in duration-200">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
              <div className="flex-1">
                <strong className="font-bold block mb-0.5">Connection Test Failed</strong>
                <span className="leading-relaxed text-red-800">{validationError}</span>
              </div>
            </div>
          )}

          {validationSuccess && (
            <div className="p-4 bg-emerald-50/90 border border-emerald-200 rounded-2xl flex items-center gap-3 text-emerald-900 text-xs animate-in fade-in duration-200">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <div className="flex-1 font-semibold">{validationSuccess}</div>
            </div>
          )}

          {/* Submit Action Button */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={isValidating}
              className="w-full h-14 bg-primary hover:bg-primaryHover text-white rounded-2xl font-bold text-sm sm:text-base flex items-center justify-center gap-2.5 transition-all shadow-md hover:shadow-lg active:scale-[0.99] disabled:opacity-65 cursor-pointer"
            >
              {isValidating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin text-white" />
                  <span>Validating Connection &amp; Model...</span>
                </>
              ) : (
                <>
                  <span>Validate &amp; Connect Engine</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};
