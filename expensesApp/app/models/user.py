"""
User Model
----------
Simple user model for Flask-Login integration.
Uses session-based authentication with a single shared password.
Supports both hashed (secure) and plaintext (legacy) passwords.
"""
import logging
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

logger = logging.getLogger(__name__)


class User(UserMixin):
    """
    Simple user class for authentication.
    For this local app, we use a single shared password.
    The 'user' is just a session identifier.
    
    Password Security:
    - Supports hashed passwords (recommended) using Werkzeug's security functions
    - Falls back to plaintext comparison for legacy configurations
    - Use generate_password_hash() to create secure password hashes
    """
    
    # Single user ID for this simple auth system
    USER_ID = "local_user"
    
    def __init__(self, user_id: str):
        self.id = user_id
    
    @classmethod
    def get(cls, user_id: str):
        """Get user by ID. Returns User if valid, None otherwise."""
        if user_id == cls.USER_ID:
            return cls(user_id)
        return None
    
    @classmethod
    def _is_hashed_password(cls, password_value: str) -> bool:
        """
        Check if a password value is a Werkzeug hash.
        Werkzeug hashes start with method identifier like 'pbkdf2:sha256:' or 'scrypt:'.
        """
        if not password_value:
            return False
        # Werkzeug password hashes have a specific format with method prefix
        hash_prefixes = ('pbkdf2:', 'scrypt:')
        return password_value.startswith(hash_prefixes)
    
    @classmethod
    def authenticate(cls, password: str) -> 'User':
        """
        Authenticate with password.
        Returns User instance if password matches, None otherwise.
        
        Supports both hashed and plaintext passwords:
        - If APP_PASSWORD starts with a hash prefix, uses secure comparison
        - Otherwise falls back to plaintext comparison (legacy mode with warning)
        """
        from ..config import get_config
        config = get_config()
        
        stored_password = config.APP_PASSWORD
        
        if not stored_password:
            logger.error("No APP_PASSWORD configured")
            return None
        
        if not password:
            return None
        
        if cls._is_hashed_password(stored_password):
            # Secure mode: compare using hash
            if check_password_hash(stored_password, password):
                return cls(cls.USER_ID)
        else:
            # Legacy mode: plaintext comparison (log warning once)
            logger.warning(
                "APP_PASSWORD is stored in plaintext. "
                "Run 'python -m scripts.hash_password' to generate a secure hash."
            )
            if password == stored_password:
                return cls(cls.USER_ID)
        
        return None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Generate a secure hash for a password.
        Use this to create hashed passwords for config_private.py.
        
        Args:
            password: The plaintext password to hash
            
        Returns:
            A secure hash string to store in APP_PASSWORD
        """
        return generate_password_hash(password, method='pbkdf2:sha256:600000')
