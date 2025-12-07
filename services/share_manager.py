"""
Share Manager - Coordinates simultaneous posting to multiple platforms.
Uses ThreadPoolExecutor for concurrent operations.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional
from services.wordpress import WordPressService
from services.facebook_share import FacebookService
from services.instagram_share import InstagramService


class ShareManager:
    """Manages simultaneous sharing to multiple social media platforms."""

    def __init__(self, wordpress_service: Optional[WordPressService] = None,
                 facebook_service: Optional[FacebookService] = None,
                 instagram_service: Optional[InstagramService] = None,
                 max_workers: int = 3):
        """
        Initialize ShareManager with platform services.

        Args:
            wordpress_service: WordPress service instance
            facebook_service: Facebook service instance
            instagram_service: Instagram service instance
            max_workers: Maximum concurrent upload threads
        """
        self.wordpress_service = wordpress_service
        self.facebook_service = facebook_service
        self.instagram_service = instagram_service
        self.max_workers = max_workers

    def share_to_platform(self, platform: str, image_path: str, caption: str) -> Tuple[str, bool, str]:
        """
        Share to a single platform.

        Args:
            platform: Platform name ('wordpress', 'facebook', 'instagram')
            image_path: Path to the image file
            caption: Post caption

        Returns:
            Tuple of (platform, success, message)
        """
        try:
            if platform == 'wordpress' and self.wordpress_service:
                success, message = self.wordpress_service.share(image_path, caption)
                return ('WordPress', success, message)

            elif platform == 'facebook' and self.facebook_service:
                success, message = self.facebook_service.share(image_path, caption)
                return ('Facebook', success, message)

            elif platform == 'instagram' and self.instagram_service:
                success, message = self.instagram_service.share(image_path, caption)
                return ('Instagram', success, message)

            else:
                return (platform.capitalize(), False, "Service not configured")

        except Exception as e:
            return (platform.capitalize(), False, f"Error: {str(e)}")

    def share_to_multiple(self, platforms: List[str], image_path: str,
                         caption: str) -> Dict[str, Tuple[bool, str]]:
        """
        Share to multiple platforms simultaneously.

        Args:
            platforms: List of platform names ('wordpress', 'facebook', 'instagram')
            image_path: Path to the image file
            caption: Post caption

        Returns:
            Dictionary mapping platform names to (success, message) tuples
        """
        results = {}

        # Use ThreadPoolExecutor for concurrent uploads
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_platform = {
                executor.submit(self.share_to_platform, platform, image_path, caption): platform
                for platform in platforms
            }

            # Collect results as they complete
            for future in as_completed(future_to_platform):
                platform_name, success, message = future.result()
                results[platform_name] = (success, message)

        return results

    def test_all_connections(self) -> Dict[str, Tuple[bool, str]]:
        """
        Test connections to all configured platforms.

        Returns:
            Dictionary mapping platform names to (success, message) tuples
        """
        results = {}

        if self.wordpress_service:
            results['WordPress'] = self.wordpress_service.test_connection()

        if self.facebook_service:
            results['Facebook'] = self.facebook_service.test_connection()

        if self.instagram_service:
            results['Instagram'] = self.instagram_service.test_connection()

        return results

    def get_summary(self, results: Dict[str, Tuple[bool, str]]) -> str:
        """
        Generate a summary message from sharing results.

        Args:
            results: Dictionary of platform results

        Returns:
            Formatted summary string
        """
        successful = [platform for platform, (success, _) in results.items() if success]
        failed = [platform for platform, (success, _) in results.items() if not success]

        summary_parts = []

        if successful:
            summary_parts.append(f"✅ Successfully posted to: {', '.join(successful)}")

        if failed:
            summary_parts.append(f"❌ Failed to post to: {', '.join(failed)}")

        # Add details
        for platform, (success, message) in results.items():
            emoji = "✅" if success else "❌"
            summary_parts.append(f"\n{emoji} {platform}: {message}")

        return '\n'.join(summary_parts)
