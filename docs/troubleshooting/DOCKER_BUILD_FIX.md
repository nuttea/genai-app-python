# Docker Build Fix - react-syntax-highlighter

## Issue

After adding `react-syntax-highlighter` to `package.json`, the Next.js app failed to compile with:

```
Module not found: Can't resolve 'react-syntax-highlighter'
```

## Root Cause

The Docker container was using a **named volume** for `node_modules` that still contained the old packages without the newly added dependency.

Even though we rebuilt the Docker image and the new package was installed during the build, when the container started, it mounted the old named volume over the fresh `node_modules`, causing the module not found error.

## Solution

### Steps to Fix

1. **Rebuild the Docker image** to install new dependencies:
   ```bash
   docker-compose build nextjs-frontend
   ```

2. **Remove the old container and volumes**:
   ```bash
   docker-compose rm -f -s -v nextjs-frontend
   docker volume rm genai-app-python_nextjs-node-modules genai-app-python_nextjs-build
   ```

3. **Recreate the container with fresh volumes**:
   ```bash
   docker-compose up -d nextjs-frontend
   ```

### Quick Fix Command

For future dependency updates, use this one-liner:

```bash
docker-compose build nextjs-frontend && \
docker-compose rm -f -s -v nextjs-frontend && \
docker volume rm genai-app-python_nextjs-node-modules genai-app-python_nextjs-build && \
docker-compose up -d nextjs-frontend
```

## Verification

After the fix:

```bash
# Check compilation logs
docker-compose logs nextjs-frontend --tail 20

# Expected output:
#  ✓ Compiled /content-creator/blog-post in 3.4s (2762 modules)

# Test the page
curl -I http://localhost:3000/content-creator/blog-post

# Expected: HTTP 200 OK
```

## Results

✅ **Build Error Resolved**
- Next.js compiled successfully
- All 2,762 modules loaded
- Blog Post page returns HTTP 200
- Content Creator landing page returns HTTP 200
- No more "Module not found" errors

## Why This Happens

Docker named volumes persist across container restarts. When you:

1. Add a new dependency to `package.json`
2. Rebuild the Docker image
3. Restart the container

The **old volume** (with old packages) is remounted, overriding the fresh `node_modules` from the new image.

**Solution**: Always remove the volume when adding new dependencies.

## Best Practices

### When Adding Dependencies

1. **Update package.json**
2. **Rebuild + Remove Volumes**:
   ```bash
   make docker-rebuild-nextjs  # If we add this to Makefile
   ```

3. **Or manually**:
   ```bash
   docker-compose build nextjs-frontend
   docker-compose rm -f -s -v nextjs-frontend
   docker volume rm genai-app-python_nextjs-node-modules genai-app-python_nextjs-build
   docker-compose up -d nextjs-frontend
   ```

### For Production Builds

In production (Cloud Run), this isn't an issue because:
- No volumes are used
- Each deployment builds fresh `node_modules`
- Dependencies are installed from `package.json` during build

## Files Modified

- `frontend/nextjs/package.json` - Added `react-syntax-highlighter` dependencies
- Docker image rebuilt with 642 packages (25 more than before)
- Named volumes recreated from scratch

## Timeline

- **Issue Reported**: User got "Module not found" error
- **Rebuild**: Installed 642 packages successfully
- **First Restart**: Error persisted (old volume)
- **Volume Remove**: Cleaned old volumes
- **Final Restart**: ✅ Compiled successfully
- **Verification**: ✅ HTTP 200 OK

## Prevention

Add to Makefile:

```makefile
docker-rebuild-nextjs: ## Rebuild Next.js with fresh dependencies
	@echo "🔨 Rebuilding Next.js with fresh dependencies..."
	docker-compose build nextjs-frontend
	docker-compose rm -f -s -v nextjs-frontend
	docker volume rm genai-app-python_nextjs-node-modules genai-app-python_nextjs-build 2>/dev/null || true
	docker-compose up -d nextjs-frontend
	@echo "✅ Next.js rebuilt with fresh dependencies"
```

Usage:
```bash
make docker-rebuild-nextjs
```

---

**Status**: ✅ **RESOLVED**  
**Impact**: No impact on production  
**Duration**: ~5 minutes  
**Lesson**: Always clean volumes when adding new npm packages

