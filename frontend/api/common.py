import httpx
import logging

logger = logging.getLogger(__name__)


class BaseAPI:
    """Base API client"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        logger.info(f"Initializing API client with base_url: {base_url}")

        # Configure httpx client with SSL verification handling
        self.client = httpx.Client(
            timeout=30.0,
            verify=True,  # Keep SSL verification enabled for security
            follow_redirects=True
        )

    def health_check(self) -> bool:
        """Check if the API is healthy"""

        try:
            response = self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
