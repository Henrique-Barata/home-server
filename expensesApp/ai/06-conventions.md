# Coding Conventions & Patterns

## Python Style

- **Version**: Python 3.10+ assumed
- **Style Guide**: PEP 8 compliant
- **Type Hints**: Used in method signatures
- **Docstrings**: Module and class level documentation

## File Organization

### Models
- One file per domain concept
- Class contains all table operations (Active Record)
- `from_row()` factory method for DB rows
- `save()` handles insert vs update logic

### Routes (Blueprints)
- One file per expense category
- Blueprint named with `bp` variable
- URL prefix matches filename (e.g., `/food` for `food.py`)
- All routes decorated with `@login_required`

### Templates
- Organized in subdirectories matching blueprint names
- `base.html` provides common layout
- Form templates named `form.html`
- List templates named `index.html`

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | snake_case | `fixed_expense.py` |
| Classes | PascalCase | `FixedExpense` |
| Functions | snake_case | `get_by_month()` |
| Routes | snake_case | `@bp.route('/add')` |
| Templates | snake_case | `month_detail.html` |
| DB Tables | snake_case | `food_expenses` |
| DB Columns | snake_case | `expense_date` |

## Database Conventions

### Table Names
- Plural nouns: `expenses`, `settlements`
- Prefixed by category: `food_expenses`, `utility_expenses`

### Column Names
- `id` - Always INTEGER PRIMARY KEY AUTOINCREMENT
- `*_date` suffix for dates: `expense_date`, `paid_date`
- `*_at` suffix for timestamps: `created_at`
- Boolean as INTEGER: `is_paid` (0/1)

### Foreign Keys
- Named as `{table}_id`: `fixed_expense_id`
- Always with ON DELETE CASCADE where appropriate

## Route Patterns

### Standard CRUD
```python
@bp.route('/')                    # List all
@bp.route('/add', methods=['GET', 'POST'])   # Create form & handler
@bp.route('/edit/<int:id>', methods=['GET', 'POST'])  # Edit form & handler
@bp.route('/delete/<int:id>', methods=['POST'])  # Delete handler
```

### Form Handling
- GET displays form
- POST processes submission
- Flash messages for feedback
- Redirect after successful POST

## Error Handling

- Database errors: Caught in model methods, re-raised
- User errors: Flash messages with `flash()`
- No custom error pages (uses Flask defaults)

## Configuration Access

```python
from ..config import get_config
config = get_config()
```

Never import `Config` class directly; use `get_config()` function.

## Logging

- Minimal logging for low-resource environment
- Expense operations logged to `expense_logs` table
- Python logging set to WARNING level
