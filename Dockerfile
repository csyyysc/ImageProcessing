# Multi-stage Dockerfile for Image Processing Application
# This Dockerfile ensures tests pass before building the final image

# Stage 1: Base image with Python and uv
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

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

# Copy .env.dev file if it exists, otherwise create a default one
RUN if [ -f .env.dev ]; then \
        echo "📄 Using .env.dev file for test environment"; \
        cp .env.dev .env; \
    else \
        echo "⚠️  No .env.dev file found, creating default test configuration"; \
        echo "API_HOST=localhost" > .env; \
        echo "API_PORT=8000" >> .env; \
        echo "FRONTEND_HOST=localhost" >> .env; \
        echo "FRONTEND_PORT=8501" >> .env; \
        echo "BACKEND_URL=http://localhost:8000" >> .env; \
        echo "DATABASE_URL=sqlite:///./data/app.db" >> .env; \
        echo "SECRET_KEY=test-secret-key" >> .env; \
        echo "ACCESS_TOKEN_EXPIRE_MINUTES=30" >> .env; \
        echo "LOG_LEVEL=INFO" >> .env; \
        echo "DEBUG=true" >> .env; \
        echo "ENVIRONMENT=development" >> .env; \
    fi

# Run tests to ensure everything works
RUN uv run scripts/test.py

# Stage 3: Production image
FROM base as production

# Copy source code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p data uploads logs && \
    chmod 755 data uploads logs

# Copy .env.prod file (required for production)
RUN echo "📄 Using .env.prod file for production environment" && \
    cp .env.prod .env

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden)
CMD ["uv", "run", "main.py", "dev"]
