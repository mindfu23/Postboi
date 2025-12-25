"""
Configuration file for Postboi application.
Loads sensitive credentials from environment variables.
Create a .env file based on .env.template and populate with your credentials.
"""

import os
from typing import Dict, List

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, will use system environment variables only
    pass

# WordPress Configuration
WORDPRESS_CONFIG: Dict[str, str] = {
    'site_url': os.getenv('WORDPRESS_SITE_URL', 'https://yoursite.wordpress.com'),
    'username': os.getenv('WORDPRESS_USERNAME', 'your_username'),
    'app_password': os.getenv('WORDPRESS_APP_PASSWORD', 'xxxx xxxx xxxx xxxx xxxx xxxx'),
    'rss_feed_url': os.getenv('WORDPRESS_SITE_URL', 'https://yoursite.wordpress.com') + '/feed/' if os.getenv('WORDPRESS_SITE_URL') else 'https://yoursite.wordpress.com/feed/',
}

# Facebook Configuration
FACEBOOK_CONFIG: Dict[str, str] = {
    'app_id': os.getenv('FACEBOOK_APP_ID', 'your_app_id'),
    'app_secret': os.getenv('FACEBOOK_APP_SECRET', 'your_app_secret'),
    'access_token': os.getenv('FACEBOOK_ACCESS_TOKEN', 'your_page_access_token'),
    'page_id': os.getenv('FACEBOOK_PAGE_ID', 'your_page_id'),
}

# Instagram Configuration
INSTAGRAM_CONFIG: Dict[str, str] = {
    'business_account_id': os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID', 'your_instagram_business_account_id'),
    'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN', 'your_access_token'),
}

# Application Settings
APP_SETTINGS: Dict[str, any] = {
    'max_image_size_mb': int(os.getenv('MAX_IMAGE_SIZE_MB', '10')),
    'supported_formats': ['jpg', 'jpeg', 'png', 'webp'],  # Supported image formats
    'thumbnail_size': (300, 300),  # Thumbnail dimensions
    'max_caption_length': 2200,  # Maximum caption length (Instagram limit)
    'concurrent_uploads': int(os.getenv('CONCURRENT_UPLOADS', '3')),
}

# Image Filter Presets
FILTER_PRESETS: Dict[str, Dict[str, float]] = {
    'none': {},
    'vintage': {'sepia': 0.5, 'contrast': 1.2},
    'bright': {'brightness': 1.3},
    'dramatic': {'contrast': 1.5, 'brightness': 0.9},
    'cool': {'temperature': -20},
}

# Post Templates
DEFAULT_TEMPLATES: List[Dict[str, str]] = [
    {
        'name': 'Announcement',
        'template': '📢 ANNOUNCEMENT\n\n{content}\n\n#announcement #news'
    },
    {
        'name': 'Quote',
        'template': '💭 "{content}"\n\n- {author}\n\n#quote #inspiration #motivation'
    },
    {
        'name': 'Product Showcase',
        'template': '✨ Introducing: {title}\n\n{content}\n\n🛒 Available now!\n\n#product #showcase'
    },
    {
        'name': 'Event Promotion',
        'template': '🎉 EVENT ALERT!\n\n📅 {date}\n📍 {location}\n\n{content}\n\n#event #joinus'
    },
    {
        'name': 'Behind the Scenes',
        'template': '🎬 Behind the Scenes\n\n{content}\n\n#bts #behindthescenes #makingof'
    },
]
