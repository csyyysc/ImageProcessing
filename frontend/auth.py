"""
Authentication pages - Main entry point
"""
import streamlit as st
from frontend.utils.auth import init_session_state, require_auth as auth_require_auth
from frontend.components.auth import show_auth_page, create_user_info_sidebar


def show_user_info():
    """Display user information in sidebar"""
    create_user_info_sidebar()


def show_auth_page_wrapper():
    """Show authentication page based on session state"""
    init_session_state()
    show_auth_page()


def require_auth():
    """Decorator function to require authentication"""
    init_session_state()

    if not auth_require_auth():
        st.warning("🔒 Please login to access this application")
        show_auth_page_wrapper()
        return False
    return True
