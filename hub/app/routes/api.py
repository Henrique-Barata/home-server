"""
Hub API Routes
--------------
REST API for managing applications.
"""
from flask import Blueprint, jsonify, request
from ..services.app_manager import AppManager

bp = Blueprint('api', __name__)

# Initialize app manager
app_manager = AppManager()


@bp.route('/apps', methods=['GET'])
def list_apps():
    """List all registered applications."""
    apps = app_manager.get_all_apps()
    return jsonify({
        'success': True,
        'apps': apps
    })


@bp.route('/apps/<app_id>/status', methods=['GET'])
def get_app_status(app_id):
    """Get the status of a specific application."""
    status = app_manager.get_app_status(app_id)
    if status is None:
        return jsonify({
            'success': False,
            'error': f'App "{app_id}" not found'
        }), 404
    
    return jsonify({
        'success': True,
        'app_id': app_id,
        'status': status
    })


@bp.route('/apps/<app_id>/start', methods=['POST'])
def start_app(app_id):
    """Start an application."""
    result = app_manager.start_app(app_id)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result)


@bp.route('/apps/<app_id>/stop', methods=['POST'])
def stop_app(app_id):
    """Stop an application."""
    result = app_manager.stop_app(app_id)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result)


@bp.route('/apps/<app_id>/restart', methods=['POST'])
def restart_app(app_id):
    """Restart an application."""
    result = app_manager.restart_app(app_id)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result)


@bp.route('/apps/<app_id>/open', methods=['GET'])
def get_app_url(app_id):
    """Get the URL to access an application."""
    url = app_manager.get_app_url(app_id)
    if url is None:
        return jsonify({
            'success': False,
            'error': f'App "{app_id}" not found'
        }), 404
    
    return jsonify({
        'success': True,
        'app_id': app_id,
        'url': url
    })
