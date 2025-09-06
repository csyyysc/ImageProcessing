"""
File handling utilities for image uploads
"""

import time
import shutil
import logging
from typing import Dict, Tuple
from pathlib import Path
from fastapi import UploadFile

logger = logging.getLogger(__name__)


UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/jpg', 'image/png',
    'image/gif', 'image/webp'
}


def ensure_upload_directory():
    """Ensure upload directory exists"""

    UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
    logger.info(f"Upload directory ready: {UPLOAD_DIR.absolute()}")


def validate_image_file(file: UploadFile) -> Tuple[bool, str]:
    """Validate uploaded image file size and type"""

    if file.size and file.size > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"

    if file.filename:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"

    if file.content_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid file type. File type: {file.content_type}"

    return True, "Valid"


def generate_unique_filename(original_filename: str, user_id: int) -> str:
    """Generate a unique filename while preserving extension"""

    if not original_filename:
        return f"{user_id}_{int(time.time())}.jpg"

    file_ext = Path(original_filename).suffix.lower()
    if not file_ext:
        file_ext = '.jpg'

    return f"{user_id}_{int(time.time())}{file_ext}"


async def save_uploaded_file(file: UploadFile, user_id: int) -> Dict[str, any]:
    """Save uploaded file and return file information"""

    is_valid, message = validate_image_file(file)
    if not is_valid:
        raise ValueError(message)

    unique_filename = generate_unique_filename(file.filename, user_id)
    file_path = UPLOAD_DIR / unique_filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = file_path.stat().st_size
        file.file.seek(0)

        logger.info(f"File saved: {file_path} ({file_size} bytes)")

        return {
            'filename': unique_filename,
            'original_name': file.filename or unique_filename,
            'file_path': str(file_path),
            'file_size': file_size,
            'mime_type': file.content_type,
            'url': f"/uploads/{unique_filename}"
        }

    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        logger.error(f"Error saving file: {e}")
        raise ValueError(f"Failed to save file, please try again.")


def delete_file(file_path: str) -> bool:
    """Delete a file from the filesystem"""

    try:
        Path(file_path).unlink(missing_ok=True)
        logger.info(f"File deleted: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        raise ValueError(f"Failed to delete file, please try again.")


def get_file_url(filename: str) -> str:
    """Get the URL for accessing a file"""

    return f"/uploads/{filename}"
