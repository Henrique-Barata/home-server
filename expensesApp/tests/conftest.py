"""
Pytest Configuration and Fixtures
----------------------------------
Shared fixtures for testing the expense tracker application.
"""
import os
import sys
import tempfile
import sqlite3
from datetime import date, datetime
from pathlib import Path

import pytest

# Add the app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.config import Config
from app.models.database import db, Database


class TestConfig(Config):
    """Test configuration with in-memory/temp database."""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    APP_PASSWORD = 'test-password'
    USERS = ['TestUser1', 'TestUser2']
    UTILITY_TYPES = ['Electricity', 'Water', 'Gas']
    FIXED_EXPENSE_TYPES = ['Rent', 'Internet']


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    # Create a temporary directory for test data
    temp_dir = tempfile.mkdtemp()
    TestConfig.DATA_DIR = Path(temp_dir)
    TestConfig.DATABASE_PATH = Path(temp_dir) / 'test_expenses.db'
    TestConfig.EXPORT_DIR = Path(temp_dir) / 'exports'
    TestConfig.EXPORT_DIR.mkdir(exist_ok=True)
    
    app = create_app(TestConfig)
    
    # Initialize test database
    with app.app_context():
        init_test_database(TestConfig.DATABASE_PATH)
    
    yield app
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def authenticated_client(app, client):
    """Create authenticated test client."""
    with client.session_transaction() as sess:
        sess['_user_id'] = 'local_user'
    return client


@pytest.fixture(scope='function')
def runner(app):
    """Create CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def test_db(app):
    """
    Provide a clean database for each test.
    Clears all tables before each test.
    """
    with app.app_context():
        clear_test_data()
        yield db
        # Clear after test as well
        clear_test_data()


def init_test_database(db_path: Path):
    """Initialize the test database with schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Food expenses table
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
    
    # Utility expenses table
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
    
    # Stuff expenses table
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
    
    # Other expenses table
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
    
    # Fixed expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fixed_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_type TEXT NOT NULL,
            amount REAL NOT NULL DEFAULT 0,
            effective_date DATE NOT NULL,
            paid_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Fixed expense types
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fixed_expense_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    
    # Stuff types
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stuff_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    
    # Settlements table
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
    
    # Expense logs table
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
    
    # Reimbursements table
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
    
    # Travels table
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
    
    # Travel expenses table
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
    
    # Budgets table
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
    
    # Fixed expense payments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fixed_expense_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fixed_expense_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            is_paid INTEGER DEFAULT 0,
            paid_by TEXT,
            paid_date DATE,
            UNIQUE(fixed_expense_id, year, month)
        )
    """)
    
    conn.commit()
    conn.close()


def clear_test_data():
    """Clear all data from test tables."""
    tables = [
        'food_expenses', 'utility_expenses', 'stuff_expenses', 'other_expenses',
        'fixed_expenses', 'fixed_expense_types', 'stuff_types', 'settlements',
        'expense_logs', 'reimbursements', 'travels', 'travel_expenses', 
        'budgets', 'fixed_expense_payments'
    ]
    
    for table in tables:
        try:
            db.execute(f"DELETE FROM {table}")
        except Exception:
            pass  # Table might not exist
