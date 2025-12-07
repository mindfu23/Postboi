"""
Post templates for Postboi.
Pre-defined caption templates for common post types with variable substitution.
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class PostTemplates:
    """Manages post templates with variable substitution."""

    def __init__(self, templates_file: str = 'templates.json'):
        """
        Initialize PostTemplates.

        Args:
            templates_file: Path to JSON file storing custom templates
        """
        self.templates_file = templates_file
        self.default_templates = self._get_default_templates()
        self.custom_templates = self._load_custom_templates()

    @staticmethod
    def _get_default_templates() -> List[Dict[str, str]]:
        """Get default built-in templates."""
        return [
            {
                'name': 'Announcement',
                'category': 'general',
                'template': '📢 ANNOUNCEMENT\n\n{content}\n\n#announcement #news #update'
            },
            {
                'name': 'Quote',
                'category': 'inspirational',
                'template': '💭 "{content}"\n\n- {author}\n\n#quote #inspiration #motivation #wisdom'
            },
            {
                'name': 'Product Showcase',
                'category': 'business',
                'template': '✨ Introducing: {title}\n\n{content}\n\n🛒 Available now!\n\n#product #showcase #new'
            },
            {
                'name': 'Event Promotion',
                'category': 'event',
                'template': '🎉 EVENT ALERT!\n\n📅 {date}\n📍 {location}\n⏰ {time}\n\n{content}\n\n#event #joinus #dontmiss'
            },
            {
                'name': 'Behind the Scenes',
                'category': 'creative',
                'template': '🎬 Behind the Scenes\n\n{content}\n\n#bts #behindthescenes #makingof #process'
            },
            {
                'name': 'Tip/Tutorial',
                'category': 'educational',
                'template': '💡 Pro Tip:\n\n{content}\n\n#tip #tutorial #howto #learn'
            },
            {
                'name': 'Thank You',
                'category': 'general',
                'template': '🙏 Thank You!\n\n{content}\n\n#thankyou #grateful #appreciation'
            },
            {
                'name': 'Question/Poll',
                'category': 'engagement',
                'template': '❓ Question for you:\n\n{content}\n\nLet us know in the comments! 👇\n\n#question #poll #engagement'
            },
            {
                'name': 'Milestone',
                'category': 'celebration',
                'template': '🎊 Milestone Alert!\n\n{content}\n\n#milestone #celebration #achievement #grateful'
            },
            {
                'name': 'Simple',
                'category': 'general',
                'template': '{content}\n\n{hashtags}'
            },
        ]

    def _load_custom_templates(self) -> List[Dict[str, str]]:
        """Load custom templates from file."""
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading custom templates: {str(e)}")
        return []

    def _save_custom_templates(self) -> bool:
        """Save custom templates to file."""
        try:
            with open(self.templates_file, 'w') as f:
                json.dump(self.custom_templates, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving custom templates: {str(e)}")
            return False

    def get_all_templates(self) -> List[Dict[str, str]]:
        """Get all templates (default + custom)."""
        return self.default_templates + self.custom_templates

    def get_template_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """
        Get template by name.

        Args:
            name: Template name

        Returns:
            Template dictionary or None
        """
        all_templates = self.get_all_templates()
        for template in all_templates:
            if template['name'] == name:
                return template
        return None

    def get_templates_by_category(self, category: str) -> List[Dict[str, str]]:
        """
        Get templates by category.

        Args:
            category: Template category

        Returns:
            List of matching templates
        """
        all_templates = self.get_all_templates()
        return [t for t in all_templates if t.get('category') == category]

    def apply_template(self, template_name: str, variables: Dict[str, str]) -> Optional[str]:
        """
        Apply a template with variable substitution.

        Args:
            template_name: Name of the template
            variables: Dictionary of variables to substitute

        Returns:
            Formatted caption string or None
        """
        template = self.get_template_by_name(template_name)
        if not template:
            return None

        # Add automatic variables
        variables.setdefault('date', datetime.now().strftime('%B %d, %Y'))
        variables.setdefault('time', datetime.now().strftime('%I:%M %p'))
        variables.setdefault('year', str(datetime.now().year))

        # Substitute variables
        try:
            caption = template['template']
            for key, value in variables.items():
                caption = caption.replace(f'{{{key}}}', str(value))
            return caption
        except Exception as e:
            print(f"Error applying template: {str(e)}")
            return None

    def create_custom_template(self, name: str, template: str,
                              category: str = 'custom') -> bool:
        """
        Create a new custom template.

        Args:
            name: Template name
            template: Template string with {variables}
            category: Template category

        Returns:
            True if successful, False otherwise
        """
        # Check if name already exists
        if self.get_template_by_name(name):
            print(f"Template '{name}' already exists")
            return False

        # Add to custom templates
        self.custom_templates.append({
            'name': name,
            'category': category,
            'template': template,
        })

        # Save to file
        return self._save_custom_templates()

    def delete_custom_template(self, name: str) -> bool:
        """
        Delete a custom template.

        Args:
            name: Template name

        Returns:
            True if successful, False otherwise
        """
        # Find and remove template
        for i, template in enumerate(self.custom_templates):
            if template['name'] == name:
                self.custom_templates.pop(i)
                return self._save_custom_templates()

        return False

    def get_template_variables(self, template_string: str) -> List[str]:
        """
        Extract variable names from a template string.

        Args:
            template_string: Template string with {variables}

        Returns:
            List of variable names
        """
        import re
        return re.findall(r'\{(\w+)\}', template_string)

    def get_categories(self) -> List[str]:
        """
        Get all unique template categories.

        Returns:
            List of category names
        """
        all_templates = self.get_all_templates()
        categories = set(t.get('category', 'general') for t in all_templates)
        return sorted(list(categories))
