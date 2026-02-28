#!/usr/bin/env python3
"""
Usage demonstration for the Essay Drafting feature.
This script shows how to use the feature programmatically.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("Essay Drafting Feature - Usage Demonstration")
print("=" * 70)

# Import the Essay Drafter
from features.essay_drafter import EssayDrafter
import config

# Initialize the Essay Drafter
print("\n1. Initialize Essay Drafter")
print("-" * 70)
drafter = EssayDrafter(
    api_key=config.ANTHROPIC_CONFIG.get('api_key', ''),
    model=config.ANTHROPIC_CONFIG.get('model', 'claude-3-5-sonnet-20241022')
)
print("✓ Essay Drafter initialized")

# Check available authorial voice files
print("\n2. Check Available Authorial Voice Files")
print("-" * 70)
voice_files = drafter.get_voice_file_names()
print(f"Available voice files: {len(voice_files)}")
for i, voice in enumerate(voice_files):
    print(f"  [{i}] {voice}")

# Example 1: Basic usage with auto-selection
print("\n3. Example: Auto-select Voice (when only one file exists)")
print("-" * 70)
selected_voice = drafter.select_authorial_voice()
if selected_voice:
    print(f"✓ Auto-selected: {os.path.basename(selected_voice)}")
else:
    print("✗ No voice files available")

# Example 2: Manual voice selection
print("\n4. Example: Manual Voice Selection (when multiple exist)")
print("-" * 70)
if len(voice_files) > 1:
    # Select the second voice file
    selected_voice = drafter.select_authorial_voice(voice_index=1)
    print(f"✓ Selected: {os.path.basename(selected_voice)}")
else:
    print("ℹ  Only one voice file available - add more to see selection")

# Example 3: Load authorial voice content
print("\n5. Example: Load Authorial Voice Content")
print("-" * 70)
if selected_voice:
    voice_content = drafter.load_authorial_voice(selected_voice)
    if voice_content:
        print(f"✓ Loaded voice content: {len(voice_content)} characters")
        print("\nPreview:")
        print(voice_content[:200] + "...\n")

# Example 4: OCR Text Extraction (requires test screenshot)
print("\n6. Example: Extract Text from Screenshot")
print("-" * 70)
test_image = 'test_screenshot.png'
if os.path.exists(test_image):
    success, result = drafter.extract_text_from_image(test_image)
    if success:
        print(f"✓ Text extracted: {len(result)} characters")
        print("\nExtracted text preview:")
        print(result[:200] + "...\n")
    else:
        print(f"✗ OCR failed: {result}")
else:
    print(f"ℹ  Test screenshot not found: {test_image}")
    print("   Run 'python create_test_image.py' to create one")

# Example 5: Complete Workflow (requires API key)
print("\n7. Example: Complete Workflow (Screenshot → Essay)")
print("-" * 70)

has_valid_api_key = (
    config.ANTHROPIC_CONFIG.get('api_key') and
    config.ANTHROPIC_CONFIG['api_key'] != 'your_anthropic_api_key'
)

if not has_valid_api_key:
    print("⊘ API not configured - showing mock workflow")
    print("\nWorkflow steps:")
    print("  1. Extract text from screenshot using OCR")
    print("  2. Send to Claude AI for summarization")
    print("  3. Load authorial voice profile")
    print("  4. Generate essay using Claude AI")
    print("  5. Format for blogging platform")
    print("\nTo run the complete workflow:")
    print("  • Add your Anthropic API key to config.py")
    print("  • Create a test screenshot: python create_test_image.py")
    print("  • Run: RUN_FULL_TEST=1 python test_integration.py")
else:
    if os.path.exists(test_image):
        print("✓ API configured and test image available")
        print("\nYou can now run the complete workflow:")
        print(f"  result = drafter.process_screenshot_to_essay('{test_image}')")
        print("\nOr run the full integration test:")
        print("  RUN_FULL_TEST=1 python test_integration.py")
    else:
        print("✓ API configured")
        print("⊘ Test screenshot not found")
        print("  Create one with: python create_test_image.py")

# Example 6: Format essay for Substack
print("\n8. Example: Format Essay for Substack")
print("-" * 70)
sample_essay = """
# The Future of Remote Work

The pandemic fundamentally changed how we think about work. Here's the thing: 
remote work isn't just about location—it's about reimagining collaboration 
and productivity in the digital age.

## Key Benefits

Let's be honest, the flexibility is unmatched. Workers can design schedules 
around their lives, not the other way around. But it's more than convenience.

## Challenges

Think about it this way: isolation and burnout are real risks. The bottom 
line is that intentional connection matters more than ever.
"""

formatted = drafter.format_for_substack(sample_essay)
print("✓ Essay formatted for Substack")
print("\nFormatted output preview:")
print(formatted[:300] + "...\n")

# Summary
print("\n" + "=" * 70)
print("Summary: How to Use the Essay Drafting Feature")
print("=" * 70)

print("""
From the Application:
  1. Launch the app: python main.py
  2. Select a screenshot containing text
  3. Click "Draft Essay" button
  4. Select authorial voice (if prompted)
  5. Wait for processing
  6. Copy the generated essay

Programmatically:
  from features.essay_drafter import EssayDrafter
  
  drafter = EssayDrafter(api_key='your_key')
  result = drafter.process_screenshot_to_essay('screenshot.png')
  
  if result['success']:
      essay = drafter.format_for_substack(result['essay'])
      # Copy essay to blogging platform

Prerequisites:
  • Tesseract OCR installed
  • Anthropic API key configured
  • Authorial voice files in authorial_styles/

For more examples and documentation:
  • See README.md for detailed setup instructions
  • See IMPLEMENTATION_SUMMARY.md for technical details
  • Run test_integration.py for complete workflow test
""")

print("=" * 70)
