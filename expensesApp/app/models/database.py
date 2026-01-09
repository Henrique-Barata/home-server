"""
Database Module
---------------
SQLite database management with connection pooling and thread safety.
Designed for minimal resource usage.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from threading import local

from ..config import get_config


class Database:
    """
    Thread-safe SQLite database manager.
    Uses connection per thread pattern for safety without connection pooling overhead.
    """
    
    _local = local()
    
    def __init__(self, db_path: Path = None):
        """Initialize database with path."""
        self.db_path = db_path or get_config().DATABASE_PATH
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get thread-local database connection.
        Creates new connection if none exists for current thread.
        """
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            # Return rows as dictionaries for easier access
            self._local.connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self._local.connection.execute("PRAGMA foreign_keys = ON")
        return self._local.connection
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        Automatically commits on success, rolls back on error.
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def execute(self, query: str, params: tuple = None):
        """Execute a query and return cursor."""
        conn = self.get_connection()
        if params:
            return conn.execute(query, params)
        return conn.execute(query)
    
    def execute_many(self, query: str, params_list: list):
        """Execute a query with multiple parameter sets."""
        conn = self.get_connection()
        return conn.executemany(query, params_list)
    
    def fetch_one(self, query: str, params: tuple = None) -> dict:
        """Fetch a single row as dictionary."""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = None) -> list:
        """Fetch all rows as list of dictionaries."""
        cursor = self.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close the thread-local connection."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None


# Global database instance
db = Database()
