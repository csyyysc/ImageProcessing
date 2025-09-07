#!/usr/bin/env python3
"""
Production Script for Image Processing Application

This script provides production deployment utilities and configurations.
Run with: uv run scripts/production.py
"""

import sys
import subprocess
import os
from pathlib import Path

from shared.config import settings

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def load_env_file():
    """Load environment variables from .env file"""

    env_file = project_root / ".env.prod"
    if env_file.exists():
        print(f"📄 Loading environment variables from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ Environment variables loaded from .env file")
    else:
        print("⚠️  No .env file found, using default configuration")
        print("💡 Create a .env file from .env.example for custom configuration")


# Load environment variables
load_env_file()


def check_production_requirements():
    """Check if production requirements are met"""

    print("🔍 Checking production requirements...")

    requirements = []

    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 10):
        print("✅ Python version: {}.{}.{}".format(*python_version[:3]))
    else:
        print(
            f"❌ Python version {python_version.major}.{python_version.minor} is too old. Need 3.10+")
        requirements.append("Python 3.10+")

    # Check if uv is available
    try:
        result = subprocess.run(["uv", "--version"],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv package manager: {result.stdout.strip()}")
        else:
            print("❌ uv package manager not found")
            requirements.append("uv package manager")
    except FileNotFoundError:
        print("❌ uv package manager not found")
        requirements.append("uv package manager")

    # Check if uploads directory exists
    uploads_dir = project_root / "uploads"
    if uploads_dir.exists():
        print("✅ Uploads directory exists")
    else:
        print("⚠️  Uploads directory not found, creating...")
        uploads_dir.mkdir(exist_ok=True)
        print("✅ Uploads directory created")

    # Check database file
    db_file = project_root / "data" / "app.db"
    if db_file.exists():
        print("✅ Database file exists")
    else:
        print("⚠️  Database file not found, will be created on first run")

    return len(requirements) == 0, requirements


def run_system_tests():
    """Run the test script to validate the system"""
    print("\n🧪 Running system tests...")

    try:
        # Run the test script
        result = subprocess.run(
            [sys.executable, "scripts/test.py"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )

        if result.returncode == 0:
            print("✅ All system tests passed!")
            print("Test output:")
            print(result.stdout)
            return True
        else:
            print("❌ System tests failed!")
            print("Test output:")
            print(result.stdout)
            print("Test errors:")
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("❌ System tests timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running system tests: {e}")
        return False


def setup_production_environment():
    """Set up production environment variables"""
    print("\n🔧 Current production environment configuration...")

    # Get current settings from config
    current_config = {
        "API_HOST": settings.API_HOST,
        "API_PORT": settings.API_PORT,
        "FRONTEND_HOST": settings.FRONTEND_HOST,
        "FRONTEND_PORT": settings.FRONTEND_PORT,
        "BACKEND_URL": settings.BACKEND_URL,
        "LOG_LEVEL": settings.LOG_LEVEL
    }

    print("Current configuration:")
    for key, value in current_config.items():
        print(f"  {key}={value}")

    # Check for production-specific environment variables
    production_vars = {
        "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite:///./data/app.db"),
        "SECRET_KEY": os.getenv("SECRET_KEY", "your-production-secret-key-change-this"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    }

    print("\nProduction-specific variables:")
    for key, value in production_vars.items():
        print(f"  {key}={value}")

    print("\n💡 To customize for production, set these environment variables:")
    for key, value in production_vars.items():
        print(f"export {key}='{value}'")

    return {**current_config, **production_vars}


def create_production_directories():
    """Create necessary production directories"""
    print("\n📁 Creating production directories...")

    directories = [
        "data",
        "logs",
        "uploads",
    ]

    for dir_name in directories:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Created directory: {dir_name}")
        else:
            print(f"✅ Directory exists: {dir_name}")


def generate_production_commands():
    """Generate production startup commands"""

    print("\n🚀 Production startup commands:")
    print("=" * 40)

    print("\n1. Development mode (with auto-reload):")
    print("   uv run main.py dev")

    print(f"\n2. Production mode (backend only):")
    print(
        f"   uv run uvicorn backend.main:app --host {settings.API_HOST} --port {settings.API_PORT}")

    print(f"\n3. Production mode (frontend only):")
    print(
        f"   uv run streamlit run frontend/app.py --server.port {settings.FRONTEND_PORT} --server.address {settings.FRONTEND_HOST}")

    print(f"\n4. Using Gunicorn (recommended for production):")
    print(
        f"   uv run gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind {settings.API_HOST}:{settings.API_PORT}")

    print(f"\n5. With nginx reverse proxy:")
    print(
        f"   # Configure nginx to proxy to {settings.API_HOST}:{settings.API_PORT} and {settings.FRONTEND_HOST}:{settings.FRONTEND_PORT}")

    print(f"\n6. Docker deployment:")
    print("   make build          # Build Docker image")
    print("   make test           # Run tests in Docker")
    print("   make dev            # Development with Docker")
    print("   make prod           # Production with Docker")
    print("   make prod-nginx     # Production with nginx")

    print(f"\n7. Docker Compose commands:")
    print("   docker-compose up --build                    # Development")
    print("   docker-compose -f docker-compose.prod.yml up --build -d  # Production")


def show_production_tips():
    """Show production deployment tips"""
    print("\n💡 Production Deployment Tips:")
    print("=" * 35)

    tips = [
        "Use a production database (PostgreSQL, MySQL) instead of SQLite",
        "Set up proper SSL/TLS certificates for HTTPS",
        "Configure nginx as a reverse proxy",
        "Use environment variables for sensitive configuration",
        "Set up proper logging and monitoring",
        "Implement proper backup strategies for uploaded images",
        "Use a process manager like systemd or supervisor",
        "Set up firewall rules to restrict access",
        "Regular security updates and dependency management",
        "Monitor disk space for uploaded images",
        "Implement rate limiting for API endpoints",
        "Use proper JWT tokens instead of basic token system",
        "Use Docker for consistent deployment across environments",
        "Run 'make prod' for production Docker deployment",
        "Use 'make prod-nginx' for production with nginx reverse proxy",
        "Monitor container health and resource usage",
        "Set up container orchestration (Docker Swarm/Kubernetes) for scaling"
    ]

    for i, tip in enumerate(tips, 1):
        print(f"{i:2d}. {tip}")


def main():
    """Main production setup function"""
    print("🏭 Image Processing Application - Production Setup")
    print("=" * 55)

    # Check requirements
    requirements_met, missing = check_production_requirements()

    if not requirements_met:
        print(f"\n❌ Missing requirements: {', '.join(missing)}")
        print("Please install missing requirements before proceeding.")
        sys.exit(1)

    # Set up environment
    setup_production_environment()

    # Run system tests to validate everything is working
    print("\n" + "="*50)
    print("🔍 PRE-PRODUCTION VALIDATION")
    print("="*50)

    tests_passed = run_system_tests()

    # Create directories
    create_production_directories()

    if not tests_passed:
        print("\n❌ System tests failed! Cannot proceed to production mode.")
        print("Please fix the issues and run the tests again.")
        print("\n💡 To run tests manually:")
        print("  uv run scripts/test.py")
        sys.exit(1)

    print("\n" + "="*50)
    print("✅ PRODUCTION READY")
    print("="*50)

    # Show commands
    generate_production_commands()

    # Show tips
    show_production_tips()

    print("\n✅ Production setup complete!")
    print("\n🔗 Service URLs:")
    print(
        f"  - API Documentation: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(
        f"  - Frontend Application: http://{settings.FRONTEND_HOST}:{settings.FRONTEND_PORT}")
    print(
        f"  - Health Check: http://{settings.API_HOST}:{settings.API_PORT}/health")
    print(f"  - Backend API: {settings.BACKEND_URL}")


if __name__ == "__main__":
    main()
