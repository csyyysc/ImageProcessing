"""
CSS styling components for Streamlit frontend
"""
import streamlit as st
import logging

logger = logging.getLogger(__name__)


def create_image_container_css() -> str:
    """
    Create CSS for consistent image container styling

    Returns:
        CSS string for image containers
    """
    return """
    <style>
    .image-container {
        width: 300px;
        height: 300px;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 5px;
        margin: 10px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #f8f9fa;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .image-container img {
        width: 100%;
        height: 100%;
        border-radius: 5px;
        object-fit: cover;
    }
    
    .image-actions {
        margin-top: 10px;
        display: flex;
        gap: 10px;
        justify-content: center;
    }
    
    .download-link {
        text-decoration: none;
        color: #1f77b4;
        font-weight: 500;
    }
    
    .download-link:hover {
        color: #0d5aa7;
        text-decoration: underline;
    }
    </style>
    """


def create_button_css() -> str:
    """
    Create CSS for button styling

    Returns:
        CSS string for buttons
    """
    return """
    <style>
    .stButton > button {
        border-radius: 8px;
        border: 1px solid #ddd;
        transition: all 0.3s ease;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 120px;
        min-width: 40px;
        padding: 4px 12px;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .download-button {
        background-color: #28a745;
        color: white;
        border: none;
    }
    
    .download-button:hover {
        background-color: #218838;
    }
    
    .bulk-download-button {
        background-color: #007bff;
        color: white;
        border: none;
    }
    
    .bulk-download-button:hover {
        background-color: #0056b3;
    }
    </style>
    """


def create_sidebar_css() -> str:
    """
    Create CSS for sidebar styling

    Returns:
        CSS string for sidebar
    """
    return """
    <style>
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    .sidebar .sidebar-content .block-container {
        padding: 1rem;
    }
    
    .metric-container {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .section-header {
        color: #2c3e50;
        font-weight: 600;
        margin-bottom: 0.5rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .truncate-text {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 200px;
    }
    
    .icon-text {
        display: inline-flex;
        align-items: center;
        white-space: nowrap;
    }
    
    .metric-label {
        font-size: 0.8rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    </style>
    """


def apply_image_container_css() -> None:
    """Apply image container CSS to the page"""
    try:
        st.markdown(create_image_container_css(), unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error applying image container CSS: {e}")


def apply_button_css() -> None:
    """Apply button CSS to the page"""
    try:
        st.markdown(create_button_css(), unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error applying button CSS: {e}")


def apply_sidebar_css() -> None:
    """Apply sidebar CSS to the page"""
    try:
        st.markdown(create_sidebar_css(), unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error applying sidebar CSS: {e}")


def apply_all_css() -> None:
    """Apply all CSS styles to the page"""
    try:
        apply_image_container_css()
        apply_button_css()
        apply_sidebar_css()
    except Exception as e:
        logger.error(f"Error applying CSS: {e}")
