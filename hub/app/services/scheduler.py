"""
Auto-Shutdown Scheduler Service
-------------------------------
Monitors app activity and shuts down idle apps after configurable timeout.
"""
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from .logger import get_scheduler_logger

logger = get_scheduler_logger()


class AppActivityTracker:
    """
    Tracks app activity and manages auto-shutdown.
    
    Monitors the last access time for each app and stops idle apps
    after a configurable timeout period.
    """
    
    def __init__(
        self,
        app_manager,
        default_idle_timeout_minutes: int = 15,
        check_interval_seconds: int = 60
    ):
        """
        Initialize the activity tracker.
        
        Args:
            app_manager: AppManager instance to control apps
            default_idle_timeout_minutes: Minutes of inactivity before shutdown
            check_interval_seconds: How often to check for idle apps
        """
        self.app_manager = app_manager
        self.default_idle_timeout = timedelta(minutes=default_idle_timeout_minutes)
        self.check_interval = check_interval_seconds
        
        # Track last activity time per app
        self._last_activity: Dict[str, datetime] = {}
        self._app_timeouts: Dict[str, timedelta] = {}
        
        # Scheduler thread
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        logger.info(
            f"AppActivityTracker initialized with {default_idle_timeout_minutes}m "
            f"default timeout, {check_interval_seconds}s check interval"
        )
    
    def record_activity(self, app_id: str) -> None:
        """
        Record activity for an app (reset idle timer).
        
        Args:
            app_id: The application identifier
        """
        with self._lock:
            self._last_activity[app_id] = datetime.now()
            logger.debug(f"Activity recorded for app '{app_id}'")
    
    def set_app_timeout(self, app_id: str, timeout_minutes: int) -> None:
        """
        Set a custom timeout for a specific app.
        
        Args:
            app_id: The application identifier
            timeout_minutes: Minutes of inactivity before shutdown
        """
        with self._lock:
            self._app_timeouts[app_id] = timedelta(minutes=timeout_minutes)
            logger.info(f"Custom timeout of {timeout_minutes}m set for app '{app_id}'")
    
    def get_app_timeout(self, app_id: str) -> timedelta:
        """Get the timeout for an app (custom or default)."""
        return self._app_timeouts.get(app_id, self.default_idle_timeout)
    
    def get_idle_time(self, app_id: str) -> Optional[timedelta]:
        """
        Get how long an app has been idle.
        
        Returns:
            Idle duration or None if no activity recorded
        """
        with self._lock:
            last_active = self._last_activity.get(app_id)
            if last_active is None:
                return None
            return datetime.now() - last_active
    
    def start(self) -> None:
        """Start the auto-shutdown scheduler."""
        if self._running:
            logger.warning("Scheduler already running")
            return
        
        self._running = True
        self._thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True,
            name="AppAutoShutdown"
        )
        self._thread.start()
        logger.info("Auto-shutdown scheduler started")
    
    def stop(self) -> None:
        """Stop the auto-shutdown scheduler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        logger.info("Auto-shutdown scheduler stopped")
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop - checks for idle apps periodically."""
        while self._running:
            try:
                self._check_idle_apps()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
            
            # Sleep in small intervals to allow quick shutdown
            for _ in range(self.check_interval):
                if not self._running:
                    break
                time.sleep(1)
    
    def _check_idle_apps(self) -> None:
        """Check all apps and stop idle ones."""
        apps = self.app_manager.get_all_apps()
        
        for app in apps:
            app_id = app['id']
            status = app.get('status', {})
            
            if not status.get('running', False):
                continue
            
            idle_time = self.get_idle_time(app_id)
            timeout = self.get_app_timeout(app_id)
            
            # If no activity recorded, record now (first check)
            if idle_time is None:
                self.record_activity(app_id)
                continue
            
            # Check if idle timeout exceeded
            if idle_time > timeout:
                logger.info(
                    f"App '{app_id}' idle for {idle_time.total_seconds() / 60:.1f}m "
                    f"(timeout: {timeout.total_seconds() / 60:.1f}m) - stopping"
                )
                
                try:
                    result = self.app_manager.stop_app(app_id)
                    if result.get('success'):
                        logger.info(f"App '{app_id}' auto-stopped due to inactivity")
                        # Clear activity record
                        with self._lock:
                            self._last_activity.pop(app_id, None)
                    else:
                        logger.error(f"Failed to auto-stop app '{app_id}': {result}")
                except Exception as e:
                    logger.error(f"Error auto-stopping app '{app_id}': {e}", exc_info=True)
    
    def get_status(self) -> dict:
        """Get scheduler status for monitoring."""
        with self._lock:
            apps_status = {}
            for app_id, last_active in self._last_activity.items():
                idle_time = datetime.now() - last_active
                timeout = self.get_app_timeout(app_id)
                apps_status[app_id] = {
                    'last_activity': last_active.isoformat(),
                    'idle_seconds': idle_time.total_seconds(),
                    'timeout_seconds': timeout.total_seconds(),
                    'time_until_shutdown': max(0, (timeout - idle_time).total_seconds())
                }
        
        return {
            'running': self._running,
            'default_timeout_minutes': self.default_idle_timeout.total_seconds() / 60,
            'check_interval_seconds': self.check_interval,
            'apps': apps_status
        }
