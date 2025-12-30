import { contentCreatorClient } from './client';

/**
 * Content Creator API types
 */

export interface FileUploadResponse {
  success: boolean;
  message: string;
  file: {
    filename: string;
    content_type: string;
    size_bytes: number;
    gcs_uri: string | null;
    file_type: string;
    extracted_text?: string | null;
  };
  files?: Array<{
    filename: string;
    content_type: string;
    size_bytes: number;
    gcs_uri: string | null;
    file_type: string;
    extracted_text?: string | null;
  }> | null;
}

export interface BlogPostRequest {
  title: string;
  description: string;
  style?: string;
  target_audience?: string;
  file_ids?: string[];
  generation_config?: {
    temperature?: number;
    max_tokens?: number;
    model?: string;
  };
}

export interface BlogPostResponse {
  title: string;
  content: string;
  summary: string;
  tags: string[];
  estimated_read_time: number;
  generated_at: string;
}

export interface VideoScriptRequest {
  title: string;
  description: string;
  duration?: number;
  file_ids?: string[];
  generation_config?: {
    temperature?: number;
    max_tokens?: number;
    model?: string;
  };
}

export interface VideoScriptResponse {
  title: string;
  duration: number;
  script: string;
  scenes: Array<{
    time: string;
    description: string;
    dialogue?: string;
  }>;
  generated_at: string;
}

export interface SocialMediaRequest {
  content: string;
  platforms: string[];
  file_ids?: string[];
  generation_config?: {
    temperature?: number;
    max_tokens?: number;
    model?: string;
  };
}

export interface SocialMediaResponse {
  posts: Array<{
    platform: string;
    content: string;
    hashtags: string[];
    character_count: number;
  }>;
  generated_at: string;
}

/**
 * Content Creator API Client
 */
export const contentCreatorApi = {
  /**
   * Upload a single file
   * - Text/Markdown files: Returns extracted text
   * - Images/Videos: Returns artifact reference
   */
  uploadFile: async (file: File): Promise<FileUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await contentCreatorClient.post<FileUploadResponse>(
      '/api/v1/upload/single',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  },

  /**
   * Upload multiple files
   */
  uploadFiles: async (files: File[]): Promise<FileUploadResponse[]> => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await contentCreatorClient.post<FileUploadResponse[]>(
      '/api/v1/upload/batch',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  },

  /**
   * Generate blog post
   */
  generateBlogPost: async (request: BlogPostRequest): Promise<BlogPostResponse> => {
    const response = await contentCreatorClient.post<BlogPostResponse>(
      '/api/v1/generate/blog-post',
      request
    );

    return response.data;
  },

  /**
   * Generate video script
   */
  generateVideoScript: async (request: VideoScriptRequest): Promise<VideoScriptResponse> => {
    const response = await contentCreatorClient.post<VideoScriptResponse>(
      '/api/v1/generate/video-script',
      request
    );

    return response.data;
  },

  /**
   * Generate social media posts
   */
  generateSocialMedia: async (request: SocialMediaRequest): Promise<SocialMediaResponse> => {
    const response = await contentCreatorClient.post<SocialMediaResponse>(
      '/api/v1/generate/social-media',
      request
    );

    return response.data;
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string; service: string }> => {
    const response = await contentCreatorClient.get('/health');
    return response.data;
  },
};

