# Architecture & Tech Stack

## Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Web Framework** | Flask 3.0 | Minimal overhead, proven, simple |
| **Database** | SQLite | File-based, no server needed, perfect for 1-2 users |
| **Authentication** | Flask-Login 0.6.3 | Simple session-based auth |
| **Templates** | Jinja2 (Flask built-in) | Server-side rendering |
| **Styling** | Vanilla CSS | No build tools, fast loading |
| **Excel Export** | openpyxl 3.1.2 | Google Sheets compatible |

## Project Structure

```
expensesApp/
├── app/                      # Application package
│   ├── __init__.py           # App factory (create_app)
│   ├── config.py             # Configuration class
│   ├── models/               # Database models (Active Record pattern)
│   │   ├── database.py       # Thread-safe SQLite manager
│   │   ├── expense.py        # Base + specific expense models
│   │   ├── fixed_expense.py  # Recurring monthly expenses
│   │   ├── settlement.py     # Balance payments between users
│   │   ├── expense_log.py    # Audit trail for all operations
│   │   ├── stuff_type.py     # Custom categories for items
│   │   └── user.py           # Flask-Login user model
│   ├── routes/               # Blueprint route handlers
│   │   ├── auth.py           # Login/logout
│   │   ├── dashboard.py      # Main views, summaries
│   │   ├── food.py           # Food expense CRUD
│   │   ├── utilities.py      # Utility expense CRUD
│   │   ├── fixed.py          # Fixed expense management
│   │   ├── stuff.py          # Item expense CRUD
│   │   ├── other.py          # Miscellaneous expense CRUD
│   │   ├── log.py            # Audit log viewer
│   │   └── export.py         # Excel export
│   ├── templates/            # Jinja2 HTML templates
│   └── static/css/           # Stylesheets
├── data/                     # SQLite database file
├── exports/                  # Generated Excel files
├── init_db.py                # Database initialization script
├── migrate_*.py              # Database migration scripts
├── run.py                    # Application entry point
└── requirements.txt          # Python dependencies
```

## Architectural Patterns

### Application Factory
- `create_app()` function in `app/__init__.py`
- Enables testing with different configurations
- Blueprints registered during app creation

### Active Record Pattern (Models)
- Each model class manages its own table
- CRUD operations as instance/class methods
- No ORM overhead (raw SQL for performance)

### Thread-Safe Database Access
- `Database` class with thread-local connections
- Context manager for transactions (`with db.transaction()`)
- Automatic commit/rollback

### Blueprint Organization
- One blueprint per expense category
- Clear URL prefixes (e.g., `/food`, `/utilities`, `/fixed`)
- Login required on all routes except auth

## Data Flow

```
User Request
    ↓
Flask Route (Blueprint)
    ↓
Model Method (SQL Query)
    ↓
Database.py (Thread-safe connection)
    ↓
SQLite File
```

## Configuration

Configuration loaded from `app/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `SECRET_KEY` | env or fallback | Flask session secret |
| `DATABASE_PATH` | `data/expenses.db` | SQLite file location |
| `APP_PASSWORD` | env or fallback | Shared login password |
| `USERS` | `["Henrique", "Carlota"]` | Allowed payer names |
| `UTILITY_TYPES` | Electricity, Gas, Water, Internet | Utility categories |
| `FIXED_EXPENSE_TYPES` | Rent, Internet | Fixed expense categories |
