"""
Button components for Streamlit frontend
"""
import logging
import streamlit as st
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def create_download_button(
    button_text: str = "📥 Download",
    button_type: str = "secondary",
    key: Optional[str] = None
) -> bool:
    """
    Create a download button with consistent styling

    Args:
        button_text: Text to display on button
        button_type: Streamlit button type
        key: Unique key for the button

    Returns:
        True if button was clicked, False otherwise
    """
    try:
        return st.button(button_text, key=key, type=button_type)
    except Exception as e:
        logger.error(f"Error creating download button: {e}")
        return False


def create_bulk_download_button(
    button_text: str = "📦 Download",
    button_type: str = "primary",
    key: str = "bulk_download"
) -> bool:
    """
    Create a bulk download button with consistent styling

    Args:
        button_text: Text to display on button
        button_type: Streamlit button type
        key: Unique key for the button

    Returns:
        True if button was clicked, False otherwise
    """
    try:
        return st.button(button_text, key=key, type=button_type)
    except Exception as e:
        logger.error(f"Error creating bulk download button: {e}")
        return False


def create_delete_button(
    button_text: str = "🗑️ Delete",
    button_type: str = "secondary",
    key: Optional[str] = None
) -> bool:
    """
    Create a delete button with consistent styling

    Args:
        button_text: Text to display on button
        button_type: Streamlit button type
        key: Unique key for the button

    Returns:
        True if button was clicked, False otherwise
    """
    try:
        return st.button(button_text, key=key, type=button_type)
    except Exception as e:
        logger.error(f"Error creating delete button: {e}")
        return False


def create_transform_button(
    button_text: str = "🎨 Transform",
    button_type: str = "primary",
    key: Optional[str] = None
) -> bool:
    """
    Create a transform button with consistent styling

    Args:
        button_text: Text to display on button
        button_type: Streamlit button type
        key: Unique key for the button

    Returns:
        True if button was clicked, False otherwise
    """
    try:
        return st.button(button_text, key=key, type=button_type)
    except Exception as e:
        logger.error(f"Error creating transform button: {e}")
        return False


def create_upload_button(
    button_text: str = "📤 Upload Image",
    button_type: str = "primary",
    key: str = "upload_button"
) -> bool:
    """
    Create an upload button with consistent styling

    Args:
        button_text: Text to display on button
        button_type: Streamlit button type
        key: Unique key for the button

    Returns:
        True if button was clicked, False otherwise
    """
    try:
        return st.button(button_text, key=key, type=button_type)
    except Exception as e:
        logger.error(f"Error creating upload button: {e}")
        return False


def create_action_buttons_layout(
    buttons: List[Dict[str, Any]],
    columns: int = 3
) -> List[bool]:
    """
    Create a consistent layout for action buttons

    Args:
        buttons: List of button configurations
        columns: Number of columns for button layout

    Returns:
        List of button click states
    """
    if not buttons:
        return []

    try:
        cols = st.columns(columns)
        results = []

        for i, button_config in enumerate(buttons):
            col_index = i % columns
            with cols[col_index]:
                clicked = st.button(
                    button_config.get('text', 'Button'),
                    key=button_config.get('key', f'button_{i}'),
                    type=button_config.get('type', 'secondary')
                )
                results.append(clicked)

        return results
    except Exception as e:
        logger.error(f"Error creating action buttons layout: {e}")
        return []


def create_confirmation_buttons(
    confirm_text: str = "✅ Yes",
    cancel_text: str = "❌ Cancel",
    confirm_type: str = "primary",
    cancel_type: str = "secondary"
) -> tuple[bool, bool]:
    """
    Create confirmation dialog buttons

    Args:
        confirm_text: Text for confirm button
        cancel_text: Text for cancel button
        confirm_type: Type for confirm button
        cancel_type: Type for cancel button

    Returns:
        Tuple of (confirm_clicked, cancel_clicked)
    """
    try:
        col1, col2 = st.columns(2)

        with col1:
            confirm_clicked = st.button(
                confirm_text, key="confirm_action", type=confirm_type)

        with col2:
            cancel_clicked = st.button(
                cancel_text, key="cancel_action", type=cancel_type)

        return confirm_clicked, cancel_clicked
    except Exception as e:
        logger.error(f"Error creating confirmation buttons: {e}")
        return False, False
