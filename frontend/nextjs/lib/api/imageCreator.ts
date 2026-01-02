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
  referenceImages?: string[];  // Optional reference images as base64 strings (for style/context)
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
   * Generate image from text prompt (non-streaming)
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
    try {
      // Get Datadog RUM session ID if available
      let rumSessionId: string | undefined;
      try {
        if (typeof window !== 'undefined' && (window as any).DD_RUM) {
          const session = (window as any).DD_RUM.getInternalContext();
          if (session?.session_id) {
            rumSessionId = `rum_${session.session_id}`;
            console.log(`📊 Using Datadog RUM session ID: ${rumSessionId}`);
          }
        }
      } catch (e) {
        console.warn('Could not get RUM session ID:', e);
      }

      // Use RUM session ID if available, otherwise provided sessionId
      const finalSessionId = rumSessionId || sessionId;

      const response = await fetch(`${API_BASE_URL}/api/v1/images/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: request.prompt,
          image_type: request.imageType || 'illustration',
          aspect_ratio: request.aspectRatio || '1:1',
          reference_images: request.referenceImages || [],  // Send reference images as array
          user_id: userId,
          session_id: finalSessionId,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }

      const data = await response.json();

      console.log('📦 Image generation response:', data);

      if (data.status === 'success' && data.image_url) {
        // Fetch the image from the URL
        console.log(`🌐 Fetching image from: ${API_BASE_URL}${data.image_url}`);
        const imageResponse = await fetch(`${API_BASE_URL}${data.image_url}`);
        
        if (!imageResponse.ok) {
          console.error(`❌ Failed to fetch image: ${imageResponse.status}`);
          throw new Error(`Failed to fetch image: ${imageResponse.status}`);
        }

        const blob = await imageResponse.blob();
        
        // Convert to base64
        const base64 = await new Promise<string>((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => {
            const dataUrl = reader.result as string;
            const base64String = dataUrl.split(',')[1];
            resolve(base64String);
          };
          reader.readAsDataURL(blob);
        });

        console.log(`✅ Image fetched: ${data.mime_type}, size: ${base64.length} chars`);

        return {
          text: data.text_response || 'Image generated successfully',
          images: [{
            mime_type: data.mime_type,
            data: base64,
          }],
          status: 'success',
        };
      } else {
        console.error('❌ Image generation failed:', data);
        return {
          text: data.error || 'Image generation failed',
          status: 'error',
          error: data.error,
        };
      }
    } catch (error) {
      console.error('❌ Image generation error:', error);
      return {
        text: '',
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
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

          // Collect all image URLs for batch fetching at the end
          const imageUrls: Array<{url: string, mimeType: string}> = [];

          while (true) {
            const { done, value } = await reader.read();

            if (done) {
              break;
            }

            buffer += decoder.decode(value, { stream: true });
            
            // SSE events are separated by double newlines
            // Split by double newline to get complete events
            const events = buffer.split('\n\n');
            
            // Keep the last incomplete event in buffer
            buffer = events.pop() || '';

            for (const event of events) {
              // Skip empty events
              if (!event.trim()) continue;
              
              // SSE events can have multiple lines, each starting with "data: "
              // Collect all data lines and concatenate them
              const dataLines = event.split('\n')
                .filter(line => line.startsWith('data: '))
                .map(line => line.slice(6));
              
              if (dataLines.length === 0) continue;
              
              // Concatenate all data lines (some SSE implementations split large JSON)
              const jsonString = dataLines.join('');
              
              if (!jsonString.trim()) continue;
              
              try {
                const data = JSON.parse(jsonString);

                // Log full data for debugging
                console.log('SSE data received:', JSON.stringify(data).substring(0, 300));

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
                    
                    // NEW: Extract image_url from tool call result
                    // The tool result is embedded in the text response
                    if (part.text && part.text.includes('image_url')) {
                      try {
                        const match = part.text.match(/"image_url":\s*"([^"]+)"/);
                        if (match) {
                          const imageUrl = match[1];
                          const mimeTypeMatch = part.text.match(/"mime_type":\s*"([^"]+)"/);
                          const mimeType = mimeTypeMatch ? mimeTypeMatch[1] : 'image/png';
                          console.log(`📥 Found image_url in text: ${imageUrl}`);
                          imageUrls.push({ url: imageUrl, mimeType });
                        }
                      } catch (e) {
                        console.error('Error extracting image_url from text:', e);
                      }
                    }
                  }
                }
                
                // Also check top-level for image_url
                if (data.image_url) {
                  console.log(`📥 Found image_url at top level: ${data.image_url}`);
                  imageUrls.push({ 
                    url: data.image_url, 
                    mimeType: data.mime_type || 'image/png' 
                  });
                }
              } catch (err) {
                console.error('Error parsing SSE event:', err);
                console.error('Event data:', jsonString.substring(0, 200) + '...');
              }
            }
          }

          // After streaming completes, fetch all images
          console.log(`📦 Fetching ${imageUrls.length} images from URLs...`);
          for (const { url, mimeType } of imageUrls) {
            try {
              const fullUrl = `${API_BASE_URL}${url}`;
              console.log(`🌐 Fetching: ${fullUrl}`);
              const res = await fetch(fullUrl);
              if (!res.ok) {
                console.error(`❌ Failed to fetch image: ${res.status} ${res.statusText}`);
                continue;
              }
              const blob = await res.blob();
              const readerPromise = new Promise<string>((resolve) => {
                const reader = new FileReader();
                reader.onloadend = () => {
                  const base64 = (reader.result as string).split(',')[1];
                  resolve(base64);
                };
                reader.readAsDataURL(blob);
              });
              const base64 = await readerPromise;
              images.push({
                mime_type: mimeType,
                data: base64,
              });
              console.log(`✅ Image fetched: ${mimeType}, size: ${base64.length} chars`);
            } catch (err) {
              console.error(`❌ Failed to fetch image from ${url}:`, err);
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

