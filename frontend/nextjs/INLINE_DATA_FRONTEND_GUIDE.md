# Frontend inline_data Handling Guide

## Overview

This guide explains how to **correctly send images to the ADK agents** using the proper `inline_data` format.

**🚨 CRITICAL**: Images must be sent as `inline_data` objects (NOT as base64 text in the prompt).

## ❌ Wrong Way (DO NOT DO THIS)

```typescript
// WRONG: Sending base64 as text
const message = {
  role: 'user',
  parts: [
    {
      text: `Here's the image: ${base64String}. Please edit it to be more colorful.`
    }
  ]
};
```

**Why this is wrong**:
- The API cannot parse base64 from text
- No MIME type information
- Model treats it as text, not as an image

## ✅ Correct Way (DO THIS)

```typescript
// CORRECT: Using inline_data format
const message = {
  role: 'user',
  parts: [
    {
      inline_data: {
        mime_type: 'image/png',  // Actual MIME type
        data: base64String        // Pure base64 (no data URL prefix)
      }
    },
    {
      text: 'Please edit it to be more colorful'
    }
  ]
};
```

**Why this is correct**:
- Proper structure that the API expects
- Includes MIME type for correct handling
- Model can process the image

---

## 🛠️ Utilities Provided

### 1. `imageUtils.ts`

Location: `lib/utils/imageUtils.ts`

Provides helper functions for working with `inline_data` format.

### 2. `imageCreator.ts`

Location: `lib/api/imageCreator.ts`

API client for the `image_creator_agent` with built-in `inline_data` support.

---

## 📖 Usage Examples

### Example 1: Generate Image from Text

```typescript
import { imageCreatorApi } from '@/lib/api/imageCreator';

// Simple text-to-image
const response = await imageCreatorApi.generateImage({
  prompt: "Create a diagram showing how Datadog APM works",
  imageType: "diagram",
  aspectRatio: "16:9"
});

// Display result
if (response.images && response.images.length > 0) {
  const imageUrl = inlineDataToDataUrl(response.images[0]);
  <img src={imageUrl} alt="Generated diagram" />
}
```

### Example 2: Edit an Existing Image

```typescript
import { imageCreatorApi } from '@/lib/api/imageCreator';

// Multi-turn editing
const response = await imageCreatorApi.editImage({
  editPrompt: "Make it more colorful",
  originalImageBase64: previousImageBase64,  // From previous generation
  aspectRatio: "1:1"
}, 'user_nextjs', sessionId);  // Keep same sessionId for multi-turn

// Display edited image
if (response.images) {
  const imageUrl = inlineDataToDataUrl(response.images[0]);
  <img src={imageUrl} alt="Edited image" />
}
```

### Example 3: Upload and Send Image File

```typescript
import { fileToInlineData, textPart } from '@/lib/utils/imageUtils';

// Handle file upload
const handleImageUpload = async (file: File) => {
  // Convert File to inline_data format
  const inlineDataPart = await fileToInlineData(file);
  
  // Create message with image + text
  const message = {
    role: 'user',
    parts: [
      inlineDataPart,  // Image first
      textPart('Analyze this image')  // Then text
    ]
  };
  
  // Send to agent
  const response = await imageCreatorApi.sendMessage(message);
};
```

### Example 4: Multi-turn Conversation with Images

```typescript
import { base64ToInlineData, textPart } from '@/lib/utils/imageUtils';

// Start conversation
const sessionId = `img_${Date.now()}`;

// Turn 1: Generate
const turn1 = await imageCreatorApi.generateImage(
  { prompt: "Generate a comic" },
  'user_nextjs',
  sessionId
);

// Turn 2: Edit (keep same sessionId)
const turn2 = await imageCreatorApi.editImage(
  {
    editPrompt: "Make the background purple",
    originalImageBase64: turn1.images![0].data
  },
  'user_nextjs',
  sessionId  // Same session!
);

// Turn 3: Further edit
const turn3 = await imageCreatorApi.editImage(
  {
    editPrompt: "Add a title at the top",
    originalImageBase64: turn2.images![0].data
  },
  'user_nextjs',
  sessionId  // Same session!
);
```

### Example 5: Use with Content Creator Agent

```typescript
import { createMultimodalMessage } from '@/lib/utils/imageUtils';
import { contentCreatorApi } from '@/lib/api/contentCreator';

