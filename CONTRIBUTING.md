# Contributing to Postboi

Thank you for your interest in contributing to Postboi! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to providing a welcoming and inspiring community for all. By participating, you are expected to uphold these values:

- Be respectful and inclusive
- Be collaborative and constructive
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected behavior** vs actual behavior
- **Screenshots** if applicable
- **Environment details** (OS, Python version, device type)
- **Error messages** and stack traces

### Suggesting Features

Feature suggestions are welcome! When suggesting a feature:

- **Use a clear title and description**
- **Explain the use case** and why it would be valuable
- **Provide examples** of how it would work
- **Consider the scope** - keep it focused and achievable

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**
6. **Push to your fork**
7. **Open a Pull Request**

## Development Setup

### Prerequisites

- Python 3.8+
- pip
- Git

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/Postboi.git
cd Postboi

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python3 test_functionality.py
```

### For Mobile Testing

**Android:**
```bash
pip install buildozer
buildozer android debug
```

**iOS (macOS only):**
```bash
pip install kivy-ios
toolchain build python3 kivy
```

## Code Style Guidelines

### Python Code Style

Follow **PEP 8** style guide with these specifics:

- **Indentation**: 4 spaces (no tabs)
- **Line length**: Maximum 100 characters (120 for long strings/URLs)
- **Imports**: Grouped and alphabetized
  ```python
  # Standard library
  import os
  import sys
  
  # Third-party
  from kivy.app import App
  from kivymd.app import MDApp
  
  # Local
  from services import ShareManager
  ```
- **Naming conventions**:
  - Classes: `PascalCase`
  - Functions/methods: `snake_case`
  - Constants: `UPPER_CASE`
  - Private methods: `_leading_underscore`

### Type Hints

Use type hints for function parameters and return values:

```python
def share_to_platform(self, platform: str, image_path: str) -> Tuple[bool, str]:
    """Share to a single platform."""
    pass
```

### Docstrings

All public classes and functions must have docstrings:

```python
def create_post(self, title: str, content: str) -> Tuple[bool, str]:
    """
    Create a new WordPress post.
    
    Args:
        title: Post title
        content: Post content/caption
    
    Returns:
        Tuple of (success, message/post_url)
    """
    pass
```

### Comments

- Use comments for complex logic only
- Prefer self-documenting code
- Keep comments updated with code changes

### KV File Style

- Consistent indentation (4 spaces)
- Group related properties
- Use descriptive IDs

```yaml
MDCard:
    orientation: 'vertical'
    padding: dp(16)
    spacing: dp(12)
    elevation: 2
    
    MDLabel:
        text: "Title"
        font_style: "H6"
```

## Pull Request Process

### Before Submitting

1. **Test your changes** thoroughly
2. **Update documentation** if needed
3. **Add/update tests** for new features
4. **Run the test script**: `python3 test_functionality.py`
5. **Check code style** follows guidelines
6. **Update README.md** if adding features

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested the changes

## Screenshots
If applicable, add screenshots

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass
```

### Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged
4. Your contribution will be acknowledged

## Project Structure

```
Postboi/
├── main.py              # Main app entry point
├── postboi.kv          # UI layout
├── config.py           # Configuration
├── services/           # Platform integrations
│   ├── wordpress.py
│   ├── facebook_share.py
│   ├── instagram_share.py
│   └── share_manager.py
├── utils/              # Utilities
│   ├── image_utils.py
│   └── filters.py
└── features/           # App features
    ├── templates.py
    └── scheduler.py
```

## Areas for Contribution

### High Priority

- Video support
- More image filters
- Analytics dashboard
- Performance optimization
- Test coverage

### Platform Support

- Twitter/X integration
- LinkedIn integration
- TikTok integration
- Pinterest integration

### Features

- Multiple image posts
- GIF support
- Caption editing
- Hashtag suggestions
- Post history

### Documentation

- Tutorial videos
- More examples
- API documentation
- Troubleshooting guides

## Getting Help

- **Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Discord**: (Coming soon)

## Recognition

Contributors will be:
- Listed in the README
- Credited in release notes
- Acknowledged in the project

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Postboi! 🎉
