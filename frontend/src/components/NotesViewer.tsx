import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { NotesData } from '../types';

interface NotesViewerProps {
  notes: NotesData;
}

export const NotesViewer: React.FC<NotesViewerProps> = ({ notes }) => {
  return (
    <div className="w-full max-w-4xl mx-auto mt-8 bg-white rounded-3xl shadow-sm border border-gray-100 p-8 md:p-12" id="notes-content">
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
