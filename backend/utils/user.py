"""
User service utilities with database support
"""
import logging
from typing import Dict, Optional
from backend.database import user_repo
from backend.utils.encrypt import hash_password, verify_password
from backend.models.user_models import UserResponse

logger = logging.getLogger(__name__)


class UserService:
    """User business logic service"""

    def __init__(self):
        self.user_repo = user_repo

    def create_user(self, username: str, password: str, email: Optional[str] = None) -> Dict:
        """Create a new user with password hashing"""

        username = username.lower().strip()
        if self.user_repo.user_exists(username):
            raise ValueError("Username already exists")

        password_hash = hash_password(password)

        user = self.user_repo.create_user(username, email, password_hash)
        logger.info(f"User created: {username}")

        return user

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with username and password"""
        username = username.lower().strip()
        user = self.user_repo.get_user_by_username(username)

        if not user:
            return None

        if not verify_password(password, user['password_hash']):
            return None

        if not user['is_active']:
            return None

        logger.info(f"User authenticated: {username}")
        return user

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return self.user_repo.get_user_by_username(username)

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        return self.user_repo.get_user_by_id(user_id)

    def user_to_response(self, user: Dict) -> UserResponse:
        """Convert database user to response model (without password)"""

        return UserResponse(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            is_active=bool(user['is_active']),
            created_at=user['created_at']
        )

    def update_user(self, user_id: int, **kwargs) -> Optional[Dict]:
        """Update user fields"""

        if 'password' in kwargs:
            kwargs['password_hash'] = hash_password(kwargs.pop('password'))

        return self.user_repo.update_user(user_id, **kwargs)

    def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        return self.user_repo.delete_user(user_id)


# Global user service instance
user_service = UserService()
