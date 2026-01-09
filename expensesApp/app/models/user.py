"""
User Model
----------
Simple user model for Flask-Login integration.
Uses session-based authentication with a single shared password.
"""
from flask_login import UserMixin


class User(UserMixin):
    """
    Simple user class for authentication.
    For this local app, we use a single shared password.
    The 'user' is just a session identifier.
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
    def authenticate(cls, password: str) -> 'User':
        """
        Authenticate with password.
        Returns User instance if password matches, None otherwise.
        """
        from ..config import get_config
        config = get_config()
        
        if password == config.APP_PASSWORD:
            return cls(cls.USER_ID)
        return None
