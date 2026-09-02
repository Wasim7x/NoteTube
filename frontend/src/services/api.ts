import axios from 'axios';
import type { GenerateNotesRequest, GenerateNotesResponse } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const api = {
    generateNotes: async (data: GenerateNotesRequest): Promise<GenerateNotesResponse> => {
        try {
            const response = await apiClient.post<GenerateNotesResponse>('/notes/generate', data);
            return response.data;
        } catch (error: any) {
            if (error.response && error.response.data) {
                 throw new Error(error.response.data.detail || 'An error occurred');
            }
            throw new Error('Network error or server is down. Please try again.');
        }
    }
};
