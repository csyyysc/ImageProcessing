# Production Dockerfile for Image Processing Application
# Optimized for minimal image size and security

# Stage 1: Base image with Python and uv (Alpine for smaller size)
FROM python:3.11-alpine as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_CACHE_DIR=/tmp/uv \
    PATH="/app/.venv/bin:$PATH"

# Install system dependencies in one layer and clean up
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libffi-dev \
    && apk add --no-cache \
    curl \
    && pip install --no-cache-dir uv \
    && apk del .build-deps

# Set work directory
WORKDIR /app

# Copy dependency files (use production config for smaller dependencies)
COPY pyproject.prod.toml pyproject.toml
COPY uv.lock ./

# Install only production dependencies and clean up cache in one layer
RUN uv sync --frozen --no-dev \
    && uv cache clean \
    && rm -rf /tmp/uv \
    && find /app/.venv -name "*.pyc" -delete \
    && find /app/.venv -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Stage 2: Production image (minimal attack surface)
FROM python:3.11-alpine as production

# Accept build arguments from GitHub Actions
ARG BACKEND_URL

# Copy only the virtual environment from base stage
COPY --from=base /app/.venv /app/.venv

# Set environment variables from build args
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    BACKEND_URL=${BACKEND_URL} \

# Install only runtime dependencies (curl for health check)
RUN apk add --no-cache curl

# Set work directory
WORKDIR /app

# Copy only necessary application files
COPY main.py ./
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY shared/ ./shared/
COPY scripts/ ./scripts/

# Create necessary directories in one layer
RUN mkdir -p data uploads logs \
    && addgroup -g 1001 -S appgroup \
    && adduser -S appuser -u 1001 -G appgroup \
    && chown -R appuser:appgroup /app

# Switch to non-root user for security
USER appuser

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden)
CMD ["uv", "run", "main.py"]
