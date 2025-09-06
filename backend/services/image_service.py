"""
Image Processing Service Implementations
"""

import logging
from typing import List
from fastapi import UploadFile, HTTPException, status

from backend.database import image_repo
from backend.models.image_models import ImageResponse, ImageUploadResponse, TransformRequest, TransformResponse
from backend.utils.image import transform_image
from backend.utils.file_handler import save_uploaded_file, get_file_url

logger = logging.getLogger(__name__)


class ImageService:
    """Image Processing Services
    1. CRUD operations for images
    2. Transformation operations for images
    """

    def __init__(self):
        self.image_repo = image_repo

    def db_to_response(self, image_data: dict) -> ImageResponse:
        """Convert database record to response model"""

        return ImageResponse(
            id=image_data['id'],
            url=get_file_url(image_data['filename']),
            user_id=image_data['user_id'],
            filename=image_data['filename'],
            original_name=image_data['original_name'],
            file_path=image_data['file_path'],
            file_size=image_data['file_size'],
            mime_type=image_data['mime_type'],
            created_at=image_data['created_at']
        )

    def get_user_image_count(self, user_id: int) -> int:
        """Get total number of images for a user"""

        return self.image_repo.get_user_image_count(user_id)

    def get_images(self, user_id: int, page: int = 1, limit: int = 10) -> List[ImageResponse]:
        """Get images for a user with pagination"""

        try:
            images_data = self.image_repo.get_images_by_user(
                user_id, page, limit)
            images = [self.db_to_response(img) for img in images_data]
            return images
        except Exception as e:
            logger.error(
                f"Failed to retrieve images for user {user_id}: {str(e)}")
            raise ValueError(
                f"Failed to retrieve images for user, please try again.")

    async def upload_image(self, file: UploadFile, user_id: int) -> ImageUploadResponse:
        """Upload and store an image specified to a user, and store it in both the database and the filesystem"""

        try:
            file_info = await save_uploaded_file(file, user_id)

            image_data = self.image_repo.create_image(
                user_id=user_id,
                filename=file_info['filename'],
                original_name=file_info['original_name'],
                file_path=file_info['file_path'],
                file_size=file_info['file_size'],
                mime_type=file_info['mime_type']
            )

            image_response = self.db_to_response(image_data)

            logger.info(
                f"Image uploaded successfully: {file_info['filename']}")

            return ImageUploadResponse(
                success=True,
                message="Image uploaded successfully!",
                image=image_response
            )

        except ValueError as e:
            logger.warning(f"Image upload validation error: {e}")
            return ImageUploadResponse(
                success=False,
                message=str(e),
                image=None
            )
        except Exception as e:
            logger.error(f"Image upload error: {e}")
            return ImageUploadResponse(
                success=False,
                message="Failed to upload image. Please try again.",
                image=None
            )

    def get_image_by_id(self, image_id: int, user_id: int) -> ImageResponse:
        """Get a specific image by ID (with user ownership check)"""

        image_data = self.image_repo.get_image_by_id(image_id)

        if not image_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )

        if image_data['user_id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return self.db_to_response(image_data)

    def delete_image(self, image_id: int, user_id: int) -> bool:
        """Delete an image specified to a user, and delete it from the filesystem"""

        image_data = self.image_repo.get_image_by_id(image_id)

        if not image_data or image_data['user_id'] != user_id:
            raise HTTPException(
                detail="Access denied",
                status_code=status.HTTP_403_FORBIDDEN
            )

        deleted = self.image_repo.delete_image(image_id, user_id)

        if deleted:
            from backend.utils.file_handler import delete_file

            delete_file(image_data['file_path'])
            logger.info(f"Image deleted: {image_id}")

        return deleted

    def transform_image(self, image_id: int, user_id: int, transform_request: TransformRequest) -> TransformResponse:
        """Transform an image and save the result"""

        try:
            image_data = self.image_repo.get_image_by_id(image_id)

            if not image_data:
                raise HTTPException(
                    detail="Image not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            if image_data['user_id'] != user_id:
                raise HTTPException(
                    detail="Access denied",
                    status_code=status.HTTP_403_FORBIDDEN
                )

            transform_dict = {}

            if transform_request.resize:
                transform_dict['resize'] = transform_request.resize
            if transform_request.crop:
                transform_dict['crop'] = transform_request.crop
            if transform_request.rotate:
                transform_dict['rotate'] = transform_request.rotate
            if transform_request.flip:
                transform_dict['flip'] = transform_request.flip
            if transform_request.mirror:
                transform_dict['mirror'] = transform_request.mirror
            if transform_request.watermark:
                transform_dict['watermark'] = transform_request.watermark
            if transform_request.compress:
                transform_dict['compress'] = transform_request.compress
            if transform_request.format:
                transform_dict['format'] = transform_request.format
            if transform_request.filter:
                transform_dict['filter'] = transform_request.filter

            logger.info(
                f"Applying transformations to image {image_id}: {list(transform_dict.keys())}")

            transformed_file_info = transform_image(
                image_data['file_path'], transform_dict)

            transformed_image_data = self.image_repo.create_image(
                user_id=user_id,
                filename=transformed_file_info['filename'],
                original_name=transformed_file_info['original_name'],
                file_path=transformed_file_info['file_path'],
                file_size=transformed_file_info['file_size'],
                mime_type=transformed_file_info['mime_type']
            )

            original_response = self.db_to_response(image_data)
            transformed_response = self.db_to_response(transformed_image_data)

            logger.info(
                f"Image transformation successful: {transformed_file_info['filename']}")

            return TransformResponse(
                success=True,
                message="Image transformed successfully!",
                original_image=original_response,
                transformed_image=transformed_response
            )
        except ValueError as e:
            logger.warning(f"Image transformation validation error: {e}")
            return TransformResponse(
                success=False,
                message=str(e),
                original_image=None,
                transformed_image=None
            )
        except Exception as e:
            logger.error(f"Image transformation error: {e}")
            return TransformResponse(
                success=False,
                message="Failed to transform image. Please try again.",
                original_image=None,
                transformed_image=None
            )


# Global service instance
image_service = ImageService()
