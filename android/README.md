# Postboi Android Starter

This directory contains starter templates and configuration for the Postboi Android application.

## 🚀 Quick Start

### Prerequisites
- Android Studio Arctic Fox or later
- Android SDK 21+ (Lollipop)
- Kotlin 1.8+
- Gradle 8.0+

## 📱 Setup Instructions

### 1. Environment Configuration

Android apps handle environment variables through Gradle build configuration. Choose one of these approaches:

#### Option A: Using gradle.properties (Recommended for Development)

1. Copy the template:
   ```bash
   cp gradle.properties.template gradle.properties
   ```

2. Edit `gradle.properties` with your credentials:
   ```properties
   WORDPRESS_SITE_URL=https://yoursite.wordpress.com
   WORDPRESS_USERNAME=your_username
   WORDPRESS_APP_PASSWORD=your_app_password
   FACEBOOK_APP_ID=your_app_id
   FACEBOOK_ACCESS_TOKEN=your_access_token
   FACEBOOK_PAGE_ID=your_page_id
   INSTAGRAM_BUSINESS_ACCOUNT_ID=your_business_account_id
   INSTAGRAM_ACCESS_TOKEN=your_access_token
   ```

3. Add to `.gitignore`:
   ```
   gradle.properties
   local.properties
   ```

4. Update your `app/build.gradle` (see `build.gradle.example`):
   ```gradle
   android {
       defaultConfig {
           buildConfigField "String", "WORDPRESS_SITE_URL", 
               "\"${project.findProperty('WORDPRESS_SITE_URL') ?: ''}\""
           // ... other fields
       }
   }
   ```

#### Option B: Using local.properties

1. Add credentials to `local.properties`:
   ```properties
   wordpress.site.url=https://yoursite.wordpress.com
   facebook.page.id=your_page_id
   ```

2. Load in `build.gradle`:
   ```gradle
   def localProperties = new Properties()
   localProperties.load(new FileInputStream(rootProject.file("local.properties")))
   
   android {
       defaultConfig {
           buildConfigField "String", "WORDPRESS_SITE_URL",
               "\"${localProperties['wordpress.site.url']}\""
       }
   }
   ```

#### Option C: Using Encrypted Shared Preferences (Production)

For production apps, use Android's EncryptedSharedPreferences:

```kotlin
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SecureConfig(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()
    
    private val prefs = EncryptedSharedPreferences.create(
        context,
        "postboi_secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
    
    fun saveCredential(key: String, value: String) {
        prefs.edit().putString(key, value).apply()
    }
    
    fun getCredential(key: String): String? {
        return prefs.getString(key, null)
    }
}
```

### 2. Add PostboiConfig.kt to Your Project

1. Create package: `com.postboi.config`
2. Copy `PostboiConfig.kt` to the package
3. Initialize in your Application class:

```kotlin
import android.app.Application
import com.postboi.config.PostboiConfig

class PostboiApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        PostboiConfig.initialize(this)
    }
}
```

4. Declare in `AndroidManifest.xml`:
```xml
<application
    android:name=".PostboiApplication"
    ...>
</application>
```

### 3. Using the Configuration

```kotlin
// Access WordPress configuration
val siteUrl = PostboiConfig.WordPress.siteUrl
val username = PostboiConfig.WordPress.username

// Access Facebook configuration
val pageId = PostboiConfig.Facebook.pageId
val accessToken = PostboiConfig.Facebook.accessToken

// Access app settings
val maxImageSize = PostboiConfig.AppSettings.maxImageSizeMb

// Check if platform is configured
if (PostboiConfig.Facebook.isConfigured) {
    // Initialize Facebook SDK
    FacebookSdk.sdkInitialize(this)
}
```

## 🔐 Security Best Practices

### 1. ProGuard/R8 Configuration

Add to `proguard-rules.pro`:

```proguard
# Keep BuildConfig
-keep class com.postboi.app.BuildConfig { *; }

# Obfuscate sensitive strings
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
}
```

### 2. Network Security Configuration

