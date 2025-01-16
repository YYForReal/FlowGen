export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface ChatCompletionResponse {
  message: string;
  diagram?: {
    xml: string;
    png: string;
  };
}

export interface DiagramUpdateResponse {
  xml: string;
  png: string;
} 