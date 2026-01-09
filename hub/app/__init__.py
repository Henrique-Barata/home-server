"""
Home Server Hub Application Factory
-----------------------------------
Central hub for managing home server applications.
"""
from flask import Flask
from pathlib import Path
import atexit


def create_app(config_dict=None):
    """
    Application factory function.
    
    Args:
        config_dict: Optional configuration dictionary override
        
    Returns:
        Configured Flask application instance
    """
    import os
    from .services.logger import get_hub_logger
    
    logger = get_hub_logger()
    logger.info("Creating Hub application...")
    
    app = Flask(__name__)
    
    # Load configuration from environment (required in production)
    app.config['SECRET_KEY'] = os.environ.get('HUB_SECRET_KEY')
    if not app.config['SECRET_KEY']:
        raise ValueError('HUB_SECRET_KEY environment variable must be set')
    app.config['HUB_ROOT'] = Path(__file__).parent.parent
    
    # Load hub settings from config.yaml
    config_path = app.config['HUB_ROOT'] / 'config.yaml'
    if config_path.exists():
        import yaml
        with open(config_path, 'r') as f:
            hub_config = yaml.safe_load(f)
            app.config['HUB_SETTINGS'] = hub_config.get('hub', {})
            logger.debug(f"Loaded hub settings from {config_path}")
    
    # Override with provided config
    if config_dict:
        app.config.update(config_dict)
    
    # Register blueprints
    from .routes import hub_bp
    from .routes import api_bp
    
    app.register_blueprint(hub_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    logger.info("Hub application created successfully")
    
    # Register cleanup on shutdown
    @atexit.register
    def cleanup():
        logger.info("Hub shutting down, cleaning up...")
        try:
            from .routes.api import _activity_tracker
            if _activity_tracker:
                _activity_tracker.stop()
                logger.info("Activity tracker stopped")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    return app
