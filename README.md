# Postboi 📱

Cross-platform mobile app (iOS & Android) for sharing images and text to Instagram, Facebook, and WordPress simultaneously. Built with Python and Kivy.

## ✨ Features

- 📷 **Select Images** - Pick images from your device gallery or camera
- ✍️ **Add Captions** - Write engaging captions with template support
- 📱 **Multi-Platform Sharing** - Share to multiple platforms at once:
  - Instagram (Business/Creator accounts via API, Personal via native share)
  - Facebook (Pages via Graph API)
  - WordPress (via REST API with featured images)
- 🎨 **Image Filters** - Apply beautiful filters before sharing:
  - Grayscale, Sepia, Vintage
  - Brightness & Contrast adjustments
  - Blur & Sharpen effects
- 📝 **Post Templates** - Pre-defined templates for common post types:
  - Announcement, Quote, Product Showcase
  - Event Promotion, Behind-the-Scenes
  - Custom template creation
- ⏰ **Scheduled Posting** - Schedule posts for optimal engagement times
- 🔄 **Concurrent Uploads** - Fast simultaneous posting using ThreadPoolExecutor

## 🛠️ Tech Stack

- **Python 3.8+** - Core programming language
- **Kivy 2.2.1+** - Cross-platform UI framework
- **KivyMD 1.1.1+** - Material Design components
- **Plyer 2.1.0+** - Cross-platform APIs (file picker, camera, etc.)
- **Pillow 10.1.0+** - Image processing
- **APScheduler 3.10.4+** - Job scheduling
- **Buildozer 1.5.0+** - Android app builder
- **kivy-ios 1.3.0+** - iOS app builder

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Platform-Specific Requirements

**For Android Builds:**
- Linux or macOS (or WSL on Windows)
- Java Development Kit (JDK) 11 or 17
- Android SDK and NDK (automatically downloaded by Buildozer)

**For iOS Builds:**
- macOS with Xcode installed
- Xcode Command Line Tools
- Apple Developer Account (for device deployment)

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/mindfu23/Postboi.git
cd Postboi
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Platform Credentials

Edit `config.py` and add your platform credentials:

```python
# WordPress Configuration
WORDPRESS_CONFIG = {
    'site_url': 'https://yoursite.wordpress.com',
    'username': 'your_username',
    'app_password': 'xxxx xxxx xxxx xxxx xxxx xxxx',
    'rss_feed_url': 'https://yoursite.wordpress.com/feed/',
}

# Facebook Configuration
FACEBOOK_CONFIG = {
    'app_id': 'your_app_id',
    'app_secret': 'your_app_secret',
    'access_token': 'your_page_access_token',
    'page_id': 'your_page_id',
}

# Instagram Configuration
INSTAGRAM_CONFIG = {
    'business_account_id': 'your_instagram_business_account_id',
    'access_token': 'your_access_token',
}
```

### 4. Run Locally (Desktop Testing)

```bash
python main.py
```

