# Event Handler Container Crash Investigation

**Date**: 2026-03-08  
**Status**: Root cause identified  
**Severity**: Critical - Event handler cannot start

---

## Summary

The event handler container is crash-looping because the PM2 ecosystem configuration references `server.js`, but this file is not copied into the Docker image during the build process.

---

## Investigation Steps

### 1. Docker Container Status
Unable to check directly (Docker not available in agent container), but confirmed crash-loop behavior from job description.

### 2. File Analysis

#### Current Dockerfile (`docker/event-handler/Dockerfile`)
```dockerfile
FROM node:22-bookworm-slim

RUN apt-get update && apt-get install -y curl git python3 make g++ && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*
RUN npm install -g pm2

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --omit=dev && \
    npm install --no-save thepopebot@$(node -p "require('./package.json').version")

COPY /templates/docker/event-handler/ecosystem.config.cjs /opt/ecosystem.config.cjs

EXPOSE 80
CMD ["pm2-runtime", "/opt/ecosystem.config.cjs"]
```

#### PM2 Ecosystem Config (`templates/docker/event-handler/ecosystem.config.cjs`)
```javascript
module.exports = {
  apps: [{
    name: 'next',
    script: 'server.js',  // ← THIS FILE DOESN'T EXIST IN THE CONTAINER
    kill_timeout: 120000,
  }]
};
```

#### Server.js File (`templates/server.js`)
```javascript
import { createServer } from 'http';
import next from 'next';
import { attachCodeProxy } from 'thepopebot/code/ws-proxy';

const app = next({ dev: false });
const handle = app.getRequestHandler();

// HACK: Prevent Next.js from registering its own WebSocket upgrade handler.
app.didWebSocketSetup = true;

app.prepare().then(() => {
  const server = createServer((req, res) => {
    handle(req, res);
  });

  attachCodeProxy(server);

  const port = process.env.PORT || 80;
  server.listen(port, () => {
    console.log(`> Ready on http://localhost:${port}`);
  });
});
```

---

## Root Cause Analysis

### The Problem
1. PM2 ecosystem config references `server.js` as the script to run
2. The Dockerfile copies the ecosystem config to `/opt/ecosystem.config.cjs`
3. **The Dockerfile never copies `server.js` into the image**
4. When PM2 starts, it tries to execute `server.js` which doesn't exist
5. PM2 fails, the container exits, Docker restarts it → crash loop

### Why This Happened
- The Dockerfile was updated to use the template ecosystem config
- The ecosystem config was changed to use `server.js` (custom HTTP server for WebSocket proxy)
- The Dockerfile was not updated to copy `server.js` into the image
- No one noticed because Docker builds might have succeeded (copy command doesn't fail), but runtime fails

### File Discrepancy
There are actually TWO different ecosystem configs in the repository:

**`docker/event-handler/ecosystem.config.cjs`** (correct, but not used):
```javascript
script: 'node_modules/.bin/next',
args: 'start -p 80',
```

**`templates/docker/event-handler/ecosystem.config.cjs`** (used by Dockerfile, broken):
```javascript
script: 'server.js',  // Missing file!
```

---

## Solution

### Option 1: Copy server.js into the image (Recommended)
This maintains the custom server setup (needed for WebSocket proxy) and just fixes the missing file.

**Update `docker/event-handler/Dockerfile`:**
```dockerfile
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --omit=dev && \
    npm install --no-save thepopebot@$(node -p "require('./package.json').version")

# Copy server.js (custom HTTP server with WebSocket proxy)
COPY /templates/server.js ./

COPY /templates/docker/event-handler/ecosystem.config.cjs /opt/ecosystem.config.cjs

EXPOSE 80
CMD ["pm2-runtime", "/opt/ecosystem.config.cjs"]
```

### Option 2: Use the correct ecosystem config
Alternatively, use the `docker/event-handler/ecosystem.config.cjs` version that runs Next.js directly without the custom server.

**Update Dockerfile COPY line:**
```dockerfile
COPY /docker/event-handler/ecosystem.config.cjs /opt/ecosystem.config.cjs
```

**However**: This would lose the WebSocket proxy functionality (`attachCodeProxy`) which is needed for Claude Code mode.

---

## Recommended Fix

**Use Option 1** — copy `server.js` into the image. This is the correct long-term solution because:
1. The custom server is needed for WebSocket proxy (Claude Code feature)
2. It's a one-line addition to the Dockerfile
3. It maintains the intended architecture

---

## Verification Steps

After applying the fix:
1. Rebuild the event handler image
2. Start the container
3. Check logs: should see `> Ready on http://localhost:80`
4. Test health check: `curl http://localhost:80/api/ping`
5. Verify WebSocket proxy works (if Claude Code is enabled)

---

## Related Files
- `docker/event-handler/Dockerfile`
- `templates/docker/event-handler/ecosystem.config.cjs`
- `templates/server.js`
- `docker/event-handler/ecosystem.config.cjs` (not currently used)

---

## Prevention

To prevent similar issues in the future:
1. Add integration tests that build and start the Docker images
2. Add health checks to CI/CD pipeline
3. Document the relationship between ecosystem.config.cjs and server.js
4. Consider consolidating the two ecosystem config files

---

## Fix Applied ✅

The fix has been successfully applied to all relevant files:

### Changes Made

#### 1. Updated Dockerfiles (3 files)
- `docker/event-handler/Dockerfile`
- `templates/docker/event-handler/Dockerfile`
- `my-agent/docker/event-handler/Dockerfile`

Added line to copy `server.js` into the container:
```dockerfile
# Copy server.js (custom HTTP server with WebSocket proxy support)
COPY /templates/server.js ./
```

#### 2. Updated Ecosystem Configs (3 files)
- `docker/event-handler/ecosystem.config.cjs`
- `templates/docker/event-handler/ecosystem.config.cjs`
- `my-agent/docker/event-handler/ecosystem.config.cjs`

All now consistently reference `server.js`:
```javascript
script: 'server.js',
```

#### 3. Added Missing File
- Copied `templates/server.js` to `my-agent/server.js`

### Verification

All files verified:
- ✅ All Dockerfiles now copy server.js
- ✅ All ecosystem configs reference server.js
- ✅ server.js exists in both templates/ and my-agent/
- ✅ No syntax errors in any JavaScript files

### Next Steps

To complete the fix:
1. Commit these changes to the repository
2. Rebuild the event handler Docker image:
   ```bash
   docker build -f docker/event-handler/Dockerfile -t thepopebot-event-handler:fixed .
   ```
3. Restart the event handler container:
   ```bash
   docker-compose up -d event-handler
   ```
4. Check logs to verify successful startup:
   ```bash
   docker logs -f thepopebot-event-handler
   ```
   Should see: `> Ready on http://localhost:80`

### Expected Behavior After Fix

The event handler should:
- Start successfully without crashing
- Listen on port 80
- Respond to `/api/ping` health checks
- Support WebSocket connections for Claude Code mode
- Log "thepopebot initialized" on startup

