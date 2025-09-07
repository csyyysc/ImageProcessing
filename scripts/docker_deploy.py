#!/usr/bin/env python3
"""
Docker Production Deployment Script
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_docker_installation():
    """Check if Docker and Docker Compose are installed"""
    print("🔍 Checking Docker installation...")

    # Check Docker
    try:
        result = subprocess.run(["docker", "--version"],
                                capture_output=True, text=True, check=True)
        print(f"✅ Docker found: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker is not installed or not in PATH")
        print("Please install Docker: https://docs.docker.com/get-docker/")
        return False

    # Check Docker Compose
    try:
        result = subprocess.run(["docker", "compose", "version"],
                                capture_output=True, text=True, check=True)
        print(f"✅ Docker Compose found: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker Compose is not available")
        print("Please install Docker Compose: https://docs.docker.com/compose/install/")
        return False

    return True


def check_required_files():
    """Check if all required files exist"""
    print("🔍 Checking required files...")

    required_files = ["docker-compose.yml", "Dockerfile", "pyproject.toml"]
    missing_files = []

    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False

    print("✅ All required files found")
    return True


def create_prod_env_file():
    """Create production environment file"""
    env_content = """# Production Environment Configuration
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=8501
BACKEND_URL=http://localhost:8000
DATABASE_URL=sqlite:///./data/app.db
SECRET_KEY=your-production-secret-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=30
LOG_LEVEL=INFO
DEBUG=false
ENVIRONMENT=production

# CORS settings
CORS_ORIGINS=["http://localhost:8501", "http://localhost:3000"]

# Rate limiting
RATE_LIMIT_ENABLED=true
API_RATE_LIMIT=60
DOWNLOAD_RATE_LIMIT=500
"""

    with open(".env.prod", "w") as f:
        f.write(env_content)

    print("✅ Created .env.prod file")
    print("⚠️  Please update the SECRET_KEY in .env.prod before production use!")


def deploy_services(build_only=False, detach=True):
    """Deploy services using Docker Compose"""
    print("🔧 Building and starting services...")

    cmd = ["docker", "compose", "up"]

    if build_only:
        cmd.append("--build")
    else:
        cmd.extend(["--build", "-d"] if detach else ["--build"])

    try:
        subprocess.run(cmd, check=True)

        if not build_only:
            print("✅ Services started successfully!")
            print()
            print("🌐 Application URLs:")
            print("  Backend API:  http://localhost:8000")
            print("  Frontend:     http://localhost:8501")
            print("  API Docs:     http://localhost:8000/docs")
            print("  Health Check: http://localhost:8000/health")
            print()
            print("📊 Management Commands:")
            print("  View logs:    docker compose logs -f")
            print("  Stop services: docker compose down")
            print("  Restart:      docker compose restart")
            print("  Status:       docker compose ps")
            print()
            print("🔍 To view logs in real-time:")
            print("  docker compose logs -f backend")
            print("  docker compose logs -f frontend")

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start services: {e}")
        print("Check the logs with: docker compose logs")
        return False

    return True


def stop_services():
    """Stop all services"""
    print("🛑 Stopping services...")

    try:
        subprocess.run(["docker", "compose", "down"], check=True)
        print("✅ Services stopped successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to stop services: {e}")
        return False

    return True


def show_status():
    """Show status of services"""
    print("📊 Service Status:")

    try:
        subprocess.run(["docker", "compose", "ps"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get status: {e}")
        return False

    return True


def show_logs(service=None, follow=False):
    """Show logs for services"""
    cmd = ["docker", "compose", "logs"]

    if follow:
        cmd.append("-f")

    if service:
        cmd.append(service)

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to show logs: {e}")
        return False

    return True


def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(
        description="Docker Production Deployment")
    parser.add_argument("action", nargs="?", default="deploy",
                        choices=["deploy", "stop", "status", "logs", "build"],
                        help="Action to perform")
    parser.add_argument("--service", help="Service name for logs command")
    parser.add_argument("--follow", "-f", action="store_true",
                        help="Follow logs in real-time")
    parser.add_argument("--no-detach", action="store_true",
                        help="Don't run in detached mode")

    args = parser.parse_args()

    print("🐳 Docker Production Deployment")
    print("=" * 40)

    # Check Docker installation
    if not check_docker_installation():
        sys.exit(1)

    # Check required files
    if not check_required_files():
        sys.exit(1)

    # Create .env.prod if it doesn't exist
    if not os.path.exists(".env.prod"):
        print("📝 Creating .env.prod file...")
        create_prod_env_file()

    # Execute action
    if args.action == "deploy":
        success = deploy_services(detach=not args.no_detach)
    elif args.action == "stop":
        success = stop_services()
    elif args.action == "status":
        success = show_status()
    elif args.action == "logs":
        success = show_logs(args.service, args.follow)
    elif args.action == "build":
        success = deploy_services(build_only=True, detach=False)
    else:
        parser.print_help()
        sys.exit(1)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
