"""
Image data models
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ImageBase(BaseModel):
    """Base Image model"""

    filename: str
    original_name: str
    file_size: int
    mime_type: str


class ImageCreate(ImageBase):
    """Model for creating a new image"""

    user_id: int
    file_path: str


class ImageResponse(BaseModel):
    """Image response model"""

    id: int
    user_id: int
    filename: str
    original_name: str
    file_path: str
    file_size: int
    mime_type: str
    created_at: datetime
    url: Optional[str] = None  # Will be populated with the accessible URL

    class Config:
        from_attributes = True


class ImageUploadResponse(BaseModel):
    """Response for image upload"""

    success: bool
    message: str
    image: Optional[ImageResponse] = None


class TransformRequest(BaseModel):
    """Request model for image transformations"""

    # Basic operations
    resize: Optional[Dict[str, int]] = None  # {'width': int, 'height': int}
    # {'x': int, 'y': int, 'width': int, 'height': int}
    crop: Optional[Dict[str, int]] = None
    rotate: Optional[Dict[str, int]] = None  # {'angle': int}
    flip: Optional[bool] = None              # True for vertical flip
    mirror: Optional[bool] = None            # True for horizontal mirror

    # Advanced operations
    # {'text': str, 'x': int, 'y': int}
    watermark: Optional[Dict[str, Any]] = None
    compress: Optional[Dict[str, int]] = None   # {'quality': int}
    format: Optional[Dict[str, str]] = None     # {'type': str}
    filter: Optional[Dict[str, str]] = None     # {'type': str}


class TransformResponse(BaseModel):
    """Response for image transformation"""

    success: bool
    message: str
    original_image: Optional[ImageResponse] = None
    transformed_image: Optional[ImageResponse] = None
