import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Sparkles } from 'lucide-react';
import type { NotesData } from '../types';

interface NotesViewerProps {
  notes: NotesData;
  provider?: string;
  model?: string;
}

export const NotesViewer: React.FC<NotesViewerProps> = ({ notes, provider, model }) => {
  return (
    <div className="w-full max-w-4xl mx-auto mt-8 bg-white rounded-3xl shadow-sm border border-gray-100 p-8 md:p-12" id="notes-content">
      {(provider || model) && (
        <div className="mb-6 pb-4 border-b border-gray-100 flex items-center justify-between">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-primary/5 text-primary rounded-full text-xs font-medium border border-primary/10">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Generated using <strong>{provider?.toUpperCase()}</strong> &bull; {model}</span>
          </div>
        </div>
      )}

      <div className="markdown-body">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            code({ node, inline, className, children, ...props }: any) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <SyntaxHighlighter
                  {...props}
                  children={String(children).replace(/\n$/, '')}
                  style={vscDarkPlus as any}
                  language={match[1]}
                  PreTag="div"
                />
              ) : (
                <code {...props} className={className}>
                  {children}
                </code>
              );
            },
          }}
        >
          {notes.content}
        </ReactMarkdown>
      </div>
    </div>
  );
};
