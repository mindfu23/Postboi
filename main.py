"""
Postboi - Cross-platform mobile app for sharing to multiple social media platforms.
Main application entry point.
"""

import os
from typing import Dict, Optional, List
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.list import OneLineListItem, MDList
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from plyer import filechooser, clipboard
import threading

# Import services
from services.wordpress import WordPressService
from services.facebook_share import FacebookService
from services.instagram_share import InstagramService
from services.share_manager import ShareManager
from services.auth_service import AuthService, AuthResult
from services.monetization_service import MonetizationService, PurchaseResult

# Import utilities
from utils.image_utils import ImageUtils
from utils.filters import ImageFilters
from utils.settings_manager import SettingsManager

# Import features
from features.templates import PostTemplates
from features.scheduler import Scheduler
from features.essay_drafter import EssayDrafter

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
    current_screen = StringProperty('main')
    
    # Settings properties for UI binding
    wp_site_url = StringProperty('')
    wp_username = StringProperty('')
    wp_app_password = StringProperty('')
    fb_page_id = StringProperty('')
    fb_access_token = StringProperty('')
    ig_business_id = StringProperty('')
    ig_access_token = StringProperty('')
    
    # Auth properties for UI binding
    auth_email = StringProperty('')
    auth_password = StringProperty('')
    auth_confirm_password = StringProperty('')
    auth_display_name = StringProperty('')
    auth_error = StringProperty('')
    auth_loading = BooleanProperty(False)
    is_authenticated = BooleanProperty(False)
    current_user_display = StringProperty('')
    current_user_email = StringProperty('')
    
    # Monetization properties
    is_premium = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Postboi"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # Auth Service
        self.auth_service = AuthService()
        
        # Monetization Service
        self.monetization_service = MonetizationService()

        # Settings Manager
        self.settings_manager = SettingsManager()

        # Services
        self.share_manager: Optional[ShareManager] = None
        self.image_utils = ImageUtils()
        self.image_filters = ImageFilters()
        self.post_templates = PostTemplates()
        self.scheduler: Optional[Scheduler] = None
        self.essay_drafter: Optional[EssayDrafter] = None

        # UI components
        self.dialog: Optional[MDDialog] = None
        self.filter_menu: Optional[MDDropdownMenu] = None
        self.template_menu: Optional[MDDropdownMenu] = None
        self.screen_manager: Optional[ScreenManager] = None

        # Check existing auth session
        self._restore_auth_session()

        # Load saved settings into properties
        self._load_settings_to_properties()

        # Initialize services
        self._init_services()
    
    def _restore_auth_session(self):
        """Restore authentication session if exists."""
        result, user = self.auth_service.check_auth()
        if result == AuthResult.SUCCESS and user:
            self.is_authenticated = True
            self.current_user_display = user.display_name
            self.current_user_email = user.email
            
            # Link monetization to user
            self.monetization_service.set_user_id(user.id)
            self.is_premium = self.monetization_service.is_premium
            
            # Link settings to user for per-user credential storage
            self.settings_manager.set_user(user.id)
            self._load_settings_to_properties()
        else:
            self.is_authenticated = False
            self.current_user_display = ''
            self.current_user_email = ''

    def _load_settings_to_properties(self):
        """Load saved settings into UI properties."""
        wp = self.settings_manager.get_wordpress_config()
        self.wp_site_url = wp.get('site_url', '')
        self.wp_username = wp.get('username', '')
        self.wp_app_password = wp.get('app_password', '')

        fb = self.settings_manager.get_facebook_config()
        self.fb_page_id = fb.get('page_id', '')
        self.fb_access_token = fb.get('access_token', '')

        ig = self.settings_manager.get_instagram_config()
        self.ig_business_id = ig.get('business_account_id', '')
        self.ig_access_token = ig.get('access_token', '')

    def _init_services(self):
        """Initialize social media services from saved settings."""
        try:
            # Initialize WordPress from saved settings
            wordpress_service = None
            if self.settings_manager.is_wordpress_configured():
                wp = self.settings_manager.get_wordpress_config()
                wordpress_service = WordPressService(
                    site_url=wp['site_url'],
                    username=wp['username'],
                    app_password=wp['app_password']
                )

            # Initialize Facebook from saved settings
            facebook_service = None
            if self.settings_manager.is_facebook_configured():
                fb = self.settings_manager.get_facebook_config()
                facebook_service = FacebookService(
                    page_id=fb['page_id'],
                    access_token=fb['access_token']
                )

            # Initialize Instagram from saved settings
            instagram_service = None
            if self.settings_manager.is_instagram_configured():
                ig = self.settings_manager.get_instagram_config()
                instagram_service = InstagramService(
                    business_account_id=ig['business_account_id'],
                    access_token=ig['access_token']
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

            # Initialize Essay Drafter
            has_valid_anthropic_api_key = (
                config.ANTHROPIC_CONFIG.get('api_key')
                and config.ANTHROPIC_CONFIG['api_key'] != config.PLACEHOLDER_ANTHROPIC_API_KEY
            )
            if has_valid_anthropic_api_key:
                self.essay_drafter = EssayDrafter(
                    api_key=config.ANTHROPIC_CONFIG['api_key'],
                    model=config.ANTHROPIC_CONFIG.get('model', 'claude-3-5-sonnet-20241022')
                )
            else:
                # Initialize without API key - user will need to configure it
                self.essay_drafter = EssayDrafter(
                    api_key='',
                    model='claude-3-5-sonnet-20241022'
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
    
    def on_start(self):
        """Called when the app starts."""
        # Determine starting screen based on auth status
        if self.screen_manager:
            if self.is_authenticated:
                self.screen_manager.current = 'main'
            else:
                # Check if this is first run or user explicitly logged out
                if self.settings_manager.is_first_run():
                    self.screen_manager.current = 'login'
                else:
                    # Allow using app without auth
                    self.screen_manager.current = 'main'

    # =====================
    # AUTH METHODS
    # =====================
    
    def go_to_login(self):
        """Navigate to login screen."""
        self._clear_auth_form()
        if self.screen_manager:
            self.screen_manager.transition = SlideTransition(direction='right')
            self.screen_manager.current = 'login'
    
    def go_to_signup(self):
        """Navigate to signup screen."""
        self._clear_auth_form()
        if self.screen_manager:
            self.screen_manager.transition = SlideTransition(direction='left')
            self.screen_manager.current = 'signup'
    
    def skip_auth(self):
        """Skip authentication and go to main screen."""
        if self.screen_manager:
            self.screen_manager.transition = SlideTransition(direction='left')
            self.screen_manager.current = 'main'
    
    def _clear_auth_form(self):
        """Clear auth form fields."""
        self.auth_email = ''
        self.auth_password = ''
        self.auth_confirm_password = ''
        self.auth_display_name = ''
        self.auth_error = ''
    
    def do_login(self):
        """Perform login."""
        # Validate
        if not self.auth_email or not self.auth_password:
            self.auth_error = "Please fill in all fields"
            return
        
        self.auth_loading = True
        self.auth_error = ''
        
        # Run in background to avoid blocking UI
        threading.Thread(target=self._perform_login, daemon=True).start()
    
    def _perform_login(self):
        """Perform login in background thread."""
        result, user = self.auth_service.login(self.auth_email, self.auth_password)
        
        # Update UI on main thread
        Clock.schedule_once(lambda dt: self._on_login_result(result, user), 0)
    
    def _on_login_result(self, result: AuthResult, user):
        """Handle login result on main thread."""
        self.auth_loading = False
        
        if result == AuthResult.SUCCESS and user:
            self.is_authenticated = True
            self.current_user_display = user.display_name
            self.current_user_email = user.email
            
            # Link monetization to user
            self.monetization_service.set_user_id(user.id)
            self.is_premium = self.monetization_service.is_premium
            
            # Link settings to user for per-user credential storage
            self.settings_manager.set_user(user.id)
            self._load_settings_to_properties()
            self._init_services()  # Reinitialize with user's settings
            
            # Clear form and go to main
            self._clear_auth_form()
            if self.screen_manager:
                self.screen_manager.transition = SlideTransition(direction='left')
                self.screen_manager.current = 'main'
            
            self.show_info_dialog(f"Welcome back, {user.display_name}!")
        else:
            error_messages = {
                AuthResult.USER_NOT_FOUND: "Account not found",
                AuthResult.INVALID_CREDENTIALS: "Invalid email or password",
                AuthResult.INVALID_EMAIL: "Invalid email address",
                AuthResult.ERROR: "An error occurred. Please try again.",
            }
            self.auth_error = error_messages.get(result, "Login failed")
    
    def do_signup(self):
        """Perform signup."""
        # Validate
        if not self.auth_email or not self.auth_password:
            self.auth_error = "Please fill in all fields"
            return
        
        if len(self.auth_password) < 6:
            self.auth_error = "Password must be at least 6 characters"
            return
        
        if self.auth_password != self.auth_confirm_password:
            self.auth_error = "Passwords do not match"
            return
        
        self.auth_loading = True
        self.auth_error = ''
        
        # Run in background
        threading.Thread(target=self._perform_signup, daemon=True).start()
    
    def _perform_signup(self):
        """Perform signup in background thread."""
        result, user = self.auth_service.signup(
            self.auth_email, 
            self.auth_password, 
            self.auth_display_name or self.auth_email.split('@')[0]
        )
        
        # Update UI on main thread
        Clock.schedule_once(lambda dt: self._on_signup_result(result, user), 0)
    
    def _on_signup_result(self, result: AuthResult, user):
        """Handle signup result on main thread."""
        self.auth_loading = False
        
        if result == AuthResult.SUCCESS and user:
            self.is_authenticated = True
            self.current_user_display = user.display_name
            self.current_user_email = user.email
            
            # Link monetization to user
            self.monetization_service.set_user_id(user.id)
            self.is_premium = self.monetization_service.is_premium
            
            # Link settings to user for per-user credential storage
            self.settings_manager.set_user(user.id)
            # New user starts with empty settings
            self._load_settings_to_properties()
            
            # Clear form and go to main
            self._clear_auth_form()
            if self.screen_manager:
                self.screen_manager.transition = SlideTransition(direction='left')
                self.screen_manager.current = 'main'
            
            self.show_info_dialog(f"Welcome, {user.display_name}! Your account has been created.")
        else:
            error_messages = {
                AuthResult.USER_EXISTS: "An account with this email already exists",
                AuthResult.INVALID_EMAIL: "Invalid email address",
                AuthResult.WEAK_PASSWORD: "Password must be at least 6 characters",
                AuthResult.ERROR: "An error occurred. Please try again.",
            }
            self.auth_error = error_messages.get(result, "Signup failed")
    
    def do_logout(self):
        """Log out current user."""
        self.auth_service.logout()
        self.is_authenticated = False
        self.current_user_display = ''
        self.current_user_email = ''
        self.is_premium = False
        
        # Reset to default settings (not user-specific)
        self.settings_manager.set_user(None)
        self._load_settings_to_properties()
        self._init_services()
        
        self.show_info_dialog("You have been signed out.")
    
    def open_account(self):
        """Open account management (settings screen)."""
        self.open_settings()
    
    def confirm_delete_account(self):
        """Show delete account confirmation dialog."""
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title="Delete Account",
            text="Are you sure you want to delete your account? This action cannot be undone.",
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Delete",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self._do_delete_account()
                )
            ],
        )
        self.dialog.open()
    
    def _do_delete_account(self):
        """Execute account deletion."""
        if self.dialog:
            self.dialog.dismiss()
        
        # For simplicity, just logout. In production, you'd verify password
        result = self.auth_service.logout()
        self.is_authenticated = False
        self.current_user_display = ''
        self.current_user_email = ''
        self.is_premium = False
        
        if self.screen_manager:
            self.screen_manager.transition = SlideTransition(direction='right')
            self.screen_manager.current = 'login'
        
        self.show_info_dialog("Your account has been deleted.")

    # =====================
    # PREMIUM/MONETIZATION METHODS
    # =====================
    
    def open_premium(self):
        """Open premium/subscription screen."""
        if self.screen_manager:
            self.screen_manager.transition = SlideTransition(direction='left')
            self.screen_manager.current = 'premium'
    
    def close_premium(self):
        """Close premium screen and return to main."""
        if self.screen_manager:
            self.screen_manager.transition = SlideTransition(direction='right')
            self.screen_manager.current = 'main'
    
    def purchase_product(self, product_id: str):
        """Purchase a product."""
        result = self.monetization_service.purchase(product_id)
        
        if result == PurchaseResult.SUCCESS:
            self.is_premium = self.monetization_service.is_premium
            self.show_info_dialog("Purchase successful! Thank you for upgrading to Premium.")
        elif result == PurchaseResult.ALREADY_OWNED:
            self.show_info_dialog("You already own this product.")
        elif result == PurchaseResult.CANCELLED:
            self.show_info_dialog("Purchase cancelled.")
        else:
            self.show_error_dialog("Purchase failed. Please try again.")
    
    def restore_purchases(self):
        """Restore previous purchases."""
        restored = self.monetization_service.restore_purchases()
        self.is_premium = self.monetization_service.is_premium
        
        if restored:
            self.show_info_dialog(f"Restored {len(restored)} purchase(s).")
        else:
            self.show_info_dialog("No purchases to restore.")

    # =====================
    # SETTINGS SCREEN METHODS
    # =====================

    def open_settings(self):
        """Open the settings screen."""
        if self.screen_manager:
            self.screen_manager.transition = SlideTransition(direction='left')
            self.screen_manager.current = 'settings'

    def close_settings(self):
        """Close settings and return to main screen."""
        if self.screen_manager:
            self.screen_manager.transition = SlideTransition(direction='right')
            self.screen_manager.current = 'main'

    def save_wordpress_settings(self):
        """Save WordPress credentials."""
        self.settings_manager.set_wordpress_config(
            site_url=self.wp_site_url,
            username=self.wp_username,
            app_password=self.wp_app_password
        )
        self._init_services()  # Reinitialize services
        self.show_info_dialog("WordPress settings saved!")

    def save_facebook_settings(self):
        """Save Facebook credentials."""
        self.settings_manager.set_facebook_config(
            app_id='',  # Optional for basic posting
            app_secret='',  # Optional for basic posting
            access_token=self.fb_access_token,
            page_id=self.fb_page_id
        )
        self._init_services()  # Reinitialize services
        self.show_info_dialog("Facebook settings saved!")

    def save_instagram_settings(self):
        """Save Instagram credentials."""
        self.settings_manager.set_instagram_config(
            business_account_id=self.ig_business_id,
            access_token=self.ig_access_token
        )
        self._init_services()  # Reinitialize services
        self.show_info_dialog("Instagram settings saved!")

    def save_all_settings(self):
        """Save all platform settings at once."""
        # Save WordPress
        self.settings_manager.set_wordpress_config(
            site_url=self.wp_site_url,
            username=self.wp_username,
            app_password=self.wp_app_password
        )
        
        # Save Facebook
        self.settings_manager.set_facebook_config(
            app_id='',
            app_secret='',
            access_token=self.fb_access_token,
            page_id=self.fb_page_id
        )
        
        # Save Instagram
        self.settings_manager.set_instagram_config(
            business_account_id=self.ig_business_id,
            access_token=self.ig_access_token
        )
        
        # Reinitialize services with new credentials
        self._init_services()
        
        # Mark first run complete
        if self.settings_manager.is_first_run():
            self.settings_manager.mark_first_run_complete()
        
        self.show_info_dialog("All settings saved successfully!")
        self.close_settings()

    def clear_all_settings(self):
        """Clear all saved credentials."""
        self.settings_manager.clear_all_credentials()
        self._load_settings_to_properties()
        self._init_services()
        self.show_info_dialog("All credentials cleared.")

    def test_wordpress_connection(self):
        """Test WordPress connection with current credentials."""
        if not self.wp_site_url or not self.wp_username or not self.wp_app_password:
            self.show_error_dialog("Please fill in all WordPress fields first.")
            return
        
        try:
            test_service = WordPressService(
                site_url=self.wp_site_url,
                username=self.wp_username,
                app_password=self.wp_app_password
            )
            # Try to get user info as a connection test
            success, message = test_service.test_connection()
            if success:
                self.show_info_dialog("✓ WordPress connection successful!")
            else:
                self.show_error_dialog(f"WordPress connection failed: {message}")
        except Exception as e:
            self.show_error_dialog(f"WordPress error: {str(e)}")

    def get_platform_status(self, platform: str) -> str:
        """Get configuration status for a platform."""
        if platform == 'wordpress':
            return "✓ Configured" if self.settings_manager.is_wordpress_configured() else "Not configured"
        elif platform == 'facebook':
            return "✓ Configured" if self.settings_manager.is_facebook_configured() else "Not configured"
        elif platform == 'instagram':
            return "✓ Configured" if self.settings_manager.is_instagram_configured() else "Not configured"
        return "Unknown"

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

    def unified_share_to_platforms(self, image_path: str, caption: str, platforms: list):
        """
        Share to platforms using unified workflow with retry logic.
        This method uses the enhanced unified_post_workflow from config.
        """
        try:
            # Import unified workflow function
            from config import unified_post_workflow, get_unified_workflow_summary
            
            # Use unified workflow with retry logic and platform-specific adjustments
            results = unified_post_workflow(
                image_path=image_path,
                caption=caption,
                platforms=platforms,
                share_manager=self.share_manager
            )
            
            # Generate detailed summary
            summary = get_unified_workflow_summary(results)
            
            # Show results on main thread
            Clock.schedule_once(
                lambda dt: self._on_share_complete(summary),
                0
            )
            
        except Exception as e:
            Clock.schedule_once(
                lambda dt: self.show_error_dialog(f"Error in unified workflow: {str(e)}"),
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

    def on_draft_essay_button(self):
        """Handle draft essay button press."""
        # Validation
        if not self.selected_image:
            self.show_error_dialog("Please select a screenshot first")
            return

        if not self.essay_drafter:
            self.show_error_dialog("Essay drafter not initialized")
            return

        # Check for authorial voice files
        voice_files = self.essay_drafter.get_voice_file_names()
        if not voice_files:
            self.show_error_dialog(
                "No authorial voice files found. Please add .txt files to the authorial_styles/ directory."
            )
            return

        # Show voice selection dialog if multiple files
        if len(voice_files) > 1:
            self._show_voice_selection_dialog(voice_files)
        else:
            # Proceed with default (only) voice
            self._start_essay_drafting(0)

    def _show_voice_selection_dialog(self, voice_files: List[str]):
        """Show dialog for selecting authorial voice."""
        if self.dialog:
            self.dialog.dismiss()

        # Create list items for voice files
        items = []
        for i, filename in enumerate(voice_files):
            item = OneLineListItem(
                text=filename,
                on_release=lambda x, idx=i: self._on_voice_selected(idx)
            )
            items.append(item)

        # Create dialog with list
        list_view = MDList()
        for item in items:
            list_view.add_widget(item)

        scroll = ScrollView()
        scroll.add_widget(list_view)

        self.dialog = MDDialog(
            title="Select Authorial Voice",
            type="custom",
            content_cls=scroll,
            size_hint=(0.8, 0.6),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
        )
        self.dialog.open()

    def _on_voice_selected(self, voice_index: int):
        """Handle voice selection."""
        if self.dialog:
            self.dialog.dismiss()
        self._start_essay_drafting(voice_index)

    def _start_essay_drafting(self, voice_index: int):
        """Start essay drafting in background thread."""
        self.is_loading = True
        threading.Thread(
            target=self._draft_essay_from_screenshot,
            args=(self.selected_image, voice_index),
            daemon=True
        ).start()

    def _draft_essay_from_screenshot(self, image_path: str, voice_index: int):
        """Draft essay from screenshot in background thread."""
        try:
            # Process screenshot to essay
            result = self.essay_drafter.process_screenshot_to_essay(
                image_path,
                voice_index
            )

            # Show results on main thread
            Clock.schedule_once(
                lambda dt: self._on_essay_draft_complete(result),
                0
            )

        except Exception as e:
            Clock.schedule_once(
                lambda dt: self.show_error_dialog(f"Error drafting essay: {str(e)}"),
                0
            )
        finally:
            Clock.schedule_once(lambda dt: setattr(self, 'is_loading', False), 0)

    def _on_essay_draft_complete(self, result: Dict):
        """Handle essay draft completion on main thread."""
        self.is_loading = False

        if not result['success']:
            self.show_error_dialog(f"Essay drafting failed: {result.get('error', 'Unknown error')}")
            return

        # Format essay for Substack
        formatted_essay = self.essay_drafter.format_for_substack(result['essay'])

        # Show essay in a dialog with copy functionality
        self._show_essay_dialog(formatted_essay, result)

    def _show_essay_dialog(self, essay: str, result: Dict):
        """Show dialog with drafted essay."""
        # Create a scrollable text field with the essay
        text_field = MDTextField(
            text=essay,
            multiline=True,
            readonly=True,
            size_hint_y=None,
            height="400dp"
        )

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(text_field)

        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title=f"Essay Draft (Voice: {result['authorial_voice_file']})",
            type="custom",
            content_cls=scroll,
            size_hint=(0.9, 0.8),
            buttons=[
                MDFlatButton(
                    text="COPY TO CLIPBOARD",
                    on_release=lambda x: self._copy_essay_to_clipboard(essay)
                ),
                MDFlatButton(
                    text="CLOSE",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
        )
        self.dialog.open()

    def _copy_essay_to_clipboard(self, essay: str):
        """Copy essay to clipboard."""
        try:
            clipboard.copy(essay)
            self.show_info_dialog("Essay copied to clipboard!")
        except Exception as e:
            self.show_error_dialog(f"Failed to copy to clipboard: {str(e)}")

    def on_stop(self):
        """Called when the app is closing."""
        if self.scheduler:
            self.scheduler.shutdown()


def main():
    """Main entry point."""
    PostboiApp().run()


if __name__ == '__main__':
    main()
