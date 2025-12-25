# Unified Posting Workflow Documentation

## Overview

The unified posting workflow enables users to upload an image and caption once, which is automatically uploaded to WordPress, Facebook, and Instagram with platform-specific optimizations.

## Features

### 1. Single Upload Interface
- Upload one image and write one caption
- Select target platforms (WordPress, Facebook, Instagram, or all)
- Automatic posting to all selected platforms simultaneously

### 2. Platform-Specific Adjustments

#### Caption Adjustments
- **Instagram**: Enforces 30 hashtag limit, truncates to 2200 characters
- **Facebook**: Allows up to 63,206 characters
- **WordPress**: No character limits, preserves formatting

#### Image Size Adjustments
- **Instagram**: Optimized to 1080×1080px (square format)
- **Facebook**: Optimized to 2048×2048px (landscape-friendly)
- **WordPress**: Optimized to 1920×1920px (high resolution)

### 3. Automatic Retry Logic
- Configurable retry attempts (default: 3)
- Configurable delay between retries (default: 2 seconds)
- Independent retry for each platform
- Detailed error logging for each attempt

### 4. Enhanced Error Handling
- Platform-specific error messages
- Detailed error logs for troubleshooting
- Suggested resolutions for common errors
- Comprehensive summary reports

## Configuration

### Environment Variables (.env)

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# WordPress Configuration
WORDPRESS_SITE_URL=https://yoursite.wordpress.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=your_app_password_here

# Facebook Configuration
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_ACCESS_TOKEN=your_access_token

# Instagram Configuration
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id
INSTAGRAM_ACCESS_TOKEN=your_access_token
```

### Unified Workflow Settings

Configure retry behavior in `config.py`:

```python
UNIFIED_WORKFLOW_CONFIG = {
    'max_retry_attempts': 3,     # Number of retries per platform
    'retry_delay': 2,            # Seconds between retries
    'timeout': 30,               # API request timeout
    'enable_logging': True,      # Enable detailed logging
}
```

## Usage

### From the UI (main.py)

The unified workflow is automatically used when sharing:

```python
app = PostboiApp()
app.selected_image = '/path/to/image.jpg'
app.caption_text = 'Your amazing caption #hashtag'
app.selected_platforms = ['wordpress', 'facebook', 'instagram']
app.on_share_button()
```

### Programmatic Usage

```python
from config import unified_post_workflow, get_unified_workflow_summary

# Post to all platforms
results = unified_post_workflow(
    image_path='/path/to/image.jpg',
    caption='Your amazing caption #hashtag',
    platforms=['wordpress', 'facebook', 'instagram']
)

# Generate and print summary
summary = get_unified_workflow_summary(results)
print(summary)
```

### Example Output

```
============================================================
UNIFIED POST WORKFLOW RESULTS
============================================================

✅ SUCCESSFUL (2/3):
  • WordPress: https://yoursite.com/post/123
  • Instagram: Posted to Instagram: 18012345678901234

❌ FAILED (1/3):
  • Facebook: Authentication failed
    Error history:
      - Attempt 1 failed: Invalid OAuth access token
      - Attempt 2 failed: Invalid OAuth access token
      - Attempt 3 failed: Invalid OAuth access token
    Possible resolutions:
      - Check API credentials and access tokens
      - Ensure tokens have not expired
============================================================
```

## Platform-Specific Functions

### Caption Adjustment

```python
from config import adjust_caption_for_platform

# Adjust caption for Instagram (limits hashtags, truncates length)
ig_caption = adjust_caption_for_platform(long_caption, 'instagram')

# Adjust caption for Facebook
fb_caption = adjust_caption_for_platform(long_caption, 'facebook')

# Adjust caption for WordPress
wp_caption = adjust_caption_for_platform(long_caption, 'wordpress')
```

### Image Adjustment

```python
from config import adjust_image_for_platform

# Resize image for Instagram (1080x1080)
ig_image = adjust_image_for_platform('/path/to/image.jpg', 'instagram')

# Resize image for Facebook (2048x2048)
fb_image = adjust_image_for_platform('/path/to/image.jpg', 'facebook')

