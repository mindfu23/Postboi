"""
Essay Drafter for Postboi.
Extracts text from screenshots and drafts essays based on authorial voice files.
"""

import os
from typing import Dict, List, Optional, Tuple
from PIL import Image
import pytesseract
from anthropic import Anthropic


class EssayDrafter:
    """Manages essay drafting from screenshots using OCR and AI."""

    def __init__(self, api_key: str, model: str = 'claude-3-5-sonnet-20241022',
                 authorial_styles_dir: str = 'authorial_styles'):
        """
        Initialize EssayDrafter.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
            authorial_styles_dir: Directory containing authorial voice files
        """
        self.api_key = api_key
        self.model = model
        self.authorial_styles_dir = authorial_styles_dir
        self.client = Anthropic(api_key=api_key) if api_key and api_key != 'your_anthropic_api_key' else None

    def get_authorial_voice_files(self) -> List[str]:
        """
        Get list of authorial voice text files.

        Returns:
            List of file paths to authorial voice files
        """
        if not os.path.exists(self.authorial_styles_dir):
            return []

        files = []
        for filename in os.listdir(self.authorial_styles_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(self.authorial_styles_dir, filename)
                files.append(filepath)

        return sorted(files)

    def select_authorial_voice(self, voice_index: Optional[int] = None) -> Optional[str]:
        """
        Select an authorial voice file.

        Args:
            voice_index: Index of voice file to use (None for auto-selection)

        Returns:
            Path to selected voice file or None if no files available
        """
        voice_files = self.get_authorial_voice_files()

        if not voice_files:
            return None

        # If only one file, auto-select it
        if len(voice_files) == 1:
            return voice_files[0]

        # If voice_index provided, use it
        if voice_index is not None:
            if 0 <= voice_index < len(voice_files):
                return voice_files[voice_index]

        # Return first file as default
        return voice_files[0]

    def load_authorial_voice(self, voice_file: str) -> Optional[str]:
        """
        Load authorial voice content from file.

        Args:
            voice_file: Path to authorial voice file

        Returns:
            Content of the voice file or None if error
        """
        try:
            with open(voice_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading authorial voice: {str(e)}")
            return None

    def extract_text_from_image(self, image_path: str) -> Tuple[bool, str]:
        """
        Extract text from screenshot using OCR.

        Args:
            image_path: Path to screenshot image

        Returns:
            Tuple of (success, extracted_text or error_message)
        """
        try:
            # Validate image file exists
            if not os.path.exists(image_path):
                return False, f"Image file not found: {image_path}"

            # Open image and perform OCR
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)

            if not text or len(text.strip()) < 10:
                return False, "No text could be extracted from the image. Please ensure the image contains readable text."

            return True, text.strip()

        except Exception as e:
            return False, f"Error extracting text: {str(e)}"

    def summarize_and_extract_arguments(self, text: str) -> Tuple[bool, str]:
        """
        Summarize extracted text and identify key arguments.

        Args:
            text: Extracted text from screenshot

        Returns:
            Tuple of (success, summary or error_message)
        """
        if not self.client:
            return False, "Claude API not configured. Please set ANTHROPIC_CONFIG in config.py"

        try:
            prompt = f"""Please analyze the following text and provide:
1. A concise summary (2-3 sentences)
2. Key arguments or main points (as bullet points)

Text to analyze:
{text}

Format your response as:
SUMMARY:
[Your summary here]

KEY ARGUMENTS:
- [Argument 1]
- [Argument 2]
- [Argument 3]
..."""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract text content from response
            if message.content and len(message.content) > 0:
                summary = message.content[0].text
                return True, summary
            else:
                return False, "No response from AI"

        except Exception as e:
            return False, f"Error summarizing text: {str(e)}"

    def draft_essay(self, arguments: str, authorial_voice: str,
                   additional_instructions: str = "") -> Tuple[bool, str]:
        """
        Draft an essay based on arguments and authorial voice.

        Args:
            arguments: Summarized arguments and key points
            authorial_voice: Authorial voice profile content
            additional_instructions: Optional additional instructions

        Returns:
            Tuple of (success, essay or error_message)
        """
        if not self.client:
            return False, "Claude API not configured. Please set ANTHROPIC_CONFIG in config.py"

        try:
            prompt = f"""You are a skilled writer tasked with drafting an essay based on the following inputs:

AUTHORIAL VOICE PROFILE:
{authorial_voice}

CONTENT TO BASE THE ESSAY ON:
{arguments}

{additional_instructions}

Please write a compelling essay that:
1. Incorporates the key arguments and points provided
2. Matches the writing style, tone, and preferences described in the authorial voice profile
3. Is well-structured with clear introduction, body, and conclusion
4. Is suitable for publication on blogging platforms like Substack
5. Is engaging and accessible to readers

Write the essay now:"""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract text content from response
            if message.content and len(message.content) > 0:
                essay = message.content[0].text
                return True, essay
            else:
                return False, "No response from AI"

        except Exception as e:
            return False, f"Error drafting essay: {str(e)}"

    def process_screenshot_to_essay(self, image_path: str,
                                   voice_index: Optional[int] = None,
                                   additional_instructions: str = "") -> Dict[str, any]:
        """
        Complete workflow: extract text from screenshot and draft essay.

        Args:
            image_path: Path to screenshot image
            voice_index: Index of authorial voice to use (None for auto)
            additional_instructions: Optional additional instructions for essay

        Returns:
            Dictionary with results:
            {
                'success': bool,
                'extracted_text': str,
                'summary': str,
                'essay': str,
                'authorial_voice_file': str,
                'error': str (if success=False)
            }
        """
        result = {
            'success': False,
            'extracted_text': '',
            'summary': '',
            'essay': '',
            'authorial_voice_file': '',
            'error': ''
        }

        # Step 1: Extract text from screenshot
        success, extracted_text = self.extract_text_from_image(image_path)
        if not success:
            result['error'] = extracted_text
            return result
        result['extracted_text'] = extracted_text

        # Step 2: Summarize and extract arguments
        success, summary = self.summarize_and_extract_arguments(extracted_text)
        if not success:
            result['error'] = summary
            return result
        result['summary'] = summary

        # Step 3: Select authorial voice
        voice_file = self.select_authorial_voice(voice_index)
        if not voice_file:
            result['error'] = "No authorial voice files found in authorial_styles/ directory"
            return result
        result['authorial_voice_file'] = os.path.basename(voice_file)

        # Step 4: Load authorial voice
        authorial_voice = self.load_authorial_voice(voice_file)
        if not authorial_voice:
            result['error'] = "Failed to load authorial voice file"
            return result

        # Step 5: Draft essay
        success, essay = self.draft_essay(summary, authorial_voice, additional_instructions)
        if not success:
            result['error'] = essay
            return result
        result['essay'] = essay

        result['success'] = True
        return result

    def format_for_substack(self, essay: str) -> str:
        """
        Format essay for easy copying to Substack or other blogging platforms.

        Args:
            essay: Draft essay text

        Returns:
            Formatted essay text
        """
        # Substack uses Markdown, so we'll ensure the essay is well-formatted
        # The essay from Claude should already be in a good format
        # This method can be extended to add additional formatting if needed

        formatted = essay.strip()

        # Add a header comment for clarity
        header = "<!-- Essay generated by Postboi Essay Drafter -->\n\n"

        return header + formatted

    def get_voice_file_names(self) -> List[str]:
        """
        Get list of authorial voice file names (without path).

        Returns:
            List of file names
        """
        voice_files = self.get_authorial_voice_files()
        return [os.path.basename(f) for f in voice_files]
