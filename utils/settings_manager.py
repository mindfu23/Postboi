"""
Settings Manager for Postboi
Handles persistent storage of user credentials and app settings.
Supports per-user settings when linked to an authenticated user.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class SettingsManager:
    """Manages persistent storage of user settings and credentials."""

    def __init__(self, app_name: str = "Postboi", user_id: Optional[str] = None):
        """
        Initialize settings manager.
        
        Args:
            app_name: Application name for settings directory
            user_id: Optional user ID to load user-specific settings
        """
        self.app_name = app_name
        self._user_id = user_id
        self._settings_dir = self._get_settings_dir()
        self._settings_file = self._get_settings_file()
        self._settings: Dict[str, Any] = {}
        self._load_settings()
    
    def set_user(self, user_id: Optional[str]):
        """
        Set or change the current user.
        Loads user-specific settings if user_id provided.
        
        Args:
            user_id: User ID to switch to, or None for default settings
        """
        if user_id != self._user_id:
            self._user_id = user_id
            self._settings_file = self._get_settings_file()
            self._load_settings()
    
    def _get_settings_file(self) -> Path:
        """Get settings file path, user-specific if user_id is set."""
        if self._user_id:
            return self._settings_dir / f"settings_{self._user_id[:16]}.json"
        return self._settings_dir / "settings.json"

    def _get_settings_dir(self) -> Path:
        """Get platform-specific settings directory."""
        # Check for different platforms
        if os.name == 'nt':  # Windows
            base_dir = Path(os.environ.get('APPDATA', Path.home()))
        elif os.name == 'posix':
            # macOS and Linux
            if 'darwin' in os.uname().sysname.lower():
                base_dir = Path.home() / 'Library' / 'Application Support'
            else:
                base_dir = Path.home() / '.config'
        else:
            base_dir = Path.home()

        settings_dir = base_dir / self.app_name
        settings_dir.mkdir(parents=True, exist_ok=True)
        return settings_dir

    def _load_settings(self):
        """Load settings from file."""
        if self._settings_file.exists():
            try:
                with open(self._settings_file, 'r') as f:
                    self._settings = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._settings = self._get_default_settings()
        else:
            self._settings = self._get_default_settings()

    def _save_settings(self):
        """Save settings to file."""
        try:
            with open(self._settings_file, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")

    def _get_default_settings(self) -> Dict[str, Any]:
        """Return default settings structure."""
        return {
            'wordpress': {
                'site_url': '',
                'username': '',
                'app_password': '',
                'rss_feed_url': '',
                'enabled': False,
            },
            'facebook': {
                'app_id': '',
                'app_secret': '',
                'access_token': '',
                'page_id': '',
                'enabled': False,
            },
            'instagram': {
                'business_account_id': '',
                'access_token': '',
                'enabled': False,
            },
            'app': {
                'max_image_size_mb': 10,
                'concurrent_uploads': 3,
                'theme': 'Light',
                'first_run': True,
            }
        }

    # WordPress Settings
    def get_wordpress_config(self) -> Dict[str, str]:
        """Get WordPress configuration."""
        return self._settings.get('wordpress', {})

    def set_wordpress_config(self, site_url: str, username: str, app_password: str, rss_feed_url: str = ''):
        """Set WordPress configuration."""
        self._settings['wordpress'] = {
            'site_url': site_url.strip(),
            'username': username.strip(),
            'app_password': app_password.strip(),
            'rss_feed_url': rss_feed_url.strip() or f"{site_url.rstrip('/')}/feed/",
            'enabled': bool(site_url and username and app_password),
        }
        self._save_settings()

    def is_wordpress_configured(self) -> bool:
        """Check if WordPress is properly configured."""
        wp = self._settings.get('wordpress', {})
        return bool(wp.get('site_url') and wp.get('username') and wp.get('app_password'))

    # Facebook Settings
    def get_facebook_config(self) -> Dict[str, str]:
        """Get Facebook configuration."""
        return self._settings.get('facebook', {})

    def set_facebook_config(self, app_id: str, app_secret: str, access_token: str, page_id: str):
        """Set Facebook configuration."""
        self._settings['facebook'] = {
            'app_id': app_id.strip(),
            'app_secret': app_secret.strip(),
            'access_token': access_token.strip(),
            'page_id': page_id.strip(),
            'enabled': bool(page_id and access_token),
        }
        self._save_settings()

    def is_facebook_configured(self) -> bool:
        """Check if Facebook is properly configured."""
        fb = self._settings.get('facebook', {})
        return bool(fb.get('page_id') and fb.get('access_token'))

    # Instagram Settings
    def get_instagram_config(self) -> Dict[str, str]:
        """Get Instagram configuration."""
        return self._settings.get('instagram', {})

    def set_instagram_config(self, business_account_id: str, access_token: str):
        """Set Instagram configuration."""
        self._settings['instagram'] = {
            'business_account_id': business_account_id.strip(),
            'access_token': access_token.strip(),
            'enabled': bool(business_account_id and access_token),
        }
        self._save_settings()

    def is_instagram_configured(self) -> bool:
        """Check if Instagram is properly configured."""
        ig = self._settings.get('instagram', {})
        return bool(ig.get('business_account_id') and ig.get('access_token'))

    # App Settings
    def get_app_settings(self) -> Dict[str, Any]:
        """Get app settings."""
        return self._settings.get('app', {})

    def set_app_setting(self, key: str, value: Any):
        """Set a single app setting."""
        if 'app' not in self._settings:
            self._settings['app'] = {}
        self._settings['app'][key] = value
        self._save_settings()

    def is_first_run(self) -> bool:
        """Check if this is the first run."""
        return self._settings.get('app', {}).get('first_run', True)

    def mark_first_run_complete(self):
        """Mark first run as complete."""
        self.set_app_setting('first_run', False)

    # Utility Methods
    def get_configured_platforms(self) -> list:
        """Get list of configured platforms."""
        platforms = []
        if self.is_wordpress_configured():
            platforms.append('wordpress')
        if self.is_facebook_configured():
            platforms.append('facebook')
        if self.is_instagram_configured():
            platforms.append('instagram')
        return platforms

    def clear_all_credentials(self):
        """Clear all stored credentials (for logout/reset)."""
        self._settings = self._get_default_settings()
        self._save_settings()

    def export_settings(self, exclude_secrets: bool = True) -> Dict[str, Any]:
        """Export settings (optionally excluding secrets)."""
        if not exclude_secrets:
            return self._settings.copy()
        
        # Create a copy without sensitive data
        export = {}
        for platform, config in self._settings.items():
            if isinstance(config, dict):
                export[platform] = {}
                for key, value in config.items():
                    if key in ('app_password', 'app_secret', 'access_token'):
                        export[platform][key] = '***' if value else ''
                    else:
                        export[platform][key] = value
            else:
                export[platform] = config
        return export
