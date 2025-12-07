"""
Image processing utilities for Postboi.
Handles image resizing, validation, thumbnail generation, and EXIF data.
"""

import os
from typing import Tuple, Optional
from PIL import Image, ExifTags
from io import BytesIO


class ImageUtils:
    """Utility class for image processing operations."""

    @staticmethod
    def validate_image(image_path: str, max_size_mb: int = 10,
                      supported_formats: list = None) -> Tuple[bool, str]:
        """
        Validate image file.

        Args:
            image_path: Path to the image file
            max_size_mb: Maximum allowed file size in MB
            supported_formats: List of supported formats (e.g., ['jpg', 'png'])

        Returns:
            Tuple of (is_valid, error_message)
        """
        if supported_formats is None:
            supported_formats = ['jpg', 'jpeg', 'png', 'webp']

        # Check if file exists
        if not os.path.exists(image_path):
            return False, "File does not exist"

        # Check file size
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return False, f"File size ({file_size_mb:.2f}MB) exceeds limit ({max_size_mb}MB)"

        # Check format
        try:
            with Image.open(image_path) as img:
                image_format = img.format.lower() if img.format else ''
                if image_format not in supported_formats:
                    return False, f"Unsupported format: {image_format}"
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"

        return True, "Valid image"

    @staticmethod
    def resize_image(image_path: str, max_width: int = 1920, max_height: int = 1920,
                    quality: int = 85) -> Optional[str]:
        """
        Resize image while maintaining aspect ratio.

        Args:
            image_path: Path to the image file
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            quality: JPEG quality (1-100)

        Returns:
            Path to resized image, or None if failed
        """
        try:
            with Image.open(image_path) as img:
                # Preserve EXIF orientation
                img = ImageUtils._correct_orientation(img)

                # Calculate new size maintaining aspect ratio
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

                # Save resized image
                output_path = image_path.replace('.', '_resized.')
                img.save(output_path, quality=quality, optimize=True)

                return output_path

        except Exception as e:
            print(f"Error resizing image: {str(e)}")
            return None

    @staticmethod
    def create_thumbnail(image_path: str, size: Tuple[int, int] = (300, 300)) -> Optional[str]:
        """
        Create a thumbnail of the image.

        Args:
            image_path: Path to the image file
            size: Thumbnail size as (width, height)

        Returns:
            Path to thumbnail, or None if failed
        """
        try:
            with Image.open(image_path) as img:
                # Preserve EXIF orientation
                img = ImageUtils._correct_orientation(img)

                # Create thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)

                # Save thumbnail
                output_path = image_path.replace('.', '_thumb.')
                img.save(output_path, quality=80)

                return output_path

        except Exception as e:
            print(f"Error creating thumbnail: {str(e)}")
            return None

    @staticmethod
    def _correct_orientation(img: Image.Image) -> Image.Image:
        """
        Correct image orientation based on EXIF data.

        Args:
            img: PIL Image object

        Returns:
            Corrected PIL Image object
        """
        try:
            # Get EXIF data using the public API
            exif = img.getexif()
            if exif is not None:
                # Get orientation tag
                orientation = exif.get(0x0112)  # 0x0112 is the Orientation tag

                # Rotate based on orientation
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)

        except (AttributeError, KeyError, IndexError):
            # No EXIF data or orientation tag
            pass

        return img

    @staticmethod
    def get_image_info(image_path: str) -> dict:
        """
        Get information about an image.

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary with image information
        """
        try:
            with Image.open(image_path) as img:
                info = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'file_size_mb': os.path.getsize(image_path) / (1024 * 1024),
                }
                return info
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def convert_to_jpg(image_path: str, quality: int = 90) -> Optional[str]:
        """
        Convert image to JPEG format.

        Args:
            image_path: Path to the image file
            quality: JPEG quality (1-100)

        Returns:
            Path to converted image, or None if failed
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background

                # Save as JPEG
                output_path = os.path.splitext(image_path)[0] + '.jpg'
                img.save(output_path, 'JPEG', quality=quality, optimize=True)

                return output_path

        except Exception as e:
            print(f"Error converting to JPEG: {str(e)}")
            return None
