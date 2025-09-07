
"""
User authentication API endpoints
"""
import logging
from fastapi import status, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer

from backend.services.auth_service import auth_service
from backend.middleware.auth_middleware import get_current_user
from backend.models.user_models import UserCreate, UserResponse, UserLogin, AuthResponse

security = HTTPBearer()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Register a new user with user-friendly error handling"""
    try:

        new_user = auth_service.create_user(
            username=user_data.username,
            password=user_data.password,
            email=user_data.email
        )

        user_response = auth_service.user_to_response(new_user)
        access_token = auth_service.generate_secure_token(
            new_user['id'], new_user['username'])

        return AuthResponse(
            success=True,
            message="Account created successfully! Welcome aboard!",
            user=user_response,
            access_token=access_token
        )

    except ValueError as e:

        error_msg = str(e)

        if "Username already exists" in error_msg:
            user_message = "This username is already taken. Please choose a different one."
        elif "Email already registered" in error_msg:
            user_message = "This email is already registered. Please use a different email or try logging in."
        else:
            user_message = f"Registration failed: {error_msg}"

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": user_message
            }
        )

    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Something went wrong. Please try again later."
            }
        )


@router.post("/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin):
    """Login with JWT authentication"""

    try:
        user, message = auth_service.authenticate_user(
            username=login_data.username,
            password=login_data.password
        )

        if not user:
            if "temporarily locked" in message:
                user_message = "Account temporarily locked due to multiple failed login attempts. Please try again in a few minutes."
            elif "disabled" in message:
                user_message = "Your account has been disabled. Please contact support."
            else:
                user_message = "Invalid username or password. Please check your credentials and try again."

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "message": user_message
                }
            )

        user_response = auth_service.user_to_response(user)
        access_token = auth_service.generate_secure_token(
            user['id'], user['username'])

        logger.info(f"User logged in: {login_data.username}")
        return AuthResponse(
            success=True,
            message=f"Welcome back, {user['username']}!",
            user=user_response,
            access_token=access_token
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Something went wrong during login. Please try again later."
            }
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(current_user: UserResponse = Depends(get_current_user)):
    """Refresh JWT token"""

    try:
        new_token = auth_service.generate_secure_token(
            current_user.id, current_user.username)

        return AuthResponse(
            success=True,
            message="Token refreshed successfully",
            user=current_user,
            access_token=new_token
        )

    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Failed to refresh token. Please login again."
            }
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information"""

    return current_user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get a specific user by ID"""
    try:
        user = auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                detail="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        return auth_service.user_to_response(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(
            detail="Internal server error while fetching user",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Soft delete user (deactivate account)"""
    try:
        success = auth_service.delete_user(user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return {"message": "User deactivated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            detail="Internal server error while deleting user",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
