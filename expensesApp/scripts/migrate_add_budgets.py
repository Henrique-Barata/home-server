#!/usr/bin/env python3
"""
Migration Script: Add Budgets Table
------------------------------------
Adds the budgets table to existing databases.

Run this script if you have an existing database that was created
before the budget feature was added.

Usage:
    python scripts/migrate_add_budgets.py
"""
import os
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_config


def migrate():
    """Add budgets table to existing database."""
    config = get_config()
    db_path = config.DATABASE_PATH
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Run init_db.py to create a new database instead.")
        return False
    
    print(f"Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='budgets'
        """)
        if cursor.fetchone():
            print("✓ budgets table already exists")
        else:
            # Create budgets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    monthly_limit REAL NOT NULL DEFAULT 0,
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    notes TEXT,
                    UNIQUE(category, year, month)
                )
            """)
            print("✓ Created budgets table")
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_budget_month 
            ON budgets(year, month)
        """)
        print("✓ Created idx_budget_month index")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_budget_category 
            ON budgets(category, year, month)
        """)
        print("✓ Created idx_budget_category index")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
