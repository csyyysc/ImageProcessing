#!/usr/bin/env python3
"""
Script to start the FastAPI backend server
"""
import uvicorn
from shared.config import settings


def main():
    """Start the backend server"""
    print("🚀 Starting FastAPI Backend...")
    print(f"   Server: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"   Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"   Reload: {settings.API_RELOAD}")
    print()

    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
