"""
Section components for Streamlit frontend
"""
import logging
import streamlit as st
from typing import Callable

logger = logging.getLogger(__name__)


def create_sidebar_section(title: str, icon: str = "📊") -> None:
    """
    Create a sidebar section with consistent styling

    Args:
        title: Section title
        icon: Icon to display
    """
    try:
        st.markdown("---")
        st.markdown(
            f'<div class="icon-text"><h3>{icon} {title}</h3></div>', unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error creating sidebar section: {e}")


def create_info_section(title: str, content: str, icon: str = "ℹ️") -> None:
    """
    Create an info section with consistent styling

    Args:
        title: Section title
        content: Section content
        icon: Icon to display
    """
    try:
        st.markdown(
            f'<div class="icon-text"><h4>{icon} {title}</h4></div>', unsafe_allow_html=True)
        st.info(content)
    except Exception as e:
        logger.error(f"Error creating info section: {e}")


def create_warning_section(title: str, content: str, icon: str = "⚠️") -> None:
    """
    Create a warning section with consistent styling

    Args:
        title: Section title
        content: Section content
        icon: Icon to display
    """
    try:
        st.markdown(
            f'<div class="icon-text"><h4>{icon} {title}</h4></div>', unsafe_allow_html=True)
        st.warning(content)
    except Exception as e:
        logger.error(f"Error creating warning section: {e}")


def create_error_section(title: str, content: str, icon: str = "❌") -> None:
    """
    Create an error section with consistent styling

    Args:
        title: Section title
        content: Section content
        icon: Icon to display
    """
    try:
        st.markdown(
            f'<div class="icon-text"><h4>{icon} {title}</h4></div>', unsafe_allow_html=True)
        st.error(content)
    except Exception as e:
        logger.error(f"Error creating error section: {e}")


def create_success_section(title: str, content: str, icon: str = "✅") -> None:
    """
    Create a success section with consistent styling

    Args:
        title: Section title
        content: Section content
        icon: Icon to display
    """
    try:
        st.markdown(
            f'<div class="icon-text"><h4>{icon} {title}</h4></div>', unsafe_allow_html=True)
        st.success(content)
    except Exception as e:
        logger.error(f"Error creating success section: {e}")


def create_expandable_section(
    title: str,
    content_func: Callable,
    expanded: bool = False
) -> None:
    """
    Create an expandable section

    Args:
        title: Section title
        content_func: Function to render content
        expanded: Whether section should be expanded by default
    """
    try:
        with st.expander(title, expanded=expanded):
            content_func()
    except Exception as e:
        logger.error(f"Error creating expandable section: {e}")


def create_tab_section(title: str, icon: str = "📋") -> None:
    """
    Create a tab section header

    Args:
        title: Section title
        icon: Icon to display
    """
    try:
        st.markdown(
            f'<div class="icon-text"><h2>{icon} {title}</h2></div>', unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error creating tab section: {e}")


def create_subsection(title: str, icon: str = "📝") -> None:
    """
    Create a subsection header

    Args:
        title: Section title
        icon: Icon to display
    """
    try:
        st.markdown(
            f'<div class="icon-text"><h3>{icon} {title}</h3></div>', unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error creating subsection: {e}")


def create_divider() -> None:
    """Create a visual divider"""
    try:
        st.markdown("---")
    except Exception as e:
        logger.error(f"Error creating divider: {e}")


def create_spacer(height: int = 1) -> None:
    """
    Create vertical spacing

    Args:
        height: Number of empty lines
    """
    try:
        for _ in range(height):
            st.markdown("")
    except Exception as e:
        logger.error(f"Error creating spacer: {e}")


def create_status_section(
    title: str,
    status: str,
    icon: str = "🔧"
) -> None:
    """
    Create a status section with appropriate styling

    Args:
        title: Section title
        status: Status message
        icon: Icon to display
    """
    try:
        st.markdown(
            f'<div class="icon-text"><h4>{icon} {title}</h4></div>', unsafe_allow_html=True)

        if status.lower() in ["healthy", "running", "success", "ok"]:
            st.success(f"✅ {status}")
        elif status.lower() in ["error", "failed", "down", "offline"]:
            st.error(f"❌ {status}")
        elif status.lower() in ["warning", "caution", "degraded"]:
            st.warning(f"⚠️ {status}")
        else:
            st.info(f"ℹ️ {status}")
    except Exception as e:
        logger.error(f"Error creating status section: {e}")
