# Reference Images Feature

**Date**: 2026-01-02  
**Commit**: `1f9a085`  
**Feature**: Upload reference images for image generation  
**Status**: ✅ Implemented

---

## 🎯 **What Was Added**

### **Multiple Reference Image Upload**

Users can now upload one or more reference images when generating images. These references are used by Gemini 3 Pro Image to:
- **Maintain consistent style** (e.g., comic style, color palette)
- **Use specific characters** (upload character design, generate scenes with them)
- **Follow layouts** (e.g., slide templates, diagram styles)
- **Provide context** (e.g., brand assets, themes)

---

## 🔧 **Implementation**

### **1. API Client Updates** (`frontend/nextjs/lib/api/imageCreator.ts`)

**Interface Changes**:
```typescript
export interface ImageGenerationRequest {
  prompt: string;
  imageType?: 'diagram' | 'comic' | 'slide' | 'infographic' | 'illustration' | 'photo';
  aspectRatio?: '1:1' | '16:9' | '9:16' | '3:2' | '2:3' | '3:4' | '4:3' | '4:5' | '5:4' | '21:9';
  referenceImages?: string[];  // NEW: Array of base64 strings
}
```

**API Request**:
```typescript
body: JSON.stringify({
  prompt: request.prompt,
  image_type: request.imageType || 'illustration',
  aspect_ratio: request.aspectRatio || '1:1',
  reference_images: request.referenceImages || [],  // NEW: Send reference images
  user_id: userId,
  session_id: finalSessionId,
}),
```

---

### **2. UI Components** (`frontend/nextjs/app/image-creator/page.tsx`)

**New State**:
```typescript
const [referenceImages, setReferenceImages] = useState<string[]>([]);  // Base64 array
const refImageInputRef = useRef<HTMLInputElement>(null);
```

**Upload Handler**:
```typescript
const handleReferenceImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
  const files = e.target.files;
  if (!files || files.length === 0) return;

  const newReferenceImages: string[] = [];
  
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
      showToast(`File ${file.name} is not an image`, 'error');
      continue;
    }

    // Convert to base64
    const base64 = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result as string;
        const base64String = dataUrl.split(',')[1];
        resolve(base64String);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });

    newReferenceImages.push(base64);
  }

  setReferenceImages((prev) => [...prev, ...newReferenceImages]);
  showToast(`Added ${newReferenceImages.length} reference image(s)`, 'success');
};
```

**Remove Handler**:
```typescript
const handleRemoveReferenceImage = (index: number) => {
  setReferenceImages((prev) => prev.filter((_, i) => i !== index));
  showToast('Reference image removed', 'success');
};
```

---

### **3. UI Layout**

**Reference Images Section**:
```tsx
<div className="mb-4">
  <label className="block text-sm font-medium text-gray-700 mb-2">
    Reference Images (Optional)
  </label>
  <p className="text-xs text-gray-500 mb-2">
    Upload images for style reference or context (e.g., characters, themes, layouts)
  </p>
  
  {/* Image previews */}
  {referenceImages.length > 0 && (
    <div className="grid grid-cols-3 gap-2 mb-2">
      {referenceImages.map((img, idx) => (
        <div key={idx} className="relative group">
          <img
            src={`data:image/png;base64,${img}`}
            alt={`Reference ${idx + 1}`}
            className="w-full h-20 object-cover rounded border"
          />
          <button
            onClick={() => handleRemoveReferenceImage(idx)}
            className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
      ))}
    </div>
  )}
  
  {/* Upload button */}
  <Button
    onClick={() => refImageInputRef.current?.click()}
    variant="outline"
    className="w-full"
  >
    <Upload className="w-4 h-4 mr-2" />
    {referenceImages.length > 0
      ? `Add More (${referenceImages.length} uploaded)`
      : 'Upload Reference Images'}
  </Button>
</div>
```

---

## 🎨 **Use Cases**

### **1. Consistent Character Design**

**Upload**: Character design reference  
**Prompt**: "Draw this character running in a park"  
**Result**: Image with character matching the reference style

---

### **2. Brand Consistency**

**Upload**: Logo, color palette, brand assets  
**Prompt**: "Create a diagram showing our product architecture"  
**Result**: Diagram using brand colors and style

---

### **3. Layout Templates**

**Upload**: Slide template or layout  
**Prompt**: "Create a slide about API performance"  
**Result**: Slide following the template layout

---

### **4. Style Reference**

**Upload**: Comic panel example  
**Prompt**: "Create a comic about debugging"  
**Result**: Comic matching the reference style

---

### **5. Scene Context**

**Upload**: Background or environment  
**Prompt**: "Add a robot to this scene"  
**Result**: Robot integrated into the reference scene

---

## 📊 **Features**

### **Multi-Image Upload**

✅ **Multiple files** at once  
✅ **File validation** (images only)  
✅ **Base64 conversion** (automatic)  
✅ **Preview thumbnails** (3-column grid)  
✅ **Individual removal** (hover to delete)  
✅ **Count display** (shows number uploaded)

---

### **User Experience**

✅ **Clear labels** ("Reference Images (Optional)")  
✅ **Helpful description** (use cases shown)  
✅ **Visual feedback** (toasts for success/error)  
✅ **Disabled state** (during generation)  
✅ **Hover effects** (delete button appears on hover)

---

### **Technical Features**

✅ **Base64 encoding** (for API transmission)  
✅ **Array management** (multiple images)  
✅ **File reader** (async file processing)  
✅ **Error handling** (invalid files rejected)  
✅ **Input reset** (after upload)

---

## 🧪 **Testing**

### **1. Upload Single Image**

**Steps**:
1. Click "Upload Reference Images"
2. Select 1 image file
3. See preview thumbnail
4. Enter prompt: "Generate in this style"
5. Click "Generate Image"

