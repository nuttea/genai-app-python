import { contentCreatorClient } from './client';

// API Base URL for SSE streaming (Next.js will replace at build time)
const getApiBaseUrl = (): string => {
  if (typeof window === 'undefined') return 'http://localhost:8002';
  return (process.env.NEXT_PUBLIC_CONTENT_CREATOR_API_URL as string) || 'http://localhost:8002';
};
const API_BASE_URL = getApiBaseUrl();

/**
 * Content Creator API types
 */

export interface FileUploadResponse {
  success: boolean;
  message: string;
  file_id?: string;
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
  platform?: string;
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
  platform?: string;
  estimated_duration?: number;
  script: string;
  scenes: Array<{
    time: string;
    description: string;
    dialogue?: string;
  }>;
  hashtags?: string[];
  generated_at: string;
}

export interface SocialMediaRequest {
  content: string;
  platforms: string[];
  topic?: string;
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
   * Helper: Create or get ADK session
   */
  _createSession: async (appName: string, userId: string, sessionId: string): Promise<any> => {
    const response = await fetch(
      `${API_BASE_URL}/apps/${appName}/users/${userId}/sessions`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId }),
      }
    );
    
    if (!response.ok) {
      // Session might already exist, try to get it
      const getResponse = await fetch(
        `${API_BASE_URL}/apps/${appName}/users/${userId}/sessions/${sessionId}`
      );
      if (getResponse.ok) {
        return await getResponse.json();
      }
      throw new Error(`Failed to create/get session: ${response.status}`);
    }
    
    return await response.json();
  },

  /**
   * Generate blog post using ADK /run_sse endpoint with streaming
   */
  generateBlogPost: async (
    request: BlogPostRequest,
    onStreamEvent?: (chunk: string) => void
  ): Promise<BlogPostResponse> => {
    const appName = 'content_creator_agent';
    const userId = 'user_nextjs';
    const sessionId = `blog_session_${Date.now()}`;

    // Step 1: Create session
    await contentCreatorApi._createSession(appName, userId, sessionId);

    // Step 2: Run agent with streaming
    const adkRequest = {
      appName,
      userId,
      sessionId,
      newMessage: {
        role: 'user',
        parts: [{
          text: `Create a blog post with the following details:
Title: ${request.title}
Description: ${request.description}
Style: ${request.style || 'professional'}
Target Audience: ${request.target_audience || 'developers'}
${request.file_ids ? `Files: ${request.file_ids.join(', ')}` : ''}`
        }]
      },
      streaming: true // Enable token-level streaming
    };

    return new Promise((resolve, reject) => {
      // Use fetch for SSE streaming
      fetch(`${API_BASE_URL}/run_sse`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(adkRequest),
      })
        .then(async (response) => {
          if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
          }

          const reader = response.body?.getReader();
          const decoder = new TextDecoder();
          let buffer = '';
          let fullContent = '';

          if (!reader) {
            throw new Error('No response body reader');
          }

          while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
              break;
            }

            // Decode the chunk
            buffer += decoder.decode(value, { stream: true });
            
            // Process complete SSE messages
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Keep incomplete line in buffer

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6)); // Remove 'data: ' prefix
                  
                  // Extract text parts from the event
                  if (data.content?.parts) {
                    for (const part of data.content.parts) {
                      if (part.text) {
                        fullContent += part.text;
                        
                        // Call streaming callback if provided
                        if (onStreamEvent) {
                          onStreamEvent(part.text);
                        }
                      }
                    }
                  }
                } catch (err) {
                  console.error('Error parsing SSE message:', err);
                }
              }
            }
          }

          // Return final response
          resolve({
            title: request.title,
            content: fullContent,
            summary: request.description,
            tags: [],
            estimated_read_time: Math.ceil(fullContent.split(' ').length / 200),
            generated_at: new Date().toISOString(),
          });
        })
        .catch((error) => {
          console.error('SSE streaming error:', error);
          reject(error);
        });
    });
  },

  /**
   * Generate video script using ADK /run_sse endpoint with streaming
   */
  generateVideoScript: async (
    request: VideoScriptRequest,
    onStreamEvent?: (chunk: string) => void
  ): Promise<VideoScriptResponse> => {
    const appName = 'content_creator_agent';
    const userId = 'user_nextjs';
    const sessionId = `video_session_${Date.now()}`;

    // Step 1: Create session
    await contentCreatorApi._createSession(appName, userId, sessionId);

    // Step 2: Run agent with streaming
    const adkRequest = {
      appName,
      userId,
      sessionId,
      newMessage: {
        role: 'user',
        parts: [{
          text: `Create a 60-second video script with the following details:
Title: ${request.title}
Description: ${request.description}
Duration: ${request.duration || 60} seconds
${request.file_ids ? `Files: ${request.file_ids.join(', ')}` : ''}`
        }]
      },
      streaming: true
    };

    return new Promise((resolve, reject) => {
      fetch(`${API_BASE_URL}/run_sse`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(adkRequest),
      })
        .then(async (response) => {
          if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
          }

          const reader = response.body?.getReader();
          const decoder = new TextDecoder();
          let buffer = '';
          let fullContent = '';

          if (!reader) {
            throw new Error('No response body reader');
          }

          while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
              break;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));
                  
                  if (data.content?.parts) {
                    for (const part of data.content.parts) {
                      if (part.text) {
                        fullContent += part.text;
                        if (onStreamEvent) {
                          onStreamEvent(part.text);
                        }
                      }
                    }
                  }
                } catch (err) {
                  console.error('Error parsing SSE message:', err);
                }
              }
            }
          }

          resolve({
            title: request.title,
            duration: request.duration || 60,
            script: fullContent,
            scenes: [],
            generated_at: new Date().toISOString(),
          });
        })
        .catch((error) => {
          console.error('SSE streaming error:', error);
          reject(error);
        });
    });
  },

  /**
   * Generate social media posts using ADK /run_sse endpoint with streaming
   */
  generateSocialMedia: async (
    request: SocialMediaRequest,
    onStreamEvent?: (chunk: string) => void
  ): Promise<SocialMediaResponse> => {
    const appName = 'content_creator_agent';
    const userId = 'user_nextjs';
    const sessionId = `social_session_${Date.now()}`;

    // Step 1: Create session
    await contentCreatorApi._createSession(appName, userId, sessionId);

    // Step 2: Run agent with streaming
    const adkRequest = {
      appName,
      userId,
      sessionId,
      newMessage: {
        role: 'user',
        parts: [{
          text: `Generate social media posts with the following details:
Content: ${request.content}
Platforms: ${request.platforms.join(', ')}
${request.file_ids ? `Files: ${request.file_ids.join(', ')}` : ''}`
        }]
      },
      streaming: true
    };

    return new Promise((resolve, reject) => {
      fetch(`${API_BASE_URL}/run_sse`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(adkRequest),
      })
        .then(async (response) => {
          if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
          }

          const reader = response.body?.getReader();
          const decoder = new TextDecoder();
          let buffer = '';
          let fullContent = '';

          if (!reader) {
            throw new Error('No response body reader');
          }

          while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
              break;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));
                  
                  if (data.content?.parts) {
                    for (const part of data.content.parts) {
                      if (part.text) {
                        fullContent += part.text;
                        if (onStreamEvent) {
                          onStreamEvent(part.text);
                        }
                      }
                    }
                  }
                } catch (err) {
                  console.error('Error parsing SSE message:', err);
                }
              }
            }
          }

          resolve({
            posts: request.platforms.map(platform => ({
              platform,
              content: fullContent,
              hashtags: [],
              character_count: fullContent.length,
            })),
            generated_at: new Date().toISOString(),
          });
        })
        .catch((error) => {
          console.error('SSE streaming error:', error);
          reject(error);
        });
    });
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string; service: string }> => {
    const response = await contentCreatorClient.get('/health');
    return response.data;
  },
};

