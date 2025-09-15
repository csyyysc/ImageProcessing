"""
Streamlit Frontend Application
"""

from frontend.components.buttons import create_download_button, create_bulk_download_button
from frontend.components.ui import apply_all_css, create_sidebar_section
from frontend.utils.download import (
    handle_download_error, show_download_error,
    trigger_direct_download, check_and_show_download_success
)
from frontend.auth import require_auth, show_user_info
from frontend.api.image import ImageAPI
from frontend.api.common import BaseAPI
from shared.config import settings, streamlit_settings
import os
import sys
import time
import logging
import base64
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BACKEND_URL = settings.BACKEND_URL

st.set_page_config(**streamlit_settings.as_dict())


@st.cache_resource
def get_api_client():
    return BaseAPI(BACKEND_URL)


def start_frontend():
    """Entry point for frontend application"""

    import sys
    import subprocess

    # Run streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "frontend/app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0"
    ])


def main():
    """Main Streamlit application"""

    # Apply all CSS styles for consistent UI (including auth forms)
    apply_all_css()

    if not require_auth():
        return

    # Check for download success messages and show popups
    check_and_show_download_success()

    st.title("Image Processing Application")
    st.markdown("---")

    # Initialize API client
    # @Note: This is a global API client for the backend
    api = get_api_client()

    with st.sidebar:
        show_user_info()

        create_sidebar_section("Image Statistics", "📊")

        # Check backend health first
        backend_healthy = api.health_check()

        if backend_healthy:
            try:
                user_id = st.session_state["user"]["id"]
                image_api = ImageAPI(settings.BACKEND_URL)

                total_count = image_api.get_total_images(user_id)

                if total_count:
                    images = image_api.get_images(
                        user_id=user_id, page=1, limit=100)

                    if images:
                        total_size = sum(img.get('file_size', 0)
                                         for img in images)
                        avg_size = total_size / len(images) if images else 0

                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total Images", total_count)
                        with col2:
                            st.metric("Total Size",
                                      f"{total_size / (1024*1024):.1f} MB")

                        col3, col4 = st.columns(2)
                        with col3:
                            st.metric("Average Size",
                                      f"{avg_size / 1024:.1f} KB")
                        with col4:
                            st.metric("Storage Used",
                                      f"{total_size / (1024*1024):.1f} MB")
                else:
                    st.info("No images found")
            except Exception as e:
                st.error(f"Unable to load statistics: {str(e)}")
        else:
            st.warning("Backend not accessible")

        create_sidebar_section("Download Statistics", "📥")

        if backend_healthy:
            try:
                user_id = st.session_state["user"]["id"]
                image_api = ImageAPI(settings.BACKEND_URL)

                # Get download stats
                download_stats = image_api.get_download_stats(user_id)
                if download_stats:
                    rate_limits = download_stats.get('rate_limits', {})

                    # API Rate Limits
                    api_calls = rate_limits.get('api_calls', {})
                    st.metric(
                        "API Calls Remaining", f"{api_calls.get('remaining', 0)}/{api_calls.get('limit', 60)}")

                    # Download Limits
                    downloads = rate_limits.get('downloads', {})
                    st.metric(
                        "Downloads Remaining", f"{downloads.get('remaining', 0)}/{downloads.get('limit', 500)}")

                    # Reset time info
                    reset_time = downloads.get('reset_time', '')
                    if reset_time:
                        try:
                            from datetime import datetime
                            reset_dt = datetime.fromisoformat(
                                reset_time.replace('Z', '+00:00'))
                            st.caption(
                                f"Resets: {reset_dt.strftime('%H:%M UTC')}")
                        except:
                            pass
                else:
                    st.info("Unable to load download statistics")
            except Exception as e:
                st.error(f"Error loading download stats: {str(e)}")
        else:
            st.warning("Backend not accessible")

        create_sidebar_section("System Status", "🔧")

        if backend_healthy:
            st.success("✅ Backend is running")
        else:
            st.error("❌ Backend is not accessible")
            st.warning(
                "Please start the backend server:\n`uv run python main.py backend`")

        # Transformation popup window
        if st.session_state.get('show_transform_any', False):
            transform_image_id = st.session_state.get('transform_image_id')

            # Get API client and user info
            image_api = ImageAPI(settings.BACKEND_URL)
            user_id = st.session_state["user"]["id"]

            st.markdown("---")
            st.header("🎨 Image Transformation")

            # Transformation options
            st.write("**Basic Operations:**")
            resize = st.checkbox("📏 Resize", key="popup_resize")
            crop = st.checkbox("✂️ Crop", key="popup_crop")
            rotate = st.checkbox("🔄 Rotate", key="popup_rotate")
            flip = st.checkbox("↔️ Flip (Horizontal)", key="popup_flip")
            mirror = st.checkbox("↕️ Mirror (Vertical)", key="popup_mirror")

            st.write("**Advanced Operations:**")
            watermark = st.checkbox("💧 Watermark", key="popup_watermark")
            compress = st.checkbox("🗜️ Compress", key="popup_compress")
            change_format = st.checkbox("🔄 Change Format", key="popup_format")
            apply_filters = st.checkbox("🎭 Apply Filters", key="popup_filters")

            # Detailed options for selected transformations
            if resize:
                st.write("**Resize Options:**")
                col1, col2 = st.columns(2)
                with col1:
                    new_width = st.number_input(
                        "Width (px)", min_value=1, max_value=4000, value=300, key="popup_width")
                with col2:
                    new_height = st.number_input(
                        "Height (px)", min_value=1, max_value=4000, value=300, key="popup_height")

            if crop:
                st.write("**Crop Options:**")
                col1, col2 = st.columns(2)
                with col1:
                    crop_x = st.number_input(
                        "X", min_value=0, value=0, key="popup_crop_x")
                    crop_w = st.number_input(
                        "Width", min_value=1, value=100, key="popup_crop_w")
                with col2:
                    crop_y = st.number_input(
                        "Y", min_value=0, value=0, key="popup_crop_y")
                    crop_h = st.number_input(
                        "Height", min_value=1, value=100, key="popup_crop_h")

            if rotate:
                st.write("**Rotate Options:**")
                rotation_angle = st.slider(
                    "Rotation Angle", -180, 180, 0, key="popup_angle")

            if watermark:
                st.write("**Watermark Options:**")
                watermark_text = st.text_input(
                    "Watermark Text", value="SAMPLE", key="popup_watermark_text")
                col1, col2 = st.columns(2)
                with col1:
                    watermark_x = st.number_input(
                        "X Position", min_value=0, value=10, key="popup_watermark_x")
                with col2:
                    watermark_y = st.number_input(
                        "Y Position", min_value=0, value=10, key="popup_watermark_y")

            if change_format:
                st.write("**Format Options:**")
                new_format = st.selectbox(
                    "New Format", ["JPEG", "PNG", "WEBP", "BMP"], key="popup_new_format")

            if apply_filters:
                st.write("**Filter Options:**")
                filter_type = st.selectbox("Filter Type", [
                                           "None", "Grayscale", "Sepia", "Blur", "Sharpen", "Edge Detection"], key="popup_filter_type")

            if compress:
                st.write("**Compression Options:**")
                quality = st.slider("Quality (%)", 1, 100,
                                    85, key="popup_quality")

            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🚀 Apply", key="popup_apply", type="primary"):

                    params = {}
                    if resize:
                        params['resize'] = {
                            'width': new_width, 'height': new_height}
                    if crop:
                        params['crop'] = {
                            'x': crop_x, 'y': crop_y, 'width': crop_w, 'height': crop_h}
                    if rotate:
                        params['rotate'] = {'angle': rotation_angle}
                    if flip:
                        params['flip'] = True
                    if mirror:
                        params['mirror'] = True
                    if watermark:
                        params['watermark'] = {
                            'text': watermark_text, 'x': watermark_x, 'y': watermark_y}
                    if change_format:
                        params['format'] = {'type': new_format}
                    if apply_filters:
                        params['filter'] = {'type': filter_type}
                    if compress:
                        params['compress'] = {'quality': quality}

                    with st.spinner("Applying transformations..."):
                        result = image_api.transform_image(
                            transform_image_id, user_id, params)

                        if result and result.get('success'):
                            st.success(
                                "✅ Transformations applied successfully!")
                            st.info(
                                f"🎨 New image created: {result.get('transformed_image', {}).get('filename', 'Unknown')}")

                            # Clear all page caches to show the new transformed image
                            for key in list(st.session_state.keys()):
                                if key.startswith(f"user_images_{user_id}_page_"):
                                    del st.session_state[key]
                            st.session_state['force_refresh'] = True
                        else:
                            error_msg = result.get(
                                'message', 'Unknown error') if result else 'No response from server'
                            st.error(f"❌ Transformation failed: {error_msg}")

                    # Close popup
                    st.session_state['show_transform_any'] = False
                    st.rerun()

            with col2:
                if st.button("❌ Cancel", key="popup_cancel"):
                    st.session_state['show_transform_any'] = False
                    st.rerun()

    if not backend_healthy:
        st.error("🚨 Cannot connect to backend server")
        st.info("Please ensure the server is accessible.")
        return

    tab1, tab2, tab3 = st.tabs(
        ["📋 View Images", "➕ Upload Image", "✏️ Manage Images"])

    with tab1:
        # Auto-fetch images when switching to View Images tab
        if 'last_active_tab' not in st.session_state:
            st.session_state['last_active_tab'] = 'view_images'

        # Check if user just switched to View Images tab
        if st.session_state.get('last_active_tab') != 'view_images':
            # Clear all page caches to force fresh fetch
            user_id = st.session_state["user"]["id"]
            for key in list(st.session_state.keys()):
                if key.startswith(f"user_images_{user_id}_page_"):
                    del st.session_state[key]
            st.session_state['last_displayed_upload_counter'] = -1
            st.session_state['last_active_tab'] = 'view_images'
        user_id = st.session_state["user"]["id"]
        image_api = ImageAPI(settings.BACKEND_URL)

        # Initialize pagination state
        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = 1
        if 'images_per_page' not in st.session_state:
            st.session_state['images_per_page'] = 10

        # Get images with smart caching - only fetch when needed
        cache_key = f"user_images_{user_id}_page_{st.session_state['current_page']}"

        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.header("📋 All Images")
        with col2:
            view_mode = st.selectbox(
                "View Mode",
                ["Grid", "Large View"],
                key="view_mode_selector"
            )
        with col3:
            new_limit = st.selectbox(
                "Images per page",
                [5, 10, 20, 50],
                index=[5, 10, 20, 50].index(
                    st.session_state['images_per_page']),
                key="images_per_page_selector"
            )
            if new_limit != st.session_state['images_per_page']:
                st.session_state['images_per_page'] = new_limit
                st.session_state['current_page'] = 1  # Reset to first page
                # Clear all page caches to force refetch with new page size
                for key in list(st.session_state.keys()):
                    if key.startswith(f"user_images_{user_id}_page_"):
                        del st.session_state[key]
                st.session_state['last_displayed_upload_counter'] = -1
                st.rerun()

        image_api = ImageAPI(settings.BACKEND_URL)

        if "user" not in st.session_state or not st.session_state["user"]:
            st.error("❌ User session not found. Please log in again.")
            return

        # Check if we have cached images and if upload counter hasn't changed
        if (cache_key not in st.session_state or
                st.session_state.get('upload_counter', 0) != st.session_state.get('last_displayed_upload_counter', -1)):

            # Only fetch from API when cache is invalid or upload counter changed
            try:
                with st.spinner("🔄 Loading images..."):
                    images = image_api.get_images(
                        user_id=user_id,
                        page=st.session_state['current_page'],
                        limit=st.session_state['images_per_page']
                    )

                    if images is None:
                        images = []

                    # Cache the results
                    st.session_state[cache_key] = images
                    st.session_state['last_displayed_upload_counter'] = st.session_state.get(
                        'upload_counter', 0)
            except Exception as e:
                st.error(f"❌ Error loading images: {str(e)}")
                images = st.session_state.get(cache_key, [])
        else:
            # Use cached images (no API call needed)
            images = st.session_state[cache_key]
            # Show a subtle indicator that we're using cached data
            if len(images) > 0:
                st.caption("📋 Showing cached images (click refresh to update)")

        # Check if there are more images on the next page
        has_next_page = len(images) == st.session_state['images_per_page']
        if has_next_page:
            # Check if there's actually a next page
            next_page_images = image_api.get_images(
                user_id=user_id,
                page=st.session_state['current_page'] + 1,
                limit=1
            )
            has_next_page = next_page_images is not None and len(
                next_page_images) > 0

        if not images:
            st.info("No images found. Upload some images to get started!")
        else:
            # Display pagination info
            start_idx = (
                st.session_state['current_page'] - 1) * st.session_state['images_per_page'] + 1
            end_idx = start_idx + len(images) - 1
            st.write(
                f"**Showing images {start_idx}-{end_idx}** (Page {st.session_state['current_page']})")

            if view_mode == "Grid":
                # Grid view (original layout)
                cols = st.columns(3)

                for idx, image in enumerate(images):
                    col = cols[idx % 3]

                    with col:
                        if isinstance(image, dict):
                            image_url = image.get('url')
                            filename = image.get('filename', 'Unknown')
                            image_id = image.get('id')

                            full_url = f"{settings.BACKEND_URL}{image_url}"

                            st.markdown(f"""
                            <div class="image-container">
                                <img src="{full_url}" alt="{filename}">
                            </div>
                            """, unsafe_allow_html=True)

                            col1, col2, col3 = st.columns([4, 4, 3])
                            with col1:
                                if create_download_button(key=f"download_{image_id}"):
                                    try:
                                        image_data = image_api.download_single_image(
                                            image_id, user_id)
                                        if image_data:
                                            trigger_direct_download(
                                                image_data,
                                                filename,
                                                image.get(
                                                    'mime_type', 'image/jpeg')
                                            )
                                        else:
                                            show_download_error(
                                                "Failed to download image")
                                    except Exception as e:
                                        show_download_error(
                                            handle_download_error(e))

                            with col2:
                                if st.button("🎨 Transform", key=f"transform_{image_id}", type="primary"):
                                    # Show transformation popup in sidebar
                                    st.session_state['show_transform_any'] = True
                                    st.session_state['transform_image_id'] = image_id
                                    st.session_state['transform_filename'] = filename
                                    st.rerun()

                            with col3:
                                if st.button("🗑️ Delete", key=f"delete_{image_id}", type="secondary"):
                                    # Show confirmation dialog
                                    st.session_state[f"show_delete_confirm_{image_id}"] = True
                                    st.rerun()

                            # Confirmation dialog
                            if st.session_state.get(f"show_delete_confirm_{image_id}", False):
                                st.warning(
                                    "⚠️ Are you sure you want to delete this image?")
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("✅ Yes, Delete", key=f"confirm_delete_{image_id}", type="primary"):
                                        with st.spinner("Deleting image..."):
                                            success = image_api.delete_image(
                                                image_id, user_id)
                                            if success:
                                                st.success(
                                                    "✅ Image deleted successfully!")
                                                # Clear all page caches
                                                for key in list(st.session_state.keys()):
                                                    if key.startswith(f"user_images_{user_id}_page_"):
                                                        del st.session_state[key]
                                                st.session_state['force_refresh'] = True
                                                # Clear confirmation state
                                                st.session_state[f"show_delete_confirm_{image_id}"] = False
                                                time.sleep(1)
                                                st.rerun()
                                            else:
                                                st.error(
                                                    "❌ Failed to delete image")
                                with col2:
                                    if st.button("❌ Cancel", key=f"cancel_delete_{image_id}"):
                                        st.session_state[f"show_delete_confirm_{image_id}"] = False
                                        st.rerun()

                        else:
                            st.write(f"📷 Image {idx + 1}")

            else:
                # Large view mode
                for idx, image in enumerate(images):
                    if isinstance(image, dict):
                        image_url = image.get('url')
                        filename = image.get('filename', 'Unknown')
                        image_id = image.get('id')

                        full_url = f"{settings.BACKEND_URL}{image_url}"

                        # Large view container
                        st.markdown(f"""
                        <div style="
                            width: 100%;
                            max-width: 600px;
                            margin: 20px auto;
                            border: 2px solid #e0e0e0;
                            border-radius: 10px;
                            padding: 10px;
                            background-color: #f8f9fa;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                            text-align: center;
                        ">
                            <img src="{full_url}" alt="{filename}" style="
                                max-width: 100%;
                                height: auto;
                                border-radius: 5px;
                            ">
                        </div>
                        """, unsafe_allow_html=True)

                        # Show filename and actions below the image
                        st.write(f"**📁 {filename}**")

                        # Action buttons
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            if st.button("🗑️ Delete", key=f"large_delete_{image_id}", type="secondary"):
                                st.session_state[f"show_delete_confirm_{image_id}"] = True
                                st.rerun()
                        with col2:
                            if st.button("🎨 Transform", key=f"large_transform_{image_id}", type="primary"):
                                st.session_state['show_transform_any'] = True
                                st.session_state['transform_image_id'] = image_id
                                st.session_state['transform_filename'] = filename
                                st.rerun()

                        # Confirmation dialog (same as grid view)
                        if st.session_state.get(f"show_delete_confirm_{image_id}", False):
                            st.warning(
                                "⚠️ Are you sure you want to delete this image?")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("✅ Yes, Delete", key=f"large_confirm_delete_{image_id}", type="primary"):
                                    with st.spinner("Deleting image..."):
                                        success = image_api.delete_image(
                                            image_id, user_id)
                                        if success:
                                            st.success(
                                                "✅ Image deleted successfully!")
                                            for key in list(st.session_state.keys()):
                                                if key.startswith(f"user_images_{user_id}_page_"):
                                                    del st.session_state[key]
                                            st.session_state['force_refresh'] = True
                                            st.session_state[f"show_delete_confirm_{image_id}"] = False
                                            time.sleep(1)
                                            st.rerun()
                                        else:
                                            st.error(
                                                "❌ Failed to delete image")
                            with col2:
                                if st.button("❌ Cancel", key=f"large_cancel_delete_{image_id}"):
                                    st.session_state[f"show_delete_confirm_{image_id}"] = False
                                    st.rerun()

                        st.markdown("---")

            # Pagination navigation
            if len(images) > 0:
                st.markdown("---")
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

                with col1:
                    # Previous page button
                    if st.session_state['current_page'] > 1:
                        if st.button("⬅️ Previous", key="prev_page"):
                            st.session_state['current_page'] -= 1
                            # Clear cache for the new page to ensure fresh data
                            new_cache_key = f"user_images_{user_id}_page_{st.session_state['current_page']}"
                            if new_cache_key in st.session_state:
                                del st.session_state[new_cache_key]
                            st.rerun()
                    else:
                        st.button("⬅️ Previous", disabled=True,
                                  key="prev_page_disabled")

                with col2:
                    # First page button
                    if st.session_state['current_page'] > 1:
                        if st.button("⏮️ First", key="first_page"):
                            st.session_state['current_page'] = 1
                            # Clear cache for the first page to ensure fresh data
                            first_cache_key = f"user_images_{user_id}_page_1"
                            if first_cache_key in st.session_state:
                                del st.session_state[first_cache_key]
                            st.rerun()
                    else:
                        st.button("⏮️ First", disabled=True,
                                  key="first_page_disabled")

                with col3:
                    # Get total images and calculate total pages
                    total_images = image_api.get_total_images(user_id)
                    if total_images is not None:
                        total_pages = max(
                            1, (total_images + st.session_state['images_per_page'] - 1) // st.session_state['images_per_page'])
                        st.write(
                            f"**Page {st.session_state['current_page']} / {total_pages}**")
                    else:
                        st.write(
                            f"**Page {st.session_state['current_page']}**")

                with col4:
                    # Last page button (if we know there are more pages)
                    if has_next_page:
                        if st.button("⏭️ Last", key="last_page"):
                            if total_images is not None:
                                # Go to actual last page
                                last_page = max(
                                    1, (total_images + st.session_state['images_per_page'] - 1) // st.session_state['images_per_page'])
                                st.session_state['current_page'] = last_page
                            else:
                                # Fallback: jump ahead 5 pages
                                st.session_state['current_page'] += 5
                            # Clear cache for the new page to ensure fresh data
                            new_cache_key = f"user_images_{user_id}_page_{st.session_state['current_page']}"
                            if new_cache_key in st.session_state:
                                del st.session_state[new_cache_key]
                            st.rerun()
                    else:
                        st.button("⏭️ Last", disabled=True,
                                  key="last_page_disabled")

                with col5:
                    # Next page button
                    if has_next_page:
                        if st.button("➡️ Next", key="next_page"):
                            st.session_state['current_page'] += 1
                            # Clear cache for the new page to ensure fresh data
                            new_cache_key = f"user_images_{user_id}_page_{st.session_state['current_page']}"
                            if new_cache_key in st.session_state:
                                del st.session_state[new_cache_key]
                            st.rerun()
                    else:
                        st.button("➡️ Next", disabled=True,
                                  key="next_page_disabled")

    with tab2:
        # Track tab change
        st.session_state['last_active_tab'] = 'upload_image'
        st.header("➕ Upload Image")

        if "user" not in st.session_state or not st.session_state["user"]:
            st.error("❌ User session not found. Please log in again.")
            return

        user_id = st.session_state["user"]["id"]
        image_api = ImageAPI(settings.BACKEND_URL)

        # Use session state to track uploads and prevent re-uploads
        if 'last_uploaded_file' not in st.session_state:
            st.session_state.last_uploaded_file = None
        if 'upload_counter' not in st.session_state:
            st.session_state.upload_counter = 0

        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=['png', 'jpg', 'jpeg'],
            help="Supported formats: PNG, JPG, JPEG (Max 10MB)",
            key=f"file_uploader_{st.session_state.upload_counter}",
        )

        if uploaded_file is not None and uploaded_file != st.session_state.last_uploaded_file:
            # Show preview with consistent styling
            file_data = uploaded_file.getvalue()
            file_type = uploaded_file.type
            base64_data = base64.b64encode(file_data).decode()

            st.markdown(f"""
            <div class="image-container">
                <img src="data:{file_type};base64,{base64_data}" alt="Preview">
            </div>
            """, unsafe_allow_html=True)

            # Show upload button for better UX
            if st.button("📤 Upload", type="primary", key="upload_btn"):
                # Auto-upload on button click
                with st.spinner("🔄 Uploading image..."):
                    try:
                        # Read file data
                        file_data = uploaded_file.read()
                        filename = uploaded_file.name

                        # Upload to backend
                        result = image_api.upload_image(
                            file_data, filename, user_id)

                        if result and result.get("success"):
                            st.success("✅ Image uploaded successfully!")

                            # Update session state to prevent re-upload
                            st.session_state.upload_counter += 1
                            st.session_state.last_uploaded_file = uploaded_file

                            # Show uploaded image details
                            if "image" in result and result["image"]:
                                image_info = result["image"]
                                st.write(
                                    f"**Filename:** {image_info.get('filename', 'N/A')}")
                                st.write(
                                    f"**Size:** {image_info.get('file_size', 0) / 1024:.1f} KB")
                                st.write(
                                    f"**Type:** {image_info.get('mime_type', 'N/A')}")

                                # Display the uploaded image immediately with consistent styling
                                if image_info.get('url'):
                                    full_url = f"{settings.BACKEND_URL}{image_info['url']}"
                                    st.markdown(f"""
                                    <div class="image-container">
                                        <img src="{full_url}" alt="Uploaded image">
                                    </div>
                                    """, unsafe_allow_html=True)

                            # Auto-refresh to show new image in the list
                            st.info("🔄 Refreshing image list...")
                            # Small delay to ensure backend processing
                            time.sleep(1)
                            st.rerun()
                        else:
                            error_msg = result.get(
                                "message", "Unknown error") if result else "Upload failed"
                            st.error(f"❌ Upload failed: {error_msg}")

                    except Exception as e:
                        st.error(f"❌ Upload error: {str(e)}")
                        logger.error(f"Frontend upload error: {e}")

            # Show upload info
            st.info("💡 Click 'Upload Image' button to upload your selected image")

    with tab3:
        # Track tab change and auto-refetch when switching to Manage Images tab
        if 'last_active_tab' not in st.session_state:
            st.session_state['last_active_tab'] = 'manage_images'

        # Check if user just switched to Manage Images tab
        if st.session_state.get('last_active_tab') != 'manage_images':
            # Clear manage images cache to force fresh fetch
            user_id = st.session_state["user"]["id"]
            manage_cache_key = f"manage_images_{user_id}"
            if manage_cache_key in st.session_state:
                del st.session_state[manage_cache_key]
            st.session_state['last_active_tab'] = 'manage_images'

        st.header("✏️ Manage Images")

        if "user" not in st.session_state or not st.session_state["user"]:
            st.error("❌ User session not found. Please log in again.")
            return

        user_id = st.session_state["user"]["id"]
        image_api = ImageAPI(settings.BACKEND_URL)

        # Auto-refresh manage images when switching to this tab
        if 'last_manage_tab_visit' not in st.session_state:
            st.session_state['last_manage_tab_visit'] = 0

        # Check if we need to refresh (either force refresh or first visit after other tabs)
        current_upload_counter = st.session_state.get('upload_counter', 0)
        force_refresh = (st.session_state.get('force_refresh_manage', False) or
                         st.session_state['last_manage_tab_visit'] < current_upload_counter)

        # Update last visit counter
        st.session_state['last_manage_tab_visit'] = current_upload_counter

        # Get images for management
        cache_key = f"manage_images_{user_id}"

        if (cache_key not in st.session_state or force_refresh):
            try:
                with st.spinner("🔄 Loading images for management..."):
                    images = image_api.get_images(
                        user_id=user_id, page=1, limit=st.session_state.get('images_per_page', 10))
                    if images is None:
                        images = []
                    st.session_state[cache_key] = images
                    st.session_state['force_refresh_manage'] = False
            except Exception as e:
                st.error(f"❌ Error loading images: {str(e)}")
                images = st.session_state.get(cache_key, [])
        else:
            images = st.session_state[cache_key]

        if not images:
            st.info("No images found. Upload some images to manage them!")
        else:
            # First row: Total Images and View Mode (View Mode in most right)
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**Total Images:** {len(images)}")
            with col2:
                # Empty space
                pass
            with col3:
                # View mode toggle in the most right position
                manage_view_mode = st.selectbox(
                    "View Mode",
                    ["Grid", "Large View"],
                    key="manage_view_mode_selector"
                )

            # Second row: Delete All and Bulk Download buttons
            col1, col2, col3 = st.columns([2, 1, 1])
            with col2:
                # Bulk Download button
                if create_bulk_download_button():
                    try:
                        # Get all image IDs
                        image_ids = [img['id'] for img in images]
                        if image_ids:
                            # Download as ZIP
                            zip_data = image_api.download_bulk_images(
                                image_ids, user_id, "zip")
                            if zip_data:
                                trigger_direct_download(
                                    zip_data,
                                    f"images_{user_id}.zip",
                                    "application/zip"
                                )
                            else:
                                show_download_error(
                                    "Failed to create ZIP file")
                        else:
                            st.warning("⚠️ No images to download")
                    except Exception as e:
                        show_download_error(handle_download_error(e))

            with col3:
                # Delete All button under View Mode but in the most right of its own row
                if st.button("🗑️ Delete All", key="delete_all", type="secondary"):
                    st.session_state['show_delete_all_confirm'] = True
                    st.rerun()

            # Delete all confirmation
            if st.session_state.get('show_delete_all_confirm', False):
                st.warning(
                    "⚠️ Are you sure you want to delete ALL images? This cannot be undone!")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, Delete All", key="confirm_delete_all", type="primary"):
                        with st.spinner("Deleting all images..."):
                            deleted_count = 0
                            for image in images:
                                if image_api.delete_image(image['id'], user_id):
                                    deleted_count += 1

                            st.success(
                                f"✅ Deleted {deleted_count} images successfully!")
                            st.session_state['show_delete_all_confirm'] = False
                            st.session_state['force_refresh_manage'] = True
                            time.sleep(1)
                            st.rerun()

                with col2:
                    if st.button("❌ Cancel", key="cancel_delete_all"):
                        st.session_state['show_delete_all_confirm'] = False
                        st.rerun()

            # Image management
            st.subheader("📋 Individual Image Management")

            if manage_view_mode == "Grid":
                # Grid view for manage images
                for idx, image in enumerate(images):
                    with st.expander(f"🖼️ {image.get('original_name', 'Unknown')}"):
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            if image.get('url'):
                                full_url = f"{settings.BACKEND_URL}{image['url']}"
                                st.markdown(f"""
                                <div class="image-container">
                                    <img src="{full_url}" alt="{image.get('original_name', 'Unknown')}">
                                </div>
                                """, unsafe_allow_html=True)

                        with col2:
                            # Action buttons
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("🗑️ Delete", key=f"manage_delete_{image['id']}", type="secondary"):
                                    # Show confirmation dialog
                                    st.session_state[f"show_manage_delete_confirm_{image['id']}"] = True
                                    st.rerun()

                            with col_btn2:
                                if create_download_button(key=f"manage_download_{image['id']}"):
                                    try:
                                        image_data = image_api.download_single_image(
                                            image['id'], user_id)
                                        if image_data:
                                            trigger_direct_download(
                                                image_data,
                                                image.get(
                                                    'original_name', 'image'),
                                                image.get(
                                                    'mime_type', 'image/jpeg')
                                            )
                                        else:
                                            show_download_error(
                                                "Failed to download image")
                                    except Exception as e:
                                        show_download_error(
                                            handle_download_error(e))

                            if st.session_state.get(f"show_manage_delete_confirm_{image['id']}", False):
                                st.warning(
                                    "⚠️ Are you sure you want to delete this image?")
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("✅ Yes, Delete", key=f"manage_confirm_delete_{image['id']}", type="primary"):
                                        with st.spinner("Deleting..."):
                                            success = image_api.delete_image(
                                                image['id'], user_id)
                                            if success:
                                                st.success("✅ Deleted!")
                                                st.session_state['force_refresh_manage'] = True
                                                # Clear confirmation state
                                                st.session_state[
                                                    f"show_manage_delete_confirm_{image['id']}"] = False
                                                time.sleep(1)
                                                st.rerun()
                                            else:
                                                st.error("❌ Delete failed")
                                with col2:
                                    if st.button("❌ Cancel", key=f"manage_cancel_delete_{image['id']}"):
                                        st.session_state[f"show_manage_delete_confirm_{image['id']}"] = False
                                        st.rerun()
            else:
                # Large view for manage images
                for idx, image in enumerate(images):
                    if image.get('url'):
                        full_url = f"{settings.BACKEND_URL}{image['url']}"
                        filename = image.get('original_name', 'Unknown')

                        # Large view container
                        st.markdown(f"""
                        <div style="
                            width: 100%;
                            max-width: 600px;
                            margin: 20px auto;
                            border: 2px solid #e0e0e0;
                            border-radius: 10px;
                            padding: 10px;
                            background-color: #f8f9fa;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                            text-align: center;
                        ">
                            <img src="{full_url}" alt="{filename}" style="
                                max-width: 100%;
                                height: auto;
                                border-radius: 5px;
                            ">
                        </div>
                        """, unsafe_allow_html=True)

                        # Show filename and actions
                        st.write(f"**📁 {filename}**")

                        # Action buttons
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            if st.button("🗑️ Delete", key=f"manage_large_delete_{image['id']}", type="secondary"):
                                st.session_state[f"show_manage_delete_confirm_{image['id']}"] = True
                                st.rerun()

                        # Confirmation dialog
                        if st.session_state.get(f"show_manage_delete_confirm_{image['id']}", False):
                            st.warning(
                                "⚠️ Are you sure you want to delete this image?")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("✅ Yes, Delete", key=f"manage_large_confirm_delete_{image['id']}", type="primary"):
                                    with st.spinner("Deleting..."):
                                        success = image_api.delete_image(
                                            image['id'], user_id)
                                        if success:
                                            st.success("✅ Deleted!")
                                            st.session_state['force_refresh_manage'] = True
                                            st.session_state[f"show_manage_delete_confirm_{image['id']}"] = False
                                            time.sleep(1)
                                            st.rerun()
                                        else:
                                            st.error("❌ Delete failed")
                            with col2:
                                if st.button("❌ Cancel", key=f"manage_large_cancel_delete_{image['id']}"):
                                    st.session_state[f"show_manage_delete_confirm_{image['id']}"] = False
                                    st.rerun()

                        st.markdown("---")


if __name__ == "__main__":
    main()
