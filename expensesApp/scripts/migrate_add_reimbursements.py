"""
Migration: Add Reimbursements Table
-----------------------------------
Adds support for tracking reimbursements (refunds) of expenses.
A reimbursement is when someone returns an item and gets money back.
The reimbursement amount is NOT divided among participants - it reduces
the original payer's expense.

Example:
  - Alice buys a table for $100, adds it as shared expense
  - The $100 is divided between Alice and Bob (50/50)
  - Alice returns the table and gets $100 back
  - Alice adds a $100 reimbursement for the table
  - The reimbursement reduces Alice's account and Bob must pay Alice their share
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_config


def migrate_add_reimbursements():
    """Add reimbursements table to track refunds."""
    
    config = get_config()
    db_path = config.DATABASE_PATH
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        print("Run init_db.py first to initialize the database.")
        return False
    
    print(f"Adding reimbursements table to: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create reimbursements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reimbursements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL DEFAULT 0,
                reimbursed_to TEXT NOT NULL,
                original_expense_type TEXT,
                original_expense_id INTEGER,
                reimbursement_date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_reimbursement_date 
            ON reimbursements(reimbursement_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_reimbursement_person 
            ON reimbursements(reimbursed_to)
        """)
        
        conn.commit()
        
        print("✅ Reimbursements table created successfully!")
        print("\nReimbursement Fields:")
        print("  - id: Unique identifier")
        print("  - name: Description of what was reimbursed (e.g., 'Table refund')")
        print("  - amount: Amount of reimbursement")
        print("  - reimbursed_to: Person who received the reimbursement")
        print("  - original_expense_type: Type of original expense (food, stuff, etc)")
        print("  - original_expense_id: ID of original expense (if known)")
        print("  - reimbursement_date: Date of reimbursement")
        print("  - notes: Optional notes")
        
        return True
        
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print("ℹ️  Reimbursements table already exists")
            return True
        else:
            print(f"❌ Migration failed: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    success = migrate_add_reimbursements()
    sys.exit(0 if success else 1)
