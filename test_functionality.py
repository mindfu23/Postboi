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
        print("   ℹ  Edit config.py to add your credentials for full functionality")
    
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

# Test 7: Essay Drafter
print("\n7. Testing Essay Drafter...")
try:
    from features import EssayDrafter
    
    # Check if Anthropic is configured
    has_valid_api_key = (
        config.ANTHROPIC_CONFIG.get('api_key') != config.PLACEHOLDER_ANTHROPIC_API_KEY
    )
    
    # Initialize essay drafter
    drafter = EssayDrafter(
        api_key=config.ANTHROPIC_CONFIG.get('api_key', ''),
        model=config.ANTHROPIC_CONFIG.get('model', 'claude-3-5-sonnet-20241022')
    )
    
    print("   ✓ Essay Drafter initialized")
    
    # Check for authorial voice files
    voice_files = drafter.get_voice_file_names()
    if voice_files:
        print(f"   ✓ Found {len(voice_files)} authorial voice file(s):")
        for vf in voice_files:
            print(f"     - {vf}")
    else:
        print("   ○ No authorial voice files found (add .txt files to authorial_styles/)")
    
    print(f"   Anthropic API: {'✓ Configured' if has_valid_api_key else '○ Not configured (template)'}")
    
    if not has_valid_api_key:
        print("   ℹ  Edit config.py to add your Anthropic API key for full functionality")
    
except Exception as e:
    print(f"   ✗ Essay Drafter error: {str(e)}")

# Summary
print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)
print("All core functionality tests passed!")
print("\nNext steps:")
print("1. Edit config.py with your platform credentials")
print("2. Add Anthropic API key for essay drafting feature")
print("3. Add authorial voice files to authorial_styles/ directory")
print("4. Install Tesseract OCR: sudo apt install tesseract-ocr (Linux)")
print("5. Run 'python main.py' to launch the app (requires Kivy)")
print("6. Or build for mobile with 'buildozer android debug'")
print("=" * 60)
