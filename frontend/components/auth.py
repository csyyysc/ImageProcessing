"""
Authentication UI components
"""
import logging
import streamlit as st

from shared.config import settings
from frontend.api.user import UserAPI
from frontend.utils.auth import (
    set_auth_session, validate_password, validate_username, validate_email,
    get_current_user, logout
)

logger = logging.getLogger(__name__)


def create_login_form():
    """Create simple login form in container"""
    try:
        with st.form("login_form"):
            # Simple welcome message
            st.markdown("### 🔐 Welcome Back")
            st.markdown("Please sign in to continue")

            # Username field
            username = st.text_input(
                "Username", placeholder="Enter your username")

            # Password field
            password = st.text_input(
                "Password", type="password", placeholder="Enter your password")

            # Buttons
            col1, col2 = st.columns(2)
            with col1:
                login_submitted = st.form_submit_button(
                    "Login", use_container_width=True)
            with col2:
                register_button = st.form_submit_button(
                    "Register", use_container_width=True)

        return {
            'login_submitted': login_submitted,
            'register_button': register_button,
            'username': username,
            'password': password
        }
    except Exception as e:
        logger.error(f"Error creating login form: {e}")
        return None


def create_register_form():
    """Create simple register form in container"""
    try:
        with st.form("register_form"):
            # Simple welcome message
            st.markdown("### 📝 Create Account")
            st.markdown("Join us to get started")

            # Username field
            username = st.text_input(
                "Username", placeholder="Choose a username")

            # Email field
            email = st.text_input("Email (optional)",
                                  placeholder="your@email.com")

            # Password field
            password = st.text_input(
                "Password", type="password", placeholder="Choose a password")

            # Confirm password field
            confirm_password = st.text_input(
                "Confirm Password", type="password", placeholder="Confirm your password")

            # Buttons
            col1, col2 = st.columns(2)
            with col1:
                register_submitted = st.form_submit_button(
                    "Register", use_container_width=True)
            with col2:
                login_button = st.form_submit_button(
                    "Login", use_container_width=True)

        return {
            'register_submitted': register_submitted,
            'login_button': login_button,
            'username': username,
            'email': email,
            'password': password,
            'confirm_password': confirm_password
        }
    except Exception as e:
        logger.error(f"Error creating register form: {e}")
        return None


def create_user_info_sidebar():
    """Create user information sidebar component"""
    try:
        user = get_current_user()
        if not user:
            return

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
    except Exception as e:
        logger.error(f"Error creating user info sidebar: {e}")


def create_auth_header(title: str, icon: str = "🔐"):
    """Create compact authentication page header"""
    try:
        # Simple centered header
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <h1 style="color: #2c3e50; font-size: 1.8rem; margin: 0;">
                {icon} {title}
            </h1>
        </div>
        """.format(icon=icon, title=title), unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error creating auth header: {e}")


def handle_login_submission(form_data: dict):
    """Handle login form submission"""
    try:
        if not form_data:
            return

        username = form_data.get('username', '').strip()
        password = form_data.get('password', '')

        if not username or not password:
            st.error("❌ Please fill in all fields")
            return

        # Validate username
        is_valid_username, username_error = validate_username(username)
        if not is_valid_username:
            st.error(f"❌ {username_error}")
            return

        # Create API client and attempt login
        api = UserAPI(settings.BACKEND_URL)

        with st.spinner("Logging in..."):
            result = api.login(username, password)

            if result and result.get('success'):
                set_auth_session(result.get('user'), result.get('token'))
                st.success(f"✅ Welcome back, {username}!")
                st.rerun()
            else:
                error_msg = result.get(
                    'message', 'Invalid credentials') if result else 'Login failed'
                st.error(f"❌ {error_msg}")
    except Exception as e:
        logger.error(f"Error handling login submission: {e}")
        st.error("❌ Login failed. Please try again.")


def handle_register_submission(form_data: dict):
    """Handle registration form submission"""
    try:
        if not form_data:
            return

        username = form_data.get('username', '').strip()
        email = form_data.get('email', '').strip()
        password = form_data.get('password', '')
        confirm_password = form_data.get('confirm_password', '')

        if not username or not password or not confirm_password:
            st.error("❌ Please fill in all required fields")
            return

        # Validate username
        is_valid_username, username_error = validate_username(username)
        if not is_valid_username:
            st.error(f"❌ {username_error}")
            return

        # Validate email
        is_valid_email, email_error = validate_email(email)
        if not is_valid_email:
            st.error(f"❌ {email_error}")
            return

        # Validate password
        is_valid_password, password_error = validate_password(password)
        if not is_valid_password:
            st.error(f"❌ {password_error}")
            return

        # Check password confirmation
        if password != confirm_password:
            st.error("❌ Passwords don't match")
            return

        # Create API client and attempt registration
        api = UserAPI(settings.BACKEND_URL)

        with st.spinner("Creating account..."):
            result = api.register(
                username, password, email if email else None)

            if result and result.get('success'):
                set_auth_session(result.get('user'), result.get('token'))
                st.success(
                    f"✅ Account created successfully! Welcome, {username}!")
                st.rerun()
            else:
                error_msg = result.get(
                    'message', 'Registration failed') if result else 'Registration failed'
                st.error(f"❌ {error_msg}")
    except Exception as e:
        logger.error(f"Error handling register submission: {e}")
        st.error("❌ Registration failed. Please try again.")


def show_login_page():
    """Display the login page"""
    try:
        create_auth_header("Login", "🔐")

        form_data = create_login_form()
        if not form_data:
            return

        if form_data['login_submitted']:
            handle_login_submission(form_data)

        if form_data['register_button']:
            st.session_state.show_register = True
            st.rerun()
    except Exception as e:
        logger.error(f"Error showing login page: {e}")
        st.error("❌ Error loading login page")


def show_register_page():
    """Display the registration page"""
    try:
        create_auth_header("Register", "📝")

        form_data = create_register_form()
        if not form_data:
            return

        if form_data['register_submitted']:
            handle_register_submission(form_data)

        if form_data['login_button']:
            st.session_state.show_register = False
            st.rerun()
    except Exception as e:
        logger.error(f"Error showing register page: {e}")
        st.error("❌ Error loading registration page")


def show_auth_page():
    """Show authentication page based on session state"""
    try:
        if st.session_state.get('show_register', False):
            show_register_page()
        else:
            show_login_page()
    except Exception as e:
        logger.error(f"Error showing auth page: {e}")
        st.error("❌ Error loading authentication page")
