"""
Home Server Hub Application Factory
-----------------------------------
Central hub for managing home server applications.
"""
from flask import Flask
from pathlib import Path


def create_app(config_dict=None):
    """
    Application factory function.
    
    Args:
        config_dict: Optional configuration dictionary override
        
    Returns:
        Configured Flask application instance
    """
    import os
    app = Flask(__name__)
    
    # Load configuration from environment (required in production)
    app.config['SECRET_KEY'] = os.environ.get('HUB_SECRET_KEY')
    if not app.config['SECRET_KEY']:
        raise ValueError('HUB_SECRET_KEY environment variable must be set')
    app.config['HUB_ROOT'] = Path(__file__).parent.parent
    
    # Override with provided config
    if config_dict:
        app.config.update(config_dict)
    
    # Register blueprints
    from .routes import hub_bp
    from .routes import api_bp
    
    app.register_blueprint(hub_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
