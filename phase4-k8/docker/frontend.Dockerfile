# Frontend Dockerfile for Phase 4 Kubernetes Deployment
# Build context: ../../phase3-chatbot/frontend/
# Usage: docker build -f phase4-k8/docker/frontend.Dockerfile -t todo-chatbot-frontend:latest phase3-chatbot/frontend/

# Multi-stage build for Next.js frontend
# Stage 1: Install dependencies
FROM node:20-alpine AS deps
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Stage 2: Build the application
FROM node:20-alpine AS builder
WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application source
COPY . .

# Set environment variable for production build
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production

# Enable standalone output for Docker (inline configuration)
RUN echo 'module.exports = { ...require("./next.config.js"), output: "standalone" }' > next.config.docker.js && \
    mv next.config.docker.js next.config.js || true

# Build the Next.js application
RUN npm run build

# Stage 3: Production image
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy necessary files from builder
# Note: Next.js standalone mode automatically includes public files in .next/standalone
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose port 80 (Next.js will run on this port)
EXPOSE 80

# Set port environment variable
ENV PORT 80
ENV HOSTNAME "0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:80/', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start Next.js server
CMD ["node", "server.js"]
