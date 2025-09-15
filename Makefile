# Makefile for Image Processing Application Docker operations

.PHONY: help dev test run build prod clean logs

# Default target
help:
	@echo "Available commands:"
	@echo "  dev       - Run in development mode"
	@echo "  test      - Run tests in Docker"
	@echo "  build     - Build the Docker image"
	@echo "  prod      - Run in production mode"
	@echo "  clean     - Clean up Docker resources"
	@echo "  logs      - Show container logs"
	@echo "  stop      - Stop all containers"

# Build the Docker image
build:
	@echo "🔨 Building Docker image..."
	./build.sh

# Run tests in Docker
test:
	@echo "🧪 Running tests in Docker..."
	docker build --target test -t image-processing-app-test .
	docker run --rm image-processing-app-test

# Development mode
dev:
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.dev.yml --profile dev up --build

# Production mode
prod:
	@echo "🏭 Starting production environment..."
	docker-compose up --build -d

# Production with nginx
prod-nginx:
	@echo "🏭 Starting production environment with nginx..."
	docker-compose --profile nginx up --build -d

# Stop all containers
stop:
	@echo "🛑 Stopping all containers..."
	docker-compose down
	docker-compose down

# Show logs
logs:
	@echo "📋 Showing container logs..."
	docker-compose logs -f

# Production logs
logs-prod:
	@echo "📋 Showing production logs..."
	docker-compose logs -f

# Clean up Docker resources
clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

# Full clean (including images)
clean-all:
	@echo "🧹 Full cleanup including images..."
	docker-compose down -v --rmi all
	docker-compose down -v --rmi all
	docker system prune -af
	docker volume prune -f

# Check if services are running
status:
	@echo "📊 Container status:"
	docker-compose ps
	@echo "\n📊 Production container status:"
	docker-compose ps

# Run production setup script
setup-prod:
	@echo "🔧 Running production setup..."
	docker run --rm -v $(PWD):/app -w /app python:3.11-slim bash -c "pip install uv && uv run scripts/production.py"
