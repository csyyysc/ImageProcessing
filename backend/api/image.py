"""
Image Processing API endpoints
"""

import logging
from typing import List
from fastapi import APIRouter, UploadFile, HTTPException, status, Query, File, Body
from fastapi.security import HTTPBearer

from backend.models.image_models import ImageResponse, ImageUploadResponse, TransformRequest, TransformResponse
from backend.services.image_service import image_service

security = HTTPBearer()
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/images", tags=["images"])


@router.get("/", response_model=List[ImageResponse])
async def get_images(
    user_id: int = Query(..., description="User ID to filter images"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(
        10, ge=1, le=100, description="Number of images per page")
):
    try:
        return image_service.get_images(user_id, page, limit)
    except Exception:
        raise HTTPException(
            detail=f"Failed to retrieve images for user {user_id}, please try again.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/total")
async def get_total_images(
    user_id: int = Query(..., description="User ID to get total image count")
):

    try:
        total_count = image_service.get_user_image_count(user_id)
        return {"total": total_count}
    except Exception as e:
        logger.error(f"Failed to get total images for user {user_id}: {e}")
        raise HTTPException(
            detail=f"Failed to get total image count for user {user_id}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: int,
    user_id: int = Query(..., description="User ID for ownership verification")
):
    try:
        return image_service.get_image_by_id(image_id, user_id)
    except Exception:
        raise HTTPException(
            detail=f"Failed to retrieve image {image_id}, please try again.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    user_id: int = Query(..., description="User ID who owns the image"),
    image: UploadFile = File(..., description="Image file to upload")
):

    try:
        result = await image_service.upload_image(image, user_id)

        if not result.success:
            raise HTTPException(
                detail=result.message or "Failed to upload image, please try again.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        return result
    except Exception:
        raise HTTPException(
            detail="Internal server error during upload, please try again.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    user_id: int = Query(..., description="User ID for ownership verification")
):

    try:
        return image_service.delete_image(image_id, user_id)
    except Exception:
        raise HTTPException(
            detail=f"Failed to delete image {image_id}, please try again.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/{image_id}/transform", response_model=TransformResponse)
async def transform_image(
    image_id: int,
    user_id: int = Query(...,
                         description="User ID for ownership verification"),
    transform_request: TransformRequest = Body(
        ..., description="Transformation parameters")
):
    """Transform an image with the specified operations"""

    try:
        result = image_service.transform_image(
            image_id, user_id, transform_request)

        if not result.success:
            raise HTTPException(
                detail=result.message,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transform API error: {e}")
        raise HTTPException(
            detail="Internal server error during transformation",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
