/**
 * Good News Network - JavaScript
 * Handles dynamic article loading and interactive features
 */

// ==========================================================================
// Configuration
// ==========================================================================

const CONFIG = {
    // API endpoint for fetching articles (replace with your actual endpoint)
    apiEndpoint: '/api/articles',
    
    // Number of articles to load per page
    articlesPerPage: 9,
    
    // Enable/disable animations
    enableAnimations: true,
    
    // Lazy loading threshold (in pixels)
    lazyLoadThreshold: 100
};

// ==========================================================================
// Article Data Structure
// ==========================================================================

/**
 * Example article data structure for integration
 * Replace this with actual API data
 */
const sampleArticleData = [
    {
        id: 1,
        title: "Community Volunteers Plant 10,000 Trees",
        subtitle: "Local initiative brings neighborhoods together for environmental action",
        imageUrl: "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?w=800&q=80",
        link: "#article1",
        category: "Environment",
        date: "2024-03-15"
    },
    // Add more articles here...
];

// ==========================================================================
// Main Application Class
// ==========================================================================

class GoodNewsApp {
    constructor() {
        this.articlesGrid = document.getElementById('articlesGrid');
        this.articles = [];
        this.currentPage = 1;
        this.isLoading = false;
        
        this.init();
    }
    
    /**
     * Initialize the application
     */
    init() {
        console.log('Good News Network initialized');
        
        // Set up intersection observer for lazy loading images
        this.setupLazyLoading();
        
        // Set up infinite scroll (optional)
        // this.setupInfiniteScroll();
        
        // Add smooth scroll behavior
        this.setupSmoothScroll();
        
        // Add animation on scroll
        if (CONFIG.enableAnimations) {
            this.setupScrollAnimations();
        }
        
        // Listen for article clicks
        this.setupArticleClickHandlers();
    }
    
    /**
     * INTEGRATION METHOD: Load articles from API
     * Replace the fetch URL with your actual API endpoint
     */
    async loadArticles(page = 1) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoadingState();
        
