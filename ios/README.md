# Postboi iOS Starter

This directory contains starter templates and configuration for the Postboi iOS application.

## 🚀 Quick Start

### Prerequisites
- macOS with Xcode installed
- iOS 13.0+ target
- Swift 5.0+
- Xcode Command Line Tools

## 📱 Setup Instructions

### 1. Environment Configuration

iOS apps handle environment variables differently than Python or Node.js. Choose one of these approaches:

#### Option A: Xcode Scheme Environment Variables (Development)

1. In Xcode, go to **Product → Scheme → Edit Scheme**
2. Select **Run** → **Arguments**
3. Add environment variables in the **Environment Variables** section:
   ```
   WORDPRESS_SITE_URL = https://yoursite.wordpress.com
   WORDPRESS_USERNAME = your_username
   WORDPRESS_APP_PASSWORD = your_app_password
   FACEBOOK_APP_ID = your_app_id
   FACEBOOK_ACCESS_TOKEN = your_access_token
   FACEBOOK_PAGE_ID = your_page_id
   INSTAGRAM_BUSINESS_ACCOUNT_ID = your_business_account_id
   INSTAGRAM_ACCESS_TOKEN = your_access_token
   ```

#### Option B: Info.plist Configuration (Build-specific)

1. Create configuration-specific `.xcconfig` files:
   - `Debug.xcconfig`
   - `Release.xcconfig`

2. Add your variables:
   ```
   WORDPRESS_SITE_URL = https://yoursite.wordpress.com
   FACEBOOK_PAGE_ID = your_page_id
   ```

3. Reference in Info.plist:
   ```xml
   <key>WordPressSiteURL</key>
   <string>$(WORDPRESS_SITE_URL)</string>
   ```

#### Option C: Keychain Storage (Production - Recommended)

For production apps, store sensitive credentials in iOS Keychain:

```swift
import Security

class KeychainManager {
    static func save(key: String, value: String) {
        let data = value.data(using: .utf8)!
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]
        SecItemAdd(query as CFDictionary, nil)
    }
    
    static func load(key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true
        ]
        
        var result: AnyObject?
        SecItemCopyMatching(query as CFDictionary, &result)
        
        if let data = result as? Data {
            return String(data: data, encoding: .utf8)
        }
        return nil
    }
}
```

### 2. Add PostboiConfig.swift to Your Project

1. Copy `PostboiConfig.swift` to your Xcode project
2. Add it to your target
3. Initialize in your AppDelegate:

```swift
import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(_ application: UIApplication, 
                    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // Initialize Postboi configuration
        PostboiConfig.initialize()
        
        return true
    }
}
```

### 3. Using the Configuration

```swift
// Access WordPress configuration
let siteUrl = PostboiConfig.WordPress.siteUrl
let username = PostboiConfig.WordPress.username

// Access Facebook configuration
let pageId = PostboiConfig.Facebook.pageId
let accessToken = PostboiConfig.Facebook.accessToken

// Access app settings
let maxImageSize = PostboiConfig.AppSettings.maxImageSizeMb
```

## 🔐 Security Best Practices

1. **Never commit credentials** to version control
2. **Use Keychain** for storing sensitive data in production
3. **Enable App Transport Security (ATS)** in Info.plist
4. **Implement certificate pinning** for API calls
5. **Use Face ID/Touch ID** for app authentication
6. **Enable data protection** for files

### Info.plist Security Settings

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
</dict>

<key>NSPhotoLibraryUsageDescription</key>
<string>Postboi needs access to your photos to share them on social media</string>

<key>NSCameraUsageDescription</key>
<string>Postboi needs access to your camera to take photos</string>
```

## 📦 Required Dependencies

### Using Swift Package Manager

Add these packages to your project:

```swift
// Package.swift or Xcode → File → Add Package Dependency

dependencies: [
    .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.8.0"),
    .package(url: "https://github.com/facebook/facebook-ios-sdk.git", from: "16.0.0")
]
```

### Using CocoaPods

```ruby
# Podfile
platform :ios, '13.0'

target 'Postboi' do
  use_frameworks!
  
  # Networking
  pod 'Alamofire', '~> 5.8'
  
  # Facebook SDK
  pod 'FBSDKCoreKit'
  pod 'FBSDKLoginKit'
  pod 'FBSDKShareKit'
  
  # Image Processing
  pod 'Kingfisher', '~> 7.0'
end
```

## 🏗️ Build Configuration

### Debug vs Release

Create different configurations for development and production:

1. **Debug**: Use test credentials, verbose logging
2. **Release**: Use production credentials, minimal logging

In `PostboiConfig.swift`:

```swift
#if DEBUG
static let apiEndpoint = "https://api-staging.example.com"
#else
static let apiEndpoint = "https://api.example.com"
#endif
```

## 📱 Building for Device

### Using kivy-ios (Python/Kivy approach)

If you're using Kivy for the main app:

```bash
# Install kivy-ios
pip install kivy-ios

# Build the toolchain
toolchain build python3 kivy pillow

# Create Xcode project
toolchain create Postboi /path/to/Postboi

# Open in Xcode
open Postboi-ios/Postboi.xcodeproj
```

### Native iOS Development

1. Create a new Xcode project
2. Add `PostboiConfig.swift`
3. Implement UI using UIKit or SwiftUI
4. Add API integration code
5. Configure signing & capabilities
6. Build and run on device

## 🔗 Related Resources

- [iOS Developer Documentation](https://developer.apple.com/documentation/)
- [Swift Programming Language](https://swift.org/documentation/)
- [Kivy iOS Documentation](https://kivy-ios.readthedocs.io/)
- [Main Project README](../README.md)

## 📝 Next Steps

1. Configure your environment variables
2. Implement API service classes
3. Create UI for image selection and posting
4. Add error handling and user feedback
5. Test on physical device
6. Submit to App Store (requires Apple Developer account)
