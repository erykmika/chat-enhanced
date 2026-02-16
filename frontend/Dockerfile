# Frontend Dockerfile - Vite + React
# Multi-stage: build with node, serve with nginx

# Build stage
FROM node:18-alpine AS build
WORKDIR /app

# Install deps first (better layer caching)
COPY package*.json ./
RUN npm ci --silent

# Copy the rest of the app and build
COPY . .
RUN npm run build

# Production stage - nginx
FROM nginx:stable-alpine

# SPA-friendly config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Static assets
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
