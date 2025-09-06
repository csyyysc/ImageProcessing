import os
import uuid
import logging
from typing import Dict, Any
from fastapi import UploadFile
from PIL import Image, ImageFilter, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


def extract_image_info(image: UploadFile) -> dict:
    """Extract image information"""

    original_name = image.filename
    file_size = image.size if hasattr(image, 'size') else 0
    mime_type = image.content_type

    # Generate unique filename
    file_extension = os.path.splitext(
        original_name)[1] if original_name else '.jpg'
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Create file path (assuming uploads directory exists)
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)

    # Save file to disk
    with open(file_path, "wb") as buffer:
        content = image.file.read()
        buffer.write(content)
        if not file_size:
            file_size = len(content)

    return {
        "filename": unique_filename,
        "original_name": original_name,
        "file_path": file_path,
        "file_size": file_size,
        "mime_type": mime_type
    }


def transform_image(file_path: str, transformations: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply multiple transformations to an image and save the result.

    Args:
        file_path: Path to the original image file
        transformations: Dictionary containing transformation parameters

    Returns:
        Dictionary with new file information
    """

    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary (for JPEG compatibility)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            logger.info(f"Starting transformations on {file_path}")

            transformed_img = img.copy()

            # 1. Resize
            if transformations.get('resize'):
                resize_params: Dict[str, int] = transformations['resize']
                width = resize_params.get('width')
                height = resize_params.get('height')
                if width and height:
                    transformed_img = transformed_img.resize(
                        (width, height), Image.Resampling.LANCZOS)
                    logger.info(f"Applied resize: {width}x{height}")

            # 2. Crop
            if transformations.get('crop'):
                crop_params: Dict[str, int] = transformations['crop']
                x = crop_params.get('x', 0)
                y = crop_params.get('y', 0)
                w = crop_params.get('width')
                h = crop_params.get('height')
                if w and h:
                    # Ensure crop area is within image bounds
                    x = max(0, min(x, transformed_img.width - w))
                    y = max(0, min(y, transformed_img.height - h))
                    w = min(w, transformed_img.width - x)
                    h = min(h, transformed_img.height - y)
                    transformed_img = transformed_img.crop(
                        (x, y, x + w, y + h))
                    logger.info(f"Applied crop: ({x}, {y}, {x + w}, {y + h})")

            # 3. Rotate
            if transformations.get('rotate'):
                rotate_params: Dict[str, int] = transformations['rotate']
                angle = rotate_params.get('angle', 0)
                if angle != 0:
                    transformed_img = transformed_img.rotate(
                        angle, expand=True)
                    logger.info(f"Applied rotation: {angle}°")

            # 4. Flip (horizontal - left to right)
            if transformations.get('flip'):
                transformed_img = transformed_img.transpose(
                    Image.Transpose.FLIP_LEFT_RIGHT)
                logger.info("Applied horizontal flip")

            # 5. Mirror (vertical - top to bottom)
            if transformations.get('mirror'):
                transformed_img = transformed_img.transpose(
                    Image.Transpose.FLIP_TOP_BOTTOM)
                logger.info("Applied vertical mirror")

            # 6. Apply filters
            if transformations.get('filter'):
                filter_params: Dict[str, str] = transformations['filter']
                filter_type = filter_params.get('type', 'None')

                if filter_type == 'Grayscale':
                    transformed_img = transformed_img.convert(
                        'L').convert('RGB')
                elif filter_type == 'Sepia':
                    transformed_img = apply_sepia_filter(transformed_img)
                elif filter_type == 'Blur':
                    transformed_img = transformed_img.filter(ImageFilter.BLUR)
                elif filter_type == 'Sharpen':
                    transformed_img = transformed_img.filter(
                        ImageFilter.SHARPEN)
                elif filter_type == 'Edge Detection':
                    transformed_img = transformed_img.filter(
                        ImageFilter.FIND_EDGES)

                logger.info(f"Applied filter: {filter_type}")

            # 7. Add watermark
            if transformations.get('watermark'):
                watermark_params: Dict[str, str] = transformations['watermark']
                text = watermark_params.get('text', 'SAMPLE')
                x = watermark_params.get('x', 0)
                y = watermark_params.get('y', 0)
                transformed_img = add_watermark(transformed_img, text, x, y)
                logger.info(f"Applied watermark: '{text}' at ({x}, {y})")

            # 8. Determine output format and quality
            output_format = 'JPEG'
            quality = 85

            if transformations.get('format'):
                format_params: Dict[str, str] = transformations['format']
                output_format = format_params.get('type', 'JPEG')

            if transformations.get('compress'):
                compress_params: Dict[str, int] = transformations['compress']
                quality = compress_params.get('quality', 85)

            # Generate new filename
            original_name = os.path.basename(file_path)
            name, _ = os.path.splitext(original_name)
            new_filename = f"{name}_transformed_{uuid.uuid4().hex[:8]}.{output_format.lower()}"
            new_file_path = os.path.join(
                os.path.dirname(file_path), new_filename)

            # Save transformed image
            save_kwargs = {'format': output_format}
            if output_format in ['JPEG', 'WEBP']:
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True

            transformed_img.save(new_file_path, **save_kwargs)

            # Get file size
            file_size = os.path.getsize(new_file_path)

            logger.info(f"Transformed image saved: {new_file_path}")

            return {
                'filename': new_filename,
                'file_path': new_file_path,
                'file_size': file_size,
                'mime_type': f'image/{output_format.lower()}',
                'original_name': original_name
            }

    except Exception as e:
        logger.error(f"Error transforming image {file_path}: {e}")
        raise ValueError(f"Failed to transform image: {str(e)}")


def apply_sepia_filter(img: Image.Image) -> Image.Image:
    """Apply sepia filter to an image"""

    # Convert to grayscale first
    gray = img.convert('L')

    # Create sepia effect
    sepia = Image.new('RGB', img.size)
    pixels = gray.getdata()
    sepia_pixels = []

    for pixel in pixels:
        r = min(255, int(pixel * 1.2))
        g = min(255, int(pixel * 0.9))
        b = min(255, int(pixel * 0.6))
        sepia_pixels.append((r, g, b))

    sepia.putdata(sepia_pixels)
    return sepia


def add_watermark(img: Image.Image, text: str, x: int, y: int) -> Image.Image:
    """Add text watermark to an image"""

    watermarked = img.copy()

    # Create drawing context
    draw = ImageDraw.Draw(watermarked)

    # Try to use a default font, fallback to basic if not available
    try:
        # Try to use a system font
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        try:
            font = ImageFont.load_default()
        except:
            font = None

    # Calculate text size
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width = len(text) * 10
        text_height = 20

    # Ensure watermark fits within image bounds
    x = max(0, min(x, img.width - text_width))
    y = max(0, min(y, img.height - text_height))

    # Add semi-transparent background
    overlay = Image.new(
        'RGBA', (text_width + 10, text_height + 10), (0, 0, 0, 128))
    watermarked.paste(overlay, (x - 5, y - 5), overlay)

    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    return watermarked
