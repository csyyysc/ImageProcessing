# Makefile for Image Processing Application Docker operations

.PHONY: help dev test build test-and-build push push-backend push-frontend prod prod-nginx clean logs stop status setup-prod

# Default target
help:
	@echo "Available commands:"
	@echo "  dev           - Run in development mode"
	@echo "  test          - Run tests only"
	@echo "  build         - Build production images (runs tests first)"
	@echo "  test-and-build- Run tests and build production if tests pass"
	@echo "  push          - Push all images to GHCR"
	@echo "  push-backend  - Push backend image to GHCR"
	@echo "  push-frontend - Push frontend image to GHCR"
	@echo "  prod          - Run in production mode"
	@echo "  clean         - Clean up Docker resources"
	@echo "  logs          - Show container logs"
	@echo "  stop          - Stop all containers"

# Run tests only
test:
	@echo "🧪 Running tests in Docker..."
	sudo docker build -f Dockerfile.test -t image-processing-app-test .
	sudo docker run --rm image-processing-app-test

# Build production images only (assumes tests already passed)
build:
	@echo "🔨 Building production Docker images..."
	sudo docker build -f Dockerfile.backend -t ghcr.io/csyyysc/image-processing-backend .
	sudo docker build -f Dockerfile.frontend -t ghcr.io/csyyysc/image-processing-frontend .

# Push backend image to GHCR
push-backend: 
	@echo "📤 Pushing backend image to GHCR..."
	sudo docker push ghcr.io/csyyysc/image-processing-backend

# Push frontend image to GHCR
push-frontend:
	@echo "📤 Pushing frontend image to GHCR..."
	sudo docker push ghcr.io/csyyysc/image-processing-frontend

# Push all images to GHCR
push: push-backend push-frontend
	@echo "✅ All images pushed to GHCR!"

# Development mode
dev:
	@echo "🚀 Starting development environment..."
	sudo docker-compose -f docker-compose.dev.yml --profile dev up --build

# Production mode (builds if needed)
prod: build
	@echo "🏭 Starting production environment..."
	sudo docker-compose up -d

# Production with nginx
prod-nginx:
	@echo "🏭 Starting production environment with nginx..."
	sudo docker-compose --profile nginx up --build -d

# Stop all containers
stop:
	@echo "🛑 Stopping all containers..."
	sudo docker-compose down
	sudo docker-compose down

# Show logs
logs:
	@echo "📋 Showing container logs..."
	sudo docker-compose logs -f

# Production logs
logs-prod:
	@echo "📋 Showing production logs..."
	sudo docker-compose logs -f

# Clean up Docker resources
clean:
	@echo "🧹 Cleaning up Docker resources..."
	sudo docker-compose down -v
	sudo docker-compose down -v
	sudo docker system prune -f
	sudo docker volume prune -f

# Full clean (including images)
clean-all:
	@echo "🧹 Full cleanup including images..."
	sudo docker-compose down -v --rmi all
	sudo docker-compose down -v --rmi all
	sudo docker system prune -af
	sudo docker volume prune -f

# Check if services are running
status:
	@echo "📊 Container status:"
	sudo docker-compose ps
	@echo "\n📊 Production container status:"
	sudo docker-compose ps

# Run production setup script
setup-prod:
	@echo "🔧 Running production setup..."
	sudo docker run --rm -v $(PWD):/app -w /app python:3.11-slim bash -c "pip install uv && uv run scripts/production.py"
