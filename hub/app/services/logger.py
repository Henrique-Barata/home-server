"""
Hub Logging Service
-------------------
Centralized logging configuration with file rotation.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    log_dir: Optional[Path] = None,
    level: int = logging.INFO,
    max_bytes: int = 5 * 1024 * 1024,  # 5MB
    backup_count: int = 3
) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name: Logger name (usually the module name)
        log_dir: Directory for log files. Defaults to hub/logs/
        level: Logging level
        max_bytes: Max size per log file before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent / 'logs'
    
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f'{name}.log'
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# Pre-configured loggers for hub components
def get_hub_logger() -> logging.Logger:
    """Get the main hub logger."""
    return setup_logger('hub')


def get_app_manager_logger() -> logging.Logger:
    """Get the app manager logger."""
    return setup_logger('app_manager')


def get_api_logger() -> logging.Logger:
    """Get the API routes logger."""
    return setup_logger('api')


def get_scheduler_logger() -> logging.Logger:
    """Get the scheduler/auto-shutdown logger."""
    return setup_logger('scheduler')