        try {
            // REPLACE THIS WITH YOUR ACTUAL API CALL
            // Example:
            // const response = await fetch(`${CONFIG.apiEndpoint}?page=${page}&limit=${CONFIG.articlesPerPage}`);
            // const data = await response.json();
            // this.articles = data.articles;
            
            // For demo purposes, using sample data
            // Remove this and uncomment the above code for production
            await this.simulateAPIDelay(1000);
            this.articles = sampleArticleData;
            
            // Render articles
            this.renderArticles(this.articles);
            
        } catch (error) {
            console.error('Error loading articles:', error);
            this.showErrorState('Failed to load articles. Please try again.');
        } finally {
            this.isLoading = false;
            this.hideLoadingState();
        }
    }
    
    /**
     * INTEGRATION METHOD: Render articles dynamically
     * Call this method with your article data
     * 
     * @param {Array} articles - Array of article objects
     * 
     * Example usage:
     * const articles = await fetchArticlesFromAPI();
     * app.renderArticles(articles);
     */
    renderArticles(articles) {
        if (!articles || articles.length === 0) {
            this.showEmptyState();
            return;
        }
        
        // Clear existing content if needed
        // this.articlesGrid.innerHTML = '';
        
        articles.forEach(article => {
            const articleCard = this.createArticleCard(article);
            this.articlesGrid.appendChild(articleCard);
        });
    }
    
    /**
     * INTEGRATION METHOD: Create article card element
     * This method shows how to structure article data for rendering
     * 
     * @param {Object} article - Article data object
     * @param {string} article.imageUrl - URL to article image
     * @param {string} article.title - Article title
     * @param {string} article.subtitle - Article subtitle/teaser
     * @param {string} article.link - URL to full article
     * @returns {HTMLElement} Article card element
     */
    createArticleCard(article) {
        const card = document.createElement('article');
        card.className = 'article-card';
        card.setAttribute('data-article-id', article.id || '');
        
        card.innerHTML = `
            <a href="${this.escapeHtml(article.link)}" class="article-link">
                <div class="article-image-wrapper">
                    <img 
                        data-src="${this.escapeHtml(article.imageUrl)}"
                        alt="${this.escapeHtml(article.title)}" 
                        class="article-image lazy-image"
                        loading="lazy"
                    >
                    <div class="article-overlay">
                        <h2 class="article-title">${this.escapeHtml(article.title)}</h2>
                        <p class="article-subtitle">${this.escapeHtml(article.subtitle)}</p>
                    </div>
                </div>
            </a>
        `;
        
        return card;
    }
    
    /**
     * Set up lazy loading for images using Intersection Observer
     */
    setupLazyLoading() {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.getAttribute('data-src');
                    
                    if (src) {
                        img.src = src;
                        img.classList.remove('lazy-image');
                        observer.unobserve(img);
                    }
                }
            });
        }, {
            rootMargin: `${CONFIG.lazyLoadThreshold}px`
        });
        
        // Observe all lazy images
        document.querySelectorAll('.lazy-image').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    /**
     * Set up infinite scroll (optional feature)
     */
    setupInfiniteScroll() {
        const scrollObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.isLoading) {
                    this.currentPage++;
                    this.loadArticles(this.currentPage);
                }
            });
        }, {
            rootMargin: '200px'
        });
        
        // Create and observe scroll trigger element
        const scrollTrigger = document.createElement('div');
        scrollTrigger.id = 'scroll-trigger';
        document.querySelector('.main-content').appendChild(scrollTrigger);
        scrollObserver.observe(scrollTrigger);
    }
    
    /**
     * Set up smooth scrolling
     */
    setupSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (href !== '#' && href !== '#article') {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }
            });
        });
    }
    
    /**
     * Set up scroll animations for article cards
     */
    setupScrollAnimations() {
        const animationObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, index * 50);
                    animationObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });
        
        // Set initial state and observe cards
        document.querySelectorAll('.article-card').forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            animationObserver.observe(card);
        });
    }
    
    /**
     * Set up click handlers for articles
     */
    setupArticleClickHandlers() {
        document.addEventListener('click', (e) => {
            const articleLink = e.target.closest('.article-link');
            if (articleLink) {
                const articleCard = articleLink.closest('.article-card');
                const articleId = articleCard?.getAttribute('data-article-id');
                
                // Track article click (for analytics)
                if (articleId) {
                    this.trackArticleClick(articleId);
                }
            }
        });
    }
    
    /**
     * Track article clicks (integrate with your analytics)
     */
    trackArticleClick(articleId) {
        console.log(`Article clicked: ${articleId}`);
        
        // INTEGRATION NOTE: Add your analytics tracking here
        // Example: gtag('event', 'article_click', { article_id: articleId });
        // Example: analytics.track('Article Viewed', { articleId: articleId });
    }
    
    /**
     * Show loading state
     */
    showLoadingState() {
        const loadingEl = document.createElement('div');
        loadingEl.className = 'loading';
        loadingEl.id = 'loading-state';
        loadingEl.textContent = 'Loading articles';
        this.articlesGrid.appendChild(loadingEl);
    }
    
    /**
     * Hide loading state
     */
    hideLoadingState() {
        const loadingEl = document.getElementById('loading-state');
        if (loadingEl) {
            loadingEl.remove();
        }
    }
    
    /**
     * Show error state
     */
    showErrorState(message) {
        const errorEl = document.createElement('div');
        errorEl.className = 'error-state';
        errorEl.textContent = message;
        errorEl.style.cssText = 'text-align: center; padding: 2rem; color: #ef4444;';
        this.articlesGrid.appendChild(errorEl);
    }
    
    /**
     * Show empty state
     */
    showEmptyState() {
        const emptyEl = document.createElement('div');
        emptyEl.className = 'empty-state';
        emptyEl.textContent = 'No articles found';
        emptyEl.style.cssText = 'text-align: center; padding: 2rem; color: #6b7280;';
        this.articlesGrid.appendChild(emptyEl);
    }
    
    /**
     * Simulate API delay (for demo purposes only - remove in production)
     */
    simulateAPIDelay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    /**
     * Escape HTML to prevent XSS attacks
     */
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
}

// ==========================================================================
// Initialize Application
// ==========================================================================

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the app
    window.goodNewsApp = new GoodNewsApp();
    
    // INTEGRATION NOTE: Uncomment the line below to load articles dynamically
    // window.goodNewsApp.loadArticles();
});

// ==========================================================================
// Export for module usage (if needed)
// ==========================================================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = GoodNewsApp;
}
