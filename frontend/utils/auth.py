"""
Authentication utility functions
"""
import logging
import streamlit as st

logger = logging.getLogger(__name__)


def init_session_state():
    """Initialize session state for authentication"""
    try:
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'token' not in st.session_state:
            st.session_state.token = None
        if 'show_register' not in st.session_state:
            st.session_state.show_register = False
    except Exception as e:
        logger.error(f"Error initializing session state: {e}")


def logout():
    """Logout the current user"""
    try:
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()
    except Exception as e:
        logger.error(f"Error during logout: {e}")


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    try:
        return st.session_state.get('authenticated', False)
    except Exception as e:
        logger.error(f"Error checking authentication status: {e}")
        return False


def get_current_user():
    """Get current authenticated user"""
    try:
        if is_authenticated():
            return st.session_state.get('user')
        return None
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return None


def get_auth_token():
    """Get current authentication token"""
    try:
        if is_authenticated():
            return st.session_state.get('token')
        return None
    except Exception as e:
        logger.error(f"Error getting auth token: {e}")
        return None


def set_auth_session(user_data: dict, token: str):
    """Set authentication session data"""
    try:
        st.session_state.authenticated = True
        st.session_state.user = user_data
        st.session_state.token = token
    except Exception as e:
        logger.error(f"Error setting auth session: {e}")


def clear_auth_session():
    """Clear authentication session data"""
    try:
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.token = None
    except Exception as e:
        logger.error(f"Error clearing auth session: {e}")


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"

        return True, ""
    except Exception as e:
        logger.error(f"Error validating password: {e}")
        return False, "Password validation failed"


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username format

    Args:
        username: Username to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"

        if len(username) > 20:
            return False, "Username must be less than 20 characters"

        if not username.replace('_', '').replace('-', '').isalnum():
            return False, "Username can only contain letters, numbers, underscores, and hyphens"

        return True, ""
    except Exception as e:
        logger.error(f"Error validating username: {e}")
        return False, "Username validation failed"


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email format

    Args:
        email: Email to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if not email:  # Email is optional
            return True, ""

        if '@' not in email or '.' not in email:
            return False, "Please enter a valid email address"

        if len(email) > 100:
            return False, "Email address is too long"

        return True, ""
    except Exception as e:
        logger.error(f"Error validating email: {e}")
        return False, "Email validation failed"


def require_auth():
    """Decorator function to require authentication"""
    try:
        init_session_state()

        if not is_authenticated():
            return False
        return True
    except Exception as e:
        logger.error(f"Error in require_auth: {e}")
        return False
