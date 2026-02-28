# Essay Drafting Feature - Quick Start Guide

## Overview
The essay drafting feature allows you to transform screenshots of your notes into polished essays using AI, written in your personal style.

## Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
# Install Python dependencies
pip install anthropic pytesseract

# Install Tesseract OCR
# Ubuntu/Debian:
sudo apt install tesseract-ocr

# macOS:
brew install tesseract

# Windows:
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### 2. Configure API Key
1. Get an API key from [Anthropic](https://www.anthropic.com/)
2. Edit `config.py`:
```python
ANTHROPIC_CONFIG = {
    'api_key': 'your_actual_api_key_here',
    'model': 'claude-3-5-sonnet-20241022',
}
```

### 3. Create Your Authorial Voice
Create a text file in `authorial_styles/` describing your writing style:

```bash
cd authorial_styles/
nano my_style.txt
```

Example content:
```
Writing Style: Conversational and engaging

Tone: Professional but approachable

Structure:
- Start with a hook
- Use short paragraphs
- Include practical examples
- End with actionable insights

Common phrases:
- "Here's what matters..."
- "The key insight is..."
```

## Usage

### Option 1: From the App
1. Run the app: `python main.py`
2. Select a screenshot with text
3. Click "Draft Essay"
4. Select your voice style
5. Copy the generated essay

### Option 2: Programmatically
```python
from features.essay_drafter import EssayDrafter

# Initialize
drafter = EssayDrafter(api_key='your_key')

# Draft essay from screenshot
result = drafter.process_screenshot_to_essay('screenshot.png')

if result['success']:
    essay = drafter.format_for_substack(result['essay'])
    print(essay)
else:
    print(f"Error: {result['error']}")
```

## Test It Out

### 1. Create a test screenshot:
```bash
python create_test_image.py
```

### 2. Run the demo:
```bash
python demo_usage.py
```

### 3. Run full integration test (requires API key):
```bash
RUN_FULL_TEST=1 python test_integration.py
```

## Tips for Best Results

### Screenshots
- Use clear, readable text
- Good contrast (dark text on light background)
- Avoid handwritten text (OCR works best with printed text)
- Crop to include only relevant content

### Authorial Voice Files
- Be specific about your style preferences
- Include examples of phrases you use
- Describe your target audience
- Mention topics you typically write about

### Essay Generation
- More detailed screenshots = better essays
- Structure your notes with clear points
- Include key arguments and evidence
- Add context about your intended message

## Troubleshooting

### "Tesseract not found"
- Make sure Tesseract is installed and in your PATH
- On Windows, add Tesseract to system PATH after installation

### "No text extracted"
- Check screenshot quality
- Ensure text is readable
- Try adjusting image contrast/brightness

### "API error"
- Verify your API key is correct
- Check your Anthropic account has credits
- Ensure internet connection is working

### "No authorial voice files"
- Create at least one .txt file in `authorial_styles/`
- File must have .txt extension
- Check file permissions

## What's Next?

After your first essay:
1. Refine your authorial voice file based on results
2. Create multiple voice files for different styles
3. Experiment with different screenshot formats
4. Share your essays on Substack, Medium, or your blog!

## Need Help?

- See `IMPLEMENTATION_SUMMARY.md` for technical details
- Check `README.md` for comprehensive documentation
- Run `python test_essay_drafter.py` to verify installation

## Examples

### Example Voice File
See `authorial_styles/example_voice.txt` for a complete example.

### Example Workflow
1. Screenshot your handwritten notes from a meeting
2. Run through essay drafter
3. Get a polished draft based on your style
4. Edit and publish to your blog

Happy writing! ✍️
