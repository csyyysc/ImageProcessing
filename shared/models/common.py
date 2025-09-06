from typing import Optional
from pydantic import BaseModel


class HealthCheck(BaseModel):
    """Health check response model"""
    status: str
    service: str


class APIResponse(BaseModel):
    """Generic API response model"""
    success: bool
    message: str
    data: Optional[dict] = None
