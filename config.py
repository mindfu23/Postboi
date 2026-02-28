"""
Configuration file for Postboi application.
Loads sensitive credentials from environment variables.
Create a .env file based on .env.template and populate with your credentials.
"""

import os
from typing import Any, Dict, List, Optional, Tuple

# Placeholder values for API keys
PLACEHOLDER_ANTHROPIC_API_KEY = 'your_anthropic_api_key'

# WordPress Configuration
WORDPRESS_CONFIG: Dict[str, str] = {
    'site_url': os.getenv('WORDPRESS_SITE_URL', 'https://yoursite.wordpress.com'),
    'username': os.getenv('WORDPRESS_USERNAME', 'your_username'),
    'app_password': os.getenv('WORDPRESS_APP_PASSWORD', 'xxxx xxxx xxxx xxxx xxxx xxxx'),
    'rss_feed_url': (os.getenv('WORDPRESS_SITE_URL', 'https://yoursite.wordpress.com').rstrip('/') + '/feed/'),
    'rss_feed_url': os.getenv('WORDPRESS_RSS_FEED', 'https://yoursite.wordpress.com/feed/'),
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

# Claude/Anthropic Configuration
ANTHROPIC_CONFIG: Dict[str, str] = {
    'api_key': PLACEHOLDER_ANTHROPIC_API_KEY,  # Anthropic API key for Claude
    'model': 'claude-3-5-sonnet-20241022',  # Claude model to use
}

# Application Settings
APP_SETTINGS: Dict[str, Any] = {
    'max_image_size_mb': 10,  # Maximum image size in MB
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

# Unified Workflow Configuration
UNIFIED_WORKFLOW_CONFIG: Dict[str, Any] = {
    'max_retry_attempts': 3,  # Number of retry attempts for failed uploads
    'retry_delay': 2,  # Delay between retries in seconds
    'timeout': 30,  # Request timeout in seconds
    'enable_logging': True,  # Enable detailed error logging
}

# Platform-Specific Requirements
PLATFORM_REQUIREMENTS: Dict[str, Dict[str, Any]] = {
    'instagram': {
        'max_caption_length': 2200,  # Instagram caption limit
        'max_hashtags': 30,  # Instagram hashtag limit
        'max_image_size': (1080, 1080),  # Recommended size for Instagram
        'aspect_ratio': (1, 1),  # Square aspect ratio preferred
    },
    'facebook': {
        'max_caption_length': 63206,  # Facebook post text limit
        'max_image_size': (2048, 2048),  # Recommended size for Facebook
        'aspect_ratio': (1.91, 1),  # Landscape aspect ratio
    },
    'wordpress': {
        'max_caption_length': None,  # No specific limit
        'max_image_size': (1920, 1920),  # Recommended size for WordPress
        'aspect_ratio': None,  # Flexible aspect ratio
    },
}


def adjust_caption_for_platform(caption: str, platform: str) -> str:
    """
    Adjust caption to meet platform-specific requirements.
    
    Args:
        caption: Original caption text
        platform: Platform name ('instagram', 'facebook', 'wordpress')
        
    Returns:
        Adjusted caption suitable for the platform
    """
    requirements = PLATFORM_REQUIREMENTS.get(platform.lower(), {})
    max_length = requirements.get('max_caption_length')
    
    # Handle Instagram-specific adjustments
    if platform.lower() == 'instagram':
        # Count and limit hashtags
        hashtags = [word for word in caption.split() if word.startswith('#')]
        max_hashtags = requirements.get('max_hashtags', 30)
        
        if len(hashtags) > max_hashtags:
            # Keep only the first max_hashtags hashtags
            caption_parts = caption.split()
            hashtag_count = 0
            filtered_parts = []
            
            for part in caption_parts:
                if part.startswith('#'):
                    if hashtag_count < max_hashtags:
                        filtered_parts.append(part)
                        hashtag_count += 1
                else:
                    filtered_parts.append(part)
            
            caption = ' '.join(filtered_parts)
    
    # Handle WordPress-specific formatting (convert markdown-style to HTML-like)
    elif platform.lower() == 'wordpress':
        # Keep caption as-is, WordPress handles rich text well
        pass
    
    # Truncate if exceeds max length
    if max_length and len(caption) > max_length:
        caption = caption[:max_length - 3] + '...'
    
    return caption


def adjust_image_for_platform(image_path: str, platform: str) -> Optional[str]:
    """
    Resize and adjust image to meet platform-specific requirements.
    
    Args:
        image_path: Path to the original image
        platform: Platform name ('instagram', 'facebook', 'wordpress')
        
    Returns:
        Path to adjusted image, or None if failed
    """
    try:
        from utils.image_utils import ImageUtils
    except ImportError as e:
        print(f"Warning: Could not import ImageUtils: {e}")
        return image_path
    
    requirements = PLATFORM_REQUIREMENTS.get(platform.lower(), {})
    max_size = requirements.get('max_image_size')
    
    if not max_size:
        return image_path  # No adjustment needed
    
    # Resize image to meet platform requirements
    try:
        adjusted_path = ImageUtils.resize_image(
            image_path,
            max_width=max_size[0],
            max_height=max_size[1],
            quality=90
        )
        return adjusted_path if adjusted_path else image_path
    except Exception as e:
        print(f"Warning: Failed to adjust image: {e}")
        return image_path


def unified_post_workflow(
    image_path: str,
    caption: str,
    platforms: List[str],
    share_manager=None
) -> Dict[str, Tuple[bool, str, List[str]]]:
    """
    Unified workflow for posting to multiple platforms simultaneously.
    
    This function:
    - Adjusts captions and images for each platform's requirements
    - Uploads simultaneously to all selected platforms
    - Implements automatic retry logic for failed uploads
    - Provides detailed error logging
    
    Args:
        image_path: Path to the image file to upload
        caption: Post caption text
        platforms: List of platform names ('wordpress', 'facebook', 'instagram')
        share_manager: ShareManager instance (if None, will create one)
        
    Returns:
        Dictionary mapping platform names to (success, message, error_log) tuples
        where error_log is a list of error messages encountered during retries
    """
    import time
    import logging
    
    # Import services (imports inside function to avoid circular dependencies)
    try:
        from services.share_manager import ShareManager
        from services.wordpress import WordPressService
        from services.facebook_share import FacebookService
        from services.instagram_share import InstagramService
    except ImportError as e:
        # Graceful fallback if services cannot be imported
        error_msg = f"Failed to import required services: {e}"
        return {
            platform: (False, error_msg, [error_msg]) 
            for platform in platforms
        }
    
    # Setup logging
    if UNIFIED_WORKFLOW_CONFIG['enable_logging']:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger('UnifiedWorkflow')
    else:
        logger = None
    
    # Initialize ShareManager if not provided
    if share_manager is None:
        wordpress_service = None
        if WORDPRESS_CONFIG.get('site_url') and \
           WORDPRESS_CONFIG['site_url'] != 'https://yoursite.wordpress.com':
            wordpress_service = WordPressService(
                site_url=WORDPRESS_CONFIG['site_url'],
                username=WORDPRESS_CONFIG['username'],
                app_password=WORDPRESS_CONFIG['app_password']
            )
        
        facebook_service = None
        if FACEBOOK_CONFIG.get('page_id') and \
           FACEBOOK_CONFIG['page_id'] != 'your_page_id':
            facebook_service = FacebookService(
                page_id=FACEBOOK_CONFIG['page_id'],
                access_token=FACEBOOK_CONFIG['access_token']
            )
        
        instagram_service = None
        if INSTAGRAM_CONFIG.get('business_account_id') and \
           INSTAGRAM_CONFIG['business_account_id'] != 'your_instagram_business_account_id':
            instagram_service = InstagramService(
                business_account_id=INSTAGRAM_CONFIG['business_account_id'],
                access_token=INSTAGRAM_CONFIG['access_token']
            )
        
        share_manager = ShareManager(
            wordpress_service=wordpress_service,
            facebook_service=facebook_service,
            instagram_service=instagram_service,
            max_workers=APP_SETTINGS['concurrent_uploads']
        )
    
    results = {}
    max_attempts = UNIFIED_WORKFLOW_CONFIG['max_retry_attempts']
    retry_delay = UNIFIED_WORKFLOW_CONFIG['retry_delay']
    
    # Process each platform
    for platform in platforms:
        platform_lower = platform.lower()
        error_log = []
        
        if logger:
            logger.info(f"Starting upload to {platform}")
        
        # Adjust caption for platform
        adjusted_caption = adjust_caption_for_platform(caption, platform_lower)
        
        if logger and adjusted_caption != caption:
            logger.info(f"Caption adjusted for {platform}: length {len(caption)} -> {len(adjusted_caption)}")
        
        # Adjust image for platform
        adjusted_image = adjust_image_for_platform(image_path, platform_lower)
        
        if logger and adjusted_image != image_path:
            logger.info(f"Image adjusted for {platform}: {image_path} -> {adjusted_image}")
        
        # Retry logic
        success = False
        message = ""
        
        for attempt in range(1, max_attempts + 1):
            try:
                if logger:
                    logger.info(f"Attempt {attempt}/{max_attempts} for {platform}")
                
                # Share to platform
                platform_name, success, message = share_manager.share_to_platform(
                    platform_lower,
                    adjusted_image,
                    adjusted_caption
                )
                
                if success:
                    if logger:
                        logger.info(f"Successfully posted to {platform}: {message}")
                    break
                else:
                    error_msg = f"Attempt {attempt} failed: {message}"
                    error_log.append(error_msg)
                    
                    if logger:
                        logger.warning(f"{platform} - {error_msg}")
                    
                    if attempt < max_attempts:
                        if logger:
                            logger.info(f"Retrying {platform} in {retry_delay} seconds...")
                        time.sleep(retry_delay)
            
            except Exception as e:
                error_msg = f"Attempt {attempt} exception: {str(e)}"
                error_log.append(error_msg)
                
                if logger:
                    logger.error(f"{platform} - {error_msg}", exc_info=True)
                
                if attempt < max_attempts:
                    if logger:
                        logger.info(f"Retrying {platform} in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    message = f"All {max_attempts} attempts failed. Last error: {str(e)}"
        
        # Store results
        results[platform] = (success, message, error_log)
        
        if logger:
            if success:
                logger.info(f"Final result for {platform}: SUCCESS")
            else:
                logger.error(f"Final result for {platform}: FAILED after {max_attempts} attempts")
                logger.error(f"Error summary: {'; '.join(error_log)}")
    
    return results


def get_unified_workflow_summary(results: Dict[str, Tuple[bool, str, List[str]]]) -> str:
    """
    Generate a detailed summary of unified workflow results.
    
    Args:
        results: Dictionary of platform results from unified_post_workflow
        
    Returns:
        Formatted summary string with success/failure details
    """
    successful = [platform for platform, (success, _, _) in results.items() if success]
    failed = [platform for platform, (success, _, _) in results.items() if not success]
    
    summary_parts = []
    summary_parts.append("=" * 60)
    summary_parts.append("UNIFIED POST WORKFLOW RESULTS")
    summary_parts.append("=" * 60)
    
    if successful:
        summary_parts.append(f"\n✅ SUCCESSFUL ({len(successful)}/{len(results)}):")
        for platform in successful:
            _, message, _ = results[platform]
            summary_parts.append(f"  • {platform}: {message}")
    
    if failed:
        summary_parts.append(f"\n❌ FAILED ({len(failed)}/{len(results)}):")
        for platform in failed:
            _, message, error_log = results[platform]
            summary_parts.append(f"  • {platform}: {message}")
            
            if error_log:
                summary_parts.append(f"    Error history:")
                for error in error_log:
                    summary_parts.append(f"      - {error}")
                
                # Suggest resolution
                summary_parts.append(f"    Possible resolutions:")
                if 'authentication' in message.lower() or 'token' in message.lower():
                    summary_parts.append(f"      - Check API credentials and access tokens")
                    summary_parts.append(f"      - Ensure tokens have not expired")
                elif 'connection' in message.lower() or 'timeout' in message.lower():
                    summary_parts.append(f"      - Check internet connection")
                    summary_parts.append(f"      - Verify platform API endpoints are accessible")
                elif 'url' in message.lower() and platform.lower() == 'instagram':
                    summary_parts.append(f"      - Instagram requires a publicly accessible image URL")
                    summary_parts.append(f"      - Consider hosting image temporarily")
                else:
                    summary_parts.append(f"      - Review error messages above")
                    summary_parts.append(f"      - Check platform-specific documentation")
    
    summary_parts.append("\n" + "=" * 60)
    
    return '\n'.join(summary_parts)
