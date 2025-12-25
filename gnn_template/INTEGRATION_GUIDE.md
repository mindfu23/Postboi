# GNN Template - Integration with Postboi Mobile App

This guide explains how to integrate the Good News Network (GNN) front-end template with the Postboi Kivy mobile application.

## Option 1: WebView Integration (Recommended for Mobile)

### Step 1: Install WebView Support

Add to your `requirements.txt`:
```
pywebview==4.0.2
```

Or for Android using Buildozer, add to `buildozer.spec`:
```ini
requirements = python3,kivy,kivymd,plyer,pillow,requests,apscheduler,android,jnius
```

### Step 2: Create GNN Screen in Kivy

Create a new file `features/gnn_screen.py`:

```python
"""
Good News Network Screen
Displays articles using the GNN web template
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from android import mActivity
from jnius import autoclass, cast

WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')


class GNNScreen(Screen):
    """Screen that displays Good News Network articles."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'gnn'
        
        # Create layout
        layout = BoxLayout(orientation='vertical')
        
        # Create WebView
        self.setup_webview()
        
        self.add_widget(layout)
    
    def setup_webview(self):
        """Set up Android WebView to display GNN template."""
        # Get the Android activity
        activity = mActivity
        
        # Create WebView
        webview = WebView(activity)
        webview.getSettings().setJavaScriptEnabled(True)
        webview.getSettings().setDomStorageEnabled(True)
        webview.setWebViewClient(WebViewClient())
        
        # Load the GNN template
        # Use file:/// URL for local files or http:// for remote
        file_path = 'file:///android_asset/gnn_template/index.html'
        webview.loadUrl(file_path)
        
        # Add to activity
        activity.addContentView(
            webview,
            LayoutParams(
                LayoutParams.MATCH_PARENT,
                LayoutParams.MATCH_PARENT
            )
        )
        
        self.webview = webview
    
    def load_articles(self, articles_json):
        """Load articles dynamically into the WebView."""
        js_code = f"""
        if (window.goodNewsApp) {{
            window.goodNewsApp.renderArticles({articles_json});
        }}
        """
        self.webview.evaluateJavascript(js_code, None)
```

### Step 3: Add GNN Template to Assets

In `buildozer.spec`, ensure the GNN template is included:

```ini
source.include_exts = py,png,jpg,kv,atlas,html,css,js

# Include the entire gnn_template directory
source.include_patterns = gnn_template/*
```

### Step 4: Add GNN Screen to Main App

In `main.py`, add the GNN screen:

```python
from features.gnn_screen import GNNScreen

class PostboiApp(MDApp):
    def build(self):
        # Create screen manager
        sm = ScreenManager()
        
        # Add GNN screen
        sm.add_widget(GNNScreen())
        
        return sm
    
    def navigate_to_gnn(self):
        """Navigate to Good News Network screen."""
        self.root.current = 'gnn'
```

### Step 5: Fetch and Display Articles

Create a service to fetch articles from WordPress:

```python
# features/gnn_service.py
import requests
import json


class GNNService:
    """Service to fetch Good News articles."""
    
    def __init__(self, wordpress_url):
        self.wordpress_url = wordpress_url
    
    def fetch_articles(self, limit=9):
        """Fetch articles from WordPress REST API."""
        try:
            url = f"{self.wordpress_url}/wp-json/wp/v2/posts"
            params = {
                '_embed': 'true',
                'per_page': limit,
                'orderby': 'date',
                'order': 'desc'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            posts = response.json()
            
            # Transform to GNN format
            articles = []
            for post in posts:
                article = {
                    'id': post['id'],
                    'title': self._strip_html(post['title']['rendered']),
                    'subtitle': self._strip_html(post['excerpt']['rendered'])[:150],
                    'imageUrl': self._get_featured_image(post),
                    'link': post['link']
                }
                articles.append(article)
            
            return articles
            
        except Exception as e:
            print(f"Error fetching articles: {str(e)}")
            return []
    
    def _strip_html(self, text):
        """Remove HTML tags from text."""
        import re
        return re.sub(r'<[^>]+>', '', text)
    
    def _get_featured_image(self, post):
        """Extract featured image URL from post."""
        try:
            return post['_embedded']['wp:featuredmedia'][0]['source_url']
        except (KeyError, IndexError):
            return 'https://via.placeholder.com/800x600?text=No+Image'


# Usage in main.py
class PostboiApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gnn_service = GNNService(config.WORDPRESS_CONFIG['site_url'])
    
    def show_gnn_articles(self):
        """Fetch and display GNN articles."""
        # Fetch articles
        articles = self.gnn_service.fetch_articles(limit=9)
        
        # Navigate to GNN screen
        self.root.current = 'gnn'
        
        # Load articles into WebView
        gnn_screen = self.root.get_screen('gnn')
        articles_json = json.dumps(articles)
        gnn_screen.load_articles(articles_json)
```

