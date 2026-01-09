"""
Hub Routes Package
"""
from .hub import bp as hub_bp
from .api import bp as api_bp

__all__ = ['hub_bp', 'api_bp']
