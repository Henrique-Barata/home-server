# Data & Persistence

## Database

**Engine**: SQLite 3  
**Location**: `data/expenses.db`

### Why SQLite?
- No separate database server needed
- File-based, easy to backup (copy the file)
- Perfect for 1-2 users with minimal concurrent access
- Zero configuration

## Schema

### Variable Expense Tables

All share common structure:

```sql
-- food_expenses, other_expenses
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount REAL NOT NULL DEFAULT 0,
    paid_by TEXT NOT NULL,
    expense_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- utility_expenses (adds utility_type)
(
    ... common fields ...,
    utility_type TEXT NOT NULL
)

-- stuff_expenses (adds stuff_type)
(
    ... common fields ...,
    stuff_type TEXT NOT NULL
)
```

### Fixed Expenses

```sql
fixed_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_type TEXT NOT NULL,       -- e.g., "Rent"
    amount REAL NOT NULL DEFAULT 0,
    effective_date DATE NOT NULL,     -- When this value starts applying
    paid_by TEXT,
    created_at DATE DEFAULT CURRENT_DATE
)

fixed_expense_payments (
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
```

### Settlements

```sql
settlements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payer TEXT NOT NULL,
    receiver TEXT NOT NULL,
    amount REAL NOT NULL,
    settlement_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Expense Log (Audit Trail)

```sql
expense_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,           -- added, updated, deleted, etc.
    expense_type TEXT NOT NULL,     -- food, utility, stuff, etc.
    expense_id INTEGER,
    paid_by TEXT,
    amount REAL,
    expense_date DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Lookup Tables

```sql
stuff_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)

fixed_expense_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
```

## Database Access Pattern

### Thread-Safety
- `Database` class uses thread-local storage for connections
- Each thread gets its own connection (no pooling overhead)
- Safe for Flask's threaded request handling

### Transactions
```python
with db.transaction() as conn:
    # Operations auto-commit on success
    # Auto-rollback on exception
```

### Query Methods
- `db.execute(sql, params)` - Execute and return cursor
- `db.fetch_one(sql, params)` - Single row as dict
- `db.fetch_all(sql, params)` - All rows as list of dicts

## Initialization & Migrations

### Initial Setup
```bash
python init_db.py
```
Creates all tables if they don't exist.

### Migrations
Manual migration scripts exist for schema changes:
- `migrate_add_expense_logs.py` - Added audit logging
- `migrate_add_fixed_payments.py` - Added payment tracking

**Pattern**: Check if table/column exists, then alter if needed.

## Backup Strategy

Simply copy `data/expenses.db` to backup location. SQLite databases are single files.
