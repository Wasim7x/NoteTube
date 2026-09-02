import { useState } from 'react';
import { Header } from './components/Header';
import { UrlInput } from './components/UrlInput';
import { LoadingState } from './components/LoadingState';
import { NotesViewer } from './components/NotesViewer';
import { Actions } from './components/Actions';
import { api } from './services/api';
import type { GenerateNotesResponse } from './types';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [data, setData] = useState<GenerateNotesResponse | null>(null);
  const [lastUrl, setLastUrl] = useState<string>('');

  const generateNotes = async (url: string) => {
    setIsLoading(true);
    setLastUrl(url);
    setData(null);
    try {
      const response = await api.generateNotes({ youtube_url: url });
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
    <div className="min-h-screen flex flex-col font-sans">
      <Header />
      
      <main className="flex-1 w-full max-w-5xl mx-auto px-4 pb-32">
        {!isLoading && !data && (
          <UrlInput onSubmit={generateNotes} isLoading={isLoading} />
        )}

        {isLoading && (
          <LoadingState />
        )}

        {data && !data.success && (
          <div className="w-full max-w-2xl mx-auto mt-20 p-6 bg-red-50 rounded-2xl border border-red-100 text-center">
            <h3 className="text-xl font-semibold text-red-800 mb-2">Oops! Something went wrong</h3>
            <p className="text-red-600 mb-6">{data.error}</p>
            <button 
              onClick={handleNew}
              className="px-6 py-2 bg-red-100 hover:bg-red-200 text-red-700 font-medium rounded-xl transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {data && data.success && data.notes && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
            {data.video && (
               <div className="w-full max-w-4xl mx-auto mt-12 flex flex-col md:flex-row items-center gap-6 bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
                 <img 
                    src={data.video.thumbnail} 
                    alt={data.video.title} 
                    className="w-full md:w-64 h-auto aspect-video object-cover rounded-xl shadow-sm"
                 />
                 <div>
                   <h2 className="text-xl font-bold text-gray-900">{data.video.title}</h2>
                   <a href={lastUrl} target="_blank" rel="noreferrer" className="text-sm text-primary hover:underline mt-1 inline-block">
                     Watch original video
                   </a>
                 </div>
               </div>
            )}
            
            <NotesViewer notes={data.notes} />
            
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
