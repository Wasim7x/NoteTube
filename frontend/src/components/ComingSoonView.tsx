import React from 'react';
import { Sparkles, Film, Cpu, Layers, Info } from 'lucide-react';

export const ComingSoonView: React.FC = () => {
  return (
    <div className="w-full max-w-2xl mx-auto my-8 p-8 bg-amber-50/70 border border-amber-200/80 rounded-3xl text-center shadow-xs animate-in fade-in duration-300">
      <div className="w-14 h-14 rounded-2xl bg-amber-100 text-amber-700 flex items-center justify-center mx-auto mb-4 shadow-xs">
        <Sparkles className="w-7 h-7" />
      </div>
      <span className="inline-block text-[11px] font-bold uppercase tracking-wider px-3 py-1 rounded-full bg-amber-200/60 text-amber-900 mb-3 border border-amber-300/60">
        Roadmap Feature
      </span>
      <h3 className="text-2xl font-bold text-gray-900 mb-3">
        Advanced Unique Slide Extraction is coming soon.
      </h3>
      <p className="text-sm text-gray-600 max-w-lg mx-auto leading-relaxed mb-6">
        This upcoming release will detect and extract every unique presentation slide throughout the video using intelligent frame sampling, perceptual hashing, and scene-change detection.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left max-w-lg mx-auto">
        <div className="p-3 bg-white/80 rounded-xl border border-amber-100">
          <div className="text-xs font-bold text-gray-900 mb-1 flex items-center gap-1.5">
            <Film className="w-3.5 h-3.5 text-amber-600" />
            Perceptual Hashing
          </div>
          <p className="text-[11px] text-gray-500">Filters visual duplicates across slide pauses.</p>
        </div>

        <div className="p-3 bg-white/80 rounded-xl border border-amber-100">
          <div className="text-xs font-bold text-gray-900 mb-1 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-amber-600" />
            Stable Frame Filter
          </div>
          <p className="text-[11px] text-gray-500">Avoids blurry video transitions and webcam overlays.</p>
        </div>

        <div className="p-3 bg-white/80 rounded-xl border border-amber-100">
          <div className="text-xs font-bold text-gray-900 mb-1 flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-amber-600" />
            Zero Video Lag
          </div>
          <p className="text-[11px] text-gray-500">High-efficiency ffmpeg keyframe seek pipeline.</p>
        </div>
      </div>

      <div className="mt-6 flex items-center justify-center gap-2 text-xs text-amber-800">
        <Info className="w-4 h-4" />
        <span>No video downloads or API calls are initiated for this preview mode.</span>
      </div>
    </div>
  );
};