// Upload image with text
const handleMultimodalMessage = async (text: string, imageFiles: File[]) => {
  // Create multimodal message
  const message = await createMultimodalMessage(text, imageFiles);
  
  // Send to content creator agent
  await contentCreatorApi.sendMessageWithInlineData(
    'content_creator_agent',
    'user_nextjs',
    sessionId,
    message,
    (chunk) => {
      console.log('Streaming:', chunk);
    }
  );
};
```

---

## 🔑 Key Functions

### `fileToInlineData(file: File)`
Converts a File object to inline_data format.

```typescript
const inlineDataPart = await fileToInlineData(imageFile);
// Returns: { inline_data: { mime_type: "image/png", data: "base64..." } }
```

### `base64ToInlineData(base64: string, mimeType?: string)`
Converts base64 string to inline_data format.

```typescript
const inlineDataPart = base64ToInlineData(base64String);
// Returns: { inline_data: { mime_type: "image/png", data: "base64..." } }
```

### `textPart(text: string)`
Creates a text part.

```typescript
const textPart = textPart("Edit this image");
// Returns: { text: "Edit this image" }
```

### `createMultimodalMessage(text: string, images?: File[])`
Creates a complete multimodal message.

```typescript
const message = await createMultimodalMessage(
  "Analyze these images",
  [file1, file2]
);
// Returns: { role: 'user', parts: [inline_data, inline_data, text] }
```

### `inlineDataToDataUrl(inlineData: InlineData)`
Converts inline_data to data URL for display.

```typescript
const url = inlineDataToDataUrl(response.images[0]);
// Returns: "data:image/png;base64,iVBORw0..."
<img src={url} />
```

---

## 📋 Message Format

### Text Only
```typescript
{
  role: 'user',
  parts: [
    { text: 'Generate an image' }
  ]
}
```

### Image Only
```typescript
{
  role: 'user',
  parts: [
    {
      inline_data: {
        mime_type: 'image/png',
        data: 'iVBORw0KGgoAAAANS...'
      }
    }
  ]
}
```

### Text + Image (Multi-turn Editing)
```typescript
{
  role: 'user',
  parts: [
    {
      inline_data: {
        mime_type: 'image/jpeg',
        data: '/9j/4AAQSkZJRgABAQAA...'
      }
    },
    { text: 'Make it more colorful' }
  ]
}
```

### Multiple Images + Text
```typescript
{
  role: 'user',
  parts: [
    { inline_data: { mime_type: 'image/png', data: 'iVBORw...' } },
    { inline_data: { mime_type: 'image/jpeg', data: '/9j/4AA...' } },
    { text: 'Compare these two images' }
  ]
}
```

---

## 🎨 React Component Example

```typescript
'use client';

import { useState } from 'react';
import { imageCreatorApi, inlineDataToDataUrl } from '@/lib/api/imageCreator';
import { fileToInlineData } from '@/lib/utils/imageUtils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function ImageCreatorPage() {
  const [sessionId] = useState(() => `img_${Date.now()}`);
  const [prompt, setPrompt] = useState('');
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const handleGenerate = async () => {
    setIsLoading(true);
    try {
      const response = await imageCreatorApi.generateImage(
        { prompt, imageType: 'diagram', aspectRatio: '16:9' },
        'user_nextjs',
        sessionId
      );
      
      if (response.images && response.images.length > 0) {
        const url = inlineDataToDataUrl(response.images[0]);
        setGeneratedImage(url);
      }
    } catch (error) {
      console.error('Generation error:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleEdit = async (editPrompt: string) => {
    if (!generatedImage) return;
    
    setIsLoading(true);
    try {
      // Extract base64 from data URL
      const base64 = generatedImage.split(',')[1];
      
      const response = await imageCreatorApi.editImage(
        { editPrompt, originalImageBase64: base64 },
        'user_nextjs',
        sessionId  // Same session for multi-turn
      );
      
      if (response.images && response.images.length > 0) {
        const url = inlineDataToDataUrl(response.images[0]);
        setGeneratedImage(url);
      }
    } catch (error) {
      console.error('Edit error:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div>
      <Input
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe the image..."
      />
      <Button onClick={handleGenerate} disabled={isLoading}>
        Generate
      </Button>
      
      {generatedImage && (
        <>
          <img src={generatedImage} alt="Generated" />
          <Button onClick={() => handleEdit('Make it more colorful')}>
            Make Colorful
          </Button>
          <Button onClick={() => handleEdit('Add a purple background')}>
            Purple Background
          </Button>
        </>
      )}
    </div>
  );
}
```

---

## 🚨 Common Mistakes

### Mistake 1: Sending Base64 as Text
```typescript
// ❌ WRONG
parts: [{ text: `Image: ${base64}` }]

// ✅ CORRECT
parts: [{ inline_data: { mime_type: 'image/png', data: base64 } }]
```

### Mistake 2: Including Data URL Prefix
```typescript
// ❌ WRONG
data: 'data:image/png;base64,iVBORw0...'

// ✅ CORRECT
data: 'iVBORw0...'  // Pure base64 only
```

### Mistake 3: Wrong MIME Type
```typescript
// ❌ WRONG (all images as PNG)
mime_type: 'image/png'

// ✅ CORRECT (detect actual type)
mime_type: detectMimeType(file)  // or detectMimeTypeFromBase64(base64)
```

### Mistake 4: Creating New Session Each Turn
```typescript
// ❌ WRONG (loses context)
const sessionId = `img_${Date.now()}`;  // New ID each time
await editImage(..., sessionId);

// ✅ CORRECT (maintains context)
const sessionId = `img_${Date.now()}`;  // Create once
await generateImage(..., sessionId);    // Turn 1
await editImage(..., sessionId);        // Turn 2 (same session)
await editImage(..., sessionId);        // Turn 3 (same session)
```

---

## 🔍 Debugging

### Check Message Format
```typescript
// Log message before sending
console.log('Sending message:', JSON.stringify(message, null, 2));

// Should see:
// {
//   "role": "user",
//   "parts": [
//     {
//       "inline_data": {
//         "mime_type": "image/png",
//         "data": "iVBORw0..."
//       }
//     },
//     {
//       "text": "Edit prompt"
//     }
//   ]
// }
```

### Verify Image Data
```typescript
// Check base64 is valid
const isValidBase64 = /^[A-Za-z0-9+/]+={0,2}$/.test(base64);

// Check length (should be >100 chars for images)
console.log('Base64 length:', base64.length);

// Display image to verify
const testUrl = `data:image/png;base64,${base64}`;
<img src={testUrl} />  // Should display the image
```

---

## 📖 References

- [Image Creator Agent Documentation](../../../services/adk-python/IMAGE_CREATOR_AGENT.md)
- [Inline Data Handling (Backend)](../../../services/adk-python/INLINE_DATA_HANDLING.md)
- [Google Cloud Image Generation](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation)

---

**Status**: ✅ Ready for use  
**Last Updated**: 2026-01-02

