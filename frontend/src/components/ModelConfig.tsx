import React, { useState } from 'react';
import { Eye, EyeOff, Key, Cpu, ExternalLink, ShieldCheck, Sparkles } from 'lucide-react';
import type { ProviderInfo } from '../types';

interface ModelConfigProps {
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
  isLoading: boolean;
  error?: string;
}

export const ModelConfig: React.FC<ModelConfigProps> = ({
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
  isLoading,
  error,
}) => {
  const [showApiKey, setShowApiKey] = useState(false);

  const currentProvider = providers.find((p) => p.id === selectedProvider) || providers[0];

  const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newProviderId = e.target.value;
    onSelectProvider(newProviderId);
    const newProvider = providers.find((p) => p.id === newProviderId);
    if (newProvider) {
      onSelectModel(newProvider.default_model);
      setIsCustomModel(false);
    }
  };

  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    if (value === '__custom__') {
      setIsCustomModel(true);
    } else {
      setIsCustomModel(false);
      onSelectModel(value);
    }
  };

  return (
    <div className="w-full bg-white/80 backdrop-blur-md rounded-2xl border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-6 transition-all duration-300 hover:shadow-[0_8px_30px_rgb(0,0,0,0.07)]">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 mb-5 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-primary/10 text-primary">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 text-base">AI Model Configuration</h3>
            <p className="text-xs text-gray-500">Choose your AI provider and enter your API key directly</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 text-emerald-700 rounded-full text-xs font-medium self-start sm:self-auto border border-emerald-100">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>Client-side session memory only</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Provider Select */}
        <div>
          <label htmlFor="ai-provider-select" className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
            Model Provider
          </label>
          <div className="relative">
            <select
              id="ai-provider-select"
              value={selectedProvider}
              onChange={handleProviderChange}
              disabled={isLoading}
              className="w-full h-11 px-3.5 bg-gray-50/70 hover:bg-gray-50 border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 rounded-xl text-sm font-medium text-gray-800 transition-all outline-none appearance-none cursor-pointer disabled:opacity-60"
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

        {/* Model Select */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label htmlFor="ai-model-select" className="block text-xs font-semibold text-gray-700 uppercase tracking-wider">
              Model Name
            </label>
            {isCustomModel && (
              <button
                type="button"
                onClick={() => setIsCustomModel(false)}
                className="text-[11px] text-primary hover:underline font-medium"
              >
                Back to presets
              </button>
            )}
          </div>

          {!isCustomModel ? (
            <div className="relative">
              <select
                id="ai-model-select"
                value={selectedModel}
                onChange={handleModelChange}
                disabled={isLoading}
                className="w-full h-11 px-3.5 bg-gray-50/70 hover:bg-gray-50 border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 rounded-xl text-sm font-medium text-gray-800 transition-all outline-none appearance-none cursor-pointer disabled:opacity-60"
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
            <div className="relative">
              <input
                id="custom-model-input"
                type="text"
                value={customModel}
                onChange={(e) => onCustomModelChange(e.target.value)}
                disabled={isLoading}
                placeholder="e.g. gpt-4o-2024-11-20, deepseek-v3"
                className="w-full h-11 px-3.5 bg-gray-50/70 hover:bg-gray-50 border border-primary focus:ring-2 focus:ring-primary/20 rounded-xl text-sm font-medium text-gray-800 transition-all outline-none disabled:opacity-60"
              />
            </div>
          )}
        </div>
      </div>

      {/* API Key Input */}
      <div className="mt-4">
        <div className="flex items-center justify-between mb-1.5">
          <label htmlFor="ai-api-key-input" className="block text-xs font-semibold text-gray-700 uppercase tracking-wider">
            API Key
          </label>
          {currentProvider?.help_url && (
            <a
              href={currentProvider.help_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-xs text-primary hover:text-primaryHover transition-colors font-medium"
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
            id="ai-api-key-input"
            type={showApiKey ? 'text' : 'password'}
            value={apiKey}
            onChange={(e) => onApiKeyChange(e.target.value)}
            disabled={isLoading}
            placeholder={`Enter your ${currentProvider?.name || 'AI'} API key (${currentProvider?.key_placeholder || 'sk-...'})`}
            autoComplete="off"
            spellCheck={false}
            className={`w-full h-11 pl-10 pr-11 bg-gray-50/70 hover:bg-gray-50 border ${
              error ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-gray-200 focus:border-primary focus:ring-primary/20'
            } focus:ring-2 rounded-xl text-sm font-mono text-gray-800 transition-all outline-none disabled:opacity-60`}
          />
          <button
            type="button"
            onClick={() => setShowApiKey(!showApiKey)}
            className="absolute right-3 p-1 text-gray-400 hover:text-gray-600 transition-colors focus:outline-none"
            title={showApiKey ? 'Hide API Key' : 'Show API Key'}
          >
            {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
        {error && <p className="mt-1.5 text-xs text-red-600 font-medium">{error}</p>}
      </div>

      {/* Helper Footer */}
      <div className="mt-3.5 pt-3 border-t border-gray-50 flex items-center justify-between text-[11px] text-gray-400">
        <div className="flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-amber-500" />
          <span>Active: <strong className="text-gray-700">{currentProvider?.name}</strong> &rarr; <strong className="text-gray-700">{isCustomModel ? (customModel || 'Custom') : selectedModel}</strong></span>
        </div>
        <span>Never stored in localStorage</span>
      </div>
    </div>
  );
};
