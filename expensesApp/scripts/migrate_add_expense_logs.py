"""
Migration script to add expense log table.
This adds the ability to track all expense additions and modifications.
"""
import sqlite3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_config


def migrate():
    """Add expense_logs table to existing database."""
    
    config = get_config()
    db_path = config.DATABASE_PATH
    
    print(f"Migrating database at: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create the expense logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            expense_type TEXT NOT NULL,
            expense_id INTEGER,
            paid_by TEXT,
            amount REAL,
            expense_date DATE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_log_date 
        ON expense_logs(created_at)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_log_type 
        ON expense_logs(expense_type)
    """)
    
    conn.commit()
    conn.close()
    
    print("✓ Migration completed successfully!")
    print("  - Added expense_logs table")
    print("  - Added indexes on (created_at) and (expense_type)")


if __name__ == '__main__':
    migrate()
