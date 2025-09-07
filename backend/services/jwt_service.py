"""
JWT service for token generation and validation
"""
import os
import logging
from jose import JWTError, jwt
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
ALGORITHM = "HS256"
SECRET_KEY = os.getenv(
    "SECRET_KEY", "your-secret-key-change-this-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class JWTService:
    """JWT token service for authentication"""

    def __init__(self):
        self.algorithm = ALGORITHM
        self.secret_key = SECRET_KEY
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""

        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(
                timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})

        try:
            encoded_jwt = jwt.encode(
                to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(
                f"JWT token created for user: {data.get('sub', 'unknown')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating JWT token: {e}")
            raise

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""

        try:
            payload = jwt.decode(token, self.secret_key,
                                 algorithms=[self.algorithm])
            user_id: Optional[str] = payload.get("sub")

            if user_id is None:
                logger.warning("JWT token missing 'sub' claim")
                return None

            exp = payload.get("exp")
            if exp and datetime.now(timezone.utc).timestamp() > exp:
                logger.warning("JWT token has expired")
                return None

            logger.info(f"JWT token verified for user: {user_id}")
            return payload
        except JWTError as e:
            logger.warning(f"JWT token verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying JWT token: {e}")
            return None

    def get_user_id_from_token(self, token: str) -> Optional[int]:
        """Extract user ID from JWT token"""

        payload = self.verify_token(token)
        if payload:
            try:
                return int(payload.get("sub"))
            except (ValueError, TypeError):
                logger.warning("Invalid user ID in JWT token")
                return None
        return None

    def create_token_for_user(self, user_id: int, username: str, additional_claims: Optional[Dict] = None) -> str:
        """Create a JWT token for a specific user"""

        data = {
            "sub": str(user_id),
            "type": "access",
            "username": username,
        }

        if additional_claims:
            data.update(additional_claims)

        return self.create_access_token(data)

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""

        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""

        return pwd_context.verify(plain_password, hashed_password)

    def is_token_expired(self, token: str) -> bool:
        """Check if a token is expired without raising an exception"""

        try:
            payload = jwt.decode(token, self.secret_key,
                                 algorithms=[self.algorithm])
            exp = payload.get("exp")

            if exp:
                return datetime.now(timezone.utc).timestamp() > exp
            return True  # No expiration means expired
        except JWTError:
            return True  # Invalid token means expired

    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get token information without verification (for debugging)"""

        try:
            # Decode without verification to get payload
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except JWTError:
            return None


# Global JWT service instance
jwt_service = JWTService()
