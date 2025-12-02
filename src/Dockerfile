# syntax=docker/dockerfile:1
# Multi-stage Dockerfile for a Node.js application.
# - Build stage installs deps, builds, then prunes devDependencies.
# - Final stage runs the production artifact as a non-root user.
# Adjust NODE_VERSION, EXPOSE and CMD to match your app.

ARG NODE_VERSION=18-alpine
FROM node:${NODE_VERSION} AS builder
WORKDIR /app

# Install dependencies (clean install for reproducibility)
COPY package*.json ./
RUN npm ci --silent

# Copy source and build (if your project has a build step)
COPY . .
RUN npm run build --if-present

# Remove devDependencies to keep artifacts lean
RUN npm prune --production --silent

FROM node:${NODE_VERSION} AS runner
WORKDIR /app
ENV NODE_ENV=production

# Create non-root user
RUN addgroup -S app && adduser -S app -G app

# Copy only what's needed for production
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/public ./public

USER app
EXPOSE 3000

# Default command: prefer npm start (adjust as needed).
CMD ["npm", "start"]