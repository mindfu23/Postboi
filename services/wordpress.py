"""
WordPress REST API integration service.
Handles image uploads and post creation using WordPress REST API.
"""

import base64
import mimetypes
from typing import Dict, Optional, Tuple
import requests
from requests.auth import HTTPBasicAuth


class WordPressService:
    """Service for interacting with WordPress REST API."""

    def __init__(self, site_url: str, username: str, app_password: str):
        """
        Initialize WordPress service.

        Args:
            site_url: WordPress site URL (e.g., 'https://yoursite.wordpress.com')
            username: WordPress username
            app_password: WordPress application password
        """
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.app_password = app_password.replace(' ', '')  # Remove spaces from app password
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        self.auth = HTTPBasicAuth(username, app_password)

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to WordPress API.

        Returns:
            Tuple of (success, message)
        """
        try:
            response = requests.get(
                f"{self.api_base}/users/me",
                auth=self.auth,
                timeout=10
            )
            if response.status_code == 200:
                return True, "Connection successful"
            else:
                return False, f"Authentication failed: {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"

    def upload_image(self, image_path: str) -> Optional[int]:
        """
        Upload image to WordPress media library.

        Args:
            image_path: Path to the image file

        Returns:
            Media ID if successful, None otherwise
        """
        try:
            # Read image file
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type:
                mime_type = 'image/jpeg'

            # Prepare headers
            headers = {
                'Content-Type': mime_type,
                'Content-Disposition': f'attachment; filename="{image_path.split("/")[-1]}"'
            }

            # Upload to media library
            response = requests.post(
                f"{self.api_base}/media",
                headers=headers,
                data=image_data,
                auth=self.auth,
                timeout=30
            )

            if response.status_code == 201:
                media_id = response.json().get('id')
                return media_id
            else:
                print(f"Failed to upload image: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Error uploading image: {str(e)}")
            return None

    def create_post(self, title: str, content: str, media_id: Optional[int] = None,
                    status: str = 'publish') -> Tuple[bool, str]:
        """
        Create a new WordPress post.

        Args:
            title: Post title
            content: Post content/caption
            media_id: Featured image media ID (optional)
            status: Post status ('draft', 'publish', 'future')

        Returns:
            Tuple of (success, message/post_url)
        """
        try:
            post_data = {
                'title': title,
                'content': content,
                'status': status,
            }

            if media_id:
                post_data['featured_media'] = media_id

            response = requests.post(
                f"{self.api_base}/posts",
                json=post_data,
                auth=self.auth,
                timeout=30
            )

            if response.status_code == 201:
                post_url = response.json().get('link', '')
                return True, post_url
            else:
                error_msg = response.json().get('message', f'Status: {response.status_code}')
                return False, f"Failed to create post: {error_msg}"

        except Exception as e:
            return False, f"Error creating post: {str(e)}"

    def share(self, image_path: str, caption: str, title: Optional[str] = None) -> Tuple[bool, str]:
        """
        Share image and caption to WordPress (high-level method).

        Args:
            image_path: Path to the image file
            caption: Post caption/content
            title: Post title (uses first line of caption if not provided)

        Returns:
            Tuple of (success, message/url)
        """
        # Use first line of caption as title if not provided
        if not title:
            title = caption.split('\n')[0][:100] if caption else 'New Post'

        # Upload image
        media_id = self.upload_image(image_path)
        if not media_id:
            return False, "Failed to upload image to WordPress"

        # Create post with featured image
        success, result = self.create_post(title, caption, media_id)
        return success, result
