import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  BookOpen,
  Cpu,
  Globe,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Layers,
  Info
} from 'lucide-react';
import type { DetailedNotesResponse } from '../types';

interface DetailedNotesViewProps {
  data: DetailedNotesResponse;
  videoTitle?: string;
  onOpenSlide?: (chapterId: string) => void;
}

export const DetailedNotesView: React.FC<DetailedNotesViewProps> = ({
  data,
  videoTitle,
}) => {
  return (
    <div className="w-full max-w-4xl mx-auto my-6 bg-white rounded-3xl border border-gray-100 shadow-sm p-6 sm:p-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="pb-6 mb-6 border-b border-gray-100">
        <div className="flex flex-wrap items-center gap-2 mb-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200">
            <BookOpen className="w-3.5 h-3.5 text-blue-600" />
            Detailed Study Notes
          </span>
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-gray-100 text-gray-600">
            <Cpu className="w-3 h-3 text-gray-500" />
            {data.provider} / {data.model}
          </span>
          {data.external_research_used ? (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
              <Globe className="w-3 h-3 text-emerald-600" />
              Supplemental External Research Added
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-indigo-50 text-indigo-700 border border-indigo-200">
              <ShieldCheck className="w-3 h-3 text-indigo-600" />
              100% Transcript-Grounded
            </span>
          )}
        </div>
        <h2 className="text-2xl font-bold text-gray-900 leading-snug">
          {data.title || videoTitle || 'Detailed Notes'}
        </h2>
      </div>

      {/* Overview Card */}
      {data.overview && (
        <div className="p-5 rounded-2xl bg-blue-50/40 border border-blue-100/70 mb-8">
          <h3 className="text-xs font-bold uppercase tracking-wider text-blue-900 mb-2 flex items-center gap-2">
            <Info className="w-4 h-4 text-blue-600" />
            Executive Overview
          </h3>
          <div className="prose prose-sm text-gray-700 leading-relaxed max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.overview}</ReactMarkdown>
          </div>
        </div>
      )}

      {/* Chapter breakdown pills if present */}
      {data.chapters && data.chapters.length > 0 && (
        <div className="mb-8 p-4 rounded-2xl bg-gray-50 border border-gray-100">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-600 mb-3 flex items-center gap-2">
            <Layers className="w-4 h-4 text-gray-500" />
            Included Chapters ({data.chapters.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {data.chapters.map((ch, idx) => {
              const timeDisplay = ch.timestamp_str || `${Math.floor(ch.start_time / 60)}:${String(Math.floor(ch.start_time % 60)).padStart(2, '0')}`;
              return (
                <span
                  key={ch.chapter_id || idx}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-white border border-gray-200 text-xs font-medium text-gray-700 shadow-xs"
                >
                  <Clock className="w-3 h-3 text-gray-400" />
                  <span>{timeDisplay}</span>
                  <span className="text-gray-300">&bull;</span>
                  <span className="truncate max-w-[200px]">{ch.title}</span>
                </span>
              );
            })}
          </div>
        </div>
      )}

      {/* Main Markdown Content */}
      <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed pt-2">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {data.markdown_content}
        </ReactMarkdown>
      </div>

      {/* Concluding Revision / Summary */}
      {data.revision_summary && (
        <div className="mt-8 pt-6 border-t border-gray-100">
          <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            Summary & Key Points
          </h3>
          <div className="p-4 rounded-2xl bg-emerald-50/30 border border-emerald-100 text-xs sm:text-sm text-gray-700 leading-relaxed prose prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.revision_summary}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
};
