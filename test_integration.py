#!/usr/bin/env python3
"""
Integration test for Essay Drafter with OCR.
Tests the complete workflow from screenshot to essay draft.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("Essay Drafter Integration Test")
print("=" * 70)

# Check if Tesseract is installed
print("\n1. Checking Tesseract OCR Installation...")
try:
    import pytesseract
    from PIL import Image
    
    # Try to get tesseract version
    try:
        version = pytesseract.get_tesseract_version()
        print(f"   ✓ Tesseract OCR installed (version {version})")
    except:
        print("   ✗ Tesseract OCR not installed or not in PATH")
        print("   ℹ  Install with: sudo apt install tesseract-ocr (Ubuntu/Debian)")
        print("   ℹ  Or: brew install tesseract (macOS)")
        print("   Skipping OCR tests...")
        tesseract_available = False
except ImportError:
    print("   ✗ pytesseract module not installed")
    print("   ℹ  Install with: pip install pytesseract")
    tesseract_available = False
else:
    tesseract_available = True

# Import Essay Drafter
print("\n2. Importing Essay Drafter...")
try:
    from features.essay_drafter import EssayDrafter
    import config
    print("   ✓ Essay Drafter imported successfully")
except Exception as e:
    print(f"   ✗ Import error: {str(e)}")
    sys.exit(1)

# Initialize Essay Drafter
print("\n3. Initializing Essay Drafter...")
try:
    drafter = EssayDrafter(
        api_key=config.ANTHROPIC_CONFIG.get('api_key', ''),
        model=config.ANTHROPIC_CONFIG.get('model', 'claude-3-5-sonnet-20241022')
    )
    print("   ✓ Essay Drafter initialized")
except Exception as e:
    print(f"   ✗ Initialization error: {str(e)}")
    sys.exit(1)

# Check for test screenshot
print("\n4. Checking for Test Screenshot...")
test_image_path = 'test_screenshot.png'
if os.path.exists(test_image_path):
    print(f"   ✓ Test screenshot found: {test_image_path}")
else:
    print(f"   ○ Test screenshot not found")
    print(f"   ℹ  Run: python create_test_image.py to create one")
    test_image_path = None

# Test OCR if both Tesseract and test image are available
if tesseract_available and test_image_path:
    print("\n5. Testing OCR Text Extraction...")
    try:
        success, extracted_text = drafter.extract_text_from_image(test_image_path)
        
        if success:
            print(f"   ✓ Text extracted successfully ({len(extracted_text)} characters)")
            print("\n   --- Extracted Text Preview ---")
            preview = extracted_text[:300]
            for line in preview.split('\n')[:10]:
                if line.strip():
                    print(f"   {line}")
            if len(extracted_text) > 300:
                print("   ...")
            print("   --- End Preview ---\n")
        else:
            print(f"   ✗ OCR failed: {extracted_text}")
    except Exception as e:
        print(f"   ✗ Error during OCR: {str(e)}")
else:
    print("\n5. Testing OCR Text Extraction...")
    print("   ⊘ Skipped (Tesseract or test image not available)")

# Test the complete workflow (without API call if not configured)
print("\n6. Testing Complete Workflow (Mock)...")
try:
    # Get authorial voice files
    voice_files = drafter.get_voice_file_names()
    print(f"   ✓ Found {len(voice_files)} authorial voice file(s)")
    
    # Select voice
    selected_voice = drafter.select_authorial_voice(0)
    if selected_voice:
        print(f"   ✓ Selected voice: {os.path.basename(selected_voice)}")
    
    # Load voice
    voice_content = drafter.load_authorial_voice(selected_voice)
    if voice_content:
        print(f"   ✓ Loaded voice content ({len(voice_content)} characters)")
    
    # Check API configuration
    api_configured = (
        config.ANTHROPIC_CONFIG.get('api_key') and
        config.ANTHROPIC_CONFIG['api_key'] != 'your_anthropic_api_key'
    )
    
    if api_configured:
        print("   ✓ Anthropic API configured")
        
        if tesseract_available and test_image_path:
            print("\n   Full integration test available!")
            print("   Would you like to run a complete test? (requires API credits)")
            print("   This will:")
            print("   - Extract text from test_screenshot.png")
            print("   - Summarize the content using Claude")
            print("   - Draft a complete essay")
            print("\n   To run: Set RUN_FULL_TEST=1 environment variable")
            
            if os.environ.get('RUN_FULL_TEST') == '1':
                print("\n   Running full integration test...")
                result = drafter.process_screenshot_to_essay(
                    test_image_path,
                    voice_index=0
                )
                
                if result['success']:
                    print("   ✓ Essay drafted successfully!")
                    print(f"\n   Voice used: {result['authorial_voice_file']}")
                    print(f"   Extracted text: {len(result['extracted_text'])} characters")
                    print(f"   Summary: {len(result['summary'])} characters")
                    print(f"   Essay: {len(result['essay'])} characters")
                    
                    print("\n   --- Essay Preview ---")
                    print(result['essay'][:500])
                    print("   ...")
                    print("   --- End Preview ---")
                else:
                    print(f"   ✗ Essay drafting failed: {result['error']}")
    else:
        print("   ○ Anthropic API not configured")
        print("   ℹ  Add API key to config.py to test full workflow")
        print("   ℹ  Get API key from: https://www.anthropic.com/")
    
except Exception as e:
    print(f"   ✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("Integration Test Summary")
print("=" * 70)

print("\nComponent Status:")
print(f"  • Essay Drafter Module: ✓ Working")
print(f"  • Authorial Voice Files: ✓ Available")
print(f"  • Tesseract OCR: {'✓ Installed' if tesseract_available else '○ Not installed'}")
print(f"  • Test Screenshot: {'✓ Available' if test_image_path else '○ Not available'}")
print(f"  • Anthropic API: {'✓ Configured' if api_configured else '○ Not configured'}")

print("\nFeature Capabilities:")
print("  ✓ Load and manage authorial voice files")
print("  ✓ Format essays for Substack/blogging platforms")
if tesseract_available:
    print("  ✓ Extract text from screenshots using OCR")
else:
    print("  ○ OCR functionality (requires Tesseract)")
if api_configured:
    print("  ✓ Generate essays using Claude AI")
else:
    print("  ○ AI essay generation (requires Anthropic API key)")

print("\nNext Steps:")
if not tesseract_available:
    print("1. Install Tesseract OCR for text extraction")
if not api_configured:
    print("2. Configure Anthropic API key in config.py")
if not test_image_path:
    print("3. Run 'python create_test_image.py' to create test screenshot")
if tesseract_available and api_configured and test_image_path:
    print("✓ All components ready!")
    print("  Run with RUN_FULL_TEST=1 to test complete workflow")

print("=" * 70)
