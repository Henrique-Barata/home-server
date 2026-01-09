"""
Hub API Routes
--------------
REST API for managing applications.
"""
from flask import Blueprint, jsonify, request, current_app
from ..services.app_manager import AppManager
from ..services.logger import get_api_logger

bp = Blueprint('api', __name__)
logger = get_api_logger()

# Initialize app manager (singleton per process)
_app_manager = None
_activity_tracker = None


def get_app_manager():
    """Get or create the AppManager singleton."""
    global _app_manager
    if _app_manager is None:
        _app_manager = AppManager()
    return _app_manager


def get_activity_tracker():
    """Get or create the ActivityTracker singleton."""
    global _activity_tracker
    if _activity_tracker is None:
        from ..services.scheduler import AppActivityTracker
        _activity_tracker = AppActivityTracker(
            get_app_manager(),
            default_idle_timeout_minutes=15,
            check_interval_seconds=60
        )
        _activity_tracker.start()
    return _activity_tracker


@bp.before_request
def log_request():
    """Log incoming API requests."""
    logger.debug(f"{request.method} {request.path}")


@bp.after_request
def log_response(response):
    """Log API responses."""
    logger.debug(f"{request.method} {request.path} -> {response.status_code}")
    return response


@bp.errorhandler(Exception)
def handle_error(error):
    """Global error handler for API routes."""
    logger.error(f"Unhandled error in {request.path}: {error}", exc_info=True)
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'details': str(error) if current_app.debug else None
    }), 500


@bp.route('/apps', methods=['GET'])
def list_apps():
    """List all registered applications with status."""
    try:
        app_manager = get_app_manager()
        apps = app_manager.get_all_apps()
        logger.info(f"Listed {len(apps)} apps")
        return jsonify({
            'success': True,
            'apps': apps
        })
    except Exception as e:
        logger.error(f"Error listing apps: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to list apps: {str(e)}'
        }), 500


@bp.route('/apps/<app_id>/status', methods=['GET'])
def get_app_status(app_id):
    """Get the status of a specific application."""
    try:
        app_manager = get_app_manager()
        status = app_manager.get_app_status(app_id)
        
        if status is None:
            logger.warning(f"App '{app_id}' not found")
            return jsonify({
                'success': False,
                'error': f'App "{app_id}" not found'
            }), 404
        
        return jsonify({
            'success': True,
            'app_id': app_id,
            'status': status
        })
    except Exception as e:
        logger.error(f"Error getting status for '{app_id}': {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to get status: {str(e)}'
        }), 500


@bp.route('/apps/<app_id>/start', methods=['POST'])
def start_app(app_id):
    """Start an application."""
    try:
        logger.info(f"API request to start app '{app_id}'")
        app_manager = get_app_manager()
        result = app_manager.start_app(app_id)
        
        if result.get('success'):
            # Record activity for auto-shutdown tracking
            tracker = get_activity_tracker()
            tracker.record_activity(app_id)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error starting '{app_id}': {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to start app: {str(e)}'
        }), 500


@bp.route('/apps/<app_id>/stop', methods=['POST'])
def stop_app(app_id):
    """Stop an application."""
    try:
        logger.info(f"API request to stop app '{app_id}'")
        app_manager = get_app_manager()
        result = app_manager.stop_app(app_id)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error stopping '{app_id}': {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to stop app: {str(e)}'
        }), 500


@bp.route('/apps/<app_id>/restart', methods=['POST'])
def restart_app(app_id):
    """Restart an application."""
    try:
        logger.info(f"API request to restart app '{app_id}'")
        app_manager = get_app_manager()
        result = app_manager.restart_app(app_id)
        
        if result.get('success'):
            # Record activity for auto-shutdown tracking
            tracker = get_activity_tracker()
            tracker.record_activity(app_id)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error restarting '{app_id}': {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to restart app: {str(e)}'
        }), 500


@bp.route('/apps/<app_id>/open', methods=['GET'])
def get_app_url(app_id):
    """Get the URL to access an application."""
    try:
        app_manager = get_app_manager()
        url = app_manager.get_app_url(app_id)
        
        if url is None:
            return jsonify({
                'success': False,
                'error': f'App "{app_id}" not found'
            }), 404
        
        # Record activity when user opens the app
        tracker = get_activity_tracker()
        tracker.record_activity(app_id)
        
        return jsonify({
            'success': True,
            'app_id': app_id,
            'url': url
        })
    except Exception as e:
        logger.error(f"Error getting URL for '{app_id}': {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to get app URL: {str(e)}'
        }), 500


@bp.route('/apps/<app_id>/logs', methods=['GET'])
def get_app_logs(app_id):
    """Get the logs for an application."""
    try:
        log_type = request.args.get('type', 'stderr')
        
        # Validate log_type
        if log_type not in ['stdout', 'stderr']:
            return jsonify({
                'success': False,
                'error': 'Invalid log type. Must be "stdout" or "stderr"'
            }), 400
        
        # Validate and parse lines parameter
        try:
            lines = int(request.args.get('lines', 100))
            if lines < 1 or lines > 10000:
                return jsonify({
                    'success': False,
                    'error': 'Lines parameter must be between 1 and 10000'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid lines parameter. Must be an integer'
            }), 400
        
        app_manager = get_app_manager()
        result = app_manager.get_app_logs(app_id, log_type, lines)
        
        status_code = 200 if result.get('success') else 404
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error getting logs for '{app_id}': {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to get logs: {str(e)}'
        }), 500


@bp.route('/apps/<app_id>/health', methods=['GET'])
def health_check(app_id):
    """Perform a health check on an application."""
    try:
        app_manager = get_app_manager()
        result = app_manager.health_check(app_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error checking health for '{app_id}': {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Health check failed: {str(e)}'
        }), 500


@bp.route('/apps/<app_id>/activity', methods=['POST'])
def record_activity(app_id):
    """Record activity for an app (reset idle timer)."""
    try:
        tracker = get_activity_tracker()
        tracker.record_activity(app_id)
        return jsonify({
            'success': True,
            'message': f'Activity recorded for "{app_id}"'
        })
    except Exception as e:
        logger.error(f"Error recording activity for '{app_id}': {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to record activity: {str(e)}'
        }), 500


@bp.route('/scheduler/status', methods=['GET'])
def scheduler_status():
    """Get the auto-shutdown scheduler status."""
    try:
        tracker = get_activity_tracker()
        return jsonify({
            'success': True,
            'scheduler': tracker.get_status()
        })
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to get scheduler status: {str(e)}'
        }), 500


@bp.route('/config/reload', methods=['POST'])
def reload_config():
    """Reload the hub configuration."""
    try:
        logger.info("API request to reload configuration")
        app_manager = get_app_manager()
        result = app_manager.reload_config()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error reloading config: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to reload config: {str(e)}'
        }), 500


@bp.route('/hub/info', methods=['GET'])
def hub_info():
    """Get hub information."""
    try:
        app_manager = get_app_manager()
        info = app_manager.get_hub_info()
        return jsonify({
            'success': True,
            'hub': info
        })
    except Exception as e:
        logger.error(f"Error getting hub info: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to get hub info: {str(e)}'
        }), 500
