"""
Authentication Service for Postboi

Handles user signup, login, logout, and session management.
Adapted from the Create app's auth module for Python/Kivy.

Features:
- Local user registration and authentication
- Secure password hashing with bcrypt
- Persistent session management
- User profile management
- Integration with social media credentials
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Try to import bcrypt, fall back to hashlib if not available
try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False
    print("[Auth] bcrypt not available, using SHA-256 (less secure)")


class AuthResult(Enum):
    """Authentication result codes"""
    SUCCESS = "success"
    INVALID_CREDENTIALS = "invalid_credentials"
    USER_EXISTS = "user_exists"
    USER_NOT_FOUND = "user_not_found"
    WEAK_PASSWORD = "weak_password"
    INVALID_EMAIL = "invalid_email"
    SESSION_EXPIRED = "session_expired"
    NOT_AUTHENTICATED = "not_authenticated"
    ERROR = "error"


@dataclass
class User:
    """User model matching Create app structure"""
    id: str
    email: str
    username: str
    display_name: str
    created_at: str
    updated_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(**data)


@dataclass
class Session:
    """Session model for persistent login"""
    session_id: str
    user_id: str
    created_at: str
    expires_at: str
    
    def is_expired(self) -> bool:
        return datetime.fromisoformat(self.expires_at) < datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        return cls(**data)


class AuthService:
    """
    Authentication service providing signup, login, logout, and session management.
    
    Usage:
        auth = AuthService()
        
        # Sign up new user
        result, user = auth.signup("user@example.com", "password123", "John Doe")
        
        # Login
        result, user = auth.login("user@example.com", "password123")
        
        # Check if authenticated
        if auth.is_authenticated:
            print(f"Logged in as {auth.current_user.display_name}")
        
        # Logout
        auth.logout()
    """
    
    MIN_PASSWORD_LENGTH = 6
    SESSION_DURATION_DAYS = 30
    
    def __init__(self, app_name: str = "Postboi"):
        """Initialize auth service with platform-specific storage"""
        self.app_name = app_name
        self._data_dir = self._get_data_directory()
        self._users_file = self._data_dir / "users.json"
        self._sessions_file = self._data_dir / "sessions.json"
        
        # Current session state
        self._current_user: Optional[User] = None
        self._current_session: Optional[Session] = None
        
        # Ensure data directory exists
        self._data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load any existing session
        self._restore_session()
    
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
        
        return base / self.app_name / "auth"
    
    def _load_users(self) -> Dict[str, Dict]:
        """Load users from storage"""
        if self._users_file.exists():
            try:
                with open(self._users_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_users(self, users: Dict[str, Dict]) -> None:
        """Save users to storage"""
        with open(self._users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def _load_sessions(self) -> Dict[str, Dict]:
        """Load sessions from storage"""
        if self._sessions_file.exists():
            try:
                with open(self._sessions_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_sessions(self, sessions: Dict[str, Dict]) -> None:
        """Save sessions to storage"""
        with open(self._sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt or SHA-256 fallback"""
        if HAS_BCRYPT:
            return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        else:
            # Fallback: SHA-256 with salt (less secure than bcrypt)
            salt = secrets.token_hex(16)
            hash_val = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
            return f"{salt}${hash_val}"
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        if HAS_BCRYPT:
            try:
                return bcrypt.checkpw(password.encode(), hashed.encode())
            except (ValueError, TypeError):
                return False
        else:
            # Fallback verification
            try:
                salt, hash_val = hashed.split('$')
                check_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
                return check_hash == hash_val
            except (ValueError, TypeError):
                return False
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        return secrets.token_hex(16)
    
    def _generate_session_id(self) -> str:
        """Generate secure session ID"""
        return secrets.token_hex(32)
    
    def _validate_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_password(self, password: str) -> bool:
        """Validate password meets requirements"""
        return len(password) >= self.MIN_PASSWORD_LENGTH
    
    def _create_session(self, user_id: str) -> Session:
        """Create a new session for user"""
        now = datetime.now()
        expires = now + timedelta(days=self.SESSION_DURATION_DAYS)
        
        session = Session(
            session_id=self._generate_session_id(),
            user_id=user_id,
            created_at=now.isoformat(),
            expires_at=expires.isoformat()
        )
        
        # Save session
        sessions = self._load_sessions()
        sessions[session.session_id] = session.to_dict()
        self._save_sessions(sessions)
        
        # Store session ID for restoration
        self._save_current_session_id(session.session_id)
        
        return session
    
    def _save_current_session_id(self, session_id: str) -> None:
        """Save current session ID for auto-login"""
        session_file = self._data_dir / "current_session.txt"
        with open(session_file, 'w') as f:
            f.write(session_id)
    
    def _get_current_session_id(self) -> Optional[str]:
        """Get stored session ID"""
        session_file = self._data_dir / "current_session.txt"
        if session_file.exists():
            try:
                with open(session_file, 'r') as f:
                    return f.read().strip()
            except IOError:
                return None
        return None
    
    def _clear_current_session_id(self) -> None:
        """Clear stored session ID"""
        session_file = self._data_dir / "current_session.txt"
        if session_file.exists():
            session_file.unlink()
    
    def _restore_session(self) -> bool:
        """Attempt to restore previous session"""
        session_id = self._get_current_session_id()
        if not session_id:
            return False
        
        sessions = self._load_sessions()
        session_data = sessions.get(session_id)
        
        if not session_data:
            self._clear_current_session_id()
            return False
        
        session = Session.from_dict(session_data)
        
        if session.is_expired():
            # Clean up expired session
            del sessions[session_id]
            self._save_sessions(sessions)
            self._clear_current_session_id()
            return False
        
        # Load user
        users = self._load_users()
        user_data = users.get(session.user_id)
        
        if not user_data:
            self._clear_current_session_id()
            return False
        
        # Restore session state
        self._current_session = session
        self._current_user = User.from_dict(user_data['user'])
        
        return True
    
    # ==========================================================================
    # Public API
    # ==========================================================================
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return self._current_user is not None and self._current_session is not None
    
    @property
    def current_user(self) -> Optional[User]:
        """Get current authenticated user"""
        return self._current_user
    
    def signup(self, email: str, password: str, display_name: str = "") -> Tuple[AuthResult, Optional[User]]:
        """
        Register a new user.
        
        Args:
            email: User's email address
            password: User's password (min 6 characters)
            display_name: User's display name (optional)
        
        Returns:
            Tuple of (AuthResult, User or None)
        """
        email = email.strip().lower()
        
        # Validate email
        if not self._validate_email(email):
            return AuthResult.INVALID_EMAIL, None
        
        # Validate password
        if not self._validate_password(password):
            return AuthResult.WEAK_PASSWORD, None
        
        # Check if user already exists
        users = self._load_users()
        if email in users:
            return AuthResult.USER_EXISTS, None
        
        # Create user
        now = datetime.now().isoformat()
        user = User(
            id=self._generate_user_id(),
            email=email,
            username=email.split('@')[0],
            display_name=display_name or email.split('@')[0],
            created_at=now,
            updated_at=now
        )
        
        # Store user with hashed password
        users[email] = {
            'user': user.to_dict(),
            'password_hash': self._hash_password(password)
        }
        self._save_users(users)
        
        # Create session (auto-login after signup)
        self._current_session = self._create_session(user.id)
        self._current_user = user
        
        return AuthResult.SUCCESS, user
    
    def login(self, email: str, password: str) -> Tuple[AuthResult, Optional[User]]:
        """
        Log in an existing user.
        
        Args:
            email: User's email address
            password: User's password
        
        Returns:
            Tuple of (AuthResult, User or None)
        """
        email = email.strip().lower()
        
        # Find user
        users = self._load_users()
        user_record = users.get(email)
        
        if not user_record:
            return AuthResult.USER_NOT_FOUND, None
        
        # Verify password
        if not self._verify_password(password, user_record['password_hash']):
            return AuthResult.INVALID_CREDENTIALS, None
        
        # Create session
        user = User.from_dict(user_record['user'])
        self._current_session = self._create_session(user.id)
        self._current_user = user
        
        return AuthResult.SUCCESS, user
    
    def logout(self) -> AuthResult:
        """Log out current user"""
        if self._current_session:
            # Remove session from storage
            sessions = self._load_sessions()
            if self._current_session.session_id in sessions:
                del sessions[self._current_session.session_id]
                self._save_sessions(sessions)
        
        self._current_session = None
        self._current_user = None
        self._clear_current_session_id()
        
        return AuthResult.SUCCESS
    
    def check_auth(self) -> Tuple[AuthResult, Optional[User]]:
        """
        Check current authentication status.
        Useful for restoring session on app startup.
        
        Returns:
            Tuple of (AuthResult, User or None)
        """
        if self.is_authenticated:
            return AuthResult.SUCCESS, self._current_user
        return AuthResult.NOT_AUTHENTICATED, None
    
    def update_profile(self, display_name: Optional[str] = None) -> Tuple[AuthResult, Optional[User]]:
        """
        Update current user's profile.
        
        Args:
            display_name: New display name (optional)
        
        Returns:
            Tuple of (AuthResult, User or None)
        """
        if not self.is_authenticated:
            return AuthResult.NOT_AUTHENTICATED, None
        
        users = self._load_users()
        user_record = users.get(self._current_user.email)
        
        if not user_record:
            return AuthResult.USER_NOT_FOUND, None
        
        # Update fields
        if display_name:
            user_record['user']['display_name'] = display_name
        
        user_record['user']['updated_at'] = datetime.now().isoformat()
        
        # Save
        users[self._current_user.email] = user_record
        self._save_users(users)
        
        # Update current user
        self._current_user = User.from_dict(user_record['user'])
        
        return AuthResult.SUCCESS, self._current_user
    
    def change_password(self, current_password: str, new_password: str) -> AuthResult:
        """
        Change current user's password.
        
        Args:
            current_password: Current password for verification
            new_password: New password (min 6 characters)
        
        Returns:
            AuthResult
        """
        if not self.is_authenticated:
            return AuthResult.NOT_AUTHENTICATED
        
        # Validate new password
        if not self._validate_password(new_password):
            return AuthResult.WEAK_PASSWORD
        
        users = self._load_users()
        user_record = users.get(self._current_user.email)
        
        if not user_record:
            return AuthResult.USER_NOT_FOUND
        
        # Verify current password
        if not self._verify_password(current_password, user_record['password_hash']):
            return AuthResult.INVALID_CREDENTIALS
        
        # Update password
        user_record['password_hash'] = self._hash_password(new_password)
        user_record['user']['updated_at'] = datetime.now().isoformat()
        
        users[self._current_user.email] = user_record
        self._save_users(users)
        
        return AuthResult.SUCCESS
    
    def delete_account(self, password: str) -> AuthResult:
        """
        Delete current user's account.
        
        Args:
            password: Current password for verification
        
        Returns:
            AuthResult
        """
        if not self.is_authenticated:
            return AuthResult.NOT_AUTHENTICATED
        
        users = self._load_users()
        user_record = users.get(self._current_user.email)
        
        if not user_record:
            return AuthResult.USER_NOT_FOUND
        
        # Verify password
        if not self._verify_password(password, user_record['password_hash']):
            return AuthResult.INVALID_CREDENTIALS
        
        # Delete user
        del users[self._current_user.email]
        self._save_users(users)
        
        # Logout
        self.logout()
        
        return AuthResult.SUCCESS
    
    def get_user_id(self) -> Optional[str]:
        """Get current user's ID (useful for linking with other data)"""
        return self._current_user.id if self._current_user else None
