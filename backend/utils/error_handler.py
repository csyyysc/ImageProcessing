"""
User-friendly error handling utilities
"""

import logging
from typing import Dict, List
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)


class ErrorMessageMapper:
    """Maps technical validation errors to user-friendly messages"""

    @staticmethod
    def map_username_error(error_type: str, error_msg: str) -> str:
        """Map username validation errors"""
        if 'min_length' in error_type:
            return "Username must be at least 3 characters long"
        elif 'max_length' in error_type:
            return "Username cannot exceed 50 characters"
        elif 'value_error' in error_type:
            if 'only contain' in error_msg:
                return "Username can only contain letters, numbers, and underscores"
            else:
                return "Please enter a valid username"
        else:
            return "Please enter a valid username"

    @staticmethod
    def map_password_error(error_type: str, error_msg: str) -> str:
        """Map password validation errors"""
        if 'min_length' in error_type:
            return "Password must be at least 8 characters long"
        elif 'value_error' in error_type:
            if 'at least one letter' in error_msg:
                return "Password must contain at least one letter"
            elif 'at least one number' in error_msg:
                return "Password must contain at least one number"
            elif 'at least 8 characters' in error_msg:
                return "Password must be at least 8 characters long"
            else:
                return "Password must contain letters and numbers"
        else:
            return "Please enter a valid password"

    @staticmethod
    def map_email_error(error_type: str, error_msg: str) -> str:
        """Map email validation errors"""
        if 'value_error' in error_type:
            return "Please enter a valid email address"
        else:
            return "Invalid email format"

    @staticmethod
    def map_field_error(field: str, error_type: str, error_msg: str) -> str:
        """Map validation errors for any field"""
        if field == 'username':
            return ErrorMessageMapper.map_username_error(error_type, error_msg)
        elif field == 'password':
            return ErrorMessageMapper.map_password_error(error_type, error_msg)
        elif field == 'email':
            return ErrorMessageMapper.map_email_error(error_type, error_msg)
        else:
            return f"Please check the {field} field"


def format_validation_errors(errors: List[Dict]) -> str:
    """Convert validation errors to user-friendly messages"""
    error_messages = []

    for error in errors:
        field = error['loc'][-1] if error['loc'] else 'field'
        error_type = error['type']
        error_msg = str(error.get('msg', ''))

        user_message = ErrorMessageMapper.map_field_error(
            field, error_type, error_msg)
        error_messages.append(user_message)

    return combine_error_messages(error_messages)


def combine_error_messages(messages: List[str]) -> str:
    """Combine multiple error messages into a user-friendly format"""
    if len(messages) == 1:
        return messages[0]
    elif len(messages) <= 3:
        return " • ".join(messages)
    else:
        return f"Please fix {len(messages)} validation errors in your input"


def create_error_response(message: str, status_code: int = 400, details: str = None) -> Dict:
    """Create standardized error response"""
    response = {
        "success": False,
        "message": message,
        "status_code": status_code
    }

    if details:
        response["details"] = details

    return response


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Global validation error handler for FastAPI"""
    # Convert errors to user-friendly message
    user_message = format_validation_errors(exc.errors())

    # Log technical error for debugging
    logger.warning(f"Validation error: {exc.errors()}")

    # Return user-friendly response
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=create_error_response(
            message=f"Registration failed: {user_message}",
            status_code=400
        )
    )


def handle_auth_error(error: Exception, context: str = "authentication") -> HTTPException:
    """Handle authentication-related errors with user-friendly messages"""

    if isinstance(error, ValueError):
        error_msg = str(error)

        # Map common ValueError messages to user-friendly ones
        if "Username already exists" in error_msg:
            message = "This username is already taken. Please choose a different one."
        elif "Email already registered" in error_msg:
            message = "This email is already registered. Please use a different email or try logging in."
        elif "Username can only contain" in error_msg:
            message = "Username can only contain letters, numbers, and underscores."
        elif "Password must contain" in error_msg:
            message = "Password must contain at least one letter and one number."
        elif "Password must be at least" in error_msg:
            message = "Password must be at least 8 characters long."
        else:
            message = f"Registration failed: {error_msg}"

        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(message)
        )

    # Generic error handling
    logger.error(f"{context} error: {error}")
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=create_error_response(
            "An error occurred. Please try again later.")
    )
