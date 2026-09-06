import axios from 'axios';
import type { GenerateNotesRequest, GenerateNotesResponse, ProvidersResponse } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const api = {
    getProviders: async (): Promise<ProvidersResponse> => {
        try {
            const response = await apiClient.get<ProvidersResponse>('/providers');
            return response.data;
        } catch (error: any) {
            console.error('Failed to fetch providers from backend, using default fallback list.', error);
            // Fallback default list if backend is not yet reached
            return {
                providers: [
                    {
                        id: 'gemini',
                        name: 'Google Gemini',
                        description: "Google's multimodal Gemini models with high speed and large context windows.",
                        default_model: 'gemini-2.5-flash',
                        key_placeholder: 'AIzaSy...',
                        help_url: 'https://aistudio.google.com/app/apikey',
                        models: [
                            { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash', description: 'Fastest & highly capable for note generation', is_recommended: true },
                            { id: 'gemini-2.5-pro', name: 'Gemini 2.5 Pro', description: 'Highest quality reasoning' },
                            { id: 'gemini-2.0-flash', name: 'Gemini 2.0 Flash', description: 'Balanced speed and structured output' },
                            { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', description: 'Lightweight model' },
                        ]
                    },
                    {
                        id: 'openai',
                        name: 'OpenAI',
                        description: 'Flagship OpenAI GPT and reasoning models.',
                        default_model: 'gpt-4o-mini',
                        key_placeholder: 'sk-...',
                        help_url: 'https://platform.openai.com/api-keys',
                        models: [
                            { id: 'gpt-4o-mini', name: 'GPT-4o Mini', description: 'Fast, cost-effective, high quality notes', is_recommended: true },
                            { id: 'gpt-4o', name: 'GPT-4o', description: 'Flagship intelligent multimodal model' },
                            { id: 'gpt-4.5-preview', name: 'GPT-4.5 Preview', description: 'Advanced reasoning' },
                            { id: 'o3-mini', name: 'o3 Mini', description: 'High-speed reasoning model' },
                        ]
                    },
                    {
                        id: 'anthropic',
                        name: 'Anthropic Claude',
                        description: "Anthropic's Claude models with nuanced synthesis.",
                        default_model: 'claude-3-7-sonnet-latest',
                        key_placeholder: 'sk-ant-...',
                        help_url: 'https://console.anthropic.com/settings/keys',
                        models: [
                            { id: 'claude-3-7-sonnet-latest', name: 'Claude 3.7 Sonnet', description: 'Hybrid reasoning & top-tier note synthesis', is_recommended: true },
                            { id: 'claude-3-5-sonnet-latest', name: 'Claude 3.5 Sonnet', description: 'Exceptional writing quality and structure' },
                            { id: 'claude-3-5-haiku-latest', name: 'Claude 3.5 Haiku', description: 'Fastest Claude model' },
                        ]
                    },
                    {
                        id: 'groq',
                        name: 'Groq',
                        description: 'Ultra-fast LPU inference hosting leading open-source models.',
                        default_model: 'openai/gpt-oss-20b',
                        key_placeholder: 'gsk_...',
                        help_url: 'https://console.groq.com/keys',
                        models: [
                            { id: 'openai/gpt-oss-20b', name: 'GPT-OSS 20B', description: 'Fast & highly capable on Groq LPUs', is_recommended: true },
                            { id: 'openai/gpt-oss-120b', name: 'GPT-OSS 120B', description: 'Large 120B parameter model on Groq' },
                            { id: 'qwen/qwen3.6-27b', name: 'Qwen 3.6 27B', description: 'Advanced multimodal/reasoning capabilities' },
                            { id: 'llama-3.3-70b-versatile', name: 'Llama 3.3 70B Versatile', description: 'State-of-the-art open-source intelligence' },
                            { id: 'llama-3.1-8b-instant', name: 'Llama 3.1 8B Instant', description: 'Blazing fast generation' },
                        ]
                    },
                    {
                        id: 'openrouter',
                        name: 'OpenRouter',
                        description: 'Universal gateway to hundreds of open-source and proprietary models.',
                        default_model: 'deepseek/deepseek-chat',
                        key_placeholder: 'sk-or-...',
                        help_url: 'https://openrouter.ai/keys',
                        models: [
                            { id: 'deepseek/deepseek-chat', name: 'DeepSeek V3 (Chat)', description: 'Extremely cost-effective, high quality', is_recommended: true },
                            { id: 'deepseek/deepseek-r1', name: 'DeepSeek R1', description: 'Deep reasoning' },
                            { id: 'meta-llama/llama-3.3-70b-instruct', name: 'Meta Llama 3.3 70B', description: 'Open-weights flagship' },
                            { id: 'anthropic/claude-3.5-sonnet', name: 'Claude 3.5 Sonnet', description: 'Via OpenRouter' },
                        ]
                    }
                ]
            };
        }
    },

    generateNotes: async (data: GenerateNotesRequest): Promise<GenerateNotesResponse> => {
        try {
            const response = await apiClient.post<GenerateNotesResponse>('/notes/generate', data);
            return response.data;
        } catch (error: any) {
            if (error.response && error.response.data) {
                 throw new Error(error.response.data.detail || error.response.data.error || 'An error occurred while generating notes.');
            }
            throw new Error('Could not connect to the backend server. Please verify the backend is running.');
        }
    }
};
