export interface ChapterItem {
    chapter_id?: string;
    title: string;
    start_time: number;
    end_time?: number;
    duration?: number;
    timestamp_str?: string;
    duration_str?: string;
    is_ai_detected?: boolean;
    content?: string;
}

export interface ChapterSlideItem {
    chapter_id: string;
    chapter_index: number;
    title: string;
    start_time: number;
    end_time: number;
    duration: number;
    timestamp_str: string;
    extraction_timestamp: number;
    extraction_timestamp_str: string;
    image_url?: string;
    status: 'completed' | 'pending' | 'failed';
    error?: string;
    slide_index?: number;
}

export interface VideoSlidesResponse {
    video_id: string;
    video_title: string;
    status: 'completed' | 'processing' | 'no_chapters' | 'failed' | 'not_started';
    has_chapters: boolean;
    message?: string;
    total_chapters: number;
    extracted_slides: number;
    slides: ChapterSlideItem[];
    ppt_download_url?: string;
    error?: string;
}

export interface ExtractSlidesRequest {
    video_id: string;
    youtube_url?: string;
    chapters?: ChapterItem[];
    force?: boolean;
}

export interface VideoMetadata {
    id: string;
    title: string;
    thumbnail: string;
    description?: string;
    duration?: number;
    chapters?: ChapterItem[];
    channel?: string;
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
    transcript_available?: boolean;
    transcript_language?: string;
    transcript_language_code?: string;
    transcript_generated?: boolean;
    video?: VideoMetadata;
    notes?: NotesData;
    overview_content?: string;
    chapters?: ChapterItem[];
    revision_content?: string;
    error?: string;
}

export interface GenerateNotesRequest {
    youtube_url: string;
    provider: string;
    model: string;
    api_key?: string;
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
    requires_api_key?: boolean;
    models: ModelOption[];
}

export interface ProvidersResponse {
    providers: ProviderInfo[];
}

export interface StreamProgressState {
    statusMessage: string;
    currentChapter?: number;
    totalChapters?: number;
    currentChapterTitle?: string;
    step?: string;
}

// -------------------------------------------------------------
// Two-Page Workflow & Mode Additions
// -------------------------------------------------------------

export interface ValidateProviderRequest {
    provider: string;
    model?: string;
    api_key?: string;
    base_url?: string;
}

export interface ValidateProviderResponse {
    success: boolean;
    provider: string;
    model: string;
    message: string;
    error?: string;
    details?: any;
}

export interface LoadVideoRequest {
    youtube_url: string;
}

export interface LoadVideoResponse {
    success: boolean;
    video_id: string;
    video?: VideoMetadata;
    transcript_available: boolean;
    transcript_language?: string;
    transcript_language_code?: string;
    transcript_generated?: boolean;
    transcript_preview?: string;
    transcript_char_count: number;
    has_chapters: boolean;
    total_chapters: number;
    chapters: ChapterItem[];
    error?: string;
}

export type ProcessingMode =
    | 'summary'
    | 'detailed'
    | 'chapter_slides'
    | 'unique_slides'
    | 'complete_notes';

export interface QuickSummaryRequest {
    video_id: string;
    youtube_url?: string;
    provider: string;
    model?: string;
    api_key?: string;
}

export interface QuickSummaryResponse {
    success: boolean;
    video_id: string;
    title: string;
    summary: string;
    key_takeaways: string[];
    core_concepts: string[];
    markdown_content: string;
    provider: string;
    model: string;
    error?: string;
}

export interface DetailedNotesRequest {
    video_id: string;
    youtube_url?: string;
    provider: string;
    model?: string;
    api_key?: string;
}

export interface DetailedNotesResponse {
    success: boolean;
    video_id: string;
    title: string;
    overview: string;
    markdown_content: string;
    chapters: ChapterItem[];
    revision_summary?: string;
    external_research_used: boolean;
    provider: string;
    model: string;
    error?: string;
}

export interface RAGSourceChunk {
    chunk_id: string;
    timestamp_str: string;
    start_time: float_number;
    end_time: float_number;
    chapter_title?: string;
    text: string;
    score: number;
}

type float_number = number;

export interface RAGQueryRequest {
    video_id: string;
    query: string;
    provider: string;
    model?: string;
    api_key?: string;
}

export interface RAGQueryResponse {
    success: boolean;
    video_id: string;
    query: string;
    answer: string;
    sources: RAGSourceChunk[];
    grounded: boolean;
    error?: string;
}

export interface RAGStatusResponse {
    indexed: boolean;
    video_id: string;
    chunk_count: number;
    embedding_model?: string;
}

export interface ChatMessage {
    id: string;
    sender: 'user' | 'assistant';
    text: string;
    timestamp: string;
    sources?: RAGSourceChunk[];
    grounded?: boolean;
}

export interface HealthResponse {
    status: string;
    service?: string;
    message?: string;
}

export type BackendHealthStatus = 'online' | 'offline' | 'error' | 'timeout' | 'checking';

export interface BackendHealthState {
    status: BackendHealthStatus;
    message: string;
    details?: string;
    statusCode?: number;
    url: string;
    lastChecked?: number;
}

