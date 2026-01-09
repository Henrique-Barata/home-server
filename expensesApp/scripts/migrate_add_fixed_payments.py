"""
Migration script to add fixed expense payments tracking table.
This adds the ability to track paid/unpaid status for fixed expenses per month.
"""
import sqlite3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_config


def migrate():
    """Add fixed_expense_payments table to existing database."""
    
    config = get_config()
    db_path = config.DATABASE_PATH
    
    print(f"Migrating database at: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create the fixed expense payments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fixed_expense_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fixed_expense_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            is_paid INTEGER DEFAULT 0,
            paid_by TEXT,
            paid_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(fixed_expense_id) REFERENCES fixed_expenses(id) ON DELETE CASCADE,
            UNIQUE(fixed_expense_id, year, month)
        )
    """)
    
    # Create index
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_fixed_payment_month 
        ON fixed_expense_payments(year, month)
    """)
    
    conn.commit()
    conn.close()
    
    print("✓ Migration completed successfully!")
    print("  - Added fixed_expense_payments table")
    print("  - Added index on (year, month)")


if __name__ == '__main__':
    migrate()
