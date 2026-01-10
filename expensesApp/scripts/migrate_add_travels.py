"""
Migration: Add Travels and Travel Expenses Tables
--------------------------------------------------
Adds support for tracking travel trips and their associated expenses.
Each travel can have multiple expense categories with individual expenses.
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_config


def migrate_add_travels():
    """Add travels and travel_expenses tables."""
    
    config = get_config()
    db_path = config.DATABASE_PATH
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        print("Run init_db.py first to initialize the database.")
        return False
    
    print(f"Adding travel tables to: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create travels table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS travels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create travel_expenses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS travel_expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                travel_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                amount REAL NOT NULL DEFAULT 0,
                paid_by TEXT NOT NULL,
                category TEXT NOT NULL,
                expense_date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(travel_id) REFERENCES travels(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_travel_date 
            ON travels(start_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_travel_expense_travel 
            ON travel_expenses(travel_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_travel_expense_category 
            ON travel_expenses(travel_id, category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_travel_expense_date 
            ON travel_expenses(expense_date)
        """)
        
        conn.commit()
        
        print("✅ Travel tables created successfully!")
        print("\nTravel Fields:")
        print("  - id: Unique identifier")
        print("  - name: Travel/trip name")
        print("  - start_date: Start date of the trip")
        print("  - end_date: End date of the trip")
        print("  - notes: Optional notes")
        print("  - created_at: When the record was created")
        print("\nTravel Expense Fields:")
        print("  - id: Unique identifier")
        print("  - travel_id: Reference to parent travel")
        print("  - name: Expense description")
        print("  - amount: Expense amount")
        print("  - paid_by: Who paid for this expense")
        print("  - category: Transportation, Accommodation, etc.")
        print("  - expense_date: Date of the expense")
        print("  - notes: Optional notes")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def check_tables_exist():
    """Check if travel tables already exist."""
    config = get_config()
    db_path = config.DATABASE_PATH
    
    if not db_path.exists():
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='travels'
    """)
    travels_exists = cursor.fetchone() is not None
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='travel_expenses'
    """)
    travel_expenses_exists = cursor.fetchone() is not None
    
    conn.close()
    
    return travels_exists and travel_expenses_exists


if __name__ == "__main__":
    if check_tables_exist():
        print("ℹ️ Travel tables already exist. No migration needed.")
    else:
        success = migrate_add_travels()
        if success:
            print("\n✅ Migration completed successfully!")
        else:
            print("\n❌ Migration failed!")
            sys.exit(1)
