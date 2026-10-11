import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import {
  Sparkles,
  Languages,
  BookOpen,
  Clock,
  ExternalLink,
  ListTree,
  Brain,
  BookmarkCheck,
  ChevronDown,
  Film,
  Presentation
} from 'lucide-react';
import type { NotesData, ChapterItem, VideoSlidesResponse } from '../types';
import { SlidesGallery } from './SlidesGallery';
import { SlidePreviewModal } from './SlidePreviewModal';
import { api } from '../services/api';

interface NotesViewerProps {
  notes: NotesData;
  provider?: string;
  model?: string;
  fallbackUsed?: boolean;
  transcriptLanguage?: string;
  transcriptGenerated?: boolean;
  videoId?: string;
  videoTitle?: string;
  overviewContent?: string;
  chapters?: ChapterItem[];
  revisionContent?: string;
  slidesData?: VideoSlidesResponse | null;
  isExtractingSlides?: boolean;
  onRetryExtractSlides?: () => void;
  activeSlideChapterId?: string | null;
  onOpenSlide?: (chapterId: string) => void;
  onCloseSlideModal?: () => void;
}

export const NotesViewer: React.FC<NotesViewerProps> = ({
  notes,
  provider,
  model,
  fallbackUsed,
  transcriptLanguage,
  transcriptGenerated,
  videoId,
  videoTitle,
  overviewContent,
  chapters = [],
  revisionContent,
  slidesData,
  isExtractingSlides = false,
  onRetryExtractSlides,
  activeSlideChapterId,
  onOpenSlide,
  onCloseSlideModal,
}) => {
  const [activeTocOpen, setActiveTocOpen] = useState(true);
  const [internalActiveSlideId, setInternalActiveSlideId] = useState<string | null>(null);

  const effectiveActiveSlideId =
    activeSlideChapterId !== undefined ? activeSlideChapterId : internalActiveSlideId;

  const handleOpenSlide = (chapterId: string) => {
    if (onOpenSlide) {
      onOpenSlide(chapterId);
    } else {
      setInternalActiveSlideId(chapterId);
    }
  };

  const handleCloseSlide = () => {
    if (onCloseSlideModal) {
      onCloseSlideModal();
    } else {
      setInternalActiveSlideId(null);
    }
  };

  const getYoutubeTimestampUrl = (startTimeSeconds: number): string => {
    const s = Math.max(0, Math.floor(startTimeSeconds));
    if (videoId) {
      return `https://www.youtube.com/watch?v=${videoId}&t=${s}s`;
    }
    return `#`;
  };

  const getChapterSectionId = (ch: ChapterItem, idx: number): string => {
    return `chapter-section-${ch.chapter_id || `ch_${idx + 1}`}`;
  };

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (!el) return;
    // Header is sticky top-0 with h-16 (64px). We provide a 76px offset so the heading is visibly below it.
    const headerOffset = 76;
    const elementPosition = el.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.scrollY - headerOffset;
    window.scrollTo({
      top: Math.max(0, offsetPosition),
      behavior: 'smooth'
    });
  };

  const markdownComponents = {
    code({ inline, className, children, ...props }: any) {
      const match = /language-(\w+)/.exec(className || '');
      return !inline && match ? (
        <div className="overflow-x-auto rounded-xl my-4 text-xs font-mono shadow-sm">
          <SyntaxHighlighter
            {...props}
            children={String(children).replace(/\n$/, '')}
            style={vscDarkPlus as any}
            language={match[1]}
            PreTag="div"
          />
        </div>
      ) : (
        <code {...props} className="px-1.5 py-0.5 rounded bg-gray-100 text-gray-800 font-mono text-xs break-words">
          {children}
        </code>
      );
    },
    table({ children }: any) {
      return (
        <div className="overflow-x-auto my-4 rounded-xl border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            {children}
          </table>
        </div>
      );
    }
  };

  const hasStructuredSections = Boolean(
    (overviewContent && overviewContent.trim()) ||
    (chapters && chapters.length > 0) ||
    (revisionContent && revisionContent.trim())
  );

  return (
    <div className="w-full max-w-4xl mx-auto mt-8" id="notes-content">
      {/* Top Metadata Header */}
      <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 md:p-8 mb-6">
        <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-gray-100">
          {(provider || model) && (
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-primary/5 text-primary rounded-full text-xs font-medium border border-primary/10">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Generated with <strong>{provider?.toUpperCase()}</strong> &bull; {model}</span>
            </div>
          )}

          {fallbackUsed ? (
            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-50 text-amber-700 rounded-full text-xs font-medium border border-amber-200">
              <BookOpen className="w-3.5 h-3.5 text-amber-600" />
              <span>Synthesized from syllabus &amp; roadmap (captions unavailable)</span>
            </div>
          ) : transcriptLanguage ? (
            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium border border-blue-200">
              <Languages className="w-3.5 h-3.5 text-blue-600" />
              <span>Transcript: {transcriptLanguage} {transcriptGenerated ? '(auto-generated)' : '(manual)'}</span>
            </div>
          ) : null}
        </div>

        {/* Table of Contents */}
        {hasStructuredSections && (
          <div className="mt-5 pt-2">
            <button
              onClick={() => setActiveTocOpen(!activeTocOpen)}
              className="flex items-center justify-between w-full text-left font-semibold text-gray-800 text-sm hover:text-primary transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-2">
                <ListTree className="w-4 h-4 text-primary" />
                <span>Table of Contents ({chapters.length > 0 ? `${chapters.length} Chapters` : 'Overview & Notes'})</span>
              </div>
              <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${activeTocOpen ? 'rotate-180' : ''}`} />
            </button>

            {activeTocOpen && (
              <div className="mt-3.5 grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 border-t border-gray-50 max-h-72 overflow-y-auto pr-1">
                {overviewContent && (
                  <button
                    onClick={() => scrollToSection('video-overview')}
                    className="flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium text-gray-700 hover:text-primary hover:bg-gray-50 border border-transparent hover:border-gray-200 transition-all text-left"
                  >
                    <BookmarkCheck className="w-3.5 h-3.5 text-primary shrink-0" />
                    <span className="truncate">Video Overview &amp; Key Objectives</span>
                  </button>
                )}

                {/* TOC Link to Chapter Slides */}
                <button
                  onClick={() => scrollToSection('chapter-slides-section')}
                  className="flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium text-indigo-700 hover:text-indigo-900 bg-indigo-50/60 hover:bg-indigo-50 border border-indigo-100 transition-all text-left"
                >
                  <Presentation className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                  <span className="truncate">
                    Chapter Slides &amp; Presentation ({slidesData?.extracted_slides ?? 0} Slides)
                  </span>
                </button>

                {chapters.map((ch, idx) => (
                  <button
                    key={ch.chapter_id || idx}
                    onClick={() => scrollToSection(getChapterSectionId(ch, idx))}
                    className="flex items-center justify-between gap-2 px-3 py-2 rounded-xl text-xs font-medium text-gray-700 hover:text-primary hover:bg-gray-50 border border-transparent hover:border-gray-200 transition-all text-left cursor-pointer"
                  >
                    <div className="flex items-center gap-2 truncate">
                      <span className="text-gray-400 font-mono text-[11px] shrink-0">#{idx + 1}</span>
                      <span className="truncate">{ch.title}</span>
                    </div>
                    {ch.timestamp_str && (
                      <span className="text-[10px] text-gray-400 shrink-0 font-mono">{ch.timestamp_str.split('–')[0].trim()}</span>
                    )}
                  </button>
                ))}

                {revisionContent && (
                  <button
                    onClick={() => scrollToSection('final-revision')}
                    className="flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium text-gray-700 hover:text-primary hover:bg-gray-50 border border-transparent hover:border-gray-200 transition-all text-left"
                  >
                    <Brain className="w-3.5 h-3.5 text-purple-600 shrink-0" />
                    <span className="truncate">Final Revision &amp; Assessment</span>
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Structured Sections Mode */}
      {hasStructuredSections ? (
        <div className="space-y-8">
          {/* Section A: Video Overview */}
          {overviewContent && (
            <section id="video-overview" className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 md:p-10 scroll-mt-20">
              <div className="flex items-center gap-2.5 pb-4 mb-6 border-b border-gray-100">
                <div className="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center text-primary font-bold text-sm">
                  A
                </div>
                <div>
                  <h2 className="text-lg font-bold text-gray-900 leading-tight">Video Overview</h2>
                  <p className="text-xs text-gray-500">High-level summary, learning objectives, and core concepts</p>
                </div>
              </div>
              <div className="markdown-body">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                  {overviewContent}
                </ReactMarkdown>
              </div>
            </section>
          )}

          {/* Section: Dedicated Chapter Slides & Presentation Gallery */}
          <SlidesGallery
            slidesData={slidesData || null}
            isLoading={Boolean(isExtractingSlides)}
            videoId={videoId}
            videoTitle={videoTitle || notes.title}
            onOpenSlide={handleOpenSlide}
            onRetryExtract={onRetryExtractSlides}
            getSlideImageUrl={api.getSlideImageUrl}
            getDownloadPptUrl={api.getDownloadPptUrl}
          />

          {/* Section B: Chapter-by-Chapter Notes */}
          {chapters.map((chapter, idx) => (
            <section
              key={chapter.chapter_id || idx}
              id={getChapterSectionId(chapter, idx)}
              className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 md:p-10 scroll-mt-24 transition-all hover:border-gray-200"
            >
              {/* Chapter Header Banner */}
              <div className="pb-5 mb-6 border-b border-gray-100">
                <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-primary text-white tracking-wide">
                      Chapter {idx + 1}
                    </span>
                    {chapter.is_ai_detected && (
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                        AI-Detected Chapter
                      </span>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    {/* View Slide Button */}
                    <button
                      onClick={() => handleOpenSlide(chapter.chapter_id || `ch_${idx + 1}`)}
                      className="inline-flex items-center gap-1.5 px-3 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-semibold rounded-full border border-indigo-200 transition-all cursor-pointer shadow-xs active:scale-[0.98]"
                      title="Click to view extracted slide frame for this chapter"
                    >
                      <Film className="w-3.5 h-3.5 text-indigo-600" />
                      <span>View Slide</span>
                    </button>

                    {chapter.timestamp_str && (
                      <a
                        href={getYoutubeTimestampUrl(chapter.start_time)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 px-3 py-1 bg-red-50 hover:bg-red-100 text-red-700 text-xs font-semibold rounded-full border border-red-200/60 transition-colors"
                        title="Click to watch this chapter on YouTube"
                      >
                        <Clock className="w-3.5 h-3.5 text-red-600" />
                        <span>{chapter.timestamp_str}</span>
                        <ExternalLink className="w-3 h-3 text-red-500 ml-0.5" />
                      </a>
                    )}
                    {chapter.duration_str && (
                      <span className="text-xs text-gray-500 hidden sm:inline">
                        ({chapter.duration_str})
                      </span>
                    )}
                  </div>
                </div>

                <h3 className="text-xl md:text-2xl font-bold text-gray-900 leading-snug">
                  {chapter.title}
                </h3>
              </div>

              {/* Chapter Content */}
              <div className="markdown-body">
                {chapter.content ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                    {chapter.content}
                  </ReactMarkdown>
                ) : (
                  <div className="py-6 text-center text-sm text-gray-400 italic">
                    Notes for this chapter are generating...
                  </div>
                )}
              </div>
            </section>
          ))}

          {/* Section C: Final Revision Section */}
          {revisionContent && (
            <section id="final-revision" className="bg-white rounded-3xl shadow-sm border border-purple-100/70 p-8 md:p-10 scroll-mt-20">
              <div className="flex items-center gap-2.5 pb-4 mb-6 border-b border-gray-100">
                <div className="w-8 h-8 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-sm">
                  C
                </div>
                <div>
                  <h2 className="text-lg font-bold text-gray-900 leading-tight">Final Revision &amp; Assessment</h2>
                  <p className="text-xs text-gray-500">Summary review, rapid notes, glossary, and self-assessment quiz</p>
                </div>
              </div>
              <div className="markdown-body">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                  {revisionContent}
                </ReactMarkdown>
              </div>
            </section>
          )}
        </div>
      ) : (
        /* Fallback Single Unified Document Mode */
        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 md:p-12">
          <div className="markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
              {notes.content}
            </ReactMarkdown>
          </div>
        </div>
      )}

      {/* Interactive Slide Preview Modal */}
      {effectiveActiveSlideId && slidesData && slidesData.slides.length > 0 && (
        <SlidePreviewModal
          slides={slidesData.slides}
          activeChapterId={effectiveActiveSlideId}
          videoId={videoId}
          onClose={handleCloseSlide}
          onSelectChapter={handleOpenSlide}
          getSlideImageUrl={api.getSlideImageUrl}
        />
      )}
    </div>
  );
};
