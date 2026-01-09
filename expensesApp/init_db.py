"""
Database Initialization Script
------------------------------
Creates all required tables for the expense tracker.
Run this script before first use: python init_db.py
"""
import sqlite3
import sys
from pathlib import Path

# Import configuration
sys.path.insert(0, str(Path(__file__).parent))

# Check if configuration exists, run setup if needed
try:
    from setup_config import check_and_setup
    if not check_and_setup():
        print("\n❌ Configuration required to initialize the database.")
        sys.exit(1)
except Exception as e:
    print(f"\n⚠️  Setup check failed: {e}")
    print("Continuing with database initialization...")

from app.config import get_config


def init_database():
    """Initialize the SQLite database with all required tables."""
    
    config = get_config()
    config.ensure_directories()
    
    db_path = config.DATABASE_PATH
    
    print(f"Initializing database at: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # === Food Expenses Table ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL DEFAULT 0,
            paid_by TEXT NOT NULL,
            expense_date DATE NOT NULL,
            individual_only INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # === Utility Expenses Table ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utility_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL DEFAULT 0,
            paid_by TEXT NOT NULL,
            expense_date DATE NOT NULL,
            utility_type TEXT NOT NULL,
            individual_only INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # === Stuff Expenses Table ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stuff_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL DEFAULT 0,
            paid_by TEXT NOT NULL,
            expense_date DATE NOT NULL,
            stuff_type TEXT NOT NULL,
            individual_only INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # === Other Expenses Table ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS other_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL DEFAULT 0,
            paid_by TEXT NOT NULL,
            expense_date DATE NOT NULL,
            individual_only INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # === Fixed Expenses Table ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fixed_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_type TEXT NOT NULL,
            amount REAL NOT NULL DEFAULT 0,
            effective_date DATE NOT NULL,
            paid_by TEXT,
            created_at DATE DEFAULT CURRENT_DATE
        )
    """)
    
    # === Fixed Expense Payments Table (tracks paid/unpaid status per month) ===
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
    
    # === Stuff Types Table ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stuff_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    
    # === Fixed Expense Types Table (for custom types) ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fixed_expense_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    
    # === Settlements Table (balance payments between users) ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settlements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payer TEXT NOT NULL,
            receiver TEXT NOT NULL,
            amount REAL NOT NULL DEFAULT 0,
            settlement_date DATE NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # === Expense Log Table (track all additions and modifications) ===
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
    
    # Create indexes for better query performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_food_date 
        ON food_expenses(expense_date)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_utility_date 
        ON utility_expenses(expense_date)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_stuff_date 
        ON stuff_expenses(expense_date)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_other_date 
        ON other_expenses(expense_date)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_fixed_type_date 
        ON fixed_expenses(expense_type, effective_date)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_fixed_payment_month 
        ON fixed_expense_payments(year, month)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_settlement_date 
        ON settlements(settlement_date)
    """)
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
    
    print("Database initialized successfully!")
    print("\nTables created:")
    print("  - food_expenses")
    print("  - utility_expenses")
    print("  - stuff_expenses")
    print("  - other_expenses")
    print("  - fixed_expenses")
    print("  - fixed_expense_types")
    print("  - stuff_types")
    print("  - settlements")
    print("\nYou can now run the application with: python run.py")


if __name__ == "__main__":
    init_database()
