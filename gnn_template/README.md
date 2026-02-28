# Good News Network (GNN) Front-End Template

## Overview

This is a modern, responsive front-end template for the Good News Network app. It displays articles in an engaging grid-based layout with images, titles, and subtitles. The template is designed to be visually appealing, responsive, and ready for dynamic content integration.

## Features

### ✨ Visual Design
- **Grid-based layout** - Responsive grid that adapts to screen sizes
- **Image-centric cards** - Each article features a prominent image
- **Overlay captions** - Title and subtitle displayed over the image with gradient overlay
- **Modern aesthetics** - Clean, professional design with Material Design principles

### 🎨 Interactive Effects
- **Hover animations** - Cards lift and images zoom on hover
- **Smooth transitions** - All interactions have smooth CSS transitions
- **Drop shadows** - Depth effects with layered shadows
- **Focus states** - Keyboard navigation support with clear focus indicators

### 📱 Responsive Design
- **Desktop** (>1024px) - Multi-column grid with 3+ articles per row
- **Tablet** (768px-1024px) - 2-3 columns, adjusted spacing
- **Mobile** (480px-768px) - 1-2 columns, optimized for touch
- **Small mobile** (<480px) - Single column, full-width cards

### 🚀 Performance
- **Lazy loading** - Images load as they enter viewport
- **Optimized animations** - GPU-accelerated transforms
- **Reduced motion support** - Respects user preferences
- **Efficient rendering** - Minimal reflows and repaints

### ♿ Accessibility
- **Semantic HTML** - Proper article, heading, and link structure
- **Alt text** - Image descriptions for screen readers
- **Keyboard navigation** - Full keyboard support with focus indicators
- **High contrast mode** - Support for high contrast preferences
- **ARIA labels** - Where appropriate (can be extended)

## File Structure

```
gnn_template/
├── index.html          # Main HTML template
├── styles.css          # Stylesheet with responsive design
├── script.js           # JavaScript for dynamic functionality
└── README.md           # This documentation file
```

## Quick Start

### 1. View the Template

Simply open `index.html` in a web browser:

```bash
# Using Python's built-in server
cd gnn_template
python -m http.server 8000

# Using Node.js http-server
npx http-server gnn_template

# Or just open the file directly
open index.html  # macOS
start index.html # Windows
xdg-open index.html # Linux
```

Then navigate to `http://localhost:8000` in your browser.

### 2. Integration with Kivy App (WebView)

If you want to display this template inside the Postboi Kivy app:

```python
# Add to main.py
from kivy.uix.webview import WebView  # Requires webview library

class GNNScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        webview = WebView()
        webview.url = 'file:///path/to/gnn_template/index.html'
        self.add_widget(webview)
```

Note: You may need to install a WebView component for Kivy.

### 3. Integration with Backend API

To connect the template to a live data source, modify `script.js`:

```javascript
// In script.js, update the loadArticles method:

async loadArticles(page = 1) {
    this.isLoading = true;
    this.showLoadingState();
    
    try {
        // Replace with your actual API endpoint
        const response = await fetch(`/api/articles?page=${page}&limit=9`);
        const data = await response.json();
        this.articles = data.articles;
        
        this.renderArticles(this.articles);
        
    } catch (error) {
        console.error('Error loading articles:', error);
        this.showErrorState('Failed to load articles. Please try again.');
    } finally {
        this.isLoading = false;
        this.hideLoadingState();
    }
}

// Then call it when the page loads:
// In the DOMContentLoaded event listener:
window.goodNewsApp.loadArticles();
```

## Integration Guide

### Article Data Structure

Each article should follow this structure:

```javascript
{
    id: 1,                          // Unique identifier
    title: "Article Title",         // Main headline (required)
    subtitle: "Brief description",  // Short teaser (required)
    imageUrl: "https://...",        // Image URL (required)
    link: "/article/1",             // Link to full article (required)
    category: "Environment",        // Optional: Article category
    date: "2024-03-15"             // Optional: Publication date
}
```

### Method 1: Static Articles (HTML)

Replace the placeholder articles in `index.html` with your own data:

```html
<article class="article-card">
    <a href="YOUR_ARTICLE_URL" class="article-link">
        <div class="article-image-wrapper">
            <img 
                src="YOUR_IMAGE_URL" 
                alt="YOUR_IMAGE_DESCRIPTION" 
                class="article-image"
                loading="lazy"
            >
            <div class="article-overlay">
                <h2 class="article-title">YOUR ARTICLE TITLE</h2>
                <p class="article-subtitle">YOUR ARTICLE SUBTITLE</p>
            </div>
        </div>
    </a>
</article>
```