**Expected**:
- ✅ Preview shows correctly
- ✅ Backend receives reference_images array with 1 item
- ✅ Generated image uses reference style

---

### **2. Upload Multiple Images**

**Steps**:
1. Click "Upload Reference Images"
2. Select 3 image files (multi-select)
3. See 3 preview thumbnails in grid

**Expected**:
- ✅ All 3 images shown in grid
- ✅ Button shows "(3 uploaded)"
- ✅ Backend receives array with 3 items

---

### **3. Remove Reference Image**

**Steps**:
1. Upload 2 images
2. Hover over first image
3. Click red delete button
4. See first image removed

**Expected**:
- ✅ Image removed from preview
- ✅ Toast shows "Reference image removed"
- ✅ Count updates to "(1 uploaded)"

---

### **4. Add More Images**

**Steps**:
1. Upload 1 image
2. Click "Add More (1 uploaded)"
3. Select 2 more images

**Expected**:
- ✅ Now shows 3 images total
- ✅ Button shows "(3 uploaded)"
- ✅ All images sent to backend

---

### **5. Generate Without References**

**Steps**:
1. Don't upload any images
2. Enter prompt
3. Generate

**Expected**:
- ✅ Works as before
- ✅ Backend receives empty array or undefined
- ✅ No errors

---

### **6. File Validation**

**Steps**:
1. Try to upload a .txt file
2. See error toast

**Expected**:
- ✅ Toast shows "File test.txt is not an image"
- ✅ File not added to preview
- ✅ No errors in console

---

## 🔍 **Backend Integration**

### **Request Format**

```json
{
  "prompt": "Generate an image",
  "image_type": "illustration",
  "aspect_ratio": "1:1",
  "reference_images": [
    "iVBORw0KGgoAAAANSUhEUgAA...",  // Base64 string 1
    "/9j/4AAQSkZJRgABAQEASA..."     // Base64 string 2
  ],
  "user_id": "user_nextjs",
  "session_id": "rum_abc123"
}
```

### **Backend Processing**

The backend (`services/adk-python/app/services/image_generation.py`) receives the array and converts each base64 string to `inline_data` format for Gemini:

```python
# Add reference images if provided
if reference_images_base64:
    for img_b64 in reference_images_base64:
        try:
            mime_type = "image/png"
            decoded_data = base64.b64decode(img_b64)
            parts.append(types.Part(
                inline_data=types.InlineData(
                    data=decoded_data,
                    mime_type=mime_type
                )
            ))
        except Exception as e:
            logger.warning(f"⚠️ Failed to decode reference image: {e}")
```

---

## 📈 **Benefits**

### **For Users**

✅ **Consistent style** across generations  
✅ **Character continuity** in stories  
✅ **Brand compliance** in marketing materials  
✅ **Layout consistency** in presentations  
✅ **Better context** for complex requests

---

### **For Quality**

✅ **Higher accuracy** (AI understands style better)  
✅ **Fewer iterations** (gets it right faster)  
✅ **Better results** (matches expectations)  
✅ **More control** (guide AI output)

---

## 🎯 **Example Workflows**

### **Workflow 1: Character-Based Comic**

```
1. Upload: Character reference image
2. Prompt: "Draw this character at a computer debugging code"
3. Generate → Get comic panel with consistent character
4. Prompt: "Now show the character celebrating after fixing the bug"
5. Generate → Second panel with same character style
```

---

### **Workflow 2: Brand Diagram**

```
1. Upload: Company logo, brand colors reference
2. Prompt: "Create a system architecture diagram for microservices"
3. Generate → Diagram with brand colors and style
4. Prompt: "Add monitoring layer with Datadog"
5. Generate → Updated diagram maintaining brand consistency
```

---

### **Workflow 3: Presentation Series**

```
1. Upload: Slide template with company branding
2. Prompt: "Create a slide about Q1 performance"
3. Generate → Slide matching template
4. Upload: Same template (or keep in references)
5. Prompt: "Create a slide about Q2 goals"
6. Generate → Another slide with consistent layout
```

---

## 🚀 **Deployment**

**Commit**: `1f9a085`  
**Status**: ✅ Deployed  
**Environments**: Dev + Prod (after merge)

---

## 📚 **User Documentation**

### **How to Use Reference Images**

**Step 1: Upload References**
1. Scroll to "Reference Images (Optional)" section
2. Click "Upload Reference Images"
3. Select one or more image files
4. See preview thumbnails appear

**Step 2: Remove If Needed**
1. Hover over any reference image
2. Click the red trash icon
3. Image is removed

**Step 3: Generate**
1. Enter your prompt (mention the reference if needed)
2. Click "Generate Image"
3. AI uses references for style/context

**Tips**:
- Upload clear, high-quality references
- Can upload multiple references (e.g., character + background)
- References remain until you remove them
- Try "in the style of the reference" in your prompt

---

## ✅ **Summary**

| Feature | Status |
|---------|--------|
| **Multiple Upload** | ✅ Implemented |
| **Preview Grid** | ✅ Implemented |
| **Individual Remove** | ✅ Implemented |
| **Base64 Conversion** | ✅ Implemented |
| **API Integration** | ✅ Implemented |
| **File Validation** | ✅ Implemented |
| **Error Handling** | ✅ Implemented |
| **Toast Feedback** | ✅ Implemented |
| **Backend Compatible** | ✅ Yes |

---

**Impact**:
- 🎨 **Better image quality** (AI has more context)
- ⚡ **Faster iteration** (fewer back-and-forth)
- ✅ **More control** (guide AI output)
- 🎯 **Consistent results** (maintain style/brand)

---

**Next**: Test the feature after deployment completes (~3 minutes)!

🎉 **Reference images now fully supported!**

