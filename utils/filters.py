"""
Image filters for Postboi.
Provides various image filters and effects.
"""

from typing import Optional
from PIL import Image, ImageEnhance, ImageFilter


class ImageFilters:
    """Collection of image filters and effects."""

    @staticmethod
    def apply_filter(image_path: str, filter_name: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Apply a filter to an image.

        Args:
            image_path: Path to the input image
            filter_name: Name of the filter to apply
            output_path: Path for output image (optional)

        Returns:
            Path to filtered image, or None if failed
        """
        try:
            with Image.open(image_path) as img:
                # Apply the specified filter
                if filter_name == 'grayscale':
                    filtered_img = ImageFilters.grayscale(img)
                elif filter_name == 'sepia':
                    filtered_img = ImageFilters.sepia(img)
                elif filter_name == 'vintage':
                    filtered_img = ImageFilters.vintage(img)
                elif filter_name == 'bright':
                    filtered_img = ImageFilters.adjust_brightness(img, 1.3)
                elif filter_name == 'dark':
                    filtered_img = ImageFilters.adjust_brightness(img, 0.7)
                elif filter_name == 'high_contrast':
                    filtered_img = ImageFilters.adjust_contrast(img, 1.5)
                elif filter_name == 'blur':
                    filtered_img = ImageFilters.blur(img)
                elif filter_name == 'sharpen':
                    filtered_img = ImageFilters.sharpen(img)
                else:
                    return None

                # Save filtered image
                if not output_path:
                    output_path = image_path.replace('.', f'_{filter_name}.')

                filtered_img.save(output_path)
                return output_path

        except Exception as e:
            print(f"Error applying filter: {str(e)}")
            return None

    @staticmethod
    def grayscale(img: Image.Image) -> Image.Image:
        """Convert image to grayscale."""
        return img.convert('L').convert('RGB')

    @staticmethod
    def sepia(img: Image.Image, intensity: float = 1.0) -> Image.Image:
        """
        Apply sepia tone effect.

        Args:
            img: PIL Image object
            intensity: Sepia intensity (0.0 to 1.0)

        Returns:
            Filtered PIL Image object
        """
        # Convert to grayscale first
        grayscale_img = img.convert('L')

        # Create sepia tone
        sepia_img = Image.new('RGB', img.size)
        pixels = sepia_img.load()
        gray_pixels = grayscale_img.load()

        for y in range(img.size[1]):
            for x in range(img.size[0]):
                gray = gray_pixels[x, y]
                # Apply sepia transformation
                r = min(255, int(gray + 2 * intensity * 40))
                g = min(255, int(gray + intensity * 20))
                b = max(0, int(gray - intensity * 20))
                pixels[x, y] = (r, g, b)

        return sepia_img

    @staticmethod
    def vintage(img: Image.Image) -> Image.Image:
        """
        Apply vintage effect (sepia + contrast + vignette).

        Args:
            img: PIL Image object

        Returns:
            Filtered PIL Image object
        """
        # Apply sepia
        vintage_img = ImageFilters.sepia(img, intensity=0.5)

        # Increase contrast slightly
        enhancer = ImageEnhance.Contrast(vintage_img)
        vintage_img = enhancer.enhance(1.2)

        # Reduce brightness slightly
        enhancer = ImageEnhance.Brightness(vintage_img)
        vintage_img = enhancer.enhance(0.95)

        return vintage_img

    @staticmethod
    def adjust_brightness(img: Image.Image, factor: float) -> Image.Image:
        """
        Adjust image brightness.

        Args:
            img: PIL Image object
            factor: Brightness factor (< 1.0 darker, > 1.0 brighter)

        Returns:
            Adjusted PIL Image object
        """
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)

    @staticmethod
    def adjust_contrast(img: Image.Image, factor: float) -> Image.Image:
        """
        Adjust image contrast.

        Args:
            img: PIL Image object
            factor: Contrast factor (< 1.0 less contrast, > 1.0 more contrast)

        Returns:
            Adjusted PIL Image object
        """
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)

    @staticmethod
    def blur(img: Image.Image, radius: int = 2) -> Image.Image:
        """
        Apply blur effect.

        Args:
            img: PIL Image object
            radius: Blur radius

        Returns:
            Blurred PIL Image object
        """
        return img.filter(ImageFilter.GaussianBlur(radius))

    @staticmethod
    def sharpen(img: Image.Image) -> Image.Image:
        """
        Apply sharpen effect.

        Args:
            img: PIL Image object

        Returns:
            Sharpened PIL Image object
        """
        return img.filter(ImageFilter.SHARPEN)

    @staticmethod
    def get_available_filters() -> list:
        """
        Get list of available filter names.

        Returns:
            List of filter names
        """
        return [
            'none',
            'grayscale',
            'sepia',
            'vintage',
            'bright',
            'dark',
            'high_contrast',
            'blur',
            'sharpen',
        ]

    @staticmethod
    def preview_filter(img: Image.Image, filter_name: str) -> Image.Image:
        """
        Generate a preview of a filter applied to an image.

        Args:
            img: PIL Image object
            filter_name: Name of the filter

        Returns:
            Filtered PIL Image object for preview
        """
        if filter_name == 'none':
            return img

        if filter_name == 'grayscale':
            return ImageFilters.grayscale(img)
        elif filter_name == 'sepia':
            return ImageFilters.sepia(img)
        elif filter_name == 'vintage':
            return ImageFilters.vintage(img)
        elif filter_name == 'bright':
            return ImageFilters.adjust_brightness(img, 1.3)
        elif filter_name == 'dark':
            return ImageFilters.adjust_brightness(img, 0.7)
        elif filter_name == 'high_contrast':
            return ImageFilters.adjust_contrast(img, 1.5)
        elif filter_name == 'blur':
            return ImageFilters.blur(img)
        elif filter_name == 'sharpen':
            return ImageFilters.sharpen(img)
        else:
            return img
