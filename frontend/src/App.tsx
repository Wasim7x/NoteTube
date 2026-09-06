import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { UrlInput } from './components/UrlInput';
import { ModelConfig } from './components/ModelConfig';
import { LoadingState } from './components/LoadingState';
import { NotesViewer } from './components/NotesViewer';
import { Actions } from './components/Actions';
import { api } from './services/api';
import type { GenerateNotesResponse, ProviderInfo } from './types';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [data, setData] = useState<GenerateNotesResponse | null>(null);
  const [lastUrl, setLastUrl] = useState<string>('');

  // Dynamic Provider & Model State
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('gemini');
  const [selectedModel, setSelectedModel] = useState<string>('gemini-2.5-flash');
  const [isCustomModel, setIsCustomModel] = useState<boolean>(false);
  const [customModel, setCustomModel] = useState<string>('');
  const [apiKey, setApiKey] = useState<string>('');
  const [apiKeyError, setApiKeyError] = useState<string>('');

  // Fetch supported providers on mount
  useEffect(() => {
    let isMounted = true;
    const loadProviders = async () => {
      try {
        const res = await api.getProviders();
        if (isMounted && res.providers && res.providers.length > 0) {
          setProviders(res.providers);
          // Set initial default provider and model
          const defaultProv = res.providers.find((p) => p.id === 'gemini') || res.providers[0];
          setSelectedProvider(defaultProv.id);
          setSelectedModel(defaultProv.default_model);
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
    if (isCustomModel) {
      return customModel.trim();
    }
    return selectedModel.trim();
  };

  const generateNotes = async (url: string) => {
    setApiKeyError('');
    const effectiveModel = getEffectiveModel();

    if (!apiKey.trim()) {
      setApiKeyError('Please provide an API key for your selected provider.');
      return;
    }

    if (isCustomModel && !effectiveModel) {
      setApiKeyError('Please enter a valid custom model name.');
      return;
    }

    setIsLoading(true);
    setLastUrl(url);
    setData(null);

    try {
      const response = await api.generateNotes({
        youtube_url: url,
        provider: selectedProvider,
        model: effectiveModel,
        api_key: apiKey.trim(),
      });
      setData(response);
    } catch (error: any) {
      setData({
        success: false,
        error: error.message || 'Something went wrong while generating the notes. Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerate = () => {
    if (lastUrl) {
      generateNotes(lastUrl);
    }
  };

  const handleNew = () => {
    setData(null);
    setLastUrl('');
  };

  return (
    <div className="min-h-screen flex flex-col font-sans bg-gradient-to-b from-gray-50/50 to-white">
      <Header />
      
      <main className="flex-1 w-full max-w-5xl mx-auto px-4 pb-32">
        {!isLoading && !data && (
          <UrlInput
            onSubmit={generateNotes}
            isLoading={isLoading}
            hasApiKey={Boolean(apiKey.trim())}
            onMissingApiKey={() => setApiKeyError('Please enter an API key for your selected AI provider above.')}
          >
            {providers.length > 0 && (
              <ModelConfig
                providers={providers}
                selectedProvider={selectedProvider}
                onSelectProvider={(p) => {
                  setSelectedProvider(p);
                  setApiKeyError('');
                }}
                selectedModel={selectedModel}
                onSelectModel={(m) => {
                  setSelectedModel(m);
                  setApiKeyError('');
                }}
                isCustomModel={isCustomModel}
                setIsCustomModel={setIsCustomModel}
                customModel={customModel}
                onCustomModelChange={(m) => {
                  setCustomModel(m);
                  setApiKeyError('');
                }}
                apiKey={apiKey}
                onApiKeyChange={(k) => {
                  setApiKey(k);
                  if (apiKeyError) setApiKeyError('');
                }}
                isLoading={isLoading}
                error={apiKeyError}
              />
            )}
          </UrlInput>
        )}

        {isLoading && (
          <LoadingState />
        )}

        {data && !data.success && (
          <div className="w-full max-w-2xl mx-auto mt-20 p-8 bg-red-50/80 rounded-3xl border border-red-100 text-center shadow-sm">
            <div className="w-12 h-12 bg-red-100 text-red-600 rounded-2xl flex items-center justify-center mx-auto mb-4 font-bold text-xl">
              !
            </div>
            <h3 className="text-xl font-bold text-red-900 mb-2">Note Generation Failed</h3>
            <p className="text-red-700 text-sm max-w-md mx-auto mb-6 leading-relaxed">{data.error}</p>
            <div className="flex items-center justify-center gap-3">
              <button 
                onClick={handleNew}
                className="px-6 py-2.5 bg-red-600 hover:bg-red-700 text-white font-medium text-sm rounded-xl transition-all shadow-sm active:scale-[0.98] cursor-pointer"
              >
                Change Settings / Try Again
              </button>
            </div>
          </div>
        )}

        {data && data.success && data.notes && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
            {data.video && (
               <div className="w-full max-w-4xl mx-auto mt-12 flex flex-col md:flex-row items-center gap-6 bg-white p-5 rounded-3xl border border-gray-100 shadow-sm">
                 <img 
                    src={data.video.thumbnail} 
                    alt={data.video.title} 
                    className="w-full md:w-64 h-auto aspect-video object-cover rounded-2xl shadow-sm"
                 />
                 <div className="flex-1">
                   <h2 className="text-xl font-bold text-gray-900 leading-snug">{data.video.title}</h2>
                   <a
                     href={lastUrl} 
                     target="_blank" 
                     rel="noreferrer" 
                     className="text-sm text-primary hover:underline mt-2 inline-block font-medium"
                   >
                     Watch original video &rarr;
                   </a>
                 </div>
               </div>
            )}
            
            <NotesViewer
              notes={data.notes}
              provider={data.provider || selectedProvider}
              model={data.model || getEffectiveModel()}
            />
            
            <Actions 
              markdownContent={data.notes.content}
              title={data.notes.title || data.video?.title || 'NoteTube Notes'}
              onRegenerate={handleRegenerate}
              onNew={handleNew}
            />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
