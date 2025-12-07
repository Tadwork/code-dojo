# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies
RUN npm ci --only=production=false

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Build Python backend
FROM python:3.10-slim AS backend-builder
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy backend files
COPY backend/pyproject.toml backend/uv.lock* ./

# Install dependencies
RUN uv sync --frozen || uv sync

# Copy backend source
COPY backend/ ./

# Run backend tests (comment out if tests are not ready)
# RUN uv run pytest --cov=app --cov-fail-under=80 || exit 1

# Stage 3: Production image
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy backend from builder
COPY --from=backend-builder /app /app
COPY --from=backend-builder /root/.local/share/uv /root/.local/share/uv

# Copy frontend build from builder
COPY --from=frontend-builder /app/frontend/build /app/static

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV PATH="/root/.local/bin:${PATH}"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

