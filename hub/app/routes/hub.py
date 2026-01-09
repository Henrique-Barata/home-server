"""
Hub Main Routes
---------------
Serves the main hub interface.
"""
from flask import Blueprint, render_template
from ..services.app_manager import AppManager

bp = Blueprint('hub', __name__)

# Initialize app manager
app_manager = AppManager()


@bp.route('/')
def index():
    """Render the main hub dashboard."""
    apps = app_manager.get_all_apps()
    hub_info = app_manager.get_hub_info()
    return render_template('index.html', apps=apps, hub=hub_info)
