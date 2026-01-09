"""
Application Configuration
-------------------------
Centralized configuration for the expense tracker.
Optimized for low-resource environments.
"""
import os
import sys
from pathlib import Path

# Import private configuration
try:
    # Try to import from the parent directory (where config_private.py should be)
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    import config_private
    HAS_PRIVATE_CONFIG = True
except ImportError:
    HAS_PRIVATE_CONFIG = False
    print("⚠️  WARNING: config_private.py not found!")
    print("   Copy config_private.py.template to config_private.py and configure it.")
    print("   Using default/insecure values for now.")


class Config:
    """Base configuration with sensible defaults for low-resource systems."""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    EXPORT_DIR = BASE_DIR / "exports"
    
    # Flask settings - Load from private config or use insecure default
    SECRET_KEY = os.environ.get("SECRET_KEY") or (
        getattr(config_private, "SECRET_KEY", "INSECURE-DEFAULT-CHANGE-ME")
        if HAS_PRIVATE_CONFIG else "INSECURE-DEFAULT-CHANGE-ME"
    )
    
    # Database - SQLite for simplicity and low resource usage
    DATABASE_PATH = (
        getattr(config_private, "DATABASE_PATH", DATA_DIR / "expenses.db")
        if HAS_PRIVATE_CONFIG else DATA_DIR / "expenses.db"
    )
    
    # Authentication - Load from private config or environment
    APP_PASSWORD = os.environ.get("APP_PASSWORD") or (
        getattr(config_private, "APP_PASSWORD", "CHANGE-THIS-PASSWORD")
        if HAS_PRIVATE_CONFIG else "CHANGE-THIS-PASSWORD"
    )
    
    # Session settings
    SESSION_COOKIE_SECURE = False  # Set True if using HTTPS
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds
    
    # Performance settings
    DEBUG = False
    TESTING = False
    
    # Logging - minimal for low resources
    LOG_LEVEL = "WARNING"
    
    # Users - Load from private config or use default
    USERS = (
        getattr(config_private, "USERS", ["User1", "User2"])
        if HAS_PRIVATE_CONFIG else ["User1", "User2"]
    )
    
    # Expense categories - Can be customized in private config
    UTILITY_TYPES = (
        getattr(config_private, "UTILITY_TYPES", ["Electricity", "Gas", "Water", "Internet"])
        if HAS_PRIVATE_CONFIG else ["Electricity", "Gas", "Water", "Internet"]
    )
    FIXED_EXPENSE_TYPES = (
        getattr(config_private, "FIXED_EXPENSE_TYPES", ["Rent", "Internet"])
        if HAS_PRIVATE_CONFIG else ["Rent", "Internet"]
    )
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.EXPORT_DIR.mkdir(exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration with debugging enabled."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration optimized for low-power hardware."""
    DEBUG = False
    LOG_LEVEL = "ERROR"


# Select configuration based on environment
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": Config
}

def get_config():
    """Get configuration based on environment variable."""
    env = os.environ.get("FLASK_ENV", "default")
    return config_map.get(env, Config)
