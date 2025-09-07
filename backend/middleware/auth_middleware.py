"""
JWT Authentication middleware and dependencies
"""
import logging
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.services.auth_service import auth_service
from backend.models.user_models import UserResponse

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Get current authenticated user from JWT token"""

    try:
        token = credentials.credentials

        user = auth_service.get_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.get('is_active', False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return auth_service.user_to_response(user)

    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Get current active user (alias for get_current_user)"""

    return current_user


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[UserResponse]:
    """Get current user if authenticated, otherwise return None"""

    if not credentials:
        return None

    try:
        token = credentials.credentials
        user = auth_service.get_user_from_token(token)
        if user and user.get('is_active', False):
            return auth_service.user_to_response(user)
    except Exception as e:
        logger.warning(f"Optional authentication failed: {e}")

    return None


def require_permissions(*permissions: str):
    """Decorator to require specific permissions (placeholder for future role-based access)"""

    def permission_checker(current_user: UserResponse = Depends(get_current_user)):
        # For now, just check if user is authenticated
        # In the future, implement role-based permissions
        if not current_user.is_active:
            raise HTTPException(
                detail="Insufficient permissions",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return current_user
    return permission_checker


class AuthDependency:
    """Authentication dependency class for different auth levels"""

    @staticmethod
    def required():
        """Require authentication"""

        return Depends(get_current_user)

    @staticmethod
    def optional():
        """Optional authentication"""

        return Depends(get_optional_user)

    @staticmethod
    def active():
        """Require active user"""

        return Depends(get_current_active_user)
