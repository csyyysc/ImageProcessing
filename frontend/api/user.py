
import logging
from typing import Dict, Optional

from frontend.api.common import BaseAPI

logger = logging.getLogger(__name__)


class UserAPI(BaseAPI):
    """API client for user management"""

    def __init__(self, base_url: str):
        super().__init__(base_url)

    def register(self, username: str, password: str, email: str = None) -> Optional[Dict]:
        """Register a new user"""

        try:
            user_data = {
                "username": username,
                "password": password,
                "email": email
            }
            response = self.client.post(
                f"{self.base_url}/api/auth/register", json=user_data)

            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            else:
                logger.error(
                    f"Registration failed: {response.status_code} - {response.text}")
                try:
                    error_data = response.json()

                    if isinstance(error_data, dict):
                        if "message" in error_data:
                            return {"success": False, "message": error_data["message"]}
                        elif "detail" in error_data:
                            detail = error_data["detail"]
                            if isinstance(detail, dict) and "message" in detail:
                                return {"success": False, "message": detail["message"]}
                            else:
                                return {"success": False, "message": str(detail)}
                    return {"success": False, "message": "Registration failed. Please check your input."}
                except:
                    return {"success": False, "message": "Registration failed. Please try again."}
        except Exception as e:
            logger.error(f"Failed to register user: {e}")
            return {"success": False, "message": "Connection error. Please try again."}

    def login(self, username: str, password: str) -> Optional[Dict]:
        """Login a user"""
        try:
            user_data = {
                "username": username,
                "password": password
            }
            response = self.client.post(
                f"{self.base_url}/api/auth/login", json=user_data)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(
                    f"Login failed: {response.status_code} - {response.text}")
                try:
                    error_data = response.json()
                    # Handle both new format and old format
                    if isinstance(error_data, dict):
                        if "message" in error_data:
                            return {"success": False, "message": error_data["message"]}
                        elif "detail" in error_data:
                            detail = error_data["detail"]
                            if isinstance(detail, dict) and "message" in detail:
                                return {"success": False, "message": detail["message"]}
                            else:
                                return {"success": False, "message": str(detail)}
                    return {"success": False, "message": "Login failed. Please check your credentials."}
                except:
                    return {"success": False, "message": "Login failed. Please try again."}
        except Exception as e:
            logger.error(f"Failed to login user: {e}")
            return {"success": False, "message": "Connection error. Please try again."}

    def get_all_users(self) -> Optional[Dict]:
        """Get all users (for testing)"""
        try:
            response = self.client.get(f"{self.base_url}/api/auth/users")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return None

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get a specific user by ID"""
        try:
            response = self.client.get(
                f"{self.base_url}/api/auth/users/{user_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None
