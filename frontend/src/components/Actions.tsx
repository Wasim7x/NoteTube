import React, { useState } from 'react';
import { Copy, Download, FileText, RefreshCcw, Plus, Check, Loader2, AlertCircle } from 'lucide-react';
// @ts-ignore
import html2pdf from 'html2pdf.js';

interface ActionsProps {
  markdownContent: string;
  title: string;
  onRegenerate: () => void;
  onNew: () => void;
  isRetrying?: boolean;
  isChatOpen?: boolean;
}

export const Actions: React.FC<ActionsProps> = ({
  markdownContent,
  title,
  onRegenerate,
  onNew,
  isRetrying = false,
  isChatOpen = false,
}) => {
  const [copied, setCopied] = useState(false);
  const [downloadedMd, setDownloadedMd] = useState(false);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState<{ text: string; isError?: boolean } | null>(null);

  const showNotification = (text: string, isError = false) => {
    setFeedbackMessage({ text, isError });
    setTimeout(() => {
      setFeedbackMessage(null);
    }, 3000);
  };

  const handleCopy = async () => {
    if (!markdownContent || !markdownContent.trim()) {
      showNotification('No notes content available to copy.', true);
      return;
    }

    let success = false;

    // 1. Try standard modern clipboard API
    if (navigator?.clipboard && typeof navigator.clipboard.writeText === 'function') {
      try {
        await navigator.clipboard.writeText(markdownContent);
        success = true;
      } catch (err) {
        console.warn('Navigator clipboard API failed, attempting fallback...', err);
      }
    }

    // 2. Fallback to hidden DOM textarea with execCommand
    if (!success) {
      try {
        const textarea = document.createElement('textarea');
        textarea.value = markdownContent;
        textarea.style.position = 'fixed';
        textarea.style.top = '-9999px';
        textarea.style.left = '-9999px';
        textarea.setAttribute('readonly', '');
        document.body.appendChild(textarea);
        textarea.select();
        success = document.execCommand('copy');
        document.body.removeChild(textarea);
      } catch (fallbackErr) {
        console.error('Copy fallback failed:', fallbackErr);
      }
    }

    if (success) {
      setCopied(true);
      showNotification('Notes copied to clipboard!');
      setTimeout(() => setCopied(false), 2000);
    } else {
      showNotification('Failed to copy to clipboard.', true);
    }
  };

  const handleDownloadMarkdown = () => {
    if (!markdownContent || !markdownContent.trim()) {
      showNotification('No notes available to download.', true);
      return;
    }

    try {
      const cleanTitle = (title || 'NoteTube_Notes')
        .replace(/[^a-zA-Z0-9_-]/g, '_')
        .replace(/_+/g, '_')
        .toLowerCase();

      const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${cleanTitle}_notes.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      setDownloadedMd(true);
      showNotification('Markdown (.md) downloaded!');
      setTimeout(() => setDownloadedMd(false), 2000);
    } catch (err: any) {
      console.error('Markdown download error:', err);
      showNotification('Failed to download Markdown file.', true);
    }
  };

  const handleDownloadPDF = async () => {
    const rawElement = document.getElementById('notes-content');
    if (!rawElement) {
      showNotification('Notes element not found for PDF export.', true);
      return;
    }

    setIsGeneratingPdf(true);
    showNotification('Generating high-resolution PDF...');

    try {
      const cleanTitle = (title || 'NoteTube_Notes')
        .replace(/[^a-zA-Z0-9_-]/g, '_')
        .replace(/_+/g, '_')
        .toLowerCase();

      // Create a clean printable clone with standardized styles to avoid oklch / canvas crashes
      const printContainer = document.createElement('div');
      printContainer.id = 'notetube-pdf-print-container';
      printContainer.style.position = 'absolute';
      printContainer.style.left = '-9999px';
      printContainer.style.top = '0';
      printContainer.style.width = '800px';
      printContainer.style.backgroundColor = '#ffffff';
      printContainer.style.color = '#1f2937';
      printContainer.style.padding = '32px';
      printContainer.style.fontFamily = 'Arial, Helvetica, sans-serif';
      printContainer.style.fontSize = '14px';
      printContainer.style.lineHeight = '1.6';

      // Clone content and remove interactive elements (modals, galleries, buttons)
      const clone = rawElement.cloneNode(true) as HTMLElement;
      clone.querySelectorAll('button').forEach((b) => b.remove());
      clone.querySelectorAll('.slides-gallery-interactive').forEach((g) => g.remove());
      clone.querySelectorAll('[role="dialog"]').forEach((d) => d.remove());
      clone.querySelectorAll('.fixed').forEach((f) => f.remove());

      // Ensure page-break avoid rules on sections and pre/code
      clone.querySelectorAll('section, h1, h2, h3, pre, table').forEach((el) => {
        const hEl = el as HTMLElement;
        hEl.style.breakInside = 'avoid';
        hEl.style.pageBreakInside = 'avoid';
      });

      // Title header
      const headerTitle = document.createElement('div');
      headerTitle.innerHTML = `
        <div style="border-bottom: 2px solid #6366f1; padding-bottom: 12px; margin-bottom: 24px;">
          <h1 style="font-size: 22px; font-weight: bold; color: #111827; margin: 0;">${title || 'NoteTube Study Notes'}</h1>
          <p style="font-size: 11px; color: #6b7280; margin: 4px 0 0 0;">Generated with NoteTube AI Video Learning Architecture</p>
        </div>
      `;
      printContainer.appendChild(headerTitle);
      printContainer.appendChild(clone);
      document.body.appendChild(printContainer);

      const opt = {
        margin: [12, 12, 12, 12] as [number, number, number, number],
        filename: `${cleanTitle}_notes.pdf`,
        image: { type: 'jpeg' as const, quality: 0.98 },
        html2canvas: {
          scale: 2,
          useCORS: true,
          letterRendering: true,
          logging: false
        },
        jsPDF: { unit: 'mm' as const, format: 'a4' as const, orientation: 'portrait' as const },
        pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
      };

      await html2pdf().set(opt).from(printContainer).save();
      document.body.removeChild(printContainer);

      showNotification('PDF downloaded successfully!');
    } catch (err: any) {
      console.error('PDF export error:', err);
      showNotification('PDF generation failed. Please try downloading as Markdown.', true);
      const existing = document.getElementById('notetube-pdf-print-container');
      if (existing) existing.remove();
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  return (
    <div
      className={`fixed bottom-8 z-40 flex flex-col items-center transition-all duration-300 pointer-events-none ${
        isChatOpen
          ? 'left-1/2 -translate-x-1/2 lg:left-[calc((100vw-420px)/2)] lg:-translate-x-1/2'
          : 'left-1/2 -translate-x-1/2'
      }`}
    >
      {/* Toast Notification Banner */}
      {feedbackMessage && (
        <div
          className={`pointer-events-auto mb-3 px-4 py-2 rounded-full text-xs font-semibold shadow-lg border backdrop-blur-md animate-in fade-in slide-in-from-bottom-2 duration-200 flex items-center gap-1.5 ${
            feedbackMessage.isError
              ? 'bg-red-900/90 text-white border-red-700'
              : 'bg-gray-900/90 text-white border-gray-700'
          }`}
        >
          {feedbackMessage.isError ? (
            <AlertCircle className="w-3.5 h-3.5 text-red-400 shrink-0" />
          ) : (
            <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
          )}
          <span>{feedbackMessage.text}</span>
        </div>
      )}

      {/* Floating Toolbar Pill */}
      <div className="pointer-events-auto bg-white/95 backdrop-blur-md rounded-full shadow-[0_10px_35px_rgba(0,0,0,0.12)] border border-gray-200/90 px-6 py-2.5 flex items-center gap-3 sm:gap-4 transition-all hover:shadow-[0_12px_40px_rgba(0,0,0,0.16)]">
        {/* Copy Button */}
        <button
          onClick={handleCopy}
          className="flex flex-col items-center justify-center gap-1 text-gray-600 hover:text-primary transition-colors min-w-[54px] cursor-pointer"
          title="Copy full notes markdown to clipboard"
        >
          {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
          <span className={`text-[10px] font-medium ${copied ? 'text-emerald-600 font-bold' : ''}`}>
            {copied ? 'Copied!' : 'Copy'}
          </span>
        </button>

        <div className="w-px h-7 bg-gray-200"></div>

        {/* Markdown Download */}
        <button
          onClick={handleDownloadMarkdown}
          className="flex flex-col items-center justify-center gap-1 text-gray-600 hover:text-primary transition-colors min-w-[54px] cursor-pointer"
          title="Download as formatted Markdown (.md)"
        >
          {downloadedMd ? (
            <Check className="w-4 h-4 text-emerald-500" />
          ) : (
            <FileText className="w-4 h-4" />
          )}
          <span className="text-[10px] font-medium">Markdown</span>
        </button>

        {/* PDF Download */}
        <button
          onClick={handleDownloadPDF}
          disabled={isGeneratingPdf}
          className="flex flex-col items-center justify-center gap-1 text-gray-600 hover:text-primary transition-colors min-w-[54px] cursor-pointer disabled:opacity-60"
          title="Export notes as PDF document"
        >
          {isGeneratingPdf ? (
            <Loader2 className="w-4 h-4 animate-spin text-primary" />
          ) : (
            <Download className="w-4 h-4" />
          )}
          <span className="text-[10px] font-medium">PDF</span>
        </button>

        <div className="w-px h-7 bg-gray-200"></div>

        {/* Retry Button */}
        <button
          onClick={onRegenerate}
          disabled={isRetrying}
          className="flex flex-col items-center justify-center gap-1 text-gray-600 hover:text-primary transition-colors min-w-[54px] cursor-pointer disabled:opacity-60"
          title="Retry or regenerate active operation"
        >
          <RefreshCcw className={`w-4 h-4 ${isRetrying ? 'animate-spin text-primary' : ''}`} />
          <span className="text-[10px] font-medium">{isRetrying ? 'Retrying...' : 'Retry'}</span>
        </button>

        {/* New Button */}
        <button
          onClick={onNew}
          className="flex flex-col items-center justify-center gap-1 text-gray-600 hover:text-primary transition-colors min-w-[54px] cursor-pointer"
          title="Process a new video"
        >
          <Plus className="w-4 h-4" />
          <span className="text-[10px] font-medium">New</span>
        </button>
      </div>
    </div>
  );
};
