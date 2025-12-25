package com.postboi.config

import android.content.Context
import android.util.Log

/**
 * Configuration manager for Postboi Android app
 * Loads API credentials from environment variables or build config
 */
object PostboiConfig {
    
    private const val TAG = "PostboiConfig"
    
    // Cache environment variables on first access
    private val envCache: Map<String, String> by lazy {
        mapOf(
            "WORDPRESS_SITE_URL" to getEnvVariable("WORDPRESS_SITE_URL", "https://yoursite.wordpress.com"),
            "WORDPRESS_USERNAME" to getEnvVariable("WORDPRESS_USERNAME", "your_username"),
            "WORDPRESS_APP_PASSWORD" to getEnvVariable("WORDPRESS_APP_PASSWORD", ""),
            "FACEBOOK_APP_ID" to getEnvVariable("FACEBOOK_APP_ID", "your_app_id"),
            "FACEBOOK_APP_SECRET" to getEnvVariable("FACEBOOK_APP_SECRET", ""),
            "FACEBOOK_ACCESS_TOKEN" to getEnvVariable("FACEBOOK_ACCESS_TOKEN", ""),
            "FACEBOOK_PAGE_ID" to getEnvVariable("FACEBOOK_PAGE_ID", "your_page_id"),
            "INSTAGRAM_BUSINESS_ACCOUNT_ID" to getEnvVariable("INSTAGRAM_BUSINESS_ACCOUNT_ID", "your_business_account_id"),
            "INSTAGRAM_ACCESS_TOKEN" to getEnvVariable("INSTAGRAM_ACCESS_TOKEN", ""),
            "MAX_IMAGE_SIZE_MB" to getEnvVariable("MAX_IMAGE_SIZE_MB", "10"),
            "CONCURRENT_UPLOADS" to getEnvVariable("CONCURRENT_UPLOADS", "3")
        )
    }
    
    // WordPress Configuration
    object WordPress {
        val siteUrl: String
            get() = envCache["WORDPRESS_SITE_URL"] ?: "https://yoursite.wordpress.com"
        
        val username: String
            get() = envCache["WORDPRESS_USERNAME"] ?: "your_username"
        
        val appPassword: String
            get() = envCache["WORDPRESS_APP_PASSWORD"] ?: ""
        
        val isConfigured: Boolean
            get() = siteUrl != "https://yoursite.wordpress.com" && appPassword.isNotEmpty()
    }
    
    // Facebook Configuration
    object Facebook {
        val appId: String
            get() = envCache["FACEBOOK_APP_ID"] ?: "your_app_id"
        
        val appSecret: String
            get() = envCache["FACEBOOK_APP_SECRET"] ?: ""
        
        val accessToken: String
            get() = envCache["FACEBOOK_ACCESS_TOKEN"] ?: ""
        
        val pageId: String
            get() = envCache["FACEBOOK_PAGE_ID"] ?: "your_page_id"
        
        val isConfigured: Boolean
            get() = appId != "your_app_id" && accessToken.isNotEmpty() && pageId != "your_page_id"
    }
    
    // Instagram Configuration
    object Instagram {
        val businessAccountId: String
            get() = envCache["INSTAGRAM_BUSINESS_ACCOUNT_ID"] ?: "your_business_account_id"
        
        val accessToken: String
            get() = envCache["INSTAGRAM_ACCESS_TOKEN"] ?: ""
        
        val isConfigured: Boolean
            get() = businessAccountId != "your_business_account_id" && accessToken.isNotEmpty()
    }
    
    // Application Settings
    object AppSettings {
        val maxImageSizeMb: Int
            get() = envCache["MAX_IMAGE_SIZE_MB"]?.toIntOrNull() ?: 10
        
        val concurrentUploads: Int
            get() = envCache["CONCURRENT_UPLOADS"]?.toIntOrNull() ?: 3
        
        val supportedFormats = listOf("jpg", "jpeg", "png", "webp")
        val maxCaptionLength = 2200
    }
    
    /**
     * Initialize configuration and validate settings
     */
    fun initialize(context: Context) {
        Log.d(TAG, "Initializing Postboi Configuration...")
        
        // Check WordPress configuration
        if (WordPress.isConfigured) {
            Log.d(TAG, "✓ WordPress configured")
        } else {
            Log.w(TAG, "⚠️ WordPress not configured")
        }
        
        // Check Facebook configuration
        if (Facebook.isConfigured) {
            Log.d(TAG, "✓ Facebook configured")
        } else {
            Log.w(TAG, "⚠️ Facebook not configured")
        }
        
        // Check Instagram configuration
        if (Instagram.isConfigured) {
            Log.d(TAG, "✓ Instagram configured")
        } else {
            Log.w(TAG, "⚠️ Instagram not configured")
        }
        
        Log.d(TAG, "Configuration initialized")
    }
    
    /**
     * Get environment variable with fallback
     * In production, this should read from BuildConfig or secure storage
     */
    private fun getEnvVariable(key: String, default: String): String {
        // Option 1: Read from System environment (works with build-time injection)
        val envValue = System.getenv(key)
        if (!envValue.isNullOrEmpty()) {
            return envValue
        }
        
        // Option 2: Read from BuildConfig (requires gradle configuration)
        // Example: BuildConfig.WORDPRESS_SITE_URL
        
        // Option 3: Read from local.properties or assets
        // This is where you'd implement loading from a secure location
        
        return default
    }
    
    /**
     * Load configuration from BuildConfig (gradle.properties)
     * Add this to your app's build.gradle:
     * 
     * android {
     *     defaultConfig {
     *         buildConfigField "String", "WORDPRESS_SITE_URL", "\"${project.findProperty('WORDPRESS_SITE_URL') ?: ''}\""
     *         buildConfigField "String", "FACEBOOK_PAGE_ID", "\"${project.findProperty('FACEBOOK_PAGE_ID') ?: ''}\""
     *         // ... other fields
     *     }
     * }
     */
}

/**
 * Usage Example in your Application class:
 * 
 * class PostboiApplication : Application() {
 *     override fun onCreate() {
 *         super.onCreate()
 *         PostboiConfig.initialize(this)
 *     }
 * }
 * 
 * Usage in Activities/Fragments:
 * 
 * val siteUrl = PostboiConfig.WordPress.siteUrl
 * val pageId = PostboiConfig.Facebook.pageId
 * val maxSize = PostboiConfig.AppSettings.maxImageSizeMb
 * 
 * if (PostboiConfig.Facebook.isConfigured) {
 *     // Initialize Facebook SDK
 * }
 */
