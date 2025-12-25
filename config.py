"""
Configuration file for Postboi application.
Copy this file and update with your actual credentials.
"""

from typing import Dict, List

# WordPress Configuration
WORDPRESS_CONFIG: Dict[str, str] = {
    'site_url': 'https://yoursite.wordpress.com',  # Your WordPress site URL
    'username': 'your_username',  # WordPress username
    'app_password': 'xxxx xxxx xxxx xxxx xxxx xxxx',  # Application password (with spaces)
    'rss_feed_url': 'https://yoursite.wordpress.com/feed/',  # RSS feed URL
}

# Facebook Configuration
FACEBOOK_CONFIG: Dict[str, str] = {
    'app_id': 'your_app_id',  # Facebook App ID
    'app_secret': 'your_app_secret',  # Facebook App Secret
    'access_token': 'your_page_access_token',  # Page Access Token (long-lived)
    'page_id': 'your_page_id',  # Facebook Page ID
}

# Instagram Configuration
INSTAGRAM_CONFIG: Dict[str, str] = {
    'business_account_id': 'your_instagram_business_account_id',  # Instagram Business Account ID
    'access_token': 'your_access_token',  # Access token (same as Facebook if linked)
}

# Claude/Anthropic Configuration
ANTHROPIC_CONFIG: Dict[str, str] = {
    'api_key': 'your_anthropic_api_key',  # Anthropic API key for Claude
    'model': 'claude-3-5-sonnet-20241022',  # Claude model to use
}

# Application Settings
APP_SETTINGS: Dict[str, any] = {
    'max_image_size_mb': 10,  # Maximum image size in MB
    'supported_formats': ['jpg', 'jpeg', 'png', 'webp'],  # Supported image formats
    'thumbnail_size': (300, 300),  # Thumbnail dimensions
    'max_caption_length': 2200,  # Maximum caption length (Instagram limit)
    'concurrent_uploads': 3,  # Number of concurrent platform uploads
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