### Method 2: Dynamic Articles (JavaScript)

Use the provided JavaScript methods to load articles dynamically:

```javascript
// Example: Fetch articles from your API
async function fetchArticles() {
    const response = await fetch('https://your-api.com/articles');
    const data = await response.json();
    
    // Render articles
    window.goodNewsApp.renderArticles(data.articles);
}

// Call when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.goodNewsApp = new GoodNewsApp();
    fetchArticles();
});
```

### Method 3: Server-Side Rendering

Generate the HTML on the server:

**Python/Flask Example:**
```python
from flask import render_template

@app.route('/')
def index():
    articles = get_articles_from_database()
    return render_template('gnn_template/index.html', articles=articles)
```

**Template (using Jinja2):**
```html
{% for article in articles %}
<article class="article-card">
    <a href="{{ article.link }}" class="article-link">
        <div class="article-image-wrapper">
            <img 
                src="{{ article.imageUrl }}" 
                alt="{{ article.title }}" 
                class="article-image"
                loading="lazy"
            >
            <div class="article-overlay">
                <h2 class="article-title">{{ article.title }}</h2>
                <p class="article-subtitle">{{ article.subtitle }}</p>
            </div>
        </div>
    </a>
</article>
{% endfor %}
```

### Method 4: WordPress Integration

If you're using WordPress, you can fetch articles via the REST API:

```javascript
async function loadWordPressArticles() {
    const response = await fetch('https://your-site.wordpress.com/wp-json/wp/v2/posts?_embed&per_page=9');
    const posts = await response.json();
    
    const articles = posts.map(post => ({
        id: post.id,
        title: post.title.rendered,
        subtitle: post.excerpt.rendered.replace(/<[^>]*>/g, '').substring(0, 150),
        imageUrl: post._embedded?.['wp:featuredmedia']?.[0]?.source_url || 'default-image.jpg',
        link: post.link
    }));
    
    window.goodNewsApp.renderArticles(articles);
}
```

## Customization

### Colors and Branding

Edit CSS variables in `styles.css`:

```css
:root {
    /* Change primary color */
    --primary-color: #2563eb;        /* Default: Blue */
    --secondary-color: #1e40af;      /* Default: Dark Blue */
    --accent-color: #f59e0b;         /* Default: Orange */
    
    /* Change text colors */
    --text-dark: #1f2937;
    --text-light: #6b7280;
    
    /* Change spacing */
    --spacing-lg: 2rem;
    --border-radius: 12px;
}
```

### Grid Layout

Adjust the grid columns in `styles.css`:

```css
.articles-grid {
    /* Change minimum card width */
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    
    /* Or use fixed columns */
    grid-template-columns: repeat(3, 1fr); /* Always 3 columns */
    
    /* Adjust gap between cards */
    gap: var(--spacing-lg);
}
```

### Image Aspect Ratio

Change the aspect ratio of article images:

```css
.article-image-wrapper {
    aspect-ratio: 16 / 10;  /* Default: 16:10 */
    /* Other options:
       aspect-ratio: 16 / 9;   - Widescreen
       aspect-ratio: 4 / 3;    - Traditional
       aspect-ratio: 1 / 1;    - Square
    */
}
```

### Typography

Update font settings:

```css
:root {
    --font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-size-xl: 1.5rem;
}

/* Or import custom fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

body {
    font-family: 'Inter', sans-serif;
}
```

## Advanced Features

### Infinite Scroll

Enable infinite scroll to load more articles as users scroll:

```javascript
// In script.js, uncomment in init():
this.setupInfiniteScroll();
```

### Animation on Scroll

Enable fade-in animations as cards enter viewport:

```javascript
// Already enabled by default in CONFIG
const CONFIG = {
    enableAnimations: true  // Set to false to disable
};
```

### Search and Filtering

Add search/filter functionality:

```javascript
// Add to GoodNewsApp class
filterArticles(category) {
    const filtered = this.articles.filter(a => a.category === category);
    this.articlesGrid.innerHTML = '';
    this.renderArticles(filtered);
}

// Add search functionality
searchArticles(query) {
    const results = this.articles.filter(a => 
        a.title.toLowerCase().includes(query.toLowerCase()) ||
        a.subtitle.toLowerCase().includes(query.toLowerCase())
    );
    this.articlesGrid.innerHTML = '';
    this.renderArticles(results);
}
```

### Analytics Integration

Track article views and clicks:

```javascript
// In script.js, update trackArticleClick method:
trackArticleClick(articleId) {
    // Google Analytics 4
    gtag('event', 'article_click', {
        article_id: articleId
    });
    
    // Or Segment
    analytics.track('Article Clicked', {
        articleId: articleId
    });
}
```

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile Safari (iOS 14+)
- ✅ Chrome Mobile (Android 9+)

