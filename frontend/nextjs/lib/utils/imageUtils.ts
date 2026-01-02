/**
 * Image utilities for handling inline_data format
 * 
 * Based on: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation
 */

/**
 * Detect MIME type from image file
 */
export function detectMimeType(file: File): string {
  // Use file.type if available
  if (file.type) {
    return file.type;
  }
  
  // Fallback to extension
  const extension = file.name.split('.').pop()?.toLowerCase();
  const mimeTypes: Record<string, string> = {
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'webp': 'image/webp',
  };
  
  return mimeTypes[extension || ''] || 'image/png';
}

/**
 * Detect MIME type from base64 string using magic bytes
 */
export function detectMimeTypeFromBase64(base64: string): string {
  // Remove data URL prefix if present
  const cleanBase64 = base64.replace(/^data:image\/\w+;base64,/, '');
  
  // Decode first few bytes to check magic numbers
  try {
    const binaryString = atob(cleanBase64.substring(0, 32));
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    
    // Check magic bytes
    // PNG: 89 50 4E 47 0D 0A 1A 0A
    if (bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4E && bytes[3] === 0x47) {
      return 'image/png';
    }
    
    // JPEG: FF D8 FF
    if (bytes[0] === 0xFF && bytes[1] === 0xD8 && bytes[2] === 0xFF) {
      return 'image/jpeg';
    }
    
    // GIF: GIF87a or GIF89a
    if (bytes[0] === 0x47 && bytes[1] === 0x49 && bytes[2] === 0x46) {
      return 'image/gif';
    }
    
    // WebP: RIFF....WEBP
    if (
      bytes[0] === 0x52 && bytes[1] === 0x49 && bytes[2] === 0x46 && bytes[3] === 0x46 &&
      bytes[8] === 0x57 && bytes[9] === 0x45 && bytes[10] === 0x42 && bytes[11] === 0x50
    ) {
      return 'image/webp';
    }
  } catch (e) {
    console.warn('Failed to detect MIME type from base64:', e);
  }
  
  // Default to PNG
  return 'image/png';
}

/**
 * Convert File to base64 string
 */
export async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        // Remove data URL prefix to get pure base64
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      } else {
        reject(new Error('Failed to convert file to base64'));
      }
    };
    
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

/**
 * Create inline_data part from File
 * 
 * CRITICAL: This is the correct format for sending images to Gemini API
 */
export async function fileToInlineData(file: File): Promise<InlineDataPart> {
  const base64 = await fileToBase64(file);
  const mimeType = detectMimeType(file);
  
  return {
    inline_data: {
      mime_type: mimeType,
      data: base64,  // Pure base64 string (no data URL prefix)
    },
  };
}

/**
 * Create inline_data part from base64 string
 * 
 * Use this when you already have a base64-encoded image
 */
export function base64ToInlineData(base64: string, mimeType?: string): InlineDataPart {
  // Remove data URL prefix if present
  const cleanBase64 = base64.replace(/^data:image\/\w+;base64,/, '');
  
  // Detect MIME type if not provided
  const detectedMimeType = mimeType || detectMimeTypeFromBase64(cleanBase64);
  
  return {
    inline_data: {
      mime_type: detectedMimeType,
      data: cleanBase64,
    },
  };
}

/**
 * Convert inline_data to data URL for display
 */
export function inlineDataToDataUrl(inlineData: { mime_type: string; data: string }): string {
  return `data:${inlineData.mime_type};base64,${inlineData.data}`;
}

/**
 * Create text part
 */
export function textPart(text: string): TextPart {
  return { text };
}

/**
 * Create multimodal message with text and images
 * 
 * Example:
 * ```ts
 * const message = createMultimodalMessage(
 *   "Edit this image to make it more colorful",
 *   [imageFile]
 * );
 * ```
 */
export async function createMultimodalMessage(
  text: string,
  images?: File[]
): Promise<MessageContent> {
  const parts: Part[] = [];
  
  // Add images first (if any)
  if (images && images.length > 0) {
    for (const image of images) {
      const inlineData = await fileToInlineData(image);
      parts.push(inlineData);
    }
  }
  
  // Add text
  if (text.trim()) {
    parts.push(textPart(text));
  }
  
  return {
    role: 'user',
    parts,
  };
}

/**
 * Type definitions for inline_data format
 */

export interface InlineData {
  mime_type: string;
  data: string;  // Base64-encoded image data (no data URL prefix)
}

export interface InlineDataPart {
  inline_data: InlineData;
}

export interface TextPart {
  text: string;
}

export type Part = TextPart | InlineDataPart;

export interface MessageContent {
  role: 'user' | 'assistant';
  parts: Part[];
}

/**
 * Type guards
 */

export function isInlineDataPart(part: Part): part is InlineDataPart {
  return 'inline_data' in part;
}

export function isTextPart(part: Part): part is TextPart {
  return 'text' in part;
}

/**
 * Extract images from message parts
 */
export function extractImagesFromParts(parts: Part[]): InlineData[] {
  return parts
    .filter(isInlineDataPart)
    .map((part) => part.inline_data);
}

/**
 * Extract text from message parts
 */
export function extractTextFromParts(parts: Part[]): string {
  return parts
    .filter(isTextPart)
    .map((part) => part.text)
    .join('\n');
}