## Option 2: Native Kivy Implementation

If you prefer a native Kivy implementation without WebView:

### Create Kivy Widgets

```python
# features/gnn_native_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.image import AsyncImage
from kivy.metrics import dp


class ArticleCard(MDCard):
    """Card widget for displaying an article."""
    
    def __init__(self, article, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(250)
        self.elevation = 2
        self.radius = [dp(12)]
        
        # Add image
        image = AsyncImage(
            source=article['imageUrl'],
            allow_stretch=True,
            keep_ratio=True
        )
        
        # Add overlay with title and subtitle
        overlay = BoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(8)
        )
        
        title = MDLabel(
            text=article['title'],
            font_style='H6',
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1)
        )
        
        subtitle = MDLabel(
            text=article['subtitle'],
            font_style='Caption',
            theme_text_color='Custom',
            text_color=(1, 1, 1, 0.9)
        )
        
        overlay.add_widget(title)
        overlay.add_widget(subtitle)
        
        self.add_widget(image)
        self.add_widget(overlay)


class GNNNativeScreen(Screen):
    """Native Kivy implementation of GNN screen."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'gnn_native'
        
        # Create scroll view
        scroll = ScrollView()
        
        # Create grid layout
        self.grid = GridLayout(
            cols=1,  # Will be adjusted based on screen width
            spacing=dp(16),
            padding=dp(16),
            size_hint_y=None
        )
        self.grid.bind(minimum_height=self.grid.setter('height'))
        
        scroll.add_widget(self.grid)
        self.add_widget(scroll)
        
        # Adjust columns based on window width
        from kivy.core.window import Window
        Window.bind(on_resize=self.on_window_resize)
        self.on_window_resize(Window, Window.width, Window.height)
    
    def on_window_resize(self, window, width, height):
        """Adjust grid columns based on window width."""
        if width < dp(600):
            self.grid.cols = 1
        elif width < dp(900):
            self.grid.cols = 2
        else:
            self.grid.cols = 3
    
    def load_articles(self, articles):
        """Load articles into the grid."""
        self.grid.clear_widgets()
        
        for article in articles:
            card = ArticleCard(article)
            self.grid.add_widget(card)
```

## Option 3: Hybrid Approach

Use the web template for desktop/testing and native Kivy for mobile:

```python
import platform


class PostboiApp(MDApp):
    def build(self):
        sm = ScreenManager()
        
        # Choose implementation based on platform
        if platform.system() == 'Linux' and 'ANDROID_ROOT' in os.environ:
            # Android - use WebView
            sm.add_widget(GNNScreen())
        else:
            # Desktop/iOS - use native or web template
            sm.add_widget(GNNNativeScreen())
        
        return sm
```

## Testing

### Test with Local Server

1. Start the local server:
```bash
cd gnn_template
python -m http.server 8000
```

2. Update the WebView URL:
```python
webview.loadUrl('http://localhost:8000/index.html')
```

3. Run the Kivy app and navigate to GNN screen

### Test with Mock Data

```python
# Test data
test_articles = [
    {
        'id': 1,
        'title': 'Test Article 1',
        'subtitle': 'This is a test article',
        'imageUrl': 'https://via.placeholder.com/800x600',
        'link': '#'
    },
    # Add more test articles...
]

# Load into screen
gnn_screen.load_articles(json.dumps(test_articles))
```

## Production Deployment

### For Android

1. Include GNN template in assets:
```bash
# Copy to assets directory
cp -r gnn_template/ .buildozer/android/platform/build/dists/postboi/assets/
```

2. Build APK:
```bash
buildozer android debug
```

### For iOS

1. Include in Xcode project resources
2. Update file path to use bundle resources
3. Build with Xcode

## Troubleshooting

### WebView Not Displaying

- Check JavaScript is enabled
- Verify file paths are correct
- Check Android permissions in manifest
- Test with remote URL first

### Images Not Loading

- Check CORS headers if loading from remote server
- Verify image URLs are accessible
- Use placeholder images for testing

### Performance Issues

- Enable image lazy loading
- Limit number of articles per load
- Use pagination for large datasets
- Optimize image sizes before display

## Next Steps

1. Choose your integration method (WebView, Native, or Hybrid)
2. Implement the chosen method
3. Test on actual devices
4. Optimize performance based on testing
5. Deploy to production

For more details, see the main [README.md](README.md) in the gnn_template directory.
