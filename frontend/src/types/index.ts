export interface VideoMetadata {
    id: string;
    title: string;
    thumbnail: string;
}

export interface NotesData {
    title: string;
    content: string;
}

export interface GenerateNotesResponse {
    success: boolean;
    provider?: string;
    model?: string;
    fallback_used?: boolean;
    video?: VideoMetadata;
    notes?: NotesData;
    error?: string;
}

export interface GenerateNotesRequest {
    youtube_url: string;
    provider: string;
    model: string;
    api_key: string;
}

export interface ModelOption {
    id: string;
    name: string;
    description?: string;
    is_recommended?: boolean;
}

export interface ProviderInfo {
    id: string;
    name: string;
    description: string;
    default_model: string;
    key_placeholder: string;
    help_url: string;
    models: ModelOption[];
}

export interface ProvidersResponse {
    providers: ProviderInfo[];
}
