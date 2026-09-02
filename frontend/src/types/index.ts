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
    video?: VideoMetadata;
    notes?: NotesData;
    error?: string;
}

export interface GenerateNotesRequest {
    youtube_url: string;
}
