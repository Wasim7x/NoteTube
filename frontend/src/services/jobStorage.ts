import type {
  LoadVideoResponse,
  ProcessingMode,
  QuickSummaryResponse,
  DetailedNotesResponse,
  VideoSlidesResponse,
  GenerateNotesResponse,
} from '../types';

export interface StoredJobData {
  jobId: string;
  url: string;
  videoData: LoadVideoResponse;
  selectedMode: ProcessingMode;
  summaryData?: QuickSummaryResponse | null;
  detailedData?: DetailedNotesResponse | null;
  slidesData?: VideoSlidesResponse | null;
  completeNotesData?: GenerateNotesResponse | null;
  lastUpdated: number;
}

const STORAGE_PREFIX = 'notetube_job_';
const CURRENT_JOB_KEY = 'notetube_current_job_id';

export const jobStorage = {
  saveJob: (jobData: StoredJobData): void => {
    try {
      localStorage.setItem(`${STORAGE_PREFIX}${jobData.jobId}`, JSON.stringify(jobData));
      localStorage.setItem(CURRENT_JOB_KEY, jobData.jobId);
    } catch (e) {
      console.warn('LocalStorage save failed:', e);
    }
  },

  getJob: (jobId: string): StoredJobData | null => {
    try {
      const data = localStorage.getItem(`${STORAGE_PREFIX}${jobId}`);
      if (!data) return null;
      return JSON.parse(data) as StoredJobData;
    } catch (e) {
      console.warn('LocalStorage read failed:', e);
      return null;
    }
  },

  getCurrentJobId: (): string | null => {
    try {
      return localStorage.getItem(CURRENT_JOB_KEY);
    } catch {
      return null;
    }
  },

  setCurrentJobId: (jobId: string): void => {
    try {
      localStorage.setItem(CURRENT_JOB_KEY, jobId);
    } catch {}
  },

  updateResult: (
    jobId: string,
    mode: ProcessingMode,
    result: QuickSummaryResponse | DetailedNotesResponse | VideoSlidesResponse | GenerateNotesResponse
  ): void => {
    try {
      const existing = jobStorage.getJob(jobId);
      if (!existing) return;

      if (mode === 'summary') existing.summaryData = result as QuickSummaryResponse;
      else if (mode === 'detailed') existing.detailedData = result as DetailedNotesResponse;
      else if (mode === 'chapter_slides') existing.slidesData = result as VideoSlidesResponse;
      else if (mode === 'complete_notes') existing.completeNotesData = result as GenerateNotesResponse;

      existing.selectedMode = mode;
      existing.lastUpdated = Date.now();
      localStorage.setItem(`${STORAGE_PREFIX}${jobId}`, JSON.stringify(existing));
    } catch (e) {
      console.warn('LocalStorage update failed:', e);
    }
  },
};
