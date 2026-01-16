// API Response Types

export interface UploadResponse {
  document_id: string;
  is_guest: boolean;
  credits_remaining?: number;
  guest_remaining_uploads?: number;
  detail?: string;  // For error responses
}

export interface DocumentInfo {
  filename: string;
  chunks: number;
  text_length: number;
  is_demo: boolean;
  can_view: boolean;
}

export interface QueryResponse {
  response: string;
  credits_remaining?: number;
}

export interface UserProfile {
  email: string;
  credits: number;
  firebase_uid: string;
}

export interface ErrorResponse {
  detail: string;
}
