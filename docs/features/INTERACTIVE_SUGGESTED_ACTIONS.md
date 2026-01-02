# Interactive Content Creator with Contextual Suggested Actions

## ✨ Overview

Replaced `interactive-v2` with an enhanced `interactive` page featuring **contextual suggested actions** - smart, pre-built workflow buttons that appear based on the current stage of the agent conversation.

---

## 🎯 Key Features

### 1. **Dynamic Suggested Actions**
Context-aware quick action buttons that appear based on agent responses:

- **Initial Stage**: Content type selection (Blog Post, Video Script, Social Media)
- **Outline Approval**: Approve & Continue, Request Changes
- **Visual Content**: Generate AI Images, Upload Images, No Images
- **Draft Review**: Approve Draft, Request Edits
- **Social Media**: Yes Create Posts, No Skip
- **Video Keyframes**: Generate Keyframes, Skip Keyframes
- **Export**: Save Content

### 2. **Optimized Streaming**
- Smooth, incremental SSE streaming
- Text deduplication to prevent replay
- Throttled updates (max 20/sec) for better performance
- `requestAnimationFrame` integration for smooth rendering
- Proper cleanup with `AbortController`

### 3. **Intelligent Workflow Detection**
The agent automatically detects workflow stages by analyzing response content:

```typescript
// Detects stage keywords in agent responses
- "what type of content" → Show content type buttons
- "approved" + "outline" → Show approval buttons
- "visual content" + "choose" → Show image generation options
- "first draft" + "feedback" → Show draft review buttons
- "social media posts" + "promote" → Show social media decision
```

---

## 🚀 Changes Made

### 1. **Replaced interactive-v2 with interactive**

**Before**:
- `/content-creator/interactive` - Old version
- `/content-creator/interactive-v2` - New optimized version

**After**:
- `/content-creator/interactive` - **New optimized version with suggested actions**
- `interactive-v2` folder deleted

### 2. **Added Suggested Actions Feature**

**New State Management**:
```typescript
const [suggestedActions, setSuggestedActions] = useState<SuggestedAction[]>([]);

interface SuggestedAction {
  icon: string;           // Icon name (FileText, Video, CheckCircle, etc.)
  label: string;          // Button label
  prompt: string;         // Pre-built prompt to send to agent
  variant?: 'default' | 'outline' | 'secondary' | 'ghost';
}
```

**New Function**:
```typescript
const extractSuggestedActions = useCallback((content: string): SuggestedAction[] => {
  // Analyzes agent response content
  // Returns contextual quick action buttons
  // Based on workflow stage keywords
}, []);
```

### 3. **UI Enhancements**

**Suggested Actions Bar** (appears below messages):
```jsx
{!isLoading && suggestedActions.length > 0 && (
  <div className="border-t bg-white px-4 py-3">
    <p className="text-xs text-gray-500 mb-2">💡 Suggested actions:</p>
    <div className="flex flex-wrap gap-2">
      {suggestedActions.map((action) => (
        <Button onClick={() => handleQuickAction(action)}>
          {action.label}
        </Button>
      ))}
    </div>
  </div>
)}
```

**Initial Quick Actions** (welcome screen):
- Large, visually appealing cards
- Blog Post, Video Script, Social Media
- Descriptive subtitles

---

## 📊 Workflow Examples

### Example 1: Blog Post Creation

**Stage 1: Initial** → User clicks "Blog Post"
```
Suggested Actions: [Upload Files]
```

**Stage 2: Outline Generated** → Agent asks for approval
```
Suggested Actions:
- ✅ Approve & Continue
- ✏️ Request Changes
- 📤 Upload Files
```

**Stage 3: Visual Content Choice** → Agent offers options
```
Suggested Actions:
- 🖼️ Generate AI Images
- 📤 Upload Images
- ❌ No Images
```

**Stage 4: Draft Generated** → Agent asks for feedback
```
Suggested Actions:
- ✅ Approve Draft
- ✏️ Request Edits
```

