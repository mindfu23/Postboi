"""
Instagram Graph API integration service.
Handles posting images to Instagram Business/Creator accounts.
Includes fallback to native share intent for personal accounts.
"""

from typing import Dict, Optional, Tuple
import requests
import time


class InstagramService:
    """Service for interacting with Instagram Graph API."""

    def __init__(self, business_account_id: str, access_token: str):
        """
        Initialize Instagram service.

        Args:
            business_account_id: Instagram Business Account ID
            access_token: Facebook access token with Instagram permissions
        """
        self.business_account_id = business_account_id
        self.access_token = access_token
        self.graph_api_base = "https://graph.facebook.com/v18.0"

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to Instagram Graph API.

        Returns:
            Tuple of (success, message)
        """
        try:
            response = requests.get(
                f"{self.graph_api_base}/{self.business_account_id}",
                params={'access_token': self.access_token, 'fields': 'username'},
                timeout=10
            )
            if response.status_code == 200:
                username = response.json().get('username', 'Unknown')
                return True, f"Connected to Instagram: @{username}"
            else:
                error = response.json().get('error', {})
                return False, f"Authentication failed: {error.get('message', 'Unknown error')}"
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"

    def create_media_container(self, image_url: str, caption: str) -> Optional[str]:
        """
        Create a media container for Instagram post.

        Args:
            image_url: Public URL of the image to post
            caption: Post caption

        Returns:
            Container ID if successful, None otherwise
        """
        try:
            url = f"{self.graph_api_base}/{self.business_account_id}/media"
            params = {
                'access_token': self.access_token,
                'image_url': image_url,
                'caption': caption,
            }

            response = requests.post(url, params=params, timeout=30)

            if response.status_code == 200:
                container_id = response.json().get('id')
                return container_id
            else:
                error = response.json().get('error', {})
                print(f"Failed to create container: {error.get('message', 'Unknown error')}")
                return None

        except Exception as e:
            print(f"Error creating media container: {str(e)}")
            return None

    def publish_media(self, container_id: str) -> Tuple[bool, str]:
        """
        Publish a media container to Instagram.

        Args:
            container_id: Media container ID from create_media_container

        Returns:
            Tuple of (success, message/post_id)
        """
        try:
            url = f"{self.graph_api_base}/{self.business_account_id}/media_publish"
            params = {
                'access_token': self.access_token,
                'creation_id': container_id,
            }

            response = requests.post(url, params=params, timeout=30)

            if response.status_code == 200:
                post_id = response.json().get('id', '')
                return True, post_id
            else:
                error = response.json().get('error', {})
                return False, f"Failed to publish: {error.get('message', 'Unknown error')}"

        except Exception as e:
            return False, f"Error publishing media: {str(e)}"

    def share_via_api(self, image_url: str, caption: str) -> Tuple[bool, str]:
        """
        Share image via Instagram Graph API (requires publicly accessible image URL).

        Args:
            image_url: Public URL of the image
            caption: Post caption

        Returns:
            Tuple of (success, message/url)
        """
        # Create media container
        container_id = self.create_media_container(image_url, caption)
        if not container_id:
            return False, "Failed to create media container"

        # Wait a moment for processing
        time.sleep(2)

        # Publish media
        success, result = self.publish_media(container_id)
        if success:
            return True, f"Posted to Instagram: {result}"
        else:
            return False, result

    def share(self, image_path: str, caption: str) -> Tuple[bool, str]:
        """
        Share image and caption to Instagram (high-level method).

        Note: This method requires the image to be hosted at a public URL.
        For local files, you'll need to upload to a temporary hosting service first,
        or use the native share intent on mobile devices.

        Args:
            image_path: Path to the image file (or public URL)
            caption: Post caption

        Returns:
            Tuple of (success, message)
        """
        # Check if it's a URL
        if image_path.startswith('http://') or image_path.startswith('https://'):
            return self.share_via_api(image_path, caption)
        else:
            return False, ("Instagram API requires a public image URL. "
                         "Please host the image online first, or use native share intent on mobile.")

    def get_native_share_data(self, caption: str) -> Dict[str, str]:
        """
        Get data for native Instagram share intent.

        Args:
            caption: Caption to copy to clipboard for manual pasting

        Returns:
            Dictionary with share intent data
        """
        return {
            'package': 'com.instagram.android',
            'type': 'image/*',
            'caption': caption,
            'message': 'Copy the caption above, then select Instagram to share!'
        }
