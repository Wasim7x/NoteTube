import React, { useState } from 'react';
import { Copy, Download, FileText, RefreshCcw, Plus, Check } from 'lucide-react';
// @ts-ignore
import html2pdf from 'html2pdf.js';

interface ActionsProps {
  markdownContent: string;
  onRegenerate: () => void;
  onNew: () => void;
  title: string;
}

export const Actions: React.FC<ActionsProps> = ({ markdownContent, onRegenerate, onNew, title }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(markdownContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handleDownloadMarkdown = () => {
    const blob = new Blob([markdownContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_notes.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDownloadPDF = () => {
    const element = document.getElementById('notes-content');
    if (!element) return;
    
    // Temporarily adjust some styles for PDF generation if needed
    const opt = {
      margin:       10,
      filename:     `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_notes.pdf`,
      image:        { type: 'jpeg', quality: 0.98 },
      html2canvas:  { scale: 2, useCORS: true },
      jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    html2pdf().set(opt).from(element).save();
  };

  return (
    <div className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-white rounded-full shadow-lg border border-gray-200 px-6 py-3 flex items-center gap-4 z-40 transition-transform hover:scale-105">
      <button 
        onClick={handleCopy}
        className="flex flex-col items-center justify-center gap-1 text-gray-600 hover:text-primary transition-colors min-w-[60px]"
        title="Copy Markdown"
      >
        {copied ? <Check className="w-5 h-5 text-green-500" /> : <Copy className="w-5 h-5" />}
        <span className="text-[10px] font-medium">{copied ? 'Copied!' : 'Copy'}</span>
      </button>
      
      <div className="w-px h-8 bg-gray-200"></div>

      <button 
        onClick={handleDownloadMarkdown}
        className="flex flex-col items-center justify-center gap-1 text-gray-600 hover:text-primary transition-colors min-w-[60px]"
        title="Download .md"
      >
        <FileText className="w-5 h-5" />
        <span className="text-[10px] font-medium">Markdown</span>
      </button>

      <button 
        onClick={handleDownloadPDF}
        className="flex flex-col items-center justify-center gap-1 text-gray-600 hover:text-primary transition-colors min-w-[60px]"
        title="Download PDF"
      >
        <Download className="w-5 h-5" />
        <span className="text-[10px] font-medium">PDF</span>
      </button>

      <div className="w-px h-8 bg-gray-200"></div>

      <button 
        onClick={onRegenerate}
        className="flex flex-col items-center justify-center gap-1 text-gray-600 hover:text-primary transition-colors min-w-[60px]"
        title="Regenerate"
      >
        <RefreshCcw className="w-5 h-5" />
        <span className="text-[10px] font-medium">Retry</span>
      </button>

      <button 
        onClick={onNew}
        className="flex flex-col items-center justify-center gap-1 text-gray-600 hover:text-primary transition-colors min-w-[60px]"
        title="New Video"
      >
        <Plus className="w-5 h-5" />
        <span className="text-[10px] font-medium">New</span>
      </button>
    </div>
  );
};
