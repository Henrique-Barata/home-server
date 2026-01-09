"""
Application Manager Service
---------------------------
Manages the lifecycle of home server applications.
Handles starting, stopping, and monitoring apps.
"""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import psutil
import yaml


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
        
        self.config_path = Path(config_path)
        self.hub_root = self.config_path.parent
        self._config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f)
        else:
            self._config = {'hub': {}, 'apps': {}}
    
    def get_hub_info(self) -> dict:
        """Get hub information."""
        return self._config.get('hub', {
            'name': 'Home Server Hub',
            'version': '1.0.0'
        })
    
    def get_all_apps(self) -> list:
        """
        Get all registered applications with their current status.
        
        Returns:
            List of app dictionaries with status information
        """
        apps = []
        for app_id, app_config in self._config.get('apps', {}).items():
            app_info = {
                'id': app_id,
                'name': app_config.get('name', app_id),
                'description': app_config.get('description', ''),
                'icon': app_config.get('icon', '📦'),
                'color': app_config.get('color', '#607D8B'),
                'port': app_config.get('port', 5000),
                'status': self.get_app_status(app_id)
            }
            apps.append(app_info)
        return apps
    
    def get_app_config(self, app_id: str) -> Optional[dict]:
        """Get configuration for a specific app."""
        return self._config.get('apps', {}).get(app_id)
    
    def get_app_status(self, app_id: str) -> Optional[dict]:
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
        
        # Check if process is running
        is_running = False
        pid = None
        
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    if process.is_running():
                        is_running = True
            except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
                # PID file exists but process is not running
                pid_file.unlink(missing_ok=True)
                pid = None
        
        # Also check if port is in use (backup check)
        port_in_use = self._is_port_in_use(port)
        
        return {
            'running': is_running or port_in_use,
            'pid': pid,
            'port': port,
            'port_in_use': port_in_use
        }
    
    def _get_pid_file(self, app_id: str) -> Path:
        """Get the PID file path for an app."""
        app_config = self.get_app_config(app_id)
        if app_config:
            app_path = self.hub_root / app_config.get('path', '')
            return app_path / 'app.pid'
        return self.hub_root / f'{app_id}.pid'
    
    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is currently in use using socket connection test."""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            return result == 0  # 0 means connection succeeded, port is in use
    
    def get_app_url(self, app_id: str) -> Optional[str]:
        """Get the URL to access an application."""
        app_config = self.get_app_config(app_id)
        if app_config is None:
            return None
        
        host = app_config.get('host', '127.0.0.1')
        port = app_config.get('port', 5000)
        
        # If host is 0.0.0.0, use localhost for display
        if host == '0.0.0.0':
            host = '127.0.0.1'
        
        return f'http://{host}:{port}'
    
    def start_app(self, app_id: str) -> dict:
        """
        Start an application.
        
        Args:
            app_id: The application identifier
            
        Returns:
            Result dictionary with success status and message
        """
        app_config = self.get_app_config(app_id)
        if app_config is None:
            return {'success': False, 'error': f'App "{app_id}" not found'}
        
        # Check if already running
        status = self.get_app_status(app_id)
        if status and status['running']:
            return {
                'success': True,
                'message': f'App "{app_id}" is already running',
                'already_running': True,
                'url': self.get_app_url(app_id)
            }
        
        # Resolve app path
        app_path = (self.hub_root / app_config.get('path', '')).resolve()
        entry_file = app_config.get('entry', 'run.py')
        port = app_config.get('port', 5000)
        host = app_config.get('host', '127.0.0.1')
        
        if not app_path.exists():
            return {'success': False, 'error': f'App path does not exist: {app_path}'}
        
        entry_path = app_path / entry_file
        if not entry_path.exists():
            return {'success': False, 'error': f'Entry file not found: {entry_path}'}
        
        try:
            # Determine Python interpreter to use
            # Prefer app's own venv if it exists
            app_venv_python = app_path / 'venv' / 'bin' / 'python'
            if app_venv_python.exists():
                python_path = str(app_venv_python)
            else:
                # Fall back to system Python
                python_path = sys.executable
            
            # Build command with arguments
            cmd = [python_path, str(entry_path), '--host', host, '--port', str(port)]
            
            # Start process in background
            process = subprocess.Popen(
                cmd,
                cwd=str(app_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True  # Detach from parent process
            )
            
            # Write PID file
            pid_file = self._get_pid_file(app_id)
            pid_file.write_text(str(process.pid))
            
            # Wait a moment for the app to start
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is not None:
                # Process exited, get error output
                _, stderr = process.communicate()
                return {
                    'success': False,
                    'error': f'App failed to start: {stderr.decode()[:500]}'
                }
            
            return {
                'success': True,
                'message': f'App "{app_id}" started successfully',
                'pid': process.pid,
                'url': self.get_app_url(app_id)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to start app: {str(e)}'}
    
    def stop_app(self, app_id: str) -> dict:
        """
        Stop an application.
        
        Args:
            app_id: The application identifier
            
        Returns:
            Result dictionary with success status and message
        """
        app_config = self.get_app_config(app_id)
        if app_config is None:
            return {'success': False, 'error': f'App "{app_id}" not found'}
        
        status = self.get_app_status(app_id)
        if not status or not status['running']:
            return {
                'success': True,
                'message': f'App "{app_id}" is not running',
                'already_stopped': True
            }
        
        pid = status.get('pid')
        if pid:
            try:
                # Send SIGTERM for graceful shutdown
                os.kill(pid, signal.SIGTERM)
                
                # Wait for process to terminate
                for _ in range(10):  # Wait up to 5 seconds
                    if not psutil.pid_exists(pid):
                        break
                    time.sleep(0.5)
                
                # Force kill if still running
                if psutil.pid_exists(pid):
                    os.kill(pid, signal.SIGKILL)
                
                # Remove PID file
                pid_file = self._get_pid_file(app_id)
                pid_file.unlink(missing_ok=True)
                
                return {
                    'success': True,
                    'message': f'App "{app_id}" stopped successfully'
                }
                
            except ProcessLookupError:
                # Process already terminated
                pid_file = self._get_pid_file(app_id)
                pid_file.unlink(missing_ok=True)
                return {
                    'success': True,
                    'message': f'App "{app_id}" was already stopped'
                }
            except Exception as e:
                return {'success': False, 'error': f'Failed to stop app: {str(e)}'}
        
        return {'success': False, 'error': 'No PID found for running app'}
    
    def restart_app(self, app_id: str) -> dict:
        """
        Restart an application.
        
        Args:
            app_id: The application identifier
            
        Returns:
            Result dictionary with success status and message
        """
        stop_result = self.stop_app(app_id)
        if not stop_result['success'] and 'already_stopped' not in stop_result:
            return stop_result
        
        # Brief pause between stop and start
        time.sleep(1)
        
        return self.start_app(app_id)
