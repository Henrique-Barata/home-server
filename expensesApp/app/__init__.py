"""
Expense Tracker Application Factory
------------------------------------
Creates and configures the Flask application.
Uses factory pattern for testability and flexibility.
"""
from flask import Flask
from flask_login import LoginManager

from .config import get_config


# Global login manager instance
login_manager = LoginManager()


def create_app(config_class=None):
    """
    Application factory function.
    
    Args:
        config_class: Optional configuration class override
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config = config_class or get_config()
    app.config.from_object(config)
    
    # Ensure directories exist
    config.ensure_directories()
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access the application."
    
    # Register blueprints (routes)
    from .routes import auth, dashboard, food, utilities, fixed, stuff, other, export, log, reimbursement
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(food.bp)
    app.register_blueprint(utilities.bp)
    app.register_blueprint(fixed.bp)
    app.register_blueprint(stuff.bp)
    app.register_blueprint(other.bp)
    app.register_blueprint(log.bp)
    app.register_blueprint(export.bp)
    app.register_blueprint(reimbursement.bp)
    
    # User loader for Flask-Login
    from .models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)
    
    return app
