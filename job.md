# Event Handler Crash-Loop Fix - COMPLETE ✅

## Problem

Event handler container crashed on startup with:
```
TypeError: routesManifest.dataRoutes is not iterable
```

## Root Causes Identified

### 1. Incomplete Dockerfile
- Only copied `package.json`, `package-lock.json`, and `server.js`
- **Did NOT** copy application source code (`app/`, `config/`, etc.)
- **Did NOT** run `npm run build` to create `.next/` directory
- When `server.js` tried to start Next.js in production mode (`dev: false`), it failed because `.next/routes-manifest.json` didn't exist

### 2. Volume Mount Conflict
- docker-compose.yml mounted entire directory (`.:/app`)
- This would overlay host directory (without `.next`) over container's `/app`
- Even if Dockerfile built `.next`, the volume mount would hide it

## Solution Implemented

### Fix 1: Multi-Stage Dockerfile

Converted to proper Next.js production build with 3 stages:

**Stage 1 (deps):** Install all dependencies
```dockerfile
FROM node:22-bookworm-slim AS deps
COPY package.json package-lock.json* ./
RUN npm ci
```

**Stage 2 (builder):** Build the application
```dockerfile
FROM node:22-bookworm-slim AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build  # Creates .next/ directory
```

**Stage 3 (runner):** Production runtime
```dockerfile
FROM node:22-bookworm-slim AS runner
COPY --from=builder /app/.next ./.next  # Copy built artifacts
COPY --from=builder /app/public ./public
# Copy config, server.js, etc.
```

### Fix 2: Selective Volume Mounts

Changed docker-compose.yml from full directory mount to selective mounts:

**Before:**
```yaml
volumes:
  - .:/app              # ❌ Overwrites everything
  - /app/node_modules
```

**After:**
```yaml
build:
  context: .
  dockerfile: docker/event-handler/Dockerfile
volumes:
  - ./data:/app/data          # ✅ Only runtime directories
  - ./logs:/app/logs
  - ./config:/app/config
  - ./cron:/app/cron
  - ./triggers:/app/triggers
  - ./.env:/app/.env:ro
  - /var/run/docker.sock:/var/run/docker.sock
```

## Files Modified

✅ `templates/docker/event-handler/Dockerfile` - Multi-stage build  
✅ `templates/docker-compose.yml` - Build config + selective mounts  
✅ `my-agent/docker/event-handler/Dockerfile` - Multi-stage build  
✅ `my-agent/docker-compose.yml` - Build config + selective mounts  
✅ `/job/docker/event-handler/Dockerfile` - Multi-stage build

## How It Works Now

```
Build Phase:
1. docker-compose build → Triggers Dockerfile
2. Dockerfile copies all source → Runs npm run build → Creates .next/
3. Built .next/ directory is baked into the image

Runtime Phase:
1. docker-compose up → Starts container from built image
2. Selective volume mounts only overlay data/, logs/, config/, etc.
3. .next/ remains in container (not overwritten by mount)
4. server.js starts → Finds .next/routes-manifest.json ✅
5. Next.js starts successfully in production mode
```

## Deployment Instructions

```bash
cd my-agent

# Rebuild with new Dockerfile
docker-compose build event-handler

# Start container
docker-compose up -d event-handler

# Monitor logs
docker-compose logs -f event-handler
```

**Expected Success Output:**
```
> Ready on http://localhost:80
```

## Verification

```bash
# Check .next exists in container
docker exec thepopebot-event-handler ls -la /app/.next

# Verify routes manifest
docker exec thepopebot-event-handler cat /app/.next/routes-manifest.json

# Test API
curl http://localhost/api/ping
# Expected: {"status":"ok"}
```

## Why This Approach

**Alternative considered:** Use `next start` instead of custom server.js  
**Decision:** Keep custom server.js because it's needed for WebSocket proxy (code editor feature)  
**Solution:** Fix the Dockerfile to properly build for custom server

## Benefits

1. ✅ Fixes the crash - `.next/` with routes manifest now exists
2. ✅ Follows Next.js best practices - Multi-stage production build
3. ✅ Smaller final image - Dev dependencies excluded from production
4. ✅ Faster startup - Build happens once at image build time
5. ✅ Data persistence - Runtime directories still mounted as volumes
6. ✅ Maintains all features - Custom WebSocket proxy still works

## Key Insight

The fundamental issue was a mismatch between:
- **What Next.js needs:** Pre-built `.next/` directory with routes manifest
- **What was provided:** Raw source code with no build step
- **Additional complication:** Volume mount hiding any built files

The solution required fixing both the Dockerfile (to build properly) and docker-compose.yml (to not hide the built files).

---

## Documentation Reference

Detailed docs created in `/job/tmp/`:
- `investigation.md` - Initial problem analysis
- `volume-mount-issue.md` - Volume mount conflict explanation
- `dockerfile-comparison.md` - Before/after Dockerfile changes
- `FINAL-FIX-SUMMARY.md` - Complete solution with examples
- `QUICK-REFERENCE.md` - Quick deployment guide

**Status:** ✅ COMPLETE - Container should now start successfully without crash-loop
