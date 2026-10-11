import React from 'react';
import {
  Zap,
  BookOpen,
  Image as ImageIcon,
  Sparkles,
  Layers,
  ArrowRight,
  Loader2,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import type { ProcessingMode } from '../types';

export interface ModeSelectorProps {
  selectedMode: ProcessingMode;
  onSelectMode: (mode: ProcessingMode) => void;
  onRunMode: (mode: ProcessingMode) => void;
  isProcessing: boolean;
  activeProcessingMode?: ProcessingMode | null;
  modeStatus?: Record<ProcessingMode, { completed: boolean; hasError?: boolean }>;
  disabled?: boolean;
}

interface ModeCardConfig {
  id: ProcessingMode;
  title: string;
  badge: string;
  badgeColor: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  isComingSoon?: boolean;
  actionLabel: string;
}

const MODES: ModeCardConfig[] = [
  {
    id: 'summary',
    title: '1. Quick Summary',
    badge: 'Fastest • Transcript Only',
    badgeColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    description: 'Fast, concise overview highlighting core takeaways and essential concepts without video download.',
    icon: Zap,
    actionLabel: 'Generate Summary',
  },
  {
    id: 'detailed',
    title: '2. Detailed Notes',
    badge: 'Comprehensive Study',
    badgeColor: 'bg-blue-50 text-blue-700 border-blue-200',
    description: 'In-depth chapter-by-chapter study notes, key terminology, practical examples, and conclusion.',
    icon: BookOpen,
    actionLabel: 'Generate Detailed Notes',
  },
  {
    id: 'chapter_slides',
    title: '3. Chapter-End Slides',
    badge: 'Visual PPTX • Fast Seek',
    badgeColor: 'bg-purple-50 text-purple-700 border-purple-200',
    description: 'Extract 1 representative frame per chapter (5s before chapter end) and build a downloadable PowerPoint presentation.',
    icon: ImageIcon,
    actionLabel: 'Extract Slides & PPT',
  },
  {
    id: 'unique_slides',
    title: '4. Advanced Unique Slides',
    badge: 'Coming Soon',
    badgeColor: 'bg-amber-50 text-amber-700 border-amber-200',
    description: 'Perceptual hashing and scene-change detection to extract all unique presentation slides. Available in next update.',
    icon: Sparkles,
    isComingSoon: true,
    actionLabel: 'Coming Soon',
  },
  {
    id: 'complete_notes',
    title: '5. Complete AI Notes',
    badge: 'Full NoteTube Pipeline',
    badgeColor: 'bg-rose-50 text-rose-700 border-rose-200',
    description: 'Original complete pipeline: Overview, Table of Contents, deep chapter notes, slide previews, and revision.',
    icon: Layers,
    actionLabel: 'Generate Complete Notes',
  },
];

export const ModeSelector: React.FC<ModeSelectorProps> = ({
  selectedMode,
  onSelectMode,
  onRunMode,
  isProcessing,
  activeProcessingMode,
  modeStatus,
  disabled = false,
}) => {
  return (
    <section className="w-full my-8 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900 tracking-tight">Choose Processing Mode</h2>
          <p className="text-sm text-gray-500">
            Select one of five specialized workflows for your loaded video.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {MODES.map((mode) => {
          const Icon = mode.icon;
          const isSelected = selectedMode === mode.id;
          const isModeRunning = isProcessing && activeProcessingMode === mode.id;
          const isCompleted = modeStatus?.[mode.id]?.completed;
          const hasError = modeStatus?.[mode.id]?.hasError;

          return (
            <div
              key={mode.id}
              onClick={() => {
                if (!isProcessing) {
                  onSelectMode(mode.id);
                }
              }}
              className={`group relative rounded-2xl p-5 border text-left transition-all duration-200 cursor-pointer flex flex-col justify-between ${
                isSelected
                  ? 'bg-white border-primary shadow-md ring-2 ring-primary/20 scale-[1.01]'
                  : 'bg-white/80 hover:bg-white border-gray-200/80 hover:border-gray-300 hover:shadow-sm'
              } ${disabled || (isProcessing && !isModeRunning) ? 'opacity-60 cursor-not-allowed' : ''}`}
            >
              <div>
                {/* Header row: Icon + Badge */}
                <div className="flex items-center justify-between gap-2 mb-3">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center transition-colors ${
                      isSelected
                        ? 'bg-primary text-white shadow-xs'
                        : 'bg-gray-100 text-gray-700 group-hover:bg-primary/10 group-hover:text-primary'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                  <span
                    className={`text-[11px] font-semibold px-2.5 py-1 rounded-full border ${mode.badgeColor}`}
                  >
                    {mode.badge}
                  </span>
                </div>

                {/* Title & Description */}
                <h3 className="font-bold text-gray-900 text-base mb-1.5 flex items-center gap-1.5">
                  {mode.title}
                  {isCompleted && (
                    <span title="Output ready">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 inline" />
                    </span>
                  )}
                  {hasError && (
                    <span title="Encountered an issue">
                      <AlertCircle className="w-4 h-4 text-red-500 shrink-0 inline" />
                    </span>
                  )}
                </h3>
                <p className="text-xs text-gray-600 leading-relaxed mb-4">
                  {mode.description}
                </p>
              </div>

              {/* Action Button */}
              <div className="pt-2 border-t border-gray-100 flex items-center justify-between">
                {mode.isComingSoon ? (
                  <span className="text-xs font-semibold text-amber-700 bg-amber-50 px-3 py-1.5 rounded-lg border border-amber-200 w-full text-center">
                    Feature Coming Soon
                  </span>
                ) : (
                  <button
                    type="button"
                    disabled={disabled || isProcessing}
                    onClick={(e) => {
                      e.stopPropagation();
                      onRunMode(mode.id);
                    }}
                    className={`w-full py-2 px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                      isModeRunning
                        ? 'bg-primary/10 text-primary border border-primary/30'
                        : isSelected
                        ? 'bg-primary hover:bg-primaryHover text-white shadow-xs active:scale-98'
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                    }`}
                  >
                    {isModeRunning ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        <span>Processing...</span>
                      </>
                    ) : (
                      <>
                        <span>{isCompleted ? `View / Re-run` : mode.actionLabel}</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
