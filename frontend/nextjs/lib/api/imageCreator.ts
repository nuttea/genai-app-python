import { API_CONFIG } from '@/lib/constants/config';
import {
  MessageContent,
  textPart,
  base64ToInlineData,
  inlineDataToDataUrl,
  InlineData,
  Part,
} from '@/lib/utils/imageUtils';

/**
 * Image Creator API Client
 * 
 * Handles communication with the image_creator_agent for:
 * - Image generation from text
 * - Multi-turn image editing
 * - Image analysis
 * 
 * CRITICAL: Uses proper inline_data format (NOT base64 as text)
 */

const API_BASE_URL = API_CONFIG.contentCreator.baseUrl;

export interface ImageGenerationRequest {
  prompt: string;
  imageType?: 'diagram' | 'comic' | 'slide' | 'infographic' | 'illustration' | 'photo';
  aspectRatio?: '1:1' | '16:9' | '9:16' | '3:2' | '2:3' | '3:4' | '4:3' | '4:5' | '5:4' | '21:9';
  referenceImageBase64?: string;  // Optional reference image for style
}

export interface ImageEditRequest {
  editPrompt: string;
  originalImageBase64: string;  // Image to edit
  aspectRatio?: string;
}

export interface ImageAnalysisRequest {
  imageBase64: string;
  analysisPrompt?: string;
}

export interface ImageCreatorResponse {
  text: string;  // Agent's text response
  images?: InlineData[];  // Generated/edited images
  status?: 'success' | 'error';
  error?: string;
}

