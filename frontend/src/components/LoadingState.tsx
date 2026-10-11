import { Loader2, CheckCircle2, Circle } from 'lucide-react';

interface LoadingStateProps {
  statusMessage?: string;
  currentChapter?: number;
  totalChapters?: number;
  currentChapterTitle?: string;
  isInline?: boolean;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  statusMessage = 'Analyzing video & transcript...',
  currentChapter,
  totalChapters,
  currentChapterTitle,
  isInline = false
}) => {
  const steps = [
    { label: 'Video metadata & chapters detected', key: 'metadata' },
    { label: 'Extracting transcript & timestamps', key: 'transcript' },
    { label: 'Synthesizing Video Overview', key: 'overview' },
    { 
      label: totalChapters 
        ? `Generating chapter notes (${currentChapter || 1} of ${totalChapters})` 
        : 'Generating structured chapter notes', 
      key: 'chapters' 
    },
    { label: 'Finalizing revision notes & glossary', key: 'revision' },
  ];

  // Infer current step active based on statusMessage or currentChapter
  let activeIndex = 0;
  const lowerMsg = statusMessage.toLowerCase();
  if (lowerMsg.includes('transcript')) activeIndex = 1;
  else if (lowerMsg.includes('overview')) activeIndex = 2;
  else if (lowerMsg.includes('chapter') || (currentChapter !== undefined && currentChapter > 0)) activeIndex = 3;
  else if (lowerMsg.includes('revision') || lowerMsg.includes('finaliz')) activeIndex = 4;

  const percent = totalChapters && totalChapters > 0
    ? Math.min(100, Math.round(((currentChapter || 1) / (totalChapters + 2)) * 100))
    : Math.min(95, (activeIndex + 1) * 20);

  if (isInline) {
    return (
      <div className="w-full max-w-4xl mx-auto my-8 p-6 bg-gradient-to-r from-primary/5 via-blue-50/40 to-primary/5 rounded-3xl border border-primary/20 shadow-sm animate-pulse">
        <div className="flex items-center gap-4">
          <div className="relative">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2 mb-1">
              <span className="text-sm font-semibold text-gray-900 truncate">
                {statusMessage}
              </span>
              {totalChapters && (
                <span className="text-xs font-bold text-primary shrink-0 bg-primary/10 px-2 py-0.5 rounded-full">
                  Chapter {currentChapter || 1} / {totalChapters}
                </span>
              )}
            </div>
            {currentChapterTitle && (
              <p className="text-xs text-gray-600 truncate mb-2">
                &ldquo;{currentChapterTitle}&rdquo;
              </p>
            )}
            <div className="w-full bg-gray-200/80 rounded-full h-1.5 overflow-hidden">
              <div 
                className="bg-primary h-1.5 rounded-full transition-all duration-500 ease-out" 
                style={{ width: `${percent}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-lg mx-auto mt-16 p-8 bg-white rounded-3xl shadow-sm border border-gray-100">
      <div className="flex flex-col items-center justify-center mb-8">
        <div className="relative">
          <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full"></div>
          <Loader2 className="w-12 h-12 text-primary animate-spin relative" />
        </div>
        <h3 className="mt-4 text-xl font-bold text-gray-900 text-center">
          Generating Chapter-by-Chapter Notes
        </h3>
        <p className="text-primary font-medium text-sm mt-1.5 text-center px-4">
          {statusMessage}
        </p>
        {currentChapterTitle && (
          <p className="text-xs text-gray-500 mt-1 italic text-center truncate max-w-xs">
            {currentChapterTitle}
          </p>
        )}
      </div>

      {totalChapters && totalChapters > 0 && (
        <div className="mb-6 px-1">
          <div className="flex justify-between items-center text-xs font-semibold text-gray-600 mb-1.5">
            <span>Overall Progress</span>
            <span>{percent}%</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
            <div 
              className="bg-primary h-2 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${percent}%` }}
            ></div>
          </div>
        </div>
      )}

      <div className="space-y-3.5 pt-2 border-t border-gray-100">
        {steps.map((s, index) => {
          const isCompleted = activeIndex > index;
          const isActive = activeIndex === index;
          
          return (
            <div key={index} className={`flex items-center gap-3 transition-opacity duration-300 ${isCompleted || isActive ? 'opacity-100' : 'opacity-40'}`}>
              {isCompleted ? (
                <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0" />
              ) : isActive ? (
                <div className="w-5 h-5 flex items-center justify-center shrink-0">
                  <div className="w-2.5 h-2.5 bg-primary rounded-full animate-ping"></div>
                </div>
              ) : (
                <Circle className="w-5 h-5 text-gray-300 shrink-0" />
              )}
              <span className={`text-sm ${isActive ? 'text-gray-900 font-semibold' : isCompleted ? 'text-gray-700 font-medium' : 'text-gray-400 font-normal'}`}>
                {s.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