**Stage 5: Social Media Offer** → Agent suggests promotion
```
Suggested Actions:
- ✅ Yes, Create Posts
- ❌ No, Skip
```

**Stage 6: Final Export** → Agent ready to save
```
Suggested Actions:
- 💾 Save Content
```

### Example 2: Video Script Creation

**Stage 1: Initial** → User clicks "Video Script"
```
Suggested Actions: [Upload Files]
```

**Stage 2: Script Generated** → Agent shows script
```
Suggested Actions:
- ✅ Approve Draft
- ✏️ Request Edits
```

**Stage 3: Keyframes Offer** → Agent suggests keyframes
```
Suggested Actions:
- ✅ Generate Keyframes
- ❌ Skip Keyframes
```

**Stage 4: Export** → Agent ready to save
```
Suggested Actions:
- 💾 Save Content
```

---

## 🎨 UI/UX Improvements

### 1. **Contextual Awareness**
- Buttons appear/disappear based on conversation stage
- Always relevant to current workflow step
- Reduces user confusion and speeds up workflow

### 2. **Visual Design**
```
💡 Suggested actions:
┌─────────────────────┐  ┌─────────────────────┐
│ ✅ Approve & Continue│  │ ✏️ Request Changes   │
└─────────────────────┘  └─────────────────────┘
```

- **Icon + Text**: Clear purpose
- **Variants**: Primary actions (default), secondary (outline)
- **Responsive**: Wraps on mobile devices

### 3. **Smart Filtering**
- Max 3-4 actions shown at once
- Most relevant actions prioritized
- Upload option always available (except when explicitly offered)

---

## 🔧 Technical Implementation

### Keyword Detection Logic

```typescript
const contentLower = content.toLowerCase();

// Stage 1: Content type selection
if (contentLower.includes('what would you like to work on') || 
    contentLower.includes('what type of content')) {
  return [
    { icon: 'FileText', label: 'Blog Post', prompt: '...' },
    { icon: 'Video', label: 'Video Script', prompt: '...' },
    { icon: 'Share2', label: 'Social Media', prompt: '...' },
  ];
}

// Stage 2: Outline approval
if (contentLower.includes('approved') && contentLower.includes('outline')) {
  return [
    { icon: 'CheckCircle', label: 'Approve & Continue', prompt: 'Yes, I approve...' },
    { icon: 'Edit', label: 'Request Changes', prompt: 'I have feedback...' },
  ];
}

// ... more stage detections ...
```

### Action Handler

```typescript
const handleQuickAction = (action: SuggestedAction) => {
  if (action.prompt === 'UPLOAD_FILES') {
    // Special case: toggle file upload UI
    setShowFileUpload(!showFileUpload);
  } else {
    // Send prompt to agent
    callAgent(action.prompt);
  }
};
```

### State Updates

```typescript
// Extract suggestions from agent's final response
if (assistantMessageId && lastText) {
  throttledUpdate(assistantMessageId, lastText);
  
  // Analyze response and set suggested actions
  const actions = extractSuggestedActions(lastText);
  setSuggestedActions(actions);
}
```

---

## 📈 Performance Optimizations

### 1. **Streaming Performance**
- **Deduplication**: Skip identical text chunks
- **Throttling**: Max 20 UI updates/sec (50ms interval)
- **RAF Integration**: Sync with browser repaint cycle
- **Cleanup**: Proper AbortController usage

### 2. **React Optimizations**
- `useCallback` for stable function references
- `React.memo` on ChatMessage component
- Minimal re-renders during streaming

### 3. **UX Performance**
```typescript
const UPDATE_THROTTLE_MS = 50; // 20 updates/sec
const timeSinceLastUpdate = now - lastUpdateTime;

if (timeSinceLastUpdate >= UPDATE_THROTTLE_MS) {
  throttledUpdate(assistantMessageId, fullText);
  lastUpdateTime = now;
}
```

---

## 🎯 Benefits

