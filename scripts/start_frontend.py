#!/usr/bin/env python3
"""
Script to start the Streamlit frontend
"""

import sys
import subprocess
from shared.config import settings


def main():
    """Start the frontend server"""
    print("🎨 Starting Streamlit Frontend...")
    print(
        f"   Server: http://{settings.FRONTEND_HOST}:{settings.FRONTEND_PORT}")
    print(f"   Backend: {settings.BACKEND_URL}")
    print()

    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "frontend/app.py",
        f"--server.port={settings.FRONTEND_PORT}",
        f"--server.address={settings.FRONTEND_HOST}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ])


if __name__ == "__main__":
    main()
