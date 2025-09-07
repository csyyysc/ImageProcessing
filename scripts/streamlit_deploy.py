#!/usr/bin/env python3
"""
Streamlit deployment script for production mode
Starts both backend and frontend services optimized for Streamlit deployment
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set production environment variables
os.environ.update({
    'ENVIRONMENT': 'production',
    'LOG_LEVEL': 'INFO',
    'API_HOST': '0.0.0.0',
    'API_PORT': '8000',
    'FRONTEND_HOST': '0.0.0.0',
    'FRONTEND_PORT': '8501',
    'BACKEND_URL': 'http://localhost:8000',
    'STREAMLIT_SERVER_HEADLESS': 'true',
    'STREAMLIT_SERVER_ENABLE_CORS': 'false',
    'STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION': 'true',
    'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
    'STREAMLIT_SERVER_PORT': '8501',
    'STREAMLIT_SERVER_ADDRESS': '0.0.0.0'
})

# Global process references
backend_process = None
frontend_process = None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n🛑 Shutting down Streamlit deployment...")
    cleanup_processes()
    sys.exit(0)


def cleanup_processes():
    """Clean up running processes"""
    global backend_process, frontend_process

    if backend_process:
        print("🛑 Stopping backend...")
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()

    if frontend_process:
        print("🛑 Stopping frontend...")
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_process.kill()


def start_backend():
    """Start the FastAPI backend in production mode"""
    global backend_process

    print("🚀 Starting FastAPI backend (production mode)...")

    backend_cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--workers", "1",  # Single worker for Streamlit deployment
        "--access-log",
        "--log-level", "info"
    ]

    try:
        backend_process = subprocess.Popen(
            backend_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Monitor backend output
        for line in iter(backend_process.stdout.readline, ''):
            if line.strip():
                print(f"[BACKEND] {line.strip()}")
                if "Application startup complete" in line:
                    print("✅ Backend started successfully!")
                    break

    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

    return True


def start_frontend():
    """Start the Streamlit frontend in production mode"""
    global frontend_process

    print("🎨 Starting Streamlit frontend (production mode)...")

    frontend_cmd = [
        sys.executable, "-m", "streamlit",
        "run", "frontend/app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "true",
        "--browser.gatherUsageStats", "false",
        "--logger.level", "info"
    ]

    try:
        frontend_process = subprocess.Popen(
            frontend_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Monitor frontend output
        for line in iter(frontend_process.stdout.readline, ''):
            if line.strip():
                print(f"[FRONTEND] {line.strip()}")
                if "You can now view your Streamlit app" in line:
                    print("✅ Frontend started successfully!")
                    break

    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

    return True


def monitor_processes():
    """Monitor both processes and restart if needed"""
    global backend_process, frontend_process

    while True:
        time.sleep(10)  # Check every 10 seconds

        # Check backend
        if backend_process and backend_process.poll() is not None:
            print("⚠️  Backend process died, restarting...")
            if start_backend():
                print("✅ Backend restarted successfully")
            else:
                print("❌ Failed to restart backend")

        # Check frontend
        if frontend_process and frontend_process.poll() is not None:
            print("⚠️  Frontend process died, restarting...")
            if start_frontend():
                print("✅ Frontend restarted successfully")
            else:
                print("❌ Failed to restart frontend")


def main():
    """Main deployment function"""
    print("🚀 Starting Streamlit Deployment (Production Mode)")
    print("=" * 50)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start backend first
        if not start_backend():
            print("❌ Failed to start backend, exiting...")
            return 1

        # Wait a moment for backend to fully start
        time.sleep(3)

        # Start frontend
        if not start_frontend():
            print("❌ Failed to start frontend, exiting...")
            cleanup_processes()
            return 1

        print("\n🎉 Streamlit deployment started successfully!")
        print("=" * 50)
        print("📊 Backend API:  http://localhost:8000")
        print("📊 API Docs:     http://localhost:8000/docs")
        print("🎨 Frontend:     http://localhost:8501")
        print("=" * 50)
        print("Press Ctrl+C to stop the deployment")
        print()

        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=monitor_processes, daemon=True)
        monitor_thread.start()

        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return 1

    finally:
        cleanup_processes()
        print("✅ Streamlit deployment stopped")

    return 0


if __name__ == "__main__":
    sys.exit(main())
