import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Zap,
  CheckCircle2,
  Copy,
  Download,
  Tag,
  Check,
  Cpu
} from 'lucide-react';
import type { QuickSummaryResponse } from '../types';

interface QuickSummaryViewProps {
  data: QuickSummaryResponse;
  videoTitle?: string;
}

export const QuickSummaryView: React.FC<QuickSummaryViewProps> = ({ data, videoTitle }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(data.markdown_content || data.summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
    }
  };

  const handleDownloadMd = () => {
    const filename = `${(videoTitle || data.title || 'quick_summary').replace(/[^a-zA-Z0-9_-]/g, '_')}_summary.md`;
    const blob = new Blob([data.markdown_content || data.summary], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full max-w-4xl mx-auto my-6 bg-white rounded-3xl border border-gray-100 shadow-sm p-6 sm:p-8 animate-in fade-in duration-300">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 mb-6 border-b border-gray-100 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <Zap className="w-3.5 h-3.5 text-emerald-600" />
              Quick Summary
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-gray-100 text-gray-600">
              <Cpu className="w-3 h-3 text-gray-500" />
              {data.provider} / {data.model}
            </span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 leading-snug">
            {data.title || videoTitle || 'Video Summary'}
          </h2>
        </div>

        {/* Quick Actions */}
        <div className="flex items-center gap-2 self-start sm:self-center">
          <button
            type="button"
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-gray-100 hover:bg-gray-200 text-gray-700 transition-all cursor-pointer"
            title="Copy summary to clipboard"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
          <button
            type="button"
            onClick={handleDownloadMd}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-primary hover:bg-primaryHover text-white transition-all cursor-pointer shadow-xs"
            title="Download summary as markdown"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download .md</span>
          </button>
        </div>
      </div>

      {/* Key Takeaways Cards */}
      {data.key_takeaways && data.key_takeaways.length > 0 && (
        <div className="mb-8">
          <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider flex items-center gap-2 mb-3">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            Key Takeaways
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {data.key_takeaways.map((takeaway, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-2xl bg-emerald-50/50 border border-emerald-100 flex items-start gap-3"
              >
                <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <p className="text-xs sm:text-sm text-gray-800 leading-relaxed font-medium">
                  {takeaway}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Core Concepts */}
      {data.core_concepts && data.core_concepts.length > 0 && (
        <div className="mb-8">
          <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider flex items-center gap-2 mb-3">
            <Tag className="w-4 h-4 text-indigo-600" />
            Core Concepts
          </h3>
          <div className="flex flex-wrap gap-2">
            {data.core_concepts.map((concept, idx) => (
              <span
                key={idx}
                className="px-3 py-1.5 rounded-xl bg-indigo-50 text-indigo-800 text-xs font-medium border border-indigo-100"
              >
                {concept}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Markdown Body */}
      <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed pt-4 border-t border-gray-100">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {data.markdown_content || data.summary}
        </ReactMarkdown>
      </div>
    </div>
  );
};
