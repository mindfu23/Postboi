"""
Postboi - Cross-platform mobile app for sharing to multiple social media platforms.
Main application entry point.
"""

import os
from typing import Dict, Optional
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.list import OneLineListItem
from kivymd.uix.menu import MDDropdownMenu
from plyer import filechooser
import threading

# Import services
from services.wordpress import WordPressService
from services.facebook_share import FacebookService
from services.instagram_share import InstagramService
from services.share_manager import ShareManager

# Import utilities
from utils.image_utils import ImageUtils
from utils.filters import ImageFilters

# Import features
from features.templates import PostTemplates
from features.scheduler import Scheduler

# Import configuration
import config


class PostboiApp(MDApp):
    """Main application class for Postboi."""

    # Properties
    selected_image = StringProperty('')
    caption_text = StringProperty('')
    selected_platforms = ListProperty([])
    selected_filter = StringProperty('none')
    is_loading = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Postboi"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # Services
        self.share_manager: Optional[ShareManager] = None
        self.image_utils = ImageUtils()
        self.image_filters = ImageFilters()
        self.post_templates = PostTemplates()
        self.scheduler: Optional[Scheduler] = None

        # UI components
        self.dialog: Optional[MDDialog] = None
        self.filter_menu: Optional[MDDropdownMenu] = None
        self.template_menu: Optional[MDDropdownMenu] = None

        # Initialize services
        self._init_services()

    def _init_services(self):
        """Initialize social media services from configuration."""
        try:
            # Initialize WordPress
            wordpress_service = None
            if config.WORDPRESS_CONFIG.get('site_url') and \
               config.WORDPRESS_CONFIG['site_url'] != 'https://yoursite.wordpress.com':
                wordpress_service = WordPressService(
                    site_url=config.WORDPRESS_CONFIG['site_url'],
                    username=config.WORDPRESS_CONFIG['username'],
                    app_password=config.WORDPRESS_CONFIG['app_password']
                )

            # Initialize Facebook
            facebook_service = None
            if config.FACEBOOK_CONFIG.get('page_id') and \
               config.FACEBOOK_CONFIG['page_id'] != 'your_page_id':
                facebook_service = FacebookService(
                    page_id=config.FACEBOOK_CONFIG['page_id'],
                    access_token=config.FACEBOOK_CONFIG['access_token']
                )

            # Initialize Instagram
            instagram_service = None
            if config.INSTAGRAM_CONFIG.get('business_account_id') and \
               config.INSTAGRAM_CONFIG['business_account_id'] != 'your_instagram_business_account_id':
                instagram_service = InstagramService(
                    business_account_id=config.INSTAGRAM_CONFIG['business_account_id'],
                    access_token=config.INSTAGRAM_CONFIG['access_token']
                )

            # Initialize ShareManager
            self.share_manager = ShareManager(
                wordpress_service=wordpress_service,
                facebook_service=facebook_service,
                instagram_service=instagram_service,
                max_workers=config.APP_SETTINGS['concurrent_uploads']
            )

            # Initialize Scheduler
            self.scheduler = Scheduler(
                share_callback=self._scheduler_share_callback
            )

        except Exception as e:
            print(f"Error initializing services: {str(e)}")

    def _scheduler_share_callback(self, image_path: str, caption: str, platforms: list) -> Dict:
        """Callback for scheduler to execute scheduled posts."""
        if not self.share_manager:
            return {}
        return self.share_manager.share_to_multiple(platforms, image_path, caption)

    def build(self):
        """Build the application UI."""
        return

    def on_select_image(self):
        """Handle image selection from device."""
        try:
            # Use plyer filechooser for cross-platform compatibility
            filechooser.open_file(
                on_selection=self._on_file_selected,
                filters=["*.jpg", "*.jpeg", "*.png", "*.webp"]
            )
        except Exception as e:
            self.show_error_dialog(f"Error opening file chooser: {str(e)}")

    def _on_file_selected(self, selection):
        """Callback when file is selected."""
        if selection:
            image_path = selection[0]

            # Validate image
            is_valid, message = self.image_utils.validate_image(
                image_path,
                max_size_mb=config.APP_SETTINGS['max_image_size_mb'],
                supported_formats=config.APP_SETTINGS['supported_formats']
            )

            if is_valid:
                self.selected_image = image_path
                self.show_info_dialog(f"Image selected: {os.path.basename(image_path)}")
            else:
                self.show_error_dialog(f"Invalid image: {message}")

    def on_share_button(self):
        """Handle share button press."""
        # Validation
        if not self.selected_image:
            self.show_error_dialog("Please select an image first")
            return

        if not self.caption_text:
            self.show_error_dialog("Please enter a caption")
            return

        if not self.selected_platforms:
            self.show_error_dialog("Please select at least one platform")
            return

        # Apply filter if selected
        image_to_share = self.selected_image
        if self.selected_filter != 'none':
            self.is_loading = True
            filtered_path = self.image_filters.apply_filter(
                self.selected_image,
                self.selected_filter
            )
            if filtered_path:
                image_to_share = filtered_path

        # Start sharing in background thread
        self.is_loading = True
        threading.Thread(
            target=self._share_to_platforms,
            args=(image_to_share, self.caption_text, self.selected_platforms),
            daemon=True
        ).start()

    def _share_to_platforms(self, image_path: str, caption: str, platforms: list):
        """Share to platforms in background thread."""
        try:
            # Share to multiple platforms
            results = self.share_manager.share_to_multiple(
                platforms,
                image_path,
                caption
            )

            # Generate summary
            summary = self.share_manager.get_summary(results)

            # Show results on main thread
            Clock.schedule_once(
                lambda dt: self._on_share_complete(summary),
                0
            )

        except Exception as e:
            Clock.schedule_once(
                lambda dt: self.show_error_dialog(f"Error sharing: {str(e)}"),
                0
            )
        finally:
            Clock.schedule_once(lambda dt: setattr(self, 'is_loading', False), 0)

    def _on_share_complete(self, summary: str):
        """Handle share completion on main thread."""
        self.is_loading = False
        self.show_info_dialog(summary)

    def on_filter_select(self, filter_name: str):
        """Handle filter selection."""
        self.selected_filter = filter_name

    def on_template_select(self, template_name: str):
        """Handle template selection."""
        # Get template
        template = self.post_templates.get_template_by_name(template_name)
        if not template:
            return

        # Get variables needed for template
        variables = self.post_templates.get_template_variables(template['template'])

        # For simplicity, we'll use placeholder values
        # In a real app, you'd show a dialog to collect these values
        var_values = {
            'content': self.caption_text or 'Your content here',
            'title': 'Your Title',
            'author': 'Author Name',
            'date': '',  # Will be auto-filled
            'time': '',  # Will be auto-filled
            'location': 'Location',
            'hashtags': '#postboi',
        }

        # Apply template
        caption = self.post_templates.apply_template(template_name, var_values)
        if caption:
            self.caption_text = caption

    def on_platform_toggle(self, platform: str, is_active: bool):
        """Handle platform checkbox toggle."""
        if is_active:
            if platform not in self.selected_platforms:
                self.selected_platforms.append(platform)
        else:
            if platform in self.selected_platforms:
                self.selected_platforms.remove(platform)

    def show_info_dialog(self, message: str):
        """Show information dialog."""
        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
        )
        self.dialog.open()

    def show_error_dialog(self, message: str):
        """Show error dialog."""
        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
        )
        self.dialog.open()

    def on_stop(self):
        """Called when the app is closing."""
        if self.scheduler:
            self.scheduler.shutdown()


def main():
    """Main entry point."""
    PostboiApp().run()


if __name__ == '__main__':
    main()
