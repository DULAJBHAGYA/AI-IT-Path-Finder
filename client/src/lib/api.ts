// lib/api.ts (or utils/api.ts)

import axios from 'axios';
import { config } from './config';

// Create axios instance with default config
export const api = axios.create({
  baseURL: config.BACKEND_URL,
  timeout: config.REQUEST_TIMEOUT,
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url, config.data);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    // Axios errors have a response property for server errors
    if (error.response) {
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // The request was made but no response was received (e.g., network error)
      console.error('API Error: No response received', error.message);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('API Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// --- API Functions - Updated to use Axios ---

interface CvApiResponse {
  json?: any; // Structured JSON data
  markdown?: string; // Markdown string (if endpoint provides)
  error?: string;
  success: boolean;
}

export async function generateCvJson(cvText: string): Promise<CvApiResponse> {
  const formData = new FormData();
  formData.append('cv_text', cvText);

  try {
    const response = await api.post<CvApiResponse>(config.ENDPOINTS.GENERATE_CV_JSON, formData);
    return response.data;
  } catch (error: any) {
    console.error('Error in generateCvJson:', error.response?.data || error.message);
    return { success: false, error: error.response?.data?.error || error.message || 'An unknown error occurred.' };
  }
}

export async function generateCvMarkdown(cvText: string): Promise<{ markdown: string; error?: string }> {
  const formData = new FormData();
  formData.append('cv_text', cvText);

  try {
    const response = await api.post<{ markdown: string }>('/generate-cv-markdown', formData);
    return { markdown: response.data.markdown };
  } catch (error: any) {
    console.error('Error in generateCvMarkdown:', error.response?.data || error.message);
    return { markdown: "", error: error.response?.data?.error || error.message || 'An unknown error occurred.' };
  }
}

export async function downloadCvPdf(cvText: string): Promise<{ blob: Blob | null; filename: string | null; error?: string }> {
  const formData = new FormData();
  formData.append('cv_text', cvText);

  try {
    const response = await api.post(config.ENDPOINTS.DOWNLOAD_CV_PDF, formData, {
      responseType: 'blob', // Important: tell axios to expect a binary response (Blob)
    });

    const contentDisposition = response.headers['content-disposition']; // Axios normalizes header names to lowercase
    let filename: string | null = 'cv.pdf'; // Default filename

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename\*?=['"]?(?:UTF-\d['"]*)?([^;\n]+)['"]?/i);
      if (filenameMatch && filenameMatch[1]) {
        filename = decodeURIComponent(filenameMatch[1].replace(/%../g, (match: string) => String.fromCharCode(parseInt(match.slice(1), 16))));
      }
    }

    return { blob: response.data, filename };

  } catch (error: any) {
    console.error('Error in downloadCvPdf:', error.response?.data || error.message);
    let errorMessage = 'An unknown error occurred during PDF download.';
    if (error.response && error.response.data instanceof Blob) {
      // Try to read error message from Blob if backend sent JSON error in Blob format
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const errorJson = JSON.parse(reader.result as string);
          errorMessage = errorJson.error || errorMessage;
        } catch (parseError) {
          errorMessage = `Non-JSON error response from server: ${error.message}`;
        }
      };
      reader.readAsText(error.response.data);
    } else if (error.response && error.response.data && typeof error.response.data === 'object') {
        errorMessage = error.response.data.error || errorMessage;
    } else if (error.message) {
        errorMessage = error.message;
    }

    return { blob: null, filename: null, error: errorMessage };
  }
}