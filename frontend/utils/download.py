"""
Download utilities for Streamlit frontend
"""
import base64
import logging
import streamlit as st
from typing import Optional

logger = logging.getLogger(__name__)


def download_file(data: bytes, filename: str, mime_type: str = "application/octet-stream") -> str:
    """
    Helper function to trigger file download in Streamlit

    Args:
        data: File data as bytes
        filename: Name of the file to download
        mime_type: MIME type of the file

    Returns:
        HTML string for download link
    """
    try:
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}" style="text-decoration: none;">📥 Download {filename}</a>'
        return href
    except Exception as e:
        logger.error(f"Error creating download link: {e}")
        return f'<span style="color: red;">❌ Download failed: {str(e)}</span>'


def trigger_direct_download(data: bytes, filename: str, mime_type: str = "application/octet-stream") -> None:
    """
    Trigger direct download without showing link

    Args:
        data: File data as bytes
        filename: Name of the file to download
        mime_type: MIME type of the file
    """
    try:
        # Use Streamlit's download button with a prominent style
        download_key = f"download_{abs(hash(filename))}_{abs(hash(str(data[:100])))}"

        # Create a download button that's more prominent
        st.download_button(
            label="Confirm",
            data=data,
            file_name=filename,
            mime=mime_type,
            key=download_key,
            help=f"Download {filename}",
            type="primary"
        )

    except Exception as e:
        logger.error(f"Error triggering direct download: {e}")
        # Fallback to showing download link
        st.markdown(download_file(data, filename, mime_type),
                    unsafe_allow_html=True)


def handle_download_error(error: Exception) -> str:
    """
    Handle download errors and return appropriate error message

    Args:
        error: Exception that occurred during download

    Returns:
        Error message string
    """
    error_str = str(error)

    if "Download limit exceeded" in error_str:
        return f"❌ {error_str}"
    elif "Rate limit exceeded" in error_str:
        return f"❌ {error_str}"
    elif "not found" in error_str.lower():
        return "❌ Image not found or access denied"
    else:
        return f"❌ Download failed: {error_str}"


def show_download_success(filename: str, count: Optional[int] = None) -> None:
    """
    Show download success message

    Args:
        filename: Name of downloaded file
        count: Optional count for bulk downloads
    """
    if count and count > 1:
        st.success(f"✅ Downloaded {count} images")
    else:
        st.success(f"✅ Downloaded")


def show_download_popup(filename: str) -> None:
    """
    Show download success popup message

    Args:
        filename: Name of downloaded file
    """
    try:
        # Create a popup-style success message positioned below Streamlit's deploy bar
        popup_id = f"download-popup-{abs(hash(filename))}"

        st.markdown(f"""
        <div id="{popup_id}" style="
            position: fixed;
            top: 80px;
            right: 20px;
            background-color: #d4edda;
            color: #155724;
            padding: 12px 20px;
            border-radius: 8px;
            border: 1px solid #c3e6cb;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 9999;
            font-weight: 500;
            font-size: 14px;
            max-width: 300px;
            word-wrap: break-word;
            cursor: pointer;
            opacity: 1;
            transition: opacity 0.5s ease-out;
        ">
            ✅ Downloaded {filename}
        </div>
        <script>
        // Auto-hide popup after 2 seconds
        setTimeout(function() {{
            const popup = document.getElementById('{popup_id}');
            if (popup) {{
                popup.style.opacity = '0';
                setTimeout(function() {{
                    if (popup.parentNode) {{
                        popup.parentNode.removeChild(popup);
                    }}
                }}, 500);
            }}
        }}, 2000);
        
        // Manual close on click
        setTimeout(function() {{
            const popup = document.getElementById('{popup_id}');
            if (popup) {{
                popup.addEventListener('click', function() {{
                    this.style.opacity = '0';
                    setTimeout(function() {{
                        if (popup.parentNode) {{
                            popup.parentNode.removeChild(popup);
                        }}
                    }}, 300);
                }});
            }}
        }}, 100);
        </script>
        """, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error showing download popup: {e}")
        st.success(f"✅ Downloaded {filename}")


def show_download_error(error_message: str) -> None:
    """
    Show download error message

    Args:
        error_message: Error message to display
    """
    st.error(error_message)


def check_and_show_download_success() -> None:
    """
    Check session state for download success messages and show popups
    This should be called at the beginning of each page render
    """
    if 'download_success' in st.session_state and st.session_state['download_success']:
        # Show popup for each successful download
        for filename in st.session_state['download_success']:
            show_download_popup(filename)

        # Clear the download success messages
        st.session_state['download_success'] = []
