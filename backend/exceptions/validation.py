"""
Validation exceptions
"""
from typing import List, Dict, Any


class ValidationError(Exception):
    """Custom validation error with user-friendly messages"""

    def __init__(self, message: str, field: str = None, errors: List[Dict[str, Any]] = None):
        self.message = message
        self.field = field
        self.errors = errors or []
        super().__init__(self.message)


class UserAlreadyExistsError(ValidationError):
    """Raised when trying to create a user that already exists"""

    def __init__(self, username: str):
        super().__init__(
            message=f"This username is already taken. Please choose a different one.",
            field="username"
        )
        self.username = username


class EmailAlreadyRegisteredError(ValidationError):
    """Raised when trying to register with an email that's already in use"""

    def __init__(self, email: str):
        super().__init__(
            message="This email is already registered. Please use a different email or try logging in.",
            field="email"
        )
        self.email = email


class AuthenticationError(Exception):
    """Raised when authentication fails"""

    def __init__(self, message: str, reason: str = None):
        self.message = message
        self.reason = reason
        super().__init__(self.message)


class AccountLockedError(AuthenticationError):
    """Raised when account is temporarily locked"""

    def __init__(self, lockout_duration: int = 300):
        super().__init__(
            message="Account temporarily locked due to multiple failed login attempts. Please try again in a few minutes.",
            reason="too_many_attempts"
        )
        self.lockout_duration = lockout_duration


class AccountDisabledError(AuthenticationError):
    """Raised when account is disabled"""

    def __init__(self):
        super().__init__(
            message="Your account has been disabled. Please contact support.",
            reason="account_disabled"
        )
