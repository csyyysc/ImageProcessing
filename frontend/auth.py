"""
Authentication pages
"""
import streamlit as st
from frontend.api.user import UserAPI
from shared.config import settings


def init_session_state():
    """Initialize session state for authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'token' not in st.session_state:
        st.session_state.token = None


def logout():
    """Logout the current user"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.token = None
    st.rerun()


def login_page():
    """Display the login page"""
    st.title("🔐 Login")
    st.markdown("---")

    # Create API client
    api = UserAPI(settings.BACKEND_URL)

    with st.form("login_form"):
        st.subheader("Welcome Back!")

        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input(
            "Password", type="password", placeholder="Enter your password")

        col1, col2 = st.columns(2)
        with col1:
            login_submitted = st.form_submit_button(
                "🚀 Login", use_container_width=True)
        with col2:
            register_button = st.form_submit_button(
                "📝 Go to Register", use_container_width=True)

    if login_submitted:
        if username and password:
            with st.spinner("Logging in..."):
                result = api.login(username, password)

                if result and result.get('success'):
                    st.session_state.authenticated = True
                    st.session_state.user = result.get('user')
                    st.session_state.token = result.get('token')
                    st.success(f"✅ Welcome back, {username}!")
                    st.rerun()
                else:
                    error_msg = result.get(
                        'message', 'Invalid credentials') if result else 'Login failed'
                    st.error(f"❌ {error_msg}")
        else:
            st.error("❌ Please fill in all fields")

    if register_button:
        st.session_state.show_register = True
        st.rerun()


def register_page():
    """Display the registration page"""
    st.title("📝 Register")
    st.markdown("---")

    # Create API client
    api = UserAPI(settings.BACKEND_URL)

    with st.form("register_form"):
        st.subheader("Create Your Account")

        username = st.text_input("Username", placeholder="Choose a username")
        email = st.text_input("Email (optional)",
                              placeholder="your.email@example.com")
        password = st.text_input(
            "Password", type="password", placeholder="Choose a strong password")
        confirm_password = st.text_input(
            "Confirm Password", type="password", placeholder="Confirm your password")

        col1, col2 = st.columns(2)
        with col1:
            register_submitted = st.form_submit_button(
                "🎉 Register", use_container_width=True)
        with col2:
            login_button = st.form_submit_button(
                "🔐 Go to Login", use_container_width=True)

    if register_submitted:
        if username and password and confirm_password:
            if password != confirm_password:
                st.error("❌ Passwords don't match")
            elif len(password) < 8:
                st.error("❌ Password must be at least 8 characters long")
            else:
                with st.spinner("Creating account..."):
                    result = api.register(
                        username, password, email if email else None)

                    if result and result.get('success'):
                        st.success(
                            f"✅ Account created successfully! Welcome, {username}!")
                        st.session_state.authenticated = True
                        st.session_state.user = result.get('user')
                        st.session_state.token = result.get('token')
                        st.rerun()
                    else:
                        error_msg = result.get(
                            'message', 'Registration failed') if result else 'Registration failed'
                        st.error(f"❌ {error_msg}")
        else:
            st.error("❌ Please fill in all required fields")

    if login_button:
        st.session_state.show_register = False
        st.rerun()


def show_user_info():
    """Display user information in sidebar"""

    if st.session_state.authenticated and st.session_state.user:
        user = st.session_state.user
        st.sidebar.success(f"👤 Welcome, {user['username']}!")

        with st.sidebar.expander("User Details"):
            st.write(f"**Username:** {user['username']}")
            if user.get('email'):
                st.write(f"**Email:** {user['email']}")
            st.write(f"**Active:** {'Yes' if user.get('is_active') else 'No'}")
            if user.get('created_at'):
                st.write(f"**Member since:** {user['created_at'][:10]}")

        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout()


def show_auth_page():
    """Show authentication page based on session state"""
    init_session_state()

    # Initialize show_register if not exists
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False

    if st.session_state.show_register:
        register_page()
    else:
        login_page()


def require_auth():
    """Decorator function to require authentication"""
    init_session_state()

    if not st.session_state.authenticated:
        st.warning("🔒 Please login to access this application")
        show_auth_page()
        return False
    return True
