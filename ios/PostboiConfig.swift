//
//  PostboiConfig.swift
//  Postboi iOS Starter Template
//
//  Configuration manager that loads API credentials from environment variables
//

import Foundation

/// Configuration structure for Postboi app
struct PostboiConfig {
    
    // MARK: - WordPress Configuration
    struct WordPress {
        static let siteUrl = ProcessInfo.processInfo.environment["WORDPRESS_SITE_URL"] ?? "https://yoursite.wordpress.com"
        static let username = ProcessInfo.processInfo.environment["WORDPRESS_USERNAME"] ?? "your_username"
        static let appPassword = ProcessInfo.processInfo.environment["WORDPRESS_APP_PASSWORD"] ?? ""
        
        static var isConfigured: Bool {
            return siteUrl != "https://yoursite.wordpress.com" && !appPassword.isEmpty
        }
    }
    
    // MARK: - Facebook Configuration
    struct Facebook {
        static let appId = ProcessInfo.processInfo.environment["FACEBOOK_APP_ID"] ?? "your_app_id"
        static let appSecret = ProcessInfo.processInfo.environment["FACEBOOK_APP_SECRET"] ?? ""
        static let accessToken = ProcessInfo.processInfo.environment["FACEBOOK_ACCESS_TOKEN"] ?? ""
        static let pageId = ProcessInfo.processInfo.environment["FACEBOOK_PAGE_ID"] ?? "your_page_id"
        
        static var isConfigured: Bool {
            return appId != "your_app_id" && !accessToken.isEmpty && pageId != "your_page_id"
        }
    }
    
    // MARK: - Instagram Configuration
    struct Instagram {
        static let businessAccountId = ProcessInfo.processInfo.environment["INSTAGRAM_BUSINESS_ACCOUNT_ID"] ?? "your_business_account_id"
        static let accessToken = ProcessInfo.processInfo.environment["INSTAGRAM_ACCESS_TOKEN"] ?? ""
        
        static var isConfigured: Bool {
            return businessAccountId != "your_business_account_id" && !accessToken.isEmpty
        }
    }
    
    // MARK: - Application Settings
    struct AppSettings {
        static let maxImageSizeMb = Int(ProcessInfo.processInfo.environment["MAX_IMAGE_SIZE_MB"] ?? "10") ?? 10
        static let concurrentUploads = Int(ProcessInfo.processInfo.environment["CONCURRENT_UPLOADS"] ?? "3") ?? 3
        static let supportedFormats = ["jpg", "jpeg", "png", "heic"]
        static let maxCaptionLength = 2200
    }
    
    // MARK: - Initialization
    
    /// Initialize and validate configuration
    static func initialize() {
        print("Initializing Postboi Configuration...")
        
        // Check WordPress configuration
        if WordPress.isConfigured {
            print("✓ WordPress configured")
        } else {
            print("⚠️ WordPress not configured")
        }
        
        // Check Facebook configuration
        if Facebook.isConfigured {
            print("✓ Facebook configured")
        } else {
            print("⚠️ Facebook not configured")
        }
        
        // Check Instagram configuration
        if Instagram.isConfigured {
            print("✓ Instagram configured")
        } else {
            print("⚠️ Instagram not configured")
        }
        
        print("Configuration initialized")
    }
    
    /// Load configuration from .env file (if using a third-party library)
    /// Note: iOS doesn't natively support .env files, so you'll need to:
    /// 1. Use build configurations (Debug, Release, etc.)
    /// 2. Use Info.plist with environment-specific keys
    /// 3. Use a third-party library like DotEnv
    /// 4. Use Xcode scheme environment variables
    static func loadFromEnvironment() {
        // For production apps, load from Info.plist or secure storage
        // Never commit sensitive credentials to version control
        
        #if DEBUG
        print("Loading configuration from environment variables...")
        print("For production, use Keychain or secure configuration management")
        #endif
    }
}

// MARK: - Usage Example

/*
 Usage in your iOS app:
 
 // In AppDelegate or SceneDelegate
 func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
     PostboiConfig.initialize()
     return true
 }
 
 // Accessing configuration
 let wordpressSiteUrl = PostboiConfig.WordPress.siteUrl
 let facebookPageId = PostboiConfig.Facebook.pageId
 let maxImageSize = PostboiConfig.AppSettings.maxImageSizeMb
 
 // Check if platform is configured
 if PostboiConfig.Facebook.isConfigured {
     // Initialize Facebook SDK
 }
 */
