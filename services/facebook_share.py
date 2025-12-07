"""
Facebook Graph API integration service.
Handles posting images and text to Facebook pages.
"""

from typing import Dict, Optional, Tuple
import requests


class FacebookService:
    """Service for interacting with Facebook Graph API."""

    def __init__(self, page_id: str, access_token: str):
        """
        Initialize Facebook service.

        Args:
            page_id: Facebook Page ID
            access_token: Page access token (long-lived recommended)
        """
        self.page_id = page_id
        self.access_token = access_token
        self.graph_api_base = "https://graph.facebook.com/v18.0"

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to Facebook Graph API.

        Returns:
            Tuple of (success, message)
        """
        try:
            response = requests.get(
                f"{self.graph_api_base}/{self.page_id}",
                params={'access_token': self.access_token, 'fields': 'name'},
                timeout=10
            )
            if response.status_code == 200:
                page_name = response.json().get('name', 'Unknown')
                return True, f"Connected to page: {page_name}"
            else:
                error = response.json().get('error', {})
                return False, f"Authentication failed: {error.get('message', 'Unknown error')}"
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"

    def upload_photo(self, image_path: str, caption: str) -> Tuple[bool, str]:
        """
        Upload photo to Facebook page.

        Args:
            image_path: Path to the image file
            caption: Photo caption/description

        Returns:
            Tuple of (success, message/post_id)
        """
        try:
            # Read image file
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Prepare the request
            url = f"{self.graph_api_base}/{self.page_id}/photos"
            files = {'source': image_data}
            data = {
                'access_token': self.access_token,
                'message': caption,
            }

            # Upload photo
            response = requests.post(url, files=files, data=data, timeout=30)

            if response.status_code == 200:
                post_id = response.json().get('id', '')
                post_url = f"https://www.facebook.com/{post_id}"
                return True, post_url
            else:
                error = response.json().get('error', {})
                return False, f"Failed to upload: {error.get('message', 'Unknown error')}"

        except Exception as e:
            return False, f"Error uploading photo: {str(e)}"

    def create_post(self, message: str, link: Optional[str] = None) -> Tuple[bool, str]:
        """
        Create a text post on Facebook page.

        Args:
            message: Post message/text
            link: Optional link to include

        Returns:
            Tuple of (success, message/post_id)
        """
        try:
            url = f"{self.graph_api_base}/{self.page_id}/feed"
            data = {
                'access_token': self.access_token,
                'message': message,
            }
            if link:
                data['link'] = link

            response = requests.post(url, data=data, timeout=30)

            if response.status_code == 200:
                post_id = response.json().get('id', '')
                return True, post_id
            else:
                error = response.json().get('error', {})
                return False, f"Failed to create post: {error.get('message', 'Unknown error')}"

        except Exception as e:
            return False, f"Error creating post: {str(e)}"

    def share(self, image_path: str, caption: str) -> Tuple[bool, str]:
        """
        Share image and caption to Facebook (high-level method).

        Args:
            image_path: Path to the image file
            caption: Post caption/description

        Returns:
            Tuple of (success, message/url)
        """
        return self.upload_photo(image_path, caption)