# Resize image for WordPress (1920x1920)
wp_image = adjust_image_for_platform('/path/to/image.jpg', 'wordpress')
```

## Error Handling

### Common Errors and Solutions

#### Authentication Errors
```
Error: Authentication failed / Invalid OAuth access token
Solutions:
- Verify credentials in .env file
- Check that access tokens haven't expired
- Regenerate tokens if necessary
- Ensure proper API permissions
```

#### Connection Errors
```
Error: Connection timeout / Network error
Solutions:
- Check internet connection
- Verify API endpoints are accessible
- Increase timeout in UNIFIED_WORKFLOW_CONFIG
- Check firewall/proxy settings
```

#### Instagram-Specific Errors
```
Error: Instagram API requires a public image URL
Solutions:
- Instagram Graph API requires publicly accessible URLs
- For local files, host temporarily or use native share
- Consider using a temporary image hosting service
- For mobile apps, use native share intent
```

#### Image Size Errors
```
Error: Image size exceeds platform limits
Solutions:
- Images are automatically resized by the workflow
- Check original image is not corrupted
- Verify Pillow is properly installed
- Check disk space for temporary files
```

## Security Considerations

### Credential Management

1. **Never commit .env file**: Already in .gitignore
2. **Use environment variables**: Keeps secrets out of code
3. **Rotate tokens regularly**: Update access tokens periodically
4. **Limit token permissions**: Use minimum required scopes

### Token Storage

```python
# Good: Environment variables
access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')

# Bad: Hardcoded in source
access_token = 'EAABsb...'  # DON'T DO THIS
```

## Testing

Run the comprehensive test suite:

```bash
python test_functionality.py
```

This validates:
- Module imports
- Template system
- Image filters and utilities
- Service configuration
- Unified workflow configuration
- Caption adjustments
- Image adjustments
- Error handling
- Summary generation

## Advanced Usage

### Custom ShareManager

```python
from config import unified_post_workflow
from services import ShareManager, WordPressService, FacebookService

# Create custom services with specific settings
wp_service = WordPressService(
    site_url='https://mysite.com',
    username='admin',
    app_password='my_password'
)

fb_service = FacebookService(
    page_id='123456789',
    access_token='my_token'
)

# Create custom share manager
custom_manager = ShareManager(
    wordpress_service=wp_service,
    facebook_service=fb_service,
    max_workers=5  # More concurrent workers
)

# Use with unified workflow
results = unified_post_workflow(
    image_path='/path/to/image.jpg',
    caption='Custom workflow test',
    platforms=['wordpress', 'facebook'],
    share_manager=custom_manager
)
```

### Custom Retry Configuration

```python
import config

# Temporarily adjust retry settings
original_attempts = config.UNIFIED_WORKFLOW_CONFIG['max_retry_attempts']
config.UNIFIED_WORKFLOW_CONFIG['max_retry_attempts'] = 5

# Run workflow with more retries
results = unified_post_workflow(...)

# Restore original settings
config.UNIFIED_WORKFLOW_CONFIG['max_retry_attempts'] = original_attempts
```

## Performance Tips

1. **Concurrent Uploads**: The workflow uses ThreadPoolExecutor for parallel uploads
2. **Image Preprocessing**: Consider resizing large images before upload
3. **Retry Strategy**: Adjust retry attempts based on network reliability
4. **Caching**: Reuse ShareManager instances to avoid re-initialization

## Troubleshooting

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now run your workflow
results = unified_post_workflow(...)
```

### Test Individual Platforms

```python
# Test one platform at a time
results = unified_post_workflow(
    image_path='test.jpg',
    caption='Test post',
    platforms=['wordpress']  # Test only WordPress
)
```

### Verify Service Configuration

```python
from services import ShareManager

manager = ShareManager(...)
connection_results = manager.test_all_connections()

for platform, (success, message) in connection_results.items():
    print(f"{platform}: {message}")
```

## Future Enhancements

Potential improvements for the unified workflow:

1. **Scheduled Posts**: Schedule unified posts for optimal times
2. **Analytics**: Track success rates per platform
3. **Draft Mode**: Save drafts before publishing
4. **Webhooks**: Notify external services on completion
5. **Batch Processing**: Upload multiple posts at once
6. **Template Integration**: Apply templates before posting
7. **A/B Testing**: Test different captions per platform

## Support

For issues or questions:

1. Check the test suite: `python test_functionality.py`
2. Review error logs in console output
3. Verify credentials in .env file
4. Check platform API documentation
5. Review ARCHITECTURE.md for system design

## Related Documentation

- [README.md](README.md) - Main project documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
