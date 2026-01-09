"""
Database Migration: Add individual_only flag to expenses
---------------------------------------------------------
Allows tracking expenses that count toward total but don't split between users.
Example: Individual video game purchase
"""
import sqlite3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_config


def migrate_database():
    """Add individual_only column to all expense tables."""
    
    config = get_config()
    db_path = config.DATABASE_PATH
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    print(f"Migrating database at: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    tables_to_migrate = [
        'food_expenses',
        'utility_expenses',
        'stuff_expenses',
        'other_expenses'
    ]
    
    for table in tables_to_migrate:
        # Check if column already exists
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'individual_only' not in columns:
            print(f"Adding individual_only column to {table}...")
            cursor.execute(f"""
                ALTER TABLE {table}
                ADD COLUMN individual_only INTEGER DEFAULT 0
            """)
        else:
            print(f"Column individual_only already exists in {table}")
    
    conn.commit()
    conn.close()
    print("Migration completed successfully!")


if __name__ == '__main__':
    migrate_database()