Note: Desktop testing has limited functionality (file picker and some native features won't work). Build for mobile for full functionality.

## 🔐 Platform Setup Guides

### WordPress Setup

#### 1. Enable REST API
- WordPress REST API is enabled by default on most WordPress installations
- Verify by visiting: `https://yoursite.wordpress.com/wp-json/`

#### 2. Create Application Password
1. Log into your WordPress admin dashboard
2. Go to **Users → Profile**
3. Scroll down to **Application Passwords**
4. Enter an application name (e.g., "Postboi")
5. Click **Add New Application Password**
6. Copy the generated password (with spaces)
7. Paste it into `config.py` as `app_password`

#### 3. Find Your Site URL
- Your site URL is the base URL of your WordPress site
- Example: `https://yoursite.wordpress.com` or `https://yoursite.com`

#### 4. Testing the Connection
```python
from services.wordpress import WordPressService

wp = WordPressService(
    site_url='https://yoursite.wordpress.com',
    username='your_username',
    app_password='xxxx xxxx xxxx xxxx xxxx xxxx'
)

success, message = wp.test_connection()
print(message)
```

#### 5. RSS Feed URLs
- Main feed: `https://yoursite.wordpress.com/feed/`
- Comments feed: `https://yoursite.wordpress.com/comments/feed/`
- Category feed: `https://yoursite.wordpress.com/category/category-name/feed/`

### Facebook Setup

#### 1. Create a Facebook Developer App
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **My Apps → Create App**
3. Select **Business** as the app type
4. Fill in app details and create the app

#### 2. Add Facebook Login Product
1. In your app dashboard, click **Add Product**
2. Find **Facebook Login** and click **Set Up**
3. Select **Web** as the platform
4. Follow the setup wizard

#### 3. Generate Access Tokens
1. In your app dashboard, go to **Tools → Graph API Explorer**
2. Select your app from the dropdown
3. Click **Generate Access Token**
4. Grant necessary permissions:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
5. Copy the **User Access Token**
6. Convert to **Page Access Token**:
   - Go to **Tools → Access Token Tool**
   - Find your page and copy the Page Access Token

#### 4. Get Your Page ID
**Method 1: From Page Settings**
1. Go to your Facebook Page
2. Click **Settings**
3. Click **Page Info**
4. Scroll to find **Page ID**

**Method 2: Using Graph API Explorer**
1. Go to Graph API Explorer
2. Enter: `me/accounts` in the query field
3. Click Submit
4. Find your page in the response and copy the `id`

#### 5. Required Permissions
- `pages_manage_posts` - Post on behalf of the page
- `pages_read_engagement` - Read engagement metrics
- `pages_show_list` - List pages the user manages

#### 6. Testing the Integration
```python
from services.facebook_share import FacebookService

fb = FacebookService(
    page_id='your_page_id',
    access_token='your_page_access_token'
)

success, message = fb.test_connection()
print(message)
```

### Instagram Setup

#### 1. Convert to Business/Creator Account
1. Open Instagram mobile app
2. Go to **Profile → Settings → Account**
3. Tap **Switch to Professional Account**
4. Choose **Business** or **Creator**
5. Follow the setup process

#### 2. Connect to Facebook Page
1. In Instagram app, go to **Settings → Account → Linked Accounts**
2. Select **Facebook**
3. Link to a Facebook Page you manage
4. This connection is required for the Instagram Graph API

#### 3. Get Instagram Business Account ID
**Method 1: Using Graph API Explorer**
1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app and generate a token with `instagram_basic` permission
3. Query: `me/accounts?fields=instagram_business_account`
4. Copy the `instagram_business_account.id`

**Method 2: Using Facebook Business Manager**
1. Go to [Facebook Business Manager](https://business.facebook.com/)
2. Navigate to **Business Settings → Instagram Accounts**
3. Your Instagram Business Account ID is displayed there

#### 4. API Limitations
**Business/Creator Accounts:**
- ✅ Full API support via Graph API
- ✅ Can post images with captions
- ✅ Supports scheduled posting
- ⚠️ Requires publicly accessible image URLs

**Personal Accounts:**
- ❌ No API access
- ✅ Native share intent supported (mobile only)
- ℹ️ App will use native sharing for personal accounts

#### 5. Native Share Fallback
For personal accounts or when API fails, the app uses native sharing:
1. Image is prepared for sharing
2. Caption is copied to clipboard
3. Instagram app opens with the image
4. User pastes caption and posts manually

#### 6. Testing the Integration
```python
from services.instagram_share import InstagramService

ig = InstagramService(
    business_account_id='your_instagram_business_account_id',
    access_token='your_access_token'
)

success, message = ig.test_connection()
print(message)
```

## 📱 Building the App

### Android Build

#### 1. Install Buildozer
```bash
pip install buildozer
```

#### 2. Install System Dependencies (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y python3-pip build-essential git ffmpeg libsdl2-dev \
    libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev \
    libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
```

#### 3. Configure buildozer.spec
The `buildozer.spec` file is already configured. You can customize:
- `title` - App name
- `package.name` - Package identifier
- `package.domain` - Your domain
- `version` - App version
- `android.permissions` - Android permissions
- `android.api` - Target Android API level

#### 4. Build Debug APK
```bash
buildozer android debug
```

This will:
- Download and setup Android SDK/NDK
- Compile Python and dependencies
- Package the APK
- Output: `bin/postboi-1.0.0-arm64-v8a-debug.apk`

#### 5. Build Release APK
```bash
buildozer android release
```

#### 6. Sign the APK (for Release)
```bash
# Generate keystore (first time only)
keytool -genkey -v -keystore postboi-release.keystore -alias postboi \
    -keyalg RSA -keysize 2048 -validity 10000

# Sign the APK
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
    -keystore postboi-release.keystore \
    bin/postboi-1.0.0-arm64-v8a-release-unsigned.apk postboi

# Align the APK
zipalign -v 4 bin/postboi-1.0.0-arm64-v8a-release-unsigned.apk \
    bin/postboi-1.0.0-release.apk
```

#### 7. Deploy to Device
```bash
# Install via ADB
adb install bin/postboi-1.0.0-arm64-v8a-debug.apk

# Or using buildozer
buildozer android debug deploy run
```

### iOS Build

#### 1. Prerequisites
- macOS with Xcode installed
- Xcode Command Line Tools: `xcode-select --install`
- Apple Developer Account

#### 2. Install kivy-ios
```bash
pip install kivy-ios
```

#### 3. Build the Toolchain
```bash
toolchain build python3 kivy pillow
```

This will compile Python and Kivy for iOS (takes 30-60 minutes).

#### 4. Create Xcode Project
```bash
toolchain create Postboi /path/to/Postboi
```

#### 5. Configure Code Signing
1. Open the generated Xcode project
2. Select the project in the navigator
3. Go to **Signing & Capabilities**
4. Select your **Team** (Apple Developer Account)
5. Ensure **Automatically manage signing** is checked

#### 6. Add Required Capabilities
1. In Xcode, go to **Signing & Capabilities**
2. Click **+ Capability**
3. Add:
   - **App Groups** (for shared storage)
   - **Background Modes** → Background fetch (for scheduled posts)

#### 7. Build and Deploy
1. Connect your iOS device via USB
2. Select your device as the build target
3. Click **Build** (Cmd + B) to build
4. Click **Run** (Cmd + R) to deploy and run

#### 8. Deploy to App Store (Optional)
1. In Xcode, select **Product → Archive**
2. Once archived, click **Distribute App**
3. Follow the App Store submission process

## 🔧 Troubleshooting

### Common Errors

#### Buildozer: "Command failed: python -m pip install..."
**Solution:** Update pip and setuptools:
```bash
python3 -m pip install --upgrade pip setuptools
```

#### Android: "SDK License Not Accepted"
**Solution:** Set `android.accept_sdk_license = True` in `buildozer.spec`

#### Kivy: "ImportError: No module named 'kivy'"
**Solution:** Ensure Kivy is installed:
```bash
pip install kivy kivymd
```

#### WordPress: "401 Unauthorized"
**Solution:**
- Verify application password is correct (with spaces removed in code)
- Check that your WordPress user has admin or editor role
- Ensure REST API is enabled

#### Facebook: "Error validating access token"
**Solution:**
- Generate a new Page Access Token
- Ensure token has required permissions
- Check token hasn't expired (use long-lived tokens)

#### Instagram: "Requires public image URL"
**Solution:**
- Instagram API requires images to be hosted at a public URL
- For local files, upload to a temporary hosting service first
- Alternative: Use native share intent on mobile devices

### Platform-Specific Issues

#### Android: App Crashes on Startup
- Check logcat: `adb logcat | grep python`
- Ensure all permissions are granted
- Verify requirements are correctly specified in `buildozer.spec`

#### iOS: Code Signing Failed
- Verify Apple Developer Account is active
- Check provisioning profiles
- Ensure bundle identifier is unique

### API Rate Limits

#### WordPress
- REST API: ~100 requests per minute per IP
- Solution: Implement request throttling if needed

#### Facebook
- Page posts: 200 posts per day per user
- Graph API: 200 calls per hour per user
- Solution: Monitor usage in Facebook Developer Dashboard

#### Instagram
- Content Publishing: 25 posts per day
- Graph API: 200 calls per hour per user
- Solution: Implement rate limiting and error handling

### Authentication Problems

#### Invalid Credentials
1. Double-check all credentials in `config.py`
2. Ensure no extra spaces or special characters
3. Test connections individually using test scripts

#### Expired Tokens
1. Facebook/Instagram tokens expire (60 days for long-lived)
2. Regenerate tokens periodically
3. Implement token refresh logic for production apps

## 🤝 Contributing

Contributions are welcome! Here's how to contribute:

### How to Contribute

1. **Fork the repository**
   ```bash
   git clone https://github.com/mindfu23/Postboi.git
   cd Postboi
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow PEP 8 style guidelines
   - Add docstrings to all functions and classes
   - Include type hints where appropriate
   - Add comments for complex logic

4. **Test your changes**
   ```bash
   python main.py
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: Description of your feature"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Describe your changes in detail
   - Link any related issues

### Code Style Guidelines

- Follow **PEP 8** for Python code
- Use **type hints** for function parameters and return values
- Write **docstrings** for all public functions and classes
- Keep functions small and focused (single responsibility)
- Use meaningful variable and function names
- Add comments for complex logic
- Format KV files consistently with proper indentation

### Pull Request Process

1. Update README.md with details of changes if applicable
2. Update requirements.txt if you add new dependencies
3. Ensure your code follows the style guidelines
4. Test on both Android and iOS if possible
5. Your PR will be reviewed by maintainers
6. Address any feedback from reviewers
7. Once approved, your PR will be merged

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [Kivy](https://kivy.org/) - Cross-platform Python framework
- [KivyMD](https://kivymd.readthedocs.io/) - Material Design components
- [Plyer](https://plyer.readthedocs.io/) - Platform-independent API access
- [Pillow](https://pillow.readthedocs.io/) - Image processing library

## 📧 Support

For issues, questions, or suggestions:
- 🐛 [Open an Issue](https://github.com/mindfu23/Postboi/issues)
- 💬 [Discussions](https://github.com/mindfu23/Postboi/discussions)

## 🗺️ Roadmap

- [ ] Video support
- [ ] Multiple image carousel posts
- [ ] Analytics dashboard
- [ ] More social platforms (Twitter, LinkedIn, TikTok)
- [ ] Cloud storage integration
- [ ] Collaboration features
- [ ] Hashtag suggestions
- [ ] Post performance tracking

---

Made with ❤️ by [mindfu23](https://github.com/mindfu23)
