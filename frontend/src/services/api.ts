import axios from 'axios';
import type {
    GenerateNotesRequest,
    GenerateNotesResponse,
    ProvidersResponse,
    ExtractSlidesRequest,
    VideoSlidesResponse,
    ValidateProviderRequest,
    ValidateProviderResponse,
    LoadVideoResponse,
    QuickSummaryRequest,
    QuickSummaryResponse,
    DetailedNotesRequest,
    DetailedNotesResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGStatusResponse,
    HealthResponse,
    BackendHealthState
} from '../types';

export const API_URL: string = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api').replace(/\/+$/, '');
export const BACKEND_BASE_URL: string = API_URL.replace(/\/api\/?$/, '');

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
            return {
                providers: [
                    {
                        id: 'ollama',
                        name: 'Ollama (Local)',
                        description: "Run open-source LLMs locally on your own machine without cloud API keys.",
                        default_model: 'qwen3:1.7b',
                        key_placeholder: 'Not required (Local)',
                        help_url: 'https://ollama.com',
                        requires_api_key: false,
                        models: [
                            { id: 'qwen3:1.7b', name: 'Qwen 3 (1.7B)', description: 'Fast & lightweight local model', is_recommended: true },
                            { id: 'qwen3.5:latest', name: 'Qwen 3.5 (9.7B)', description: 'High capability local model' },
                            { id: 'llama3.2:3b', name: 'Llama 3.2 (3B)', description: 'Lightweight Meta local model' },
                        ]
                    },
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
    },

    generateNotesStream: async (
        data: GenerateNotesRequest,
        onEvent: (event: any) => void
    ): Promise<GenerateNotesResponse> => {
        const streamUrl = `${API_URL}/notes/generate-stream`;
        const response = await fetch(streamUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            let errorMsg = 'Failed to generate notes.';
            try {
                const errJson = await response.json();
                errorMsg = errJson.detail || errJson.error || errorMsg;
            } catch {
                errorMsg = `Server error (status ${response.status})`;
            }
            throw new Error(errorMsg);
        }

        if (!response.body) {
            throw new Error('Response body stream is not available in browser.');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        let finalResponse: GenerateNotesResponse | null = null;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const parts = buffer.split('\n\n');
            buffer = parts.pop() || '';

            for (const part of parts) {
                const lines = part.split('\n');
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const jsonStr = line.slice(6).trim();
                        if (jsonStr) {
                            try {
                                const parsed = JSON.parse(jsonStr);
                                onEvent(parsed);
                                if (parsed.type === 'complete' && parsed.response) {
                                    finalResponse = parsed.response;
                                } else if (parsed.type === 'error') {
                                    throw new Error(parsed.error || 'Generation failed.');
                                }
                            } catch (e: any) {
                                if (e.message && !e.message.includes('JSON')) {
                                    throw e;
                                }
                            }
                        }
                    }
                }
            }
        }

        if (finalResponse) {
            return finalResponse;
        }

        throw new Error('Stream concluded without returning complete notes.');
    },

    extractSlides: async (data: ExtractSlidesRequest): Promise<VideoSlidesResponse> => {
        try {
            const response = await apiClient.post<VideoSlidesResponse>('/slides/extract', data);
            return response.data;
        } catch (error: any) {
            if (error.response && error.response.data) {
                throw new Error(error.response.data.detail || error.response.data.message || 'Failed to extract chapter slides.');
            }
            throw new Error('Could not connect to the backend server to extract slides.');
        }
    },

    getSlides: async (videoId: string): Promise<VideoSlidesResponse> => {
        try {
            const response = await apiClient.get<VideoSlidesResponse>(`/slides/${encodeURIComponent(videoId)}`);
            return response.data;
        } catch (error: any) {
            if (error.response && error.response.data) {
                throw new Error(error.response.data.detail || 'Failed to retrieve chapter slides.');
            }
            throw new Error('Could not connect to the backend server to retrieve slides.');
        }
    },

    getSlideImageUrl: (videoId: string, chapterId: string): string => {
        return `${API_URL}/slides/${encodeURIComponent(videoId)}/images/${encodeURIComponent(chapterId)}`;
    },

    getDownloadPptUrl: (videoId: string): string => {
        return `${API_URL}/slides/${encodeURIComponent(videoId)}/download-ppt`;
    },

    validateProvider: async (data: ValidateProviderRequest): Promise<ValidateProviderResponse> => {
        try {
            const response = await apiClient.post<ValidateProviderResponse>('/providers/validate', data);
            return response.data;
        } catch (error: any) {
            if (error.response && error.response.data) {
                return {
                    success: false,
                    provider: data.provider,
                    model: data.model || '',
                    message: error.response.data.detail || 'Connection test failed.',
                    error: error.response.data.detail || 'Connection test failed.'
                };
            }
            return {
                success: false,
                provider: data.provider,
                model: data.model || '',
                message: 'Could not connect to the backend server.',
                error: 'Could not connect to the backend server.'
            };
        }
    },

    loadVideo: async (youtubeUrl: string): Promise<LoadVideoResponse> => {
        try {
            const response = await apiClient.post<LoadVideoResponse>('/video/load', { youtube_url: youtubeUrl });
            return response.data;
        } catch (error: any) {
            if (error.response && error.response.data) {
                throw new Error(error.response.data.detail || 'Failed to load video information.');
            }
            throw new Error('Could not connect to the backend server to load video.');
        }
    },

    getVideoJob: async (videoId: string): Promise<LoadVideoResponse> => {
        try {
            const response = await apiClient.get<LoadVideoResponse>(`/video/${encodeURIComponent(videoId)}`);
            return response.data;
        } catch (error: any) {
            if (error.response && error.response.data) {
                throw new Error(error.response.data.detail || 'Failed to retrieve video details.');
            }
            throw new Error('Could not connect to the backend server to retrieve video details.');
        }
    },

    generateQuickSummary: async (data: QuickSummaryRequest): Promise<QuickSummaryResponse> => {
        try {
            const response = await apiClient.post<QuickSummaryResponse>('/modes/quick-summary', data);
            return response.data;
        } catch (error: any) {
            if (error.response && error.response.data) {
                throw new Error(error.response.data.detail || error.response.data.error || 'Failed to generate quick summary.');
            }
            throw new Error('Could not connect to backend server for quick summary.');
        }
    },

    generateDetailedNotes: async (data: DetailedNotesRequest): Promise<DetailedNotesResponse> => {
        try {
            const response = await apiClient.post<DetailedNotesResponse>('/modes/detailed-notes', data);
            return response.data;
        } catch (error: any) {
            if (error.response && error.response.data) {
                throw new Error(error.response.data.detail || error.response.data.error || 'Failed to generate detailed notes.');
            }
            throw new Error('Could not connect to backend server for detailed notes.');
        }
    },

    askChatbot: async (data: RAGQueryRequest): Promise<RAGQueryResponse> => {
        try {
            const response = await apiClient.post<RAGQueryResponse>('/rag/ask', data);
            return response.data;
        } catch (error: any) {
            if (error.response && error.response.data) {
                throw new Error(error.response.data.detail || error.response.data.error || 'Chatbot query failed.');
            }
            throw new Error('Could not connect to backend server for chatbot.');
        }
    },

    getRagStatus: async (videoId: string): Promise<RAGStatusResponse> => {
        try {
            const response = await apiClient.get<RAGStatusResponse>(`/rag/status/${encodeURIComponent(videoId)}`);
            return response.data;
        } catch (error: any) {
            return {
                indexed: false,
                video_id: videoId,
                chunk_count: 0
            };
        }
    },

    checkHealth: async (): Promise<BackendHealthState> => {
        try {
            // First check apiClient which resolves to ${API_URL}/health -> http://127.0.0.1:8000/api/health
            const response = await apiClient.get<HealthResponse>('/health', { timeout: 4000 });
            if (response.status === 200 && (response.data?.status === 'healthy' || response.data?.status === 'ok' || response.data?.service === 'NoteTube')) {
                return {
                    status: 'online',
                    message: 'Backend is connected and healthy',
                    url: BACKEND_BASE_URL,
                    lastChecked: Date.now()
                };
            }
            return {
                status: 'error',
                message: 'Backend Error',
                details: `Unexpected response status: ${response.status}`,
                statusCode: response.status,
                url: BACKEND_BASE_URL,
                lastChecked: Date.now()
            };
        } catch (error: any) {
            // If primary check returned 404 (nonexistent endpoint under /api), fallback to root /health
            if (error.response && error.response.status === 404) {
                try {
                    const directResponse = await axios.get<HealthResponse>(`${BACKEND_BASE_URL}/health`, { timeout: 4000 });
                    if (directResponse.status === 200) {
                        return {
                            status: 'online',
                            message: 'Backend is connected and healthy',
                            url: BACKEND_BASE_URL,
                            lastChecked: Date.now()
                        };
                    }
                } catch (fallbackError: any) {
                    if (fallbackError.response) {
                        return {
                            status: 'error',
                            message: 'Backend Error',
                            details: `Server returned HTTP ${fallbackError.response.status}: ${fallbackError.response.data?.detail || fallbackError.response.statusText || 'Error response'}`,
                            statusCode: fallbackError.response.status,
                            url: BACKEND_BASE_URL,
                            lastChecked: Date.now()
                        };
                    }
                    if (fallbackError.code === 'ECONNABORTED' || fallbackError.message?.toLowerCase().includes('timeout')) {
                        return {
                            status: 'timeout',
                            message: 'Connection Timeout',
                            details: 'Health check request timed out after 4 seconds.',
                            url: BACKEND_BASE_URL,
                            lastChecked: Date.now()
                        };
                    }
                    return {
                        status: 'offline',
                        message: 'Backend Offline',
                        details: `Unable to connect to the NoteTube FastAPI server at ${BACKEND_BASE_URL}.`,
                        url: BACKEND_BASE_URL,
                        lastChecked: Date.now()
                    };
                }
            }

            // Server responded with an HTTP error status (4xx / 5xx)
            if (error.response) {
                return {
                    status: 'error',
                    message: 'Backend Error',
                    details: `Server returned HTTP ${error.response.status}: ${error.response.data?.detail || error.response.statusText || 'Error response'}`,
                    statusCode: error.response.status,
                    url: BACKEND_BASE_URL,
                    lastChecked: Date.now()
                };
            }

            // Health request timed out
            if (error.code === 'ECONNABORTED' || error.message?.toLowerCase().includes('timeout')) {
                return {
                    status: 'timeout',
                    message: 'Connection Timeout',
                    details: 'Health check request timed out after 4 seconds.',
                    url: BACKEND_BASE_URL,
                    lastChecked: Date.now()
                };
            }

            // Connection refused or server unreachable
            return {
                status: 'offline',
                message: 'Backend Offline',
                details: `Unable to connect to the NoteTube FastAPI server at ${BACKEND_BASE_URL}.`,
                url: BACKEND_BASE_URL,
                lastChecked: Date.now()
            };
        }
    },

    getBaseUrl: (): string => BACKEND_BASE_URL,
    getApiUrl: (): string => API_URL,
};

