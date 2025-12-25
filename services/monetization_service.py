"""
Monetization Service for Postboi

Handles ads, in-app purchases, and subscription management.
Adapted from the Create app's monetization module for Python/Kivy.

Features:
- Ad display (banner, interstitial, rewarded)
- In-app purchases
- Subscription tiers (Free, Premium, Premium Plus)
- Feature gating based on subscription tier
- Local receipt validation

Note: Full implementation requires platform-specific SDKs:
- Android: Google Play Billing Library
- iOS: StoreKit
- Ads: AdMob SDK via kivy-ads or kivmob

This module provides the interface and mock implementations for testing.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum

# Try to import KivMob for ads (install: pip install kivmob)
try:
    from kivmob import KivMob
    HAS_KIVMOB = True
except ImportError:
    HAS_KIVMOB = False


class SubscriptionTier(Enum):
    """Subscription tier levels"""
    FREE = "free"
    PREMIUM = "premium"
    PREMIUM_PLUS = "premium_plus"


class ProductType(Enum):
    """Product types"""
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"


class PurchaseResult(Enum):
    """Purchase result codes"""
    SUCCESS = "success"
    CANCELLED = "cancelled"
    ERROR = "error"
    ALREADY_OWNED = "already_owned"
    NOT_AVAILABLE = "not_available"
    PENDING = "pending"


@dataclass
class Product:
    """Product definition"""
    id: str
    name: str
    description: str
    price: float
    currency: str = "USD"
    product_type: ProductType = ProductType.ONE_TIME
    period: Optional[str] = None  # monthly, yearly for subscriptions
    features: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['product_type'] = self.product_type.value
        return data


@dataclass
class Purchase:
    """Purchase record"""
    product_id: str
    purchase_token: str
    purchased_at: str
    expires_at: Optional[str] = None
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Purchase':
        return cls(**data)


@dataclass
class MonetizationStatus:
    """Current monetization status for user"""
    is_premium: bool = False
    has_active_subscription: bool = False
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    ads_enabled: bool = True
    purchased_products: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['subscription_tier'] = self.subscription_tier.value
        return data


# =============================================================================
# CONFIGURATION
# =============================================================================

class MonetizationConfig:
    """Monetization configuration - adjust these values for your app"""
    
    # Feature Flags
    ENABLED = False  # Master switch - set True when ready
    ADS_ENABLED = False
    PURCHASES_ENABLED = False
    SUBSCRIPTIONS_ENABLED = False
    DEBUG_MODE = True
    
    # AdMob Configuration (replace with your actual ad unit IDs)
    ADMOB_APP_ID = "ca-app-pub-XXXXXXXXXXXXXXXX~XXXXXXXXXX"
    BANNER_AD_UNIT = "ca-app-pub-3940256099942544/6300978111"  # Test ID
    INTERSTITIAL_AD_UNIT = "ca-app-pub-3940256099942544/1033173712"  # Test ID
    REWARDED_AD_UNIT = "ca-app-pub-3940256099942544/5224354917"  # Test ID
    
    # Show interstitial every N major actions
    INTERSTITIAL_FREQUENCY = 5
    
    # Product Definitions
    PRODUCTS = [
        Product(
            id="postboi_premium",
            name="Postboi Premium",
            description="Remove ads and unlock all features",
            price=4.99,
            currency="USD",
            product_type=ProductType.ONE_TIME,
            features=[
                "Remove all ads permanently",
                "Unlimited scheduled posts",
                "Advanced analytics",
                "Priority support",
            ]
        ),
        Product(
            id="postboi_premium_monthly",
            name="Postboi Premium Monthly",
            description="Premium features with monthly billing",
            price=1.99,
            currency="USD",
            product_type=ProductType.SUBSCRIPTION,
            period="monthly",
            features=[
                "Remove all ads",
                "Unlimited scheduled posts",
                "Advanced analytics",
                "Cancel anytime",
            ]
        ),
        Product(
            id="postboi_premium_yearly",
            name="Postboi Premium Yearly",
            description="Premium features with yearly billing (save 33%)",
            price=15.99,
            currency="USD",
            product_type=ProductType.SUBSCRIPTION,
            period="yearly",
            features=[
                "Remove all ads",
                "Unlimited scheduled posts",
                "Advanced analytics",
                "Cancel anytime",
                "Save 33% vs monthly",
            ]
        ),
    ]
    
    # Tier Features
    TIER_FEATURES = {
        SubscriptionTier.FREE: [
            "Post to WordPress, Facebook, Instagram",
            "Basic scheduling (5 posts/day)",
            "Local draft storage",
            "Ads displayed",
        ],
        SubscriptionTier.PREMIUM: [
            "Everything in Free",
            "No ads",
            "Unlimited scheduled posts",
            "Post analytics",
            "Bulk upload",
            "Priority support",
        ],
        SubscriptionTier.PREMIUM_PLUS: [
            "Everything in Premium",
            "Multi-account support",
            "Team collaboration",
            "API access",
            "Custom integrations",
            "White-label options",
        ],
    }


# =============================================================================
# AD SERVICE
# =============================================================================

class AdService:
    """
    Ad service for displaying banner, interstitial, and rewarded ads.
    Uses KivMob when available, otherwise provides mock implementations.
    """
    
    def __init__(self):
        self._kivmob = None
        self._action_count = 0
        self._initialized = False
        self._reward_callback: Optional[Callable] = None
        
        if HAS_KIVMOB and MonetizationConfig.ADS_ENABLED:
            self._initialize_admob()
    
    def _initialize_admob(self) -> bool:
        """Initialize AdMob via KivMob"""
        if not MonetizationConfig.ENABLED or not MonetizationConfig.ADS_ENABLED:
            if MonetizationConfig.DEBUG_MODE:
                print("[Ads] Ads disabled by feature flag")
            return False
        
        if not HAS_KIVMOB:
            if MonetizationConfig.DEBUG_MODE:
                print("[Ads] KivMob not available - using mock ads")
            return False
        
        try:
            self._kivmob = KivMob(MonetizationConfig.ADMOB_APP_ID)
            self._kivmob.new_banner(MonetizationConfig.BANNER_AD_UNIT)
            self._kivmob.new_interstitial(MonetizationConfig.INTERSTITIAL_AD_UNIT)
            self._kivmob.request_banner()
            self._kivmob.request_interstitial()
            self._initialized = True
            
            if MonetizationConfig.DEBUG_MODE:
                print("[Ads] AdMob initialized successfully")
            return True
        except Exception as e:
            print(f"[Ads] Failed to initialize AdMob: {e}")
            return False
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized
    
    def show_banner(self) -> bool:
        """Show banner ad at bottom of screen"""
        if not MonetizationConfig.ADS_ENABLED:
            return False
        
        if self._kivmob:
            try:
                self._kivmob.show_banner()
                return True
            except Exception as e:
                print(f"[Ads] Banner error: {e}")
                return False
        else:
            if MonetizationConfig.DEBUG_MODE:
                print("[Ads] Mock banner displayed")
            return True
    
    def hide_banner(self) -> None:
        """Hide banner ad"""
        if self._kivmob:
            try:
                self._kivmob.hide_banner()
            except Exception:
                pass
    
    def show_interstitial(self) -> bool:
        """Show full-screen interstitial ad"""
        if not MonetizationConfig.ADS_ENABLED:
            return False
        
        if self._kivmob:
            try:
                if self._kivmob.is_interstitial_loaded():
                    self._kivmob.show_interstitial()
                    self._kivmob.request_interstitial()  # Load next one
                    return True
                return False
            except Exception as e:
                print(f"[Ads] Interstitial error: {e}")
                return False
        else:
            if MonetizationConfig.DEBUG_MODE:
                print("[Ads] Mock interstitial displayed")
            return True
    
    def show_interstitial_if_due(self) -> bool:
        """
        Show interstitial ad if enough actions have occurred.
        Call this after major user actions.
        """
        self._action_count += 1
        
        if self._action_count >= MonetizationConfig.INTERSTITIAL_FREQUENCY:
            self._action_count = 0
            return self.show_interstitial()
        return False
    
    def show_rewarded_ad(self, on_reward: Callable[[], None]) -> bool:
        """
        Show rewarded video ad.
        
        Args:
            on_reward: Callback to execute when user earns reward
        """
        if not MonetizationConfig.ADS_ENABLED:
            if MonetizationConfig.DEBUG_MODE:
                print("[Ads] Rewarded ads disabled, granting reward anyway in debug")
                on_reward()
            return False
        
        self._reward_callback = on_reward
        
        if self._kivmob:
            # Note: KivMob rewarded ad implementation varies
            # This is a simplified version
            if MonetizationConfig.DEBUG_MODE:
                print("[Ads] Rewarded ad shown")
            # In real implementation, callback is triggered by ad SDK
            return True
        else:
            if MonetizationConfig.DEBUG_MODE:
                print("[Ads] Mock rewarded ad - granting reward")
            on_reward()
            return True


# =============================================================================
# PURCHASE SERVICE
# =============================================================================

class PurchaseService:
    """
    Purchase service for handling in-app purchases and subscriptions.
    Provides local storage and mock implementation for testing.
    
    For production, integrate with:
    - Android: Google Play Billing (via android.billing)
    - iOS: StoreKit (via pyobjus)
    """
    
    def __init__(self, app_name: str = "Postboi", user_id: Optional[str] = None):
        self.app_name = app_name
        self._user_id = user_id
        self._data_dir = self._get_data_directory()
        self._purchases_file = self._data_dir / "purchases.json"
        
        # Ensure data directory exists
        self._data_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache
        self._status: Optional[MonetizationStatus] = None
    
    def _get_data_directory(self) -> Path:
        """Get platform-specific app data directory"""
        import platform
        system = platform.system()
        
        if system == "Darwin":  # macOS
            base = Path.home() / "Library" / "Application Support"
        elif system == "Windows":
            base = Path(os.environ.get("APPDATA", Path.home()))
        else:  # Linux and others
            base = Path.home() / ".local" / "share"
        
        return base / self.app_name / "purchases"
    
    def _load_purchases(self) -> Dict[str, Dict]:
        """Load purchases from storage"""
        if self._purchases_file.exists():
            try:
                with open(self._purchases_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_purchases(self, purchases: Dict[str, Dict]) -> None:
        """Save purchases to storage"""
        with open(self._purchases_file, 'w') as f:
            json.dump(purchases, f, indent=2)
    
    def set_user_id(self, user_id: str) -> None:
        """Set user ID for purchase tracking"""
        self._user_id = user_id
        self._status = None  # Clear cache
    
    def get_products(self) -> List[Product]:
        """Get available products"""
        return MonetizationConfig.PRODUCTS.copy()
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        for product in MonetizationConfig.PRODUCTS:
            if product.id == product_id:
                return product
        return None
    
    def get_monetization_status(self) -> MonetizationStatus:
        """
        Get current monetization status.
        Checks purchases and determines tier.
        """
        if self._status:
            return self._status
        
        if not MonetizationConfig.ENABLED or not MonetizationConfig.PURCHASES_ENABLED:
            return MonetizationStatus()
        
        purchases = self._load_purchases()
        user_purchases = purchases.get(self._user_id or "anonymous", {})
        
        # Determine status from purchases
        is_premium = False
        has_subscription = False
        tier = SubscriptionTier.FREE
        purchased_products = []
        
        for product_id, purchase_data in user_purchases.items():
            purchase = Purchase.from_dict(purchase_data)
            
            if not purchase.is_active:
                continue
            
            # Check subscription expiry
            if purchase.expires_at:
                if datetime.fromisoformat(purchase.expires_at) < datetime.now():
                    continue
                has_subscription = True
            
            purchased_products.append(product_id)
            
            # Determine tier
            if "premium_plus" in product_id:
                tier = SubscriptionTier.PREMIUM_PLUS
                is_premium = True
            elif "premium" in product_id:
                if tier != SubscriptionTier.PREMIUM_PLUS:
                    tier = SubscriptionTier.PREMIUM
                is_premium = True
        
        self._status = MonetizationStatus(
            is_premium=is_premium,
            has_active_subscription=has_subscription,
            subscription_tier=tier,
            ads_enabled=not is_premium and MonetizationConfig.ADS_ENABLED,
            purchased_products=purchased_products
        )
        
        return self._status
    
    def purchase(self, product_id: str) -> PurchaseResult:
        """
        Initiate purchase for a product.
        
        In production, this would:
        - Android: Launch Google Play billing flow
        - iOS: Create SKPayment
        
        For testing, this creates a mock purchase.
        """
        if not MonetizationConfig.ENABLED or not MonetizationConfig.PURCHASES_ENABLED:
            if MonetizationConfig.DEBUG_MODE:
                print(f"[Purchases] Purchases disabled, creating mock purchase for {product_id}")
                return self._create_mock_purchase(product_id)
            return PurchaseResult.NOT_AVAILABLE
        
        product = self.get_product(product_id)
        if not product:
            return PurchaseResult.NOT_AVAILABLE
        
        # Check if already owned (for one-time purchases)
        if product.product_type == ProductType.ONE_TIME:
            status = self.get_monetization_status()
            if product_id in status.purchased_products:
                return PurchaseResult.ALREADY_OWNED
        
        # In production, launch platform-specific billing
        # For now, create mock purchase
        return self._create_mock_purchase(product_id)
    
    def _create_mock_purchase(self, product_id: str) -> PurchaseResult:
        """Create mock purchase for testing"""
        product = self.get_product(product_id)
        if not product:
            return PurchaseResult.NOT_AVAILABLE
        
        now = datetime.now()
        expires_at = None
        
        if product.product_type == ProductType.SUBSCRIPTION:
            if product.period == "monthly":
                expires_at = (now + timedelta(days=30)).isoformat()
            elif product.period == "yearly":
                expires_at = (now + timedelta(days=365)).isoformat()
        
        purchase = Purchase(
            product_id=product_id,
            purchase_token=f"mock_{product_id}_{now.timestamp()}",
            purchased_at=now.isoformat(),
            expires_at=expires_at,
            is_active=True
        )
        
        # Save purchase
        purchases = self._load_purchases()
        user_key = self._user_id or "anonymous"
        
        if user_key not in purchases:
            purchases[user_key] = {}
        
        purchases[user_key][product_id] = purchase.to_dict()
        self._save_purchases(purchases)
        
        # Clear cached status
        self._status = None
        
        if MonetizationConfig.DEBUG_MODE:
            print(f"[Purchases] Mock purchase created: {product_id}")
        
        return PurchaseResult.SUCCESS
    
    def restore_purchases(self) -> List[str]:
        """
        Restore previous purchases.
        
        In production, this would query the app store.
        For testing, returns locally stored purchases.
        """
        if not MonetizationConfig.ENABLED:
            return []
        
        purchases = self._load_purchases()
        user_purchases = purchases.get(self._user_id or "anonymous", {})
        
        restored = []
        for product_id, purchase_data in user_purchases.items():
            purchase = Purchase.from_dict(purchase_data)
            if purchase.is_active:
                restored.append(product_id)
        
        if MonetizationConfig.DEBUG_MODE:
            print(f"[Purchases] Restored {len(restored)} purchases")
        
        return restored
    
    def has_feature(self, feature: str) -> bool:
        """
        Check if user has access to a specific feature.
        
        Args:
            feature: Feature name to check
        
        Returns:
            True if user's tier includes the feature
        """
        status = self.get_monetization_status()
        tier_features = MonetizationConfig.TIER_FEATURES.get(status.subscription_tier, [])
        
        # Check if feature is in tier's features
        for tier_feature in tier_features:
            if feature.lower() in tier_feature.lower():
                return True
        return False
    
    def get_tier_features(self, tier: Optional[SubscriptionTier] = None) -> List[str]:
        """Get features for a tier (defaults to current tier)"""
        if tier is None:
            status = self.get_monetization_status()
            tier = status.subscription_tier
        return MonetizationConfig.TIER_FEATURES.get(tier, [])


# =============================================================================
# COMBINED MONETIZATION SERVICE
# =============================================================================

class MonetizationService:
    """
    Combined monetization service providing ads, purchases, and subscriptions.
    
    Usage:
        monetization = MonetizationService()
        monetization.set_user_id(user_id)
        
        # Check premium status
        if monetization.is_premium:
            # Show premium features
        else:
            monetization.show_banner_ad()
        
        # Purchase premium
        result = monetization.purchase("postboi_premium")
    """
    
    def __init__(self, app_name: str = "Postboi"):
        self.app_name = app_name
        self._ads = AdService()
        self._purchases = PurchaseService(app_name)
    
    def set_user_id(self, user_id: str) -> None:
        """Set user ID for purchase tracking"""
        self._purchases.set_user_id(user_id)
    
    @property
    def is_premium(self) -> bool:
        """Check if user has premium status"""
        return self._purchases.get_monetization_status().is_premium
    
    @property
    def subscription_tier(self) -> SubscriptionTier:
        """Get current subscription tier"""
        return self._purchases.get_monetization_status().subscription_tier
    
    @property
    def ads_enabled(self) -> bool:
        """Check if ads should be shown"""
        return self._purchases.get_monetization_status().ads_enabled
    
    def get_status(self) -> MonetizationStatus:
        """Get full monetization status"""
        return self._purchases.get_monetization_status()
    
    def get_products(self) -> List[Product]:
        """Get available products"""
        return self._purchases.get_products()
    
    def purchase(self, product_id: str) -> PurchaseResult:
        """Purchase a product"""
        return self._purchases.purchase(product_id)
    
    def restore_purchases(self) -> List[str]:
        """Restore previous purchases"""
        return self._purchases.restore_purchases()
    
    def has_feature(self, feature: str) -> bool:
        """Check if user has access to a feature"""
        return self._purchases.has_feature(feature)
    
    def show_banner_ad(self) -> bool:
        """Show banner ad (if ads enabled and not premium)"""
        if self.is_premium:
            return False
        return self._ads.show_banner()
    
    def hide_banner_ad(self) -> None:
        """Hide banner ad"""
        self._ads.hide_banner()
    
    def show_interstitial_ad(self) -> bool:
        """Show interstitial ad (if ads enabled and not premium)"""
        if self.is_premium:
            return False
        return self._ads.show_interstitial()
    
    def track_action(self) -> None:
        """Track user action and show interstitial if due"""
        if not self.is_premium:
            self._ads.show_interstitial_if_due()
    
    def show_rewarded_ad(self, on_reward: Callable[[], None]) -> bool:
        """Show rewarded ad"""
        return self._ads.show_rewarded_ad(on_reward)
