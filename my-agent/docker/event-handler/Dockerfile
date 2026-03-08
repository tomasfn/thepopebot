# Multi-stage build for Next.js event handler with custom server

# Stage 1: Dependencies
FROM node:22-bookworm-slim AS deps

RUN apt-get update && apt-get install -y curl git python3 make g++ && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

# Stage 2: Build
FROM node:22-bookworm-slim AS builder
WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy all application source files
COPY . .

# Build Next.js application (creates .next directory)
RUN npm run build

# Stage 3: Production
FROM node:22-bookworm-slim AS runner

RUN apt-get update && apt-get install -y curl git python3 make g++ && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*
RUN npm install -g pm2

WORKDIR /app

ENV NODE_ENV=production

# Copy production dependencies (we'll install fresh to avoid platform issues)
COPY package.json package-lock.json* ./
RUN npm install --omit=dev && \
    npm install --no-save thepopebot@$(node -p "require('./package.json').version")

# Copy built Next.js application from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# Copy necessary config files
COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/instrumentation.js ./
COPY --from=builder /app/middleware.js ./
COPY --from=builder /app/postcss.config.mjs ./

# Copy runtime directories (will be populated at runtime, but structure needs to exist)
COPY --from=builder /app/config ./config
COPY --from=builder /app/cron ./cron
COPY --from=builder /app/triggers ./triggers

# Copy custom server
COPY server.js ./

# Copy PM2 config
COPY docker/event-handler/ecosystem.config.cjs /opt/ecosystem.config.cjs

EXPOSE 80
CMD ["pm2-runtime", "/opt/ecosystem.config.cjs"]
