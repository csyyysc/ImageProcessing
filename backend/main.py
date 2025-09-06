"""
Image Processing Backend Server
"""
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from shared.config import settings
from shared.models.common import HealthCheck
from backend.api.user import router as user_router
from backend.api.image import router as image_router
from backend.database import db_manager  # Initialize database on import
from backend.utils.error_handler import validation_exception_handler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting Image Processing Backend...")

    # Create uploads directory if it doesn't exist
    from pathlib import Path
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    logger.info(f"Uploads directory ready: {uploads_dir.absolute()}")

    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down Image Processing Backend...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Image Processing Backend",
    description="API for Image Processing Application",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for image serving
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(user_router)
app.include_router(image_router)

# Register global error handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Image Procressing Backend API"}


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return HealthCheck(status="healthy", service="Image Procressing Backend")


def start_backend():
    """Entry point for backend server"""

    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    start_backend()
