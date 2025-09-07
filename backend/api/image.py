"""
Image Processing API endpoints
"""

import io
import logging
import zipfile
from typing import List
from fastapi import APIRouter, UploadFile, HTTPException, status, Query, File, Body
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer

from backend.models.image_models import ImageResponse, ImageUploadResponse, TransformRequest, TransformResponse
from backend.services.image_service import image_service
from backend.services.rate_limit_service import rate_limit_service

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


@router.get("/download/single/{image_id}")
async def download_single_image(
    image_id: int,
    user_id: int = Query(..., description="User ID for ownership verification")
):
    """Download a single image"""

    try:
        logger.info(f"Download request for image {image_id} by user {user_id}")

        allowed, info = rate_limit_service.check_download_limit(user_id)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "DOWNLOAD_LIMIT_EXCEEDED",
                    "message": info.get("message", "Daily download limit exceeded"),
                    "remaining": info.get("remaining", 0),
                    "limit": info.get("limit", 500)
                }
            )

        image = image_service.get_image_data_for_download(
            image_id, user_id)
        if not image:
            logger.warning(
                f"Image {image_id} not found or access denied for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found or access denied"
            )

        # Record download
        rate_limit_service.record_download(user_id, 1)

        # Return file as streaming response
        return StreamingResponse(
            io.BytesIO(image['data']),
            media_type=image['mime_type'],
            headers={
                "Content-Length": str(len(image['data'])),
                "Content-Disposition": f"attachment; filename={image['filename']}",
            }
        )
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during download"
        )


@router.get("/download/bulk")
async def download_bulk_images(
    user_id: int = Query(...,
                         description="User ID for ownership verification"),
    image_ids: str = Query(...,
                           description="Comma-separated list of image IDs"),
    format: str = Query(
        "zip", description="Download format: zip or individual")
):
    """Download multiple images as a ZIP file"""

    try:
        try:
            ids = [int(id.strip())
                   for id in image_ids.split(",") if id.strip()]
        except ValueError:
            raise HTTPException(
                detail="Invalid image IDs format",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not ids:
            raise HTTPException(
                detail="No image IDs provided",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if len(ids) > 100:  # Limit bulk downloads
            raise HTTPException(
                detail="Maximum 100 images per bulk download",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Check download limit
        allowed, info = rate_limit_service.check_download_limit(user_id)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "DOWNLOAD_LIMIT_EXCEEDED",
                    "message": info.get("message", "Daily download limit exceeded"),
                    "remaining": info.get("remaining", 0),
                    "limit": info.get("limit", 500)
                }
            )

        # Check if user has enough remaining downloads
        if len(ids) > info.get("remaining", 0):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "INSUFFICIENT_DOWNLOAD_QUOTA",
                    "message": f"Requested {len(ids)} images but only {info.get('remaining', 0)} downloads remaining",
                    "remaining": info.get("remaining", 0),
                    "limit": info.get("limit", 500)
                }
            )

        # Get images data
        images_data = image_service.get_bulk_images_data_for_download(
            ids, user_id)
        if not images_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No images found or access denied"
            )

        # Record download
        rate_limit_service.record_download(user_id, len(images_data))

        if format == "zip":
            # Create ZIP file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for img_data in images_data:
                    zip_file.writestr(img_data['filename'], img_data['data'])

            zip_buffer.seek(0)

            return StreamingResponse(
                io.BytesIO(zip_buffer.read()),
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename=images_{user_id}.zip",
                    "Content-Length": str(zip_buffer.tell())
                }
            )
        else:
            # Return first image (for individual format)
            if images_data:
                first_image = images_data[0]
                return StreamingResponse(
                    io.BytesIO(first_image['data']),
                    media_type=first_image['mime_type'],
                    headers={
                        "Content-Disposition": f"attachment; filename={first_image['filename']}",
                        "Content-Length": str(len(first_image['data']))
                    }
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No images found"
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk download error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during bulk download"
        )


@router.get("/download/stats")
async def get_download_stats(
    user_id: int = Query(..., description="User ID to get download stats")
):
    """Get download and rate limit statistics for a user"""
    try:
        stats = rate_limit_service.get_user_stats(user_id)
        return {
            "user_id": user_id,
            "rate_limits": stats
        }
    except Exception as e:
        logger.error(f"Error getting download stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/download/reset-limits")
async def reset_user_limits(
    user_id: int = Query(..., description="User ID to reset limits for")
):
    """Reset rate limits for a user (for testing purposes)"""
    try:
        rate_limit_service.reset_user_limits(user_id)
        logger.info(f"Reset rate limits for user {user_id}")
        return {
            "message": f"Rate limits reset for user {user_id}",
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error resetting user limits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