### For Users
1. **Faster Workflow** - One-click actions instead of typing
2. **Guided Experience** - Always know what to do next
3. **Reduced Errors** - Pre-validated prompts
4. **Consistent Language** - Standard agent communication

### For Agents
1. **Clearer Intent** - Well-structured user inputs
2. **Predictable Flow** - Expected workflow progression
3. **Easier Parsing** - Known prompt formats

### For Developers
1. **Extensible** - Easy to add new stage detections
2. **Maintainable** - Clear separation of concerns
3. **Testable** - Pure function for suggestion extraction

---

## 🔄 Migration Notes

### Old Route (Removed)
- `frontend/nextjs/app/content-creator/interactive-v2/` - **DELETED**

### New Route (Active)
- `frontend/nextjs/app/content-creator/interactive/` - **Enhanced with suggestions**

### No Breaking Changes
- URL remains the same: `/content-creator/interactive`
- All existing functionality preserved
- New features are additive

---

## 🎬 Demo

### Screenshot: Contextual Actions in Action

![Suggested Actions Demo](./.playwright-mcp/interactive-suggested-actions-demo.png)

**Shown**: 
- Full blog post content streamed successfully
- "Suggested actions" bar with contextual button
- Smooth markdown rendering
- Beautiful UI with purple/blue gradient

### Test Flow (Verified)
1. ✅ Click "Blog Post" → Agent starts planning
2. ✅ Agent generates outline → "Approve & Continue" button appears
3. ✅ Click "Approve & Continue" → Agent writes blog post
4. ✅ Full blog post streamed incrementally
5. ✅ Suggested actions updated based on stage
6. ✅ No replay effect, smooth rendering

---

## 📝 Code Files Changed

### Created/Modified
- `frontend/nextjs/app/content-creator/interactive/page.tsx` - **Replaced with optimized version**

### Deleted
- `frontend/nextjs/app/content-creator/interactive-v2/` - **Removed entire folder**

### New Features Added
1. `SuggestedAction` interface
2. `suggestedActions` state management
3. `extractSuggestedActions()` function
4. Suggested Actions Bar component
5. Enhanced `callAgent()` with suggestion extraction
6. Icon mapping function `getIcon()`

---

## 🚀 Deployment Status

- ✅ Local testing complete
- ✅ Interactive page replaced successfully
- ✅ Suggested actions working correctly
- ✅ Streaming optimized and smooth
- 🔜 Ready for production deployment

---

## 🎓 Usage Tips

### For Content Creators

**Tip 1: Use Suggested Actions First**
- Always check suggested actions before typing
- Faster than typing custom prompts
- Ensures consistent agent communication

**Tip 2: Upload Files Early**
- Click "Upload Files" at the beginning
- Agent can analyze context for better content
- Supports images, videos, documents

**Tip 3: Iterate with Quick Actions**
- Use "Request Changes" for specific feedback
- Click "Approve & Continue" when ready
- Natural workflow progression

### For Developers

**Adding New Stage Detections**:
```typescript
// In extractSuggestedActions()
if (contentLower.includes('your_new_stage_keyword')) {
  return [
    { icon: 'IconName', label: 'Action Label', prompt: 'Action prompt' },
  ];
}
```

**Adding New Icons**:
```typescript
// In getIcon() function
const icons: Record<string, any> = {
  FileText,
  Video,
  // Add your new icon here
  YourNewIcon,
};
```

---

## 🎉 Summary

Replaced `interactive-v2` with an enhanced `interactive` page featuring:

✅ **Contextual Suggested Actions** - Smart, stage-aware quick action buttons  
✅ **Optimized Streaming** - Smooth, incremental, no replay  
✅ **Beautiful UI** - Purple/blue gradient, responsive design  
✅ **Guided Workflow** - Clear next steps at every stage  
✅ **Performance** - Throttled updates, RAF integration, cleanup  
✅ **Extensible** - Easy to add new stages and actions  

**Status**: 🚀 Production Ready!

---

**Created**: January 2, 2026  
**Version**: 2.0.0  
**Route**: `/content-creator/interactive`