### Polyfills for Older Browsers

If you need to support older browsers, add these polyfills:

```html
<!-- Add to <head> in index.html -->
<script src="https://polyfill.io/v3/polyfill.min.js?features=IntersectionObserver,Promise,fetch"></script>
```

## Performance Optimization

### Image Optimization

1. **Use appropriate image formats:**
   - WebP for modern browsers
   - JPEG fallback for compatibility
   - SVG for icons/logos

2. **Optimize image sizes:**
   - Desktop: 800-1200px wide
   - Mobile: 400-600px wide
   - Compression: 80-85% quality

3. **Use responsive images:**
```html
<img 
    srcset="
        image-400.jpg 400w,
        image-800.jpg 800w,
        image-1200.jpg 1200w
    "
    sizes="(max-width: 768px) 100vw, 50vw"
    src="image-800.jpg"
    alt="Description"
>
```

### CDN Integration

Serve images from a CDN for better performance:

```javascript
const CDN_BASE = 'https://cdn.yoursite.com/images/';

createArticleCard(article) {
    const imageUrl = article.imageUrl.startsWith('http') 
        ? article.imageUrl 
        : CDN_BASE + article.imageUrl;
    // ...
}
```

## Security Considerations

### XSS Protection

The template includes XSS protection via the `escapeHtml()` method. Always use it when rendering user-generated content:

```javascript
// Good - Escaped
card.innerHTML = `<h2>${this.escapeHtml(article.title)}</h2>`;

// Bad - Vulnerable to XSS
card.innerHTML = `<h2>${article.title}</h2>`;
```

### Content Security Policy

Add CSP headers to your server:

```html
<!-- Add to <head> -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; img-src 'self' https:; script-src 'self' 'unsafe-inline'">
```

## Testing

### Manual Testing Checklist

- [ ] View on desktop (>1024px)
- [ ] View on tablet (768-1024px)
- [ ] View on mobile (<768px)
- [ ] Test hover effects (desktop)
- [ ] Test touch interactions (mobile)
- [ ] Test keyboard navigation (Tab, Enter)
- [ ] Test with screen reader
- [ ] Test with slow network (throttling)
- [ ] Test with JavaScript disabled
- [ ] Verify images load correctly
- [ ] Check responsive breakpoints

### Automated Testing

Example using Playwright:

```javascript
const { test, expect } = require('@playwright/test');

test('GNN template loads correctly', async ({ page }) => {
    await page.goto('http://localhost:8000');
    
    // Check title
    await expect(page.locator('.logo')).toHaveText('Good News Network');
    
    // Check articles are present
    const articles = page.locator('.article-card');
    await expect(articles).toHaveCount(9);
    
    // Test hover effect
    await articles.first().hover();
    // Add assertions for hover state
});
```

## Troubleshooting

### Images Not Loading

**Problem:** Images show broken icon
**Solution:** 
- Check image URLs are correct
- Verify CORS headers if loading from different domain
- Check network tab in browser DevTools

### Layout Issues on Mobile

**Problem:** Cards overlap or don't resize
**Solution:**
- Check viewport meta tag is present
- Clear browser cache
- Test in different mobile browsers

### Performance Issues

**Problem:** Page loads slowly
**Solution:**
- Enable lazy loading (already implemented)
- Optimize image sizes
- Use CDN for assets
- Enable gzip compression on server

### JavaScript Errors

**Problem:** Console shows errors
**Solution:**
- Check browser console for specific errors
- Verify all files are loaded correctly
- Check for typos in API endpoints

## Next Steps

1. **Replace placeholder data** - Update `index.html` with your actual articles
2. **Connect to API** - Integrate with your backend (see Integration Guide)
3. **Customize styling** - Adjust colors, fonts, and spacing to match your brand
4. **Add features** - Implement search, filtering, pagination as needed
5. **Test thoroughly** - Test on various devices and browsers
6. **Deploy** - Host on your web server or integrate with Kivy app

## Support and Resources

- **Postboi Repository:** https://github.com/mindfu23/Postboi
- **CSS Grid Guide:** https://css-tricks.com/snippets/css/complete-guide-grid/
- **Responsive Design:** https://web.dev/responsive-web-design-basics/
- **Web Accessibility:** https://www.w3.org/WAI/fundamentals/

## License

This template is part of the Postboi project and is licensed under the MIT License. See the main project LICENSE file for details.

---

**Created for:** Postboi - Good News Network Feature
**Version:** 1.0.0
**Last Updated:** December 2024
