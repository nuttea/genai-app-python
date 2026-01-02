# Image Creator Agent - ADK Directory Naming Fix

## 🎯 Root Cause

ADK framework expects agent directory names to match the agent's `name` field.

### The Problem
- **Agent name**: `image_creator`
- **Directory name**: `image_creator_agent` ❌

ADK searches for: `/app/image_creator/` but found: `/app/image_creator_agent/`

### Error Message
```
ValueError: No root_agent found for 'image_creator'. 
Searched in 'image_creator.agent.root_agent', 'image_creator.root_agent' 
and 'image_creator/root_agent.yaml'.
```

## 🔧 The Fix

### 1. Renamed Directory
```bash
mv services/adk-python/image_creator_agent → services/adk-python/image_creator
```

### 2. Updated All Imports

**main_adk.py:**
```python
# Old
from image_creator_agent.agent import root_agent as image_creator_root_agent

# New
from image_creator.agent import root_agent as image_creator_root_agent
```

**image_creator/__init__.py:**
```python
# Old
from image_creator_agent.agent import image_creator_agent, root_agent

# New
from image_creator.agent import image_creator_agent, root_agent
```

**image_creator/agent.py:**
```python
# Old
from image_creator_agent.config import config
from image_creator_agent.tools.image_tools import (...)

# New
from image_creator.config import config
from image_creator.tools.image_tools import (...)
```

**image_creator/tools/__init__.py:**
```python
# Old
from image_creator_agent.tools.image_tools import (...)

# New
from image_creator.tools.image_tools import (...)
```

**image_creator/tools/image_tools.py:**
```python
# Old
from image_creator_agent.config import config

# New
from image_creator.config import config
```

### 3. Updated Dockerfiles

**Dockerfile & Dockerfile.cloudrun:**
```dockerfile
# Old
COPY image_creator_agent/ ./image_creator_agent/

# New
COPY image_creator/ ./image_creator/
```

## ✅ Verification

```bash
docker logs genai-adk-python --tail 20
```

**Expected output:**
```
✅ Content Creator Agent loaded: interactive_content_creator with 2 tools
✅ Image Creator Agent loaded: image_creator with 3 tools
```

## 🎉 Success

The agent now:
- Loads successfully without errors
- Creates sessions: `POST /apps/image_creator/users/{user}/sessions`
- Generates images: `✅ Image generated successfully`

## 📋 Remaining Issue

There's a `400 INVALID_ARGUMENT` error when returning the image in the response.
This is likely due to how `inline_data` is being sent back to the frontend.

**Next steps:**
- Investigate response size limits
- Check inline_data format in the agent's return value
- Possibly need to return image URL instead of base64