Create `res/xml/network_security_config.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
    
    <!-- Certificate Pinning for APIs -->
    <domain-config>
        <domain includeSubdomains="true">graph.facebook.com</domain>
        <pin-set>
            <pin digest="SHA-256">YOUR_CERTIFICATE_PIN</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

Add to `AndroidManifest.xml`:

```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
</application>
```

### 3. Required Permissions

Add to `AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" 
    android:maxSdkVersion="32" />
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.CAMERA" />
```

## 📦 Dependencies

### Add to your app's `build.gradle`:

```gradle
dependencies {
    // Core Android
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
    
    // Networking
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    implementation 'com.squareup.okhttp3:okhttp:4.12.0'
    
    // Image Loading & Processing
    implementation 'com.github.bumptech.glide:glide:4.16.0'
    annotationProcessor 'com.github.bumptech.glide:compiler:4.16.0'
    
    // Facebook SDK
    implementation 'com.facebook.android:facebook-android-sdk:16.0.0'
    
    // Coroutines
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'
    
    // Security
    implementation 'androidx.security:security-crypto:1.1.0-alpha06'
}
```

## 🏗️ Build Variants

### Configure build types in `app/build.gradle`:

```gradle
android {
    buildTypes {
        debug {
            applicationIdSuffix ".debug"
            versionNameSuffix "-DEBUG"
            debuggable true
        }
        
        staging {
            applicationIdSuffix ".staging"
            versionNameSuffix "-STAGING"
            debuggable false
            minifyEnabled true
        }
        
        release {
            debuggable false
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 
                'proguard-rules.pro'
        }
    }
}
```

## 🔨 Building the App

### Using Android Studio

1. Open Android Studio
2. File → Open → Select Postboi project
3. Build → Make Project
4. Run → Run 'app'

### Using Gradle Command Line

```bash
# Debug build
./gradlew assembleDebug

# Release build
./gradlew assembleRelease

# Install on connected device
./gradlew installDebug

# Run tests
./gradlew test
```

### Using Buildozer (Kivy)

If using the existing Kivy setup:

```bash
# Install dependencies
pip install buildozer cython

# Initialize buildozer
buildozer init

# Build debug APK
buildozer android debug

# Build and deploy
buildozer android debug deploy run
```

## 📱 Testing

### Unit Tests

```kotlin
class PostboiConfigTest {
    @Test
    fun testWordPressConfiguration() {
        assertTrue(PostboiConfig.WordPress.siteUrl.isNotEmpty())
    }
    
    @Test
    fun testFacebookConfiguration() {
        if (PostboiConfig.Facebook.isConfigured) {
            assertNotEquals("your_page_id", PostboiConfig.Facebook.pageId)
        }
    }
}
```

### Integration Tests

```kotlin
@RunWith(AndroidJUnit4::class)
class APIIntegrationTest {
    @Test
    fun testFacebookConnection() {
        val pageId = PostboiConfig.Facebook.pageId
        val accessToken = PostboiConfig.Facebook.accessToken
        
        // Test API call
        // ...
    }
}
```

## 🚀 Deployment

### Signing the APK

1. Generate keystore:
   ```bash
   keytool -genkey -v -keystore postboi-release.keystore \
       -alias postboi -keyalg RSA -keysize 2048 -validity 10000
   ```

2. Add to `gradle.properties`:
   ```properties
   KEYSTORE_FILE=/path/to/postboi-release.keystore
   KEYSTORE_PASSWORD=your_password
   KEY_ALIAS=postboi
   KEY_PASSWORD=your_key_password
   ```

3. Configure in `app/build.gradle`:
   ```gradle
   android {
       signingConfigs {
           release {
               storeFile file(project.findProperty('KEYSTORE_FILE'))
               storePassword project.findProperty('KEYSTORE_PASSWORD')
               keyAlias project.findProperty('KEY_ALIAS')
               keyPassword project.findProperty('KEY_PASSWORD')
           }
       }
       
       buildTypes {
           release {
               signingConfig signingConfigs.release
           }
       }
   }
   ```

### Publishing to Google Play

1. Build release APK/AAB:
   ```bash
   ./gradlew bundleRelease
   ```

2. Upload to Google Play Console
3. Fill in app details, screenshots, etc.
4. Submit for review

## 🔗 Related Resources

- [Android Developer Documentation](https://developer.android.com/)
- [Kotlin Programming Language](https://kotlinlang.org/)
- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [Main Project README](../README.md)

## 📝 Next Steps

1. Configure your `gradle.properties` with credentials
2. Set up your Application class
3. Implement API service classes
4. Create UI for image selection and posting
5. Add error handling and user feedback
6. Test on physical device or emulator
7. Prepare for Google Play release
