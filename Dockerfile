# Multi-stage Dockerfile for Image Processing Application
# This Dockerfile ensures tests pass before building the final image

# Stage 1: Base image with Python and uv
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_CACHE_DIR=/app/.cache/uv

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Stage 2: Test stage - runs tests before building final image
FROM base as test

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p data uploads logs

# Run tests to ensure everything works
RUN uv run scripts/test.py

# Stage 3: Production image
FROM base as production

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p data uploads logs

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden)
CMD ["uv", "run", "main.py"]
