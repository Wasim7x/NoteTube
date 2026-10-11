import React, { useState, useRef, useEffect } from 'react';
import {
  X,
  Send,
  Loader2,
  Trash2,
  Clock,
  ExternalLink,
  ShieldCheck
} from 'lucide-react';
import geminiChatbotSvg from '../assets/gemini-chatbot.svg';
import type { ChatMessage, RAGSourceChunk } from '../types';
import { api } from '../services/api';

interface ChatbotDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  videoId: string;
  videoTitle: string;
  provider: string;
  model: string;
  apiKey: string;
}

export const ChatbotDrawer: React.FC<ChatbotDrawerProps> = ({
  isOpen,
  onClose,
  videoId,
  videoTitle,
  provider,
  model,
  apiKey,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  // Load existing chat history from localStorage or set initial welcome message
  useEffect(() => {
    if (videoId) {
      try {
        const saved = localStorage.getItem(`notetube_chat_${videoId}`);
        if (saved) {
          const parsed = JSON.parse(saved);
          if (Array.isArray(parsed) && parsed.length > 0) {
            setMessages(parsed);
            return;
          }
        }
      } catch (e) {
        console.warn('Failed to parse saved chat history:', e);
      }

      setMessages([
        {
          id: 'welcome_msg',
          sender: 'assistant',
          text: `Hi! I'm your transcript study assistant for "${videoTitle || 'this video'}". Ask me anything discussed in the video, and I will cite the exact timestamps!`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          grounded: true
        }
      ]);
    }
  }, [videoId, videoTitle]);

  // Persist messages whenever updated
  useEffect(() => {
    if (videoId && messages.length > 0) {
      try {
        localStorage.setItem(`notetube_chat_${videoId}`, JSON.stringify(messages));
      } catch (e) {
        console.warn('Failed to save chat history:', e);
      }
    }
  }, [videoId, messages]);

  if (!isOpen) {
    return null;
  }

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const query = input.trim();
    if (!query || isLoading) return;

    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.askChatbot({
        video_id: videoId,
        query: query,
        provider: provider,
        model: model,
        api_key: apiKey
      });

      const assistantMsg: ChatMessage = {
        id: `assistant_${Date.now()}`,
        sender: 'assistant',
        text: response.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sources: response.sources || [],
        grounded: response.grounded
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err_${Date.now()}`,
        sender: 'assistant',
        text: err.message || 'Sorry, I encountered an issue querying the video transcript. Please try again.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        grounded: false
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: `welcome_${Date.now()}`,
        sender: 'assistant',
        text: 'Chat history cleared. What else would you like to know about this video?',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        grounded: true
      }
    ]);
    if (videoId) {
      try {
        localStorage.removeItem(`notetube_chat_${videoId}`);
      } catch (e) {}
    }
  };

  const getYoutubeTimestampUrl = (startTimeSeconds: number): string => {
    const s = Math.max(0, Math.floor(startTimeSeconds));
    return `https://www.youtube.com/watch?v=${videoId}&t=${s}s`;
  };

  return (
    <aside
      className="fixed inset-y-0 right-0 z-50 w-full sm:w-[420px] bg-white border-l border-gray-200 shadow-2xl flex flex-col animate-in slide-in-from-right duration-300"
      aria-label="Video transcript assistant chat"
    >
      {/* Drawer Header */}
      <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/80 backdrop-blur-md">
        <div className="flex items-center gap-2.5 min-w-0 pr-2">
          <div className="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center shrink-0 p-1">
            <img src={geminiChatbotSvg} alt="AI Chatbot" className="w-6 h-6 object-contain drop-shadow-2xs" />
          </div>
          <div className="min-w-0">
            <h3 className="text-sm font-bold text-gray-900 truncate">Transcript Chatbot</h3>
            <p className="text-[11px] text-gray-500 truncate">{videoTitle || 'Ask about this video'}</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 shrink-0">
          <button
            onClick={handleClearChat}
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors cursor-pointer"
            title="Clear chat messages"
          >
            <Trash2 className="w-4 h-4" />
          </button>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors cursor-pointer"
            title="Close chatbot"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Grounding Info Strip */}
      <div className="px-4 py-2 bg-indigo-50/70 border-b border-indigo-100/60 flex items-center justify-between text-[11px] text-indigo-900">
        <div className="flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
          <span>Grounded in video transcript &bull; With timestamp citations</span>
        </div>
        <span className="font-mono text-[10px] text-indigo-600 bg-white/80 px-2 py-0.5 rounded border border-indigo-100">
          RAG
        </span>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';
          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} animate-in fade-in duration-200`}
            >
              <div
                className={`max-w-[88%] rounded-2xl p-3.5 text-xs sm:text-sm leading-relaxed ${
                  isUser
                    ? 'bg-primary text-white shadow-xs rounded-br-xs'
                    : 'bg-gray-100/90 text-gray-800 border border-gray-200/60 rounded-bl-xs'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.text}</p>

                {/* Grounded Source Chunks with Timestamp Links */}
                {!isUser && msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-gray-200/80 space-y-1.5">
                    <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">
                      Transcript References:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.sources.map((src: RAGSourceChunk) => (
                        <a
                          key={src.chunk_id}
                          href={getYoutubeTimestampUrl(src.start_time)}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-white text-indigo-700 hover:bg-indigo-50 border border-indigo-200 text-[10px] font-semibold transition-colors"
                          title={src.text}
                        >
                          <Clock className="w-2.5 h-2.5 text-indigo-500" />
                          <span>{src.timestamp_str}</span>
                          <ExternalLink className="w-2.5 h-2.5 opacity-60" />
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <span className="text-[10px] text-gray-400 mt-1 px-1 font-mono">
                {msg.timestamp}
              </span>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-start gap-2 text-xs text-gray-500 animate-in fade-in">
            <div className="bg-gray-100 rounded-2xl rounded-bl-xs p-3.5 border border-gray-200/60 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-primary" />
              <span>Analyzing transcript and citing timestamps...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input Pinned Bottom */}
      <form onSubmit={handleSend} className="p-3 border-t border-gray-100 bg-white">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            placeholder="Ask about this video..."
            className="w-full h-11 pl-4 pr-11 bg-gray-50/90 hover:bg-gray-50 focus:bg-white border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 rounded-xl text-xs sm:text-sm text-gray-800 transition-all outline-none"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 p-2 rounded-lg bg-primary hover:bg-primaryHover text-white disabled:opacity-40 transition-all cursor-pointer shadow-xs active:scale-95"
            title="Send question"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
        <p className="text-[10px] text-gray-400 text-center mt-1.5">
          Answers are strictly verified against the video transcript.
        </p>
      </form>
    </aside>
  );
};
