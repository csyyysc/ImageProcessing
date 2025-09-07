import logging
from typing import Dict, Optional

from frontend.api.common import BaseAPI


logger = logging.getLogger(__name__)


class ImageAPI(BaseAPI):
    """API client for image processing"""

    def __init__(self, base_url: str):
        super().__init__(base_url)

    def get_total_images(self, user_id: int) -> Optional[int]:
        """Get total number of images of a user"""

        try:
            response = self.client.get(
                f"{self.base_url}/api/images/total?user_id={user_id}")
            if response.status_code == 200:
                result = response.json()
                return result.get('total', 0)
            else:
                logger.error(
                    f"Failed to get total images: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Failed to get total images: {e}")
            return None

    def get_images(self, user_id: int, page: int, limit: int) -> Optional[list]:
        """Get all images of a user"""

        try:
            response = self.client.get(
                f"{self.base_url}/api/images/?user_id={user_id}&page={page}&limit={limit}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get images: {e}")
            return None

    def upload_image(self, file_data: bytes, filename: str, user_id: int) -> Optional[Dict]:
        """Upload an image file"""

        try:
            files = {
                'image': (filename, file_data, 'image/jpeg')
            }
            params = {'user_id': user_id}

            response = self.client.post(
                f"{self.base_url}/api/images/upload",
                files=files,
                params=params
            )

            if response.status_code == 200:
                result = response.json()
                return result
            else:
                logger.error(
                    f"Upload failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "message": f"Upload failed: {response.status_code}"
                }

        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            return {
                "success": False,
                "message": f"Upload error: {str(e)}"
            }

    def delete_image(self, image_id: int, user_id: int) -> bool:
        """Delete an image"""

        try:
            response = self.client.delete(
                f"{self.base_url}/api/images/{image_id}?user_id={user_id}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to delete image: {e}")
            return False

    def transform_image(self, image_id: int, user_id: int, transform_params: Dict) -> Optional[Dict]:
        """Transform an image with specified parameters"""

        try:
            response = self.client.post(
                f"{self.base_url}/api/images/{image_id}/transform?user_id={user_id}",
                json=transform_params
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(
                    f"Transform failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "message": f"Transform failed: {response.status_code}"
                }

        except Exception as e:
            logger.error(f"Failed to transform image: {e}")
            return {
                "success": False,
                "message": f"Transform error: {str(e)}"
            }

    def download_single_image(self, image_id: int, user_id: int) -> Optional[bytes]:
        """Download a single image"""

        try:
            response = self.client.get(
                f"{self.base_url}/api/images/download/single/{image_id}?user_id={user_id}"
            )

            if response.status_code == 200:
                return response.content
            elif response.status_code == 429:
                # Rate limit exceeded
                error_data = response.json()
                raise Exception(
                    f"Download limit exceeded: {error_data.get('message', 'Daily download limit exceeded')}")
            else:
                logger.error(
                    f"Download failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            raise e

    def download_bulk_images(self, image_ids: list, user_id: int, format: str = "zip") -> Optional[bytes]:
        """Download multiple images as ZIP"""

        try:
            ids_str = ",".join(map(str, image_ids))
            response = self.client.get(
                f"{self.base_url}/api/images/download/bulk?user_id={user_id}&image_ids={ids_str}&format={format}"
            )

            if response.status_code == 200:
                return response.content
            elif response.status_code == 429:
                # Rate limit exceeded
                error_data = response.json()
                raise Exception(
                    f"Download limit exceeded: {error_data.get('message', 'Daily download limit exceeded')}")
            else:
                logger.error(
                    f"Bulk download failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Failed to download bulk images: {e}")
            raise e

    def get_download_stats(self, user_id: int) -> Optional[dict]:
        """Get download and rate limit statistics"""
        try:
            response = self.client.get(
                f"{self.base_url}/api/images/download/stats?user_id={user_id}"
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(
                    f"Failed to get download stats: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Failed to get download stats: {e}")
            return None

    def reset_user_limits(self, user_id: int) -> bool:
        """Reset rate limits for a user (for testing purposes)"""
        try:
            response = self.client.post(
                f"{self.base_url}/api/images/download/reset-limits?user_id={user_id}"
            )
            if response.status_code == 200:
                logger.info(f"Reset rate limits for user {user_id}")
                return True
            else:
                logger.error(
                    f"Failed to reset user limits: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error resetting user limits: {e}")
            return False
