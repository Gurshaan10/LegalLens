// API Configuration
// Uses environment variable for base URL, falls back to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiEndpoints = {
  // User endpoints
  me: `${API_BASE_URL}/me`,

  // Document endpoints
  upload: `${API_BASE_URL}/upload/`,
  query: (docId: string) => `${API_BASE_URL}/query/${docId}`,
  documentInfo: (docId: string) => `${API_BASE_URL}/document/${docId}`,
  documentView: (docId: string) => `${API_BASE_URL}/document/${docId}/view`,

  // Health check
  health: `${API_BASE_URL}/health`,
};

export default apiEndpoints;
