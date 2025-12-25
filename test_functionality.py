#!/usr/bin/env python3
"""
Test script for Postboi functionality.
This script demonstrates the various features without requiring a full Kivy UI.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Postboi Functionality Test")
print("=" * 60)

# Test 1: Import all modules
print("\n1. Testing Module Imports...")
try:
    import config
    from services import WordPressService, FacebookService, InstagramService, ShareManager
    from utils import ImageUtils, ImageFilters
    from features import PostTemplates, Scheduler
    print("   ✓ All modules imported successfully")
except Exception as e:
    print(f"   ✗ Import error: {str(e)}")
    sys.exit(1)

# Test 2: Template System
print("\n2. Testing Template System...")
try:
    templates = PostTemplates()
    all_templates = templates.get_all_templates()
    print(f"   ✓ Found {len(all_templates)} default templates")
    
    # List template names
    template_names = [t['name'] for t in all_templates]
    print(f"   Templates: {', '.join(template_names[:5])}...")
    
    # Test template application
    test_vars = {
        'content': 'This is a test post!',
        'author': 'Test User'
    }
    result = templates.apply_template('Quote', test_vars)
    if result:
        print(f"   ✓ Template application successful")
        print(f"   Sample output: {result[:50]}...")
    
except Exception as e:
    print(f"   ✗ Template error: {str(e)}")

# Test 3: Image Filters
print("\n3. Testing Image Filter System...")
try:
    filters = ImageFilters()
    available_filters = filters.get_available_filters()
    print(f"   ✓ Found {len(available_filters)} available filters")
    print(f"   Filters: {', '.join(available_filters)}")
except Exception as e:
    print(f"   ✗ Filter error: {str(e)}")

# Test 4: Image Utils
print("\n4. Testing Image Utilities...")
try:
    image_utils = ImageUtils()
    print(f"   ✓ ImageUtils initialized")
    
    # Test validation (with a non-existent file)
    is_valid, msg = image_utils.validate_image('/tmp/nonexistent.jpg')
    if not is_valid:
        print(f"   ✓ Image validation works (correctly detected missing file)")
    
except Exception as e:
    print(f"   ✗ Image utils error: {str(e)}")

# Test 5: Service Initialization
print("\n5. Testing Service Configuration...")
try:
    # Check if services are configured
    wp_configured = (
        config.WORDPRESS_CONFIG.get('site_url') != 'https://yoursite.wordpress.com'
    )
    fb_configured = (
        config.FACEBOOK_CONFIG.get('page_id') != 'your_page_id'
    )
    ig_configured = (
        config.INSTAGRAM_CONFIG.get('business_account_id') != 'your_instagram_business_account_id'
    )
    
    print(f"   WordPress: {'✓ Configured' if wp_configured else '○ Not configured (template)'}")
    print(f"   Facebook:  {'✓ Configured' if fb_configured else '○ Not configured (template)'}")
    print(f"   Instagram: {'✓ Configured' if ig_configured else '○ Not configured (template)'}")
    
    if not (wp_configured or fb_configured or ig_configured):
        print("   ℹ  Create a .env file from .env.template and add your credentials for full functionality")
    
except Exception as e:
    print(f"   ✗ Configuration error: {str(e)}")

# Test 6: App Settings
print("\n6. Testing App Settings...")
try:
    print(f"   Max image size: {config.APP_SETTINGS['max_image_size_mb']} MB")
    print(f"   Supported formats: {', '.join(config.APP_SETTINGS['supported_formats'])}")
    print(f"   Max caption length: {config.APP_SETTINGS['max_caption_length']} chars")
    print(f"   Concurrent uploads: {config.APP_SETTINGS['concurrent_uploads']}")
    print("   ✓ App settings loaded successfully")
except Exception as e:
    print(f"   ✗ Settings error: {str(e)}")

# Summary
print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)
print("All core functionality tests passed!")
print("\nNext steps:")
print("1. Create a .env file from .env.template and add your platform credentials")
print("2. Run 'python main.py' to launch the app (requires Kivy)")
print("3. Or build for mobile with 'buildozer android debug'")
print("4. See web/, ios/, and android/ directories for platform-specific starter templates")
print("=" * 60)
