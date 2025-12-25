#!/usr/bin/env python3
"""
Create a sample screenshot image with text for testing OCR functionality.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_screenshot():
    """Create a test screenshot with readable text."""
    # Create a white background image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Add some text content that simulates notes/ideas for an essay
    text_content = """
Key Ideas for Essay on Remote Work:

1. Flexibility and Work-Life Balance
   - Workers can design their own schedules
   - More time with family and personal pursuits
   - Reduced commute stress and time savings

2. Productivity Insights
   - Studies show mixed results on productivity
   - Individual differences matter more than location
   - Importance of proper home office setup

3. Challenges to Address
   - Communication difficulties across time zones
   - Risk of isolation and burnout
   - Need for intentional collaboration

4. Future of Work Trends
   - Hybrid models becoming the norm
   - Companies rethinking office space
   - Technology enabling better remote collaboration

Main Argument: Remote work is not just about location - 
it's about reimagining how we work, collaborate, and 
maintain work-life boundaries in the digital age.
    """
    
    # Use a basic font (PIL's default)
    try:
        # Try to use a default font, fall back to PIL default if not available
        font = ImageFont.load_default()
    except:
        font = None
    
    # Draw the text
    y_position = 30
    for line in text_content.strip().split('\n'):
        draw.text((30, y_position), line, fill='black', font=font)
        y_position += 20
    
    # Save the image
    output_path = 'test_screenshot.png'
    image.save(output_path)
    print(f"Created test screenshot: {output_path}")
    return output_path

if __name__ == '__main__':
    create_test_screenshot()
