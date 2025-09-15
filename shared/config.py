"""
Shared configuration settings
"""

import os


class Settings:
    """Application settings"""

    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() == "true"

    # Frontend Configuration
    FRONTEND_HOST: str = os.getenv("FRONTEND_HOST", "0.0.0.0")
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "8501"))

    # Backend URL for frontend - prioritize environment variable
    BACKEND_URL: str = os.getenv(
        "BACKEND_URL") or f"http://localhost:{int(os.getenv('API_PORT', '8000'))}"

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # CORS Configuration
    CORS_ORIGINS: list = [
        f"http://localhost:{FRONTEND_PORT}",
        f"http://127.0.0.1:{FRONTEND_PORT}",
        "http://localhost:3000",  # For future React frontend
        "https://image-processing.csyyysc.com",  # Deployed frontend
    ]

    # Additional CORS origins from environment variable (comma-separated)
    ADDITIONAL_CORS_ORIGINS: str = os.getenv("ADDITIONAL_CORS_ORIGINS", "")

    @property
    def all_cors_origins(self) -> list:
        """Get all CORS origins including additional ones from environment"""
        origins = self.CORS_ORIGINS.copy()
        if self.ADDITIONAL_CORS_ORIGINS:
            additional_origins = [
                origin.strip() for origin in self.ADDITIONAL_CORS_ORIGINS.split(",")]
            origins.extend(additional_origins)
        return origins


class StreamlitSettings:
    """Streamlit settings"""

    PAGE_TITLE: str = "Image Processing Application"
    PAGE_ICON: str = "🚀"
    LAYOUT: str = "wide"
    INITIAL_SIDEBAR_STATE: str = "expanded"

    @classmethod
    def as_dict(cls) -> dict:
        """Return settings as a dictionary"""

        return {
            "page_title": cls.PAGE_TITLE,
            "page_icon": cls.PAGE_ICON,
            "layout": cls.LAYOUT,
            "initial_sidebar_state": cls.INITIAL_SIDEBAR_STATE,
        }


# Global settings instance
settings = Settings()
streamlit_settings = StreamlitSettings()
