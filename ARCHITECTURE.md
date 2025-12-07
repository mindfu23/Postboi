# Postboi Architecture

## Application Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                      (postboi.kv)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Image   │  │ Filters  │  │ Caption  │  │Platforms │  │
│  │  Picker  │  │Selection │  │  Input   │  │Selection │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                          │                                   │
│                          ▼                                   │
│                   ┌────────────┐                            │
│                   │Share Button│                            │
│                   └────────────┘                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Main Application                          │
│                      (main.py)                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              PostboiApp (MDApp)                      │  │
│  │  • Image selection handler                           │  │
│  │  • Filter application                                │  │
│  │  • Template management                               │  │
│  │  • Platform coordination                             │  │
│  │  • UI state management                               │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌─────────────┐ ┌────────────┐ ┌───────────┐
│   Services  │ │   Utils    │ │ Features  │
│   Package   │ │  Package   │ │  Package  │
└─────────────┘ └────────────┘ └───────────┘
```

## Component Architecture

### 1. Services Layer (Platform Integration)

```
┌─────────────────────────────────────────────────────────────┐
│                     Share Manager                            │
│              (Concurrent Operations Coordinator)             │
│                                                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │        ThreadPoolExecutor (max_workers=3)          │   │
│  │                                                     │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │   │
│  │  │WordPress │  │ Facebook │  │Instagram │        │   │
│  │  │ Service  │  │  Service │  │ Service  │        │   │
│  │  └──────────┘  └──────────┘  └──────────┘        │   │
│  │      │              │              │               │   │
│  │      ▼              ▼              ▼               │   │
│  │  ┌─────────────────────────────────────┐          │   │
│  │  │   Parallel Upload Execution          │          │   │
│  │  └─────────────────────────────────────┘          │   │
│  └────────────────────────────────────────────────────┘   │
│                          │                                 │
│                          ▼                                 │
│              ┌──────────────────────┐                     │
│              │  Results Aggregation  │                     │
│              └──────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌───────────────┐  ┌──────────────┐  ┌─────────────┐
│   REST API    │  │  Graph API   │  │  Graph API  │
│   (WP v2)     │  │  (FB v18.0)  │  │ (IG v18.0)  │
└───────────────┘  └──────────────┘  └─────────────┘
```

### 2. Utils Layer (Image Processing)

```
┌─────────────────────────────────────────────────────────────┐
│                     Image Processing                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Image Utils                              │  │
│  │  • validate_image()                                   │  │
│  │  • resize_image()                                     │  │
│  │  • create_thumbnail()                                 │  │
│  │  • correct_orientation() (EXIF)                       │  │
│  │  • convert_to_jpg()                                   │  │
│  │  • get_image_info()                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Image Filters                            │  │
│  │  • grayscale()        • brightness()                  │  │
│  │  • sepia()            • contrast()                    │  │
│  │  • vintage()          • blur()                        │  │
│  │  • apply_filter()     • sharpen()                     │  │
│  │  • preview_filter()                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│                  ┌──────────────┐                           │
│                  │ Pillow (PIL) │                           │
│                  └──────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

### 3. Features Layer (Advanced Functionality)

```
┌─────────────────────────────────────────────────────────────┐
│                     Post Templates                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Default Templates (10)                              │  │
│  │  • Announcement    • Product Showcase                │  │
│  │  • Quote          • Event Promotion                  │  │
│  │  • Tutorial       • Behind the Scenes                │  │
│  │  • Thank You      • Question/Poll                    │  │
│  │  • Milestone      • Simple                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Variable Substitution Engine                         │  │
│  │  {content} {title} {author} {date} {time}            │  │
│  │  {location} {hashtags}                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Custom Templates (JSON Storage)                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Scheduled Posting                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            APScheduler (Background)                   │  │
│  │                                                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │  Pending   │  │  Queued    │  │  Failed    │    │  │
│  │  │   Posts    │  │   Posts    │  │   Posts    │    │  │
│  │  └────────────┘  └────────────┘  └────────────┘    │  │
│  │        │               │               │             │  │
│  │        └───────────────┼───────────────┘             │  │
│  │                        ▼                              │  │
│  │            ┌──────────────────────┐                  │  │
│  │            │  DateTrigger Jobs    │                  │  │
│  │            └──────────────────────┘                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  JSON Persistence (scheduled_posts.json)             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Typical Share Operation

```
1. User Action
   ↓
