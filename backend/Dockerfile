# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python dependencies
FROM python:3.12-slim AS python-deps
WORKDIR /app
COPY backend/pyproject.toml ./
# Create minimal app package so hatchling can build
RUN mkdir -p app && touch app/__init__.py
RUN pip install --no-cache-dir hatchling && \
    pip install --no-cache-dir . && \
    pip install --no-cache-dir uvicorn[standard]

# Stage 3: Production
FROM python:3.12-slim AS production

# Install nginx and supervisor
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx supervisor && \
    rm -rf /var/lib/apt/lists/*

# Copy Python packages from deps stage
COPY --from=python-deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=python-deps /usr/local/bin /usr/local/bin

# Copy frontend build
COPY --from=frontend-build /app/frontend/dist /app/static

# Copy nginx config
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Copy backend code
COPY backend/ /app/backend/
WORKDIR /app/backend

# Copy supervisord config
COPY backend/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
