import React, { useEffect, useState } from 'react';
import { Loader2, CheckCircle2, Circle } from 'lucide-react';

export const LoadingState: React.FC = () => {
  const [step, setStep] = useState(0);

  useEffect(() => {
    // Simulate progression for better UX
    const timers = [
      setTimeout(() => setStep(1), 1500),
      setTimeout(() => setStep(2), 4000),
      setTimeout(() => setStep(3), 8000),
    ];

    return () => timers.forEach(clearTimeout);
  }, []);

  const steps = [
    { label: 'Video detected' },
    { label: 'Extracting transcript' },
    { label: 'Understanding video content' },
    { label: 'Structuring and finalizing notes' },
  ];

  return (
    <div className="w-full max-w-lg mx-auto mt-20 p-8 bg-white rounded-3xl shadow-sm border border-gray-100">
      <div className="flex flex-col items-center justify-center mb-8">
        <div className="relative">
          <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full"></div>
          <Loader2 className="w-12 h-12 text-primary animate-spin relative" />
        </div>
        <h3 className="mt-4 text-xl font-semibold text-gray-800">Working magic...</h3>
        <p className="text-gray-500 text-sm mt-1">This might take a minute for long videos.</p>
      </div>

      <div className="space-y-4">
        {steps.map((s, index) => {
          const isCompleted = step > index;
          const isActive = step === index;
          
          return (
            <div key={index} className={`flex items-center gap-3 transition-opacity duration-500 ${isCompleted || isActive ? 'opacity-100' : 'opacity-40'}`}>
              {isCompleted ? (
                <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0" />
              ) : isActive ? (
                <div className="w-5 h-5 flex items-center justify-center shrink-0">
                  <div className="w-2 h-2 bg-primary rounded-full animate-ping"></div>
                </div>
              ) : (
                <Circle className="w-5 h-5 text-gray-300 shrink-0" />
              )}
              <span className={`text-sm font-medium ${isActive ? 'text-gray-900' : isCompleted ? 'text-gray-600' : 'text-gray-400'}`}>
                {s.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
