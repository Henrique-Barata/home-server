"""
Application Manager Service
---------------------------
Manages the lifecycle of home server applications.
Handles starting, stopping, and monitoring apps.
"""
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

import psutil
import yaml

from .logger import get_app_manager_logger

logger = get_app_manager_logger()


class AppManager:
    """
    Manages home server applications.
    
    Responsibilities:
    - Load app configurations from config.yaml
    - Start/stop/restart applications
    - Monitor application status
    - Provide app information for the UI
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the AppManager.
        
        Args:
            config_path: Path to config.yaml. Defaults to hub/config.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / 'config.yaml'
        
        self.config_path = Path(config_path).resolve()
        self.hub_root = self.config_path.parent.resolve()
        self._config: Dict[str, Any] = {}
        self._load_config()
        
        logger.info(f"AppManager initialized with config: {self.config_path}")
        logger.info(f"Hub root: {self.hub_root}")
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self._config = yaml.safe_load(f) or {}
                logger.info(f"Loaded config with {len(self._config.get('apps', {}))} apps")
            else:
                logger.warning(f"Config file not found: {self.config_path}")
                self._config = {'hub': {}, 'apps': {}}
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse config file: {e}")
            self._config = {'hub': {}, 'apps': {}}
        except Exception as e:
            logger.error(f"Error loading config: {e}", exc_info=True)
            self._config = {'hub': {}, 'apps': {}}
    
    def reload_config(self) -> Dict[str, Any]:
        """Reload configuration from disk."""
        logger.info("Reloading configuration")
        self._load_config()
        return {'success': True, 'message': 'Configuration reloaded'}
    
    def get_hub_info(self) -> Dict[str, Any]:
        """Get hub information."""
        default = {
            'name': 'Home Server Hub',
            'version': '1.0.0',
            'description': 'Central management for home server applications'
        }
        return {**default, **self._config.get('hub', {})}
    
    def get_all_apps(self) -> list:
        """
        Get all registered applications with their current status.
        
        Returns:
            List of app dictionaries with status information
        """
        apps = []
        for app_id, app_config in self._config.get('apps', {}).items():
            try:
                app_info = {
                    'id': app_id,
                    'name': app_config.get('name', app_id),
                    'description': app_config.get('description', ''),
                    'icon': app_config.get('icon', '📦'),
                    'color': app_config.get('color', '#607D8B'),
                    'port': app_config.get('port', 5000),
                    'idle_timeout_minutes': app_config.get('idle_timeout_minutes', 15),
                    'status': self.get_app_status(app_id)
                }
                apps.append(app_info)
            except Exception as e:
                logger.error(f"Error getting info for app '{app_id}': {e}")
                apps.append({
                    'id': app_id,
                    'name': app_id,
                    'error': str(e),
                    'status': {'running': False, 'error': True}
                })
        return apps
    
    def get_app_config(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific app."""
        return self._config.get('apps', {}).get(app_id)
    
    def get_app_status(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of an application.
        
        Args:
            app_id: The application identifier
            
        Returns:
            Status dictionary or None if app not found
        """
        app_config = self.get_app_config(app_id)
        if app_config is None:
            return None
        
        port = app_config.get('port', 5000)
        pid_file = self._get_pid_file(app_id)
        
        is_running = False
        pid = None
        process_info = {}
        
        # Check PID file
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    if process.is_running() and process.status() != psutil.STATUS_ZOMBIE:
                        is_running = True
                        # Get process info
                        try:
                            process_info = {
                                'cpu_percent': process.cpu_percent(),
                                'memory_mb': round(process.memory_info().rss / 1024 / 1024, 2),
                                'create_time': process.create_time(),
                                'status': process.status()
                            }
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                else:
                    # Process not running, clean up PID file
                    logger.debug(f"Cleaning stale PID file for '{app_id}'")
                    pid_file.unlink(missing_ok=True)
                    pid = None
            except ValueError as e:
                logger.warning(f"Invalid PID in file for '{app_id}': {e}")
                pid_file.unlink(missing_ok=True)
                pid = None
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.debug(f"Process check failed for '{app_id}': {e}")
                pid_file.unlink(missing_ok=True)
                pid = None
        
        # Backup check: is the port in use?
        port_in_use = self._is_port_in_use(port)
        
        return {
            'running': is_running or port_in_use,
            'pid': pid,
            'port': port,
            'port_in_use': port_in_use,
            'process': process_info if is_running else None
        }
    
    def _get_pid_file(self, app_id: str) -> Path:
        """Get the PID file path for an app."""
        app_config = self.get_app_config(app_id)
        if app_config:
            app_path = (self.hub_root / app_config.get('path', '')).resolve()
            return app_path / 'app.pid'
        return self.hub_root / 'logs' / f'{app_id}.pid'
    
    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is currently in use."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                return result == 0
        except Exception as e:
            logger.debug(f"Port check error for {port}: {e}")
            return False
    
    def get_app_url(self, app_id: str) -> Optional[str]:
        """Get the URL to access an application."""
        app_config = self.get_app_config(app_id)
        if app_config is None:
            return None
        
        host = app_config.get('host', '127.0.0.1')
        port = app_config.get('port', 5000)
        
        # Use localhost for 0.0.0.0 bindings
        if host == '0.0.0.0':
            host = '127.0.0.1'
        
        return f'http://{host}:{port}'
    
    def start_app(self, app_id: str) -> Dict[str, Any]:
        """
        Start an application.
        
        Args:
            app_id: The application identifier
            
        Returns:
            Result dictionary with success status and message
        """
        logger.info(f"Starting app '{app_id}'")
        
        app_config = self.get_app_config(app_id)
        if app_config is None:
            logger.error(f"App '{app_id}' not found in config")
            return {'success': False, 'error': f'App "{app_id}" not found'}
        
        # Check if already running
        status = self.get_app_status(app_id)
        if status and status['running']:
            logger.info(f"App '{app_id}' is already running (PID: {status.get('pid')})")
            return {
                'success': True,
                'message': f'App "{app_id}" is already running',
                'already_running': True,
                'url': self.get_app_url(app_id),
                'pid': status.get('pid')
            }
        
        # Resolve paths
        app_rel_path = app_config.get('path', '')
        app_path = (self.hub_root / app_rel_path).resolve()
        entry_file = app_config.get('entry', 'run.py')
        port = app_config.get('port', 5000)
        host = app_config.get('host', '127.0.0.1')
        
        logger.debug(f"App path: {app_path}")
        logger.debug(f"Entry file: {entry_file}")
        
        if not app_path.exists():
            logger.error(f"App path does not exist: {app_path}")
            return {'success': False, 'error': f'App path does not exist: {app_path}'}
        
        entry_path = app_path / entry_file
        if not entry_path.exists():
            logger.error(f"Entry file not found: {entry_path}")
            return {'success': False, 'error': f'Entry file not found: {entry_path}'}
        
        try:
            # Determine Python interpreter
            app_venv_python = app_path / 'venv' / 'bin' / 'python'
            if app_venv_python.exists():
                python_path = str(app_venv_python)
                logger.debug(f"Using app venv: {python_path}")
            else:
                python_path = sys.executable
                logger.debug(f"Using system Python: {python_path}")
            
            # Create logs directory
            logs_dir = self.hub_root / 'logs'
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            # Log files for the app
            stdout_log = logs_dir / f'{app_id}_stdout.log'
            stderr_log = logs_dir / f'{app_id}_stderr.log'
            
            # Build command
            cmd = [python_path, str(entry_path), '--host', host, '--port', str(port)]
            logger.info(f"Starting with command: {' '.join(cmd)}")
            
            # Clean environment - remove any inherited Flask/Werkzeug vars
            env = os.environ.copy()
            vars_to_remove = [
                'WERKZEUG_RUN_MAIN',
                'WERKZEUG_SERVER_FD',
                'FLASK_ENV',
                'FLASK_DEBUG',
            ]
            for var in vars_to_remove:
                env.pop(var, None)
            
            # Set PYTHONPATH to include app directory
            env['PYTHONPATH'] = str(app_path)
            
            # Start process
            with open(stdout_log, 'a') as out_f, open(stderr_log, 'a') as err_f:
                # Write startup marker
                startup_msg = f"\n{'='*60}\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting app...\n{'='*60}\n"
                out_f.write(startup_msg)
                err_f.write(startup_msg)
                out_f.flush()
                err_f.flush()
                
                process = subprocess.Popen(
                    cmd,
                    cwd=str(app_path),
                    stdout=out_f,
                    stderr=err_f,
                    start_new_session=True,
                    env=env,
                )
            
            # Write PID file
            pid_file = self._get_pid_file(app_id)
            pid_file.write_text(str(process.pid))
            logger.info(f"Started app '{app_id}' with PID {process.pid}")
            
            # Wait for startup and verify
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is not None:
                exit_code = process.returncode
                logger.error(f"App '{app_id}' exited immediately with code {exit_code}")
                
                # Read error log
                try:
                    with open(stderr_log, 'r') as f:
                        lines = f.readlines()
                        error_msg = ''.join(lines[-20:]) if lines else 'Unknown error'
                except Exception:
                    error_msg = 'Could not read error log'
                
                pid_file.unlink(missing_ok=True)
                
                return {
                    'success': False,
                    'error': f'App failed to start (exit code {exit_code})',
                    'details': error_msg[:1000],
                    'log_file': str(stderr_log)
                }
            
            # Verify port is responding
            for i in range(5):
                if self._is_port_in_use(port):
                    logger.info(f"App '{app_id}' is now responding on port {port}")
                    break
                time.sleep(0.5)
            
            return {
                'success': True,
                'message': f'App "{app_id}" started successfully',
                'pid': process.pid,
                'port': port,
                'url': self.get_app_url(app_id),
                'logs': {
                    'stdout': str(stdout_log),
                    'stderr': str(stderr_log)
                }
            }
            
        except PermissionError as e:
            logger.error(f"Permission denied starting '{app_id}': {e}")
            return {'success': False, 'error': f'Permission denied: {e}'}
        except FileNotFoundError as e:
            logger.error(f"File not found starting '{app_id}': {e}")
            return {'success': False, 'error': f'File not found: {e}'}
        except Exception as e:
            logger.error(f"Failed to start app '{app_id}': {e}", exc_info=True)
            return {'success': False, 'error': f'Failed to start app: {str(e)}'}
    
    def stop_app(self, app_id: str) -> Dict[str, Any]:
        """
        Stop an application gracefully.
        
        Args:
            app_id: The application identifier
            
        Returns:
            Result dictionary with success status and message
        """
        logger.info(f"Stopping app '{app_id}'")
        
        app_config = self.get_app_config(app_id)
        if app_config is None:
            return {'success': False, 'error': f'App "{app_id}" not found'}
        
        status = self.get_app_status(app_id)
        if not status or not status['running']:
            logger.info(f"App '{app_id}' is not running")
            return {
                'success': True,
                'message': f'App "{app_id}" is not running',
                'already_stopped': True
            }
        
        pid = status.get('pid')
        if not pid:
            # Try to find process by port
            port = app_config.get('port', 5000)
            logger.warning(f"No PID for '{app_id}', but port {port} is in use")
            return {
                'success': False,
                'error': f'No PID found. Port {port} may be used by another process.'
            }
        
        try:
            # Send SIGTERM for graceful shutdown
            logger.debug(f"Sending SIGTERM to PID {pid}")
            os.kill(pid, signal.SIGTERM)
            
            # Wait for graceful shutdown
            for i in range(10):
                if not psutil.pid_exists(pid):
                    break
                time.sleep(0.5)
            
            # Force kill if still running
            if psutil.pid_exists(pid):
                logger.warning(f"App '{app_id}' did not stop gracefully, sending SIGKILL")
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)
            
            # Clean up PID file
            pid_file = self._get_pid_file(app_id)
            pid_file.unlink(missing_ok=True)
            
            logger.info(f"App '{app_id}' stopped successfully")
            return {
                'success': True,
                'message': f'App "{app_id}" stopped successfully'
            }
            
        except ProcessLookupError:
            logger.info(f"App '{app_id}' was already stopped")
            pid_file = self._get_pid_file(app_id)
            pid_file.unlink(missing_ok=True)
            return {
                'success': True,
                'message': f'App "{app_id}" was already stopped'
            }
        except PermissionError as e:
            logger.error(f"Permission denied stopping '{app_id}': {e}")
            return {'success': False, 'error': f'Permission denied: {e}'}
        except Exception as e:
            logger.error(f"Failed to stop app '{app_id}': {e}", exc_info=True)
            return {'success': False, 'error': f'Failed to stop app: {str(e)}'}
    
    def restart_app(self, app_id: str) -> Dict[str, Any]:
        """
        Restart an application.
        
        Args:
            app_id: The application identifier
            
        Returns:
            Result dictionary with success status and message
        """
        logger.info(f"Restarting app '{app_id}'")
        
        stop_result = self.stop_app(app_id)
        if not stop_result['success'] and 'already_stopped' not in stop_result:
            return stop_result
        
        # Brief pause between stop and start
        time.sleep(1)
        
        start_result = self.start_app(app_id)
        if start_result['success']:
            start_result['message'] = f'App "{app_id}" restarted successfully'
        
        return start_result
    
    def get_app_logs(
        self,
        app_id: str,
        log_type: str = 'stderr',
        lines: int = 100
    ) -> Dict[str, Any]:
        """
        Get the logs for an application.
        
        Args:
            app_id: The application identifier
            log_type: 'stdout' or 'stderr'
            lines: Number of lines to return from the end
            
        Returns:
            Result dictionary with log content
        """
        app_config = self.get_app_config(app_id)
        if app_config is None:
            return {'success': False, 'error': f'App "{app_id}" not found'}
        
        logs_dir = self.hub_root / 'logs'
        log_file = logs_dir / f'{app_id}_{log_type}.log'
        
        if not log_file.exists():
            return {
                'success': True,
                'log_content': f'No {log_type} log file found for "{app_id}".\nApp may not have been started yet.',
                'log_file': str(log_file),
                'total_lines': 0
            }
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                all_lines = f.readlines()
                log_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                log_content = ''.join(log_lines)
            
            return {
                'success': True,
                'log_content': log_content,
                'log_file': str(log_file),
                'total_lines': len(all_lines),
                'showing_lines': len(log_lines)
            }
        except Exception as e:
            logger.error(f"Failed to read logs for '{app_id}': {e}")
            return {'success': False, 'error': f'Failed to read log: {str(e)}'}
    
    def health_check(self, app_id: str) -> Dict[str, Any]:
        """
        Perform a health check on an application.
        
        Args:
            app_id: The application identifier
            
        Returns:
            Health check result
        """
        app_config = self.get_app_config(app_id)
        if app_config is None:
            return {'success': False, 'healthy': False, 'error': 'App not found'}
        
        status = self.get_app_status(app_id)
        if not status or not status['running']:
            return {'success': True, 'healthy': False, 'reason': 'Not running'}
        
        # Check if port responds
        port = app_config.get('port', 5000)
        health_endpoint = app_config.get('health_endpoint', '/')
        
        try:
            import urllib.request
            import urllib.error
            
            url = f'http://127.0.0.1:{port}{health_endpoint}'
            req = urllib.request.Request(url, method='HEAD')
            
            with urllib.request.urlopen(req, timeout=5) as response:
                return {
                    'success': True,
                    'healthy': True,
                    'status_code': response.status,
                    'url': url
                }
        except urllib.error.HTTPError as e:
            # HTTP errors (4xx, 5xx) still mean the app is responding
            return {
                'success': True,
                'healthy': True,
                'status_code': e.code,
                'url': url
            }
        except Exception as e:
            logger.warning(f"Health check failed for '{app_id}': {e}")
            return {
                'success': True,
                'healthy': False,
                'reason': str(e)
            }