export const imageCreatorApi = {
  /**
   * Create or get session
   */
  _createSession: async (userId: string, sessionId: string): Promise<any> => {
    const appName = 'image_creator';
    const response = await fetch(
      `${API_BASE_URL}/apps/${appName}/users/${userId}/sessions`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId }),
      }
    );

    if (!response.ok) {
      // Session might already exist
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
   * Generate image from text prompt
   * 
   * Example:
   * ```ts
   * const response = await imageCreatorApi.generateImage({
   *   prompt: "Create a diagram showing how APM works",
   *   imageType: "diagram",
   *   aspectRatio: "16:9"
   * });
   * ```
   */
  generateImage: async (
    request: ImageGenerationRequest,
    userId: string = 'user_nextjs',
    sessionId?: string,
    onStreamEvent?: (text: string) => void
  ): Promise<ImageCreatorResponse> => {
    const sid = sessionId || `img_${Date.now()}`;

    // Create session
    await imageCreatorApi._createSession(userId, sid);

    // Build message parts (text only for generation)
    const parts: Part[] = [];

    // Add reference image if provided
    if (request.referenceImageBase64) {
      parts.push(base64ToInlineData(request.referenceImageBase64));
    }

    // Build prompt
    let fullPrompt = `Generate ${request.imageType || 'illustration'}: ${request.prompt}`;
    if (request.aspectRatio) {
      fullPrompt += `\nAspect ratio: ${request.aspectRatio}`;
    }

    parts.push(textPart(fullPrompt));

    // Call agent with streaming
    return await imageCreatorApi._callAgentSSE(
      'image_creator',
      userId,
      sid,
      { role: 'user', parts },
      onStreamEvent
    );
  },

  /**
   * Edit an existing image
   * 
   * CRITICAL: Sends image as inline_data (NOT as text)
   * 
   * Example:
   * ```ts
   * const response = await imageCreatorApi.editImage({
   *   editPrompt: "Make it more colorful",
   *   originalImageBase64: "iVBORw0KGgoAAAANS...",
   *   aspectRatio: "1:1"
   * });
   * ```
   */
  editImage: async (
    request: ImageEditRequest,
    userId: string = 'user_nextjs',
    sessionId?: string,
    onStreamEvent?: (text: string) => void
  ): Promise<ImageCreatorResponse> => {
    const sid = sessionId || `img_${Date.now()}`;

    // Create session
    await imageCreatorApi._createSession(userId, sid);

    // Build message parts: [inline_data, text]
    // CRITICAL: Image MUST be sent as inline_data, not as text
    const parts: Part[] = [
      base64ToInlineData(request.originalImageBase64),
      textPart(request.editPrompt),
    ];

    // Call agent
    return await imageCreatorApi._callAgentSSE(
      'image_creator',
      userId,
      sid,
      { role: 'user', parts },
      onStreamEvent
    );
  },

  /**
   * Analyze an image
   * 
   * Example:
   * ```ts
   * const response = await imageCreatorApi.analyzeImage({
   *   imageBase64: "iVBORw0KGgoAAAANS...",
   *   analysisPrompt: "What objects are in this image?"
   * });
   * ```
   */
  analyzeImage: async (
    request: ImageAnalysisRequest,
    userId: string = 'user_nextjs',
    sessionId?: string,
    onStreamEvent?: (text: string) => void
  ): Promise<ImageCreatorResponse> => {
    const sid = sessionId || `img_${Date.now()}`;

    // Create session
    await imageCreatorApi._createSession(userId, sid);

    // Build message parts: [inline_data, text]
    const parts: Part[] = [
      base64ToInlineData(request.imageBase64),
      textPart(request.analysisPrompt || 'Describe this image in detail'),
    ];

    // Call agent
    return await imageCreatorApi._callAgentSSE(
      'image_creator',
      userId,
      sid,
      { role: 'user', parts },
      onStreamEvent
    );
  },

  /**
   * Call agent with SSE streaming
   * 
   * INTERNAL: Handles proper inline_data format
   */
  _callAgentSSE: async (
    appName: string,
    userId: string,
    sessionId: string,
    newMessage: MessageContent,
    onStreamEvent?: (text: string) => void
  ): Promise<ImageCreatorResponse> => {
    const adkRequest = {
      appName,
      userId,
      sessionId,
      newMessage,  // Already has proper inline_data format
      streaming: true,
    };

    return new Promise((resolve, reject) => {
      fetch(`${API_BASE_URL}/run_sse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
          let fullText = '';
          const images: InlineData[] = [];

          if (!reader) {
            throw new Error('No response body reader');
          }

          while (true) {
            const { done, value } = await reader.read();

            if (done) {
              break;
            }

            buffer += decoder.decode(value, { stream: true });
            
            // Split by newlines to process complete SSE messages
            const lines = buffer.split('\n');
            
            // Keep the last incomplete line in buffer
            buffer = lines.pop() || '';

            for (const line of lines) {
              // Skip empty lines
              if (!line.trim()) continue;
              
              if (line.startsWith('data: ')) {
                const jsonString = line.slice(6).trim();
                
                // Skip empty data
                if (!jsonString) continue;
                
                try {
                  const data = JSON.parse(jsonString);

                  if (data.content?.parts) {
                    for (const part of data.content.parts) {
                      // Extract text
                      if (part.text) {
                        fullText = part.text;  // Use full text (not incremental)
                        if (onStreamEvent) {
                          onStreamEvent(part.text);
                        }
                      }

                      // Extract images from inline_data
                      // Response format: { inline_data: { mime_type: "...", data: "..." } }
                      if (part.inline_data) {
                        images.push({
                          mime_type: part.inline_data.mime_type,
                          data: part.inline_data.data,
                        });
                        console.log(
                          `✅ Image received: ${part.inline_data.mime_type}, ` +
                          `size: ${part.inline_data.data.length} chars`
                        );
                      }
                    }
                  }
                } catch (err) {
                  console.error('Error parsing SSE message:', err, 'Line:', jsonString.substring(0, 100));
                }
              }
            }
          }

          resolve({
            text: fullText,
            images: images.length > 0 ? images : undefined,
            status: 'success',
          });
        })
        .catch((error) => {
          console.error('SSE streaming error:', error);
          reject({
            text: '',
            status: 'error',
            error: error.message,
          });
        });
    });
  },

  /**
   * Send a custom message (for advanced use)
   * 
   * Allows sending any combination of text and images
   */
  sendMessage: async (
    message: MessageContent,
    userId: string = 'user_nextjs',
    sessionId?: string,
    onStreamEvent?: (text: string) => void
  ): Promise<ImageCreatorResponse> => {
    const sid = sessionId || `img_${Date.now()}`;

    // Create session
    await imageCreatorApi._createSession(userId, sid);

    // Call agent
    return await imageCreatorApi._callAgentSSE(
      'image_creator',
      userId,
      sid,
      message,
      onStreamEvent
    );
  },
};

/**
 * Helper: Display image from inline_data
 * 
 * Usage in React:
 * ```tsx
 * const imageUrl = inlineDataToDataUrl(response.images[0]);
 * <img src={imageUrl} alt="Generated" />
 * ```
 */
export { inlineDataToDataUrl };

