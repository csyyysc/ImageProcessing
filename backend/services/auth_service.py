"""
Authentication service with better security and features
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
from backend.database import user_repo
from backend.services.jwt_service import jwt_service
from backend.models.user_models import UserResponse

logger = logging.getLogger(__name__)


class AuthService:
    """User Authentication service"""

    def __init__(self):
        self.user_repo = user_repo
        self.max_attempts = 5
        self.failed_attempts = {}  # In production, use Redis
        self.lockout_duration = 300  # 5 minutes

    def create_user(self, username: str, password: str, email: Optional[str] = None) -> Dict:
        """Create a new user with validation"""

        # Normalization
        username = username.lower().strip()

        if self.user_repo.user_exists(username):
            raise ValueError("Username already exists")

        if email and self.user_repo.get_user_by_email(email):
            raise ValueError("Email already registered")

        # Hash the password with bcrypt
        password_hash = jwt_service.hash_password(password)

        # Create user in database
        user = self.user_repo.create_user(username, email, password_hash)
        logger.info(f"User created: {username}")

        return user

    def authenticate_user(self, username: str, password: str) -> Tuple[Optional[Dict], str]:
        """Authenticate user with rate limiting"""

        username = username.lower().strip()

        # Check for rate limiting
        if self._is_account_locked(username):
            return None, "Account temporarily locked due to too many failed attempts"

        user = self.user_repo.get_user_by_username(username)

        if not user:
            self._record_failed_attempt(username)
            return None, "Invalid username or password"

        try:
            if not jwt_service.verify_password(password, user['password_hash']):
                self._record_failed_attempt(username)
                return None, "Invalid username or password"
        except Exception as e:
            # Handle cases where password hash is corrupted or uses unsupported format
            logger.warning(
                f"Password verification failed for user {username}: {e}")
            self._record_failed_attempt(username)
            return None, "Invalid username or password"

        if not user['is_active']:
            return None, "Account is disabled"

        # Clear failed attempts on successful login
        self._clear_failed_attempts(username)

        # Update last login
        self.user_repo.update_user(
            user['id'], last_login=datetime.now(timezone.utc))

        logger.info(f"User authenticated: {username}")
        return user, "Login successful"

    def _is_account_locked(self, username: str) -> bool:
        """Check if account is temporarily locked"""
        if username not in self.failed_attempts:
            return False

        attempts, last_attempt = self.failed_attempts[username]

        # Check if lockout period has expired
        if datetime.now(timezone.utc) - last_attempt > timedelta(seconds=self.lockout_duration):
            del self.failed_attempts[username]
            return False

        return attempts >= self.max_attempts

    def _record_failed_attempt(self, username: str):
        """Record a failed login attempt"""

        now = datetime.now(timezone.utc)
        if username in self.failed_attempts:
            attempts, _ = self.failed_attempts[username]
            self.failed_attempts[username] = (attempts + 1, now)
        else:
            self.failed_attempts[username] = (1, now)

        attempts, _ = self.failed_attempts[username]
        logger.warning(
            f"Failed login attempt for {username} (attempt {attempts})")

    def _clear_failed_attempts(self, username: str):
        """Clear failed attempts for successful login"""
        if username in self.failed_attempts:
            del self.failed_attempts[username]

    def generate_secure_token(self, user_id: int, username: str = None) -> str:
        """Generate a JWT access token"""

        if not username:
            user = self.get_user_by_id(user_id)
            username = user['username'] if user else 'unknown'

        return jwt_service.create_token_for_user(user_id, username)

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return self.user_repo.get_user_by_username(username.lower().strip())

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""

        return self.user_repo.get_user_by_id(user_id)

    def user_to_response(self, user: Dict) -> UserResponse:
        """Convert database user to response model"""

        return UserResponse(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            is_active=bool(user['is_active']),
            created_at=user['created_at'],
            last_login=user.get('last_login')
        )

    def update_user(self, user_id: int, **kwargs) -> Optional[Dict]:
        """Update user with validation"""

        if 'password' in kwargs:
            kwargs['password_hash'] = jwt_service.hash_password(
                kwargs.pop('password'))

        return self.user_repo.update_user(user_id, **kwargs)

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password with current password verification"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        # Verify current password
        if not jwt_service.verify_password(current_password, user['password_hash']):
            return False

        # Update with new password
        new_hash = jwt_service.hash_password(new_password)
        self.user_repo.update_user(user_id, password_hash=new_hash)

        logger.info(f"Password changed for user {user['username']}")
        return True

    def delete_user(self, user_id: int) -> bool:
        """Soft delete user (deactivate)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        # Soft delete by deactivating
        self.user_repo.update_user(user_id, is_active=False)
        logger.info(f"User deactivated: {user['username']}")
        return True

    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""

        return jwt_service.verify_token(token)

    def get_user_from_token(self, token: str) -> Optional[Dict]:
        """Get user from JWT token"""

        user_id = jwt_service.get_user_id_from_token(token)
        if user_id:
            return self.get_user_by_id(user_id)
        return None

    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh JWT token if valid"""

        payload = self.verify_jwt_token(token)
        if payload:
            user_id = int(payload.get("sub"))
            username = payload.get("username", "unknown")
            return self.generate_secure_token(user_id, username)
        return None


# Global auth service instance
auth_service = AuthService()