2. Image Selection (Plyer FilePicker)
   ↓
3. Filter Application (Optional)
   ↓
4. Caption Entry / Template Selection
   ↓
5. Platform Selection (Checkboxes)
   ↓
6. Share Button Click
   ↓
7. Background Thread Spawned
   ↓
8. ShareManager.share_to_multiple()
   ↓
9. ThreadPoolExecutor Creates 3 Workers
   ↓
10. Parallel Upload to Selected Platforms
    ├─> WordPress REST API
    ├─> Facebook Graph API
    └─> Instagram Graph API
   ↓
11. Results Aggregation
   ↓
12. UI Update (Main Thread via Clock.schedule_once)
   ↓
13. Success/Error Dialog Display
```

### Scheduled Post Execution

```
1. User Schedules Post (date/time selection)
   ↓
2. ScheduledPost Object Created
   ↓
3. Job Added to APScheduler
   ↓
4. Saved to JSON (persistence)
   ↓
... (Wait for scheduled time) ...
   ↓
5. APScheduler Triggers Job
   ↓
6. Callback Executes ShareManager
   ↓
7. Multi-Platform Upload
   ↓
8. Status Updated (published/failed)
   ↓
9. Saved to JSON
   ↓
10. (Optional) User Notification
```

## Configuration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      config.py                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  WORDPRESS_CONFIG                                     │  │
│  │  • site_url                                          │  │
│  │  • username                                          │  │
│  │  • app_password                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FACEBOOK_CONFIG                                      │  │
│  │  • app_id                                            │  │
│  │  • app_secret                                        │  │
│  │  • access_token                                      │  │
│  │  • page_id                                           │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  INSTAGRAM_CONFIG                                     │  │
│  │  • business_account_id                               │  │
│  │  • access_token                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  APP_SETTINGS                                         │  │
│  │  • max_image_size_mb                                 │  │
│  │  • supported_formats                                 │  │
│  │  • max_caption_length                                │  │
│  │  • concurrent_uploads                                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      main.py                                 │
│                  _init_services()                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Service Initialization                               │  │
│  │  • Validate configuration                            │  │
│  │  • Create service instances                          │  │
│  │  • Initialize ShareManager                           │  │
│  │  • Setup Scheduler                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                  Application Layer                           │
│                                                              │
│  Python 3.8+ (Core Language)                                │
│  ├─ Kivy 2.2.1 (UI Framework)                              │
│  ├─ KivyMD 1.1.1 (Material Design)                         │
│  └─ Plyer 2.1.0 (Platform APIs)                            │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                    Services Layer                            │
│                                                              │
│  Requests 2.31.0 (HTTP Client)                              │
│  └─ REST API / Graph API Communication                      │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                   Processing Layer                           │
│                                                              │
│  Pillow 10.1.0 (Image Processing)                           │
│  └─ Image manipulation, filters, EXIF                       │
│                                                              │
│  APScheduler 3.10.4 (Task Scheduling)                       │
│  └─ Background job execution                                │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                    Build Tools                               │
│                                                              │
│  Android: Buildozer 1.5.0+                                  │
│  iOS: kivy-ios 1.3.0+                                       │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

### Android Deployment

```
Source Code
    ↓
Buildozer
    ↓
Python-for-Android
    ↓
Android SDK/NDK
    ↓
Gradle Build
    ↓
APK Package
    ↓
Google Play / Manual Install
```

### iOS Deployment

```
Source Code
    ↓
kivy-ios Toolchain
    ↓
Python Compilation
    ↓
Xcode Project
    ↓
Code Signing
    ↓
IPA Package
    ↓
App Store / TestFlight
```

## Security Considerations

- ✅ No hardcoded credentials
- ✅ Configuration template provided
- ✅ HTTPS for all API communications
- ✅ Access tokens never logged
- ✅ Secure app password handling (WordPress)
- ✅ .gitignore excludes sensitive files
- ✅ Input validation on image uploads
- ✅ CodeQL security scanning passed

## Performance Optimizations

- ✅ ThreadPoolExecutor for concurrent uploads
- ✅ Background threading for non-blocking UI
- ✅ Efficient filter algorithms
- ✅ Image resizing before upload
- ✅ Lazy service initialization
- ✅ APScheduler for background jobs
- ✅ JSON persistence for quick data access

---

**Architecture designed for scalability, maintainability, and cross-platform compatibility.**
