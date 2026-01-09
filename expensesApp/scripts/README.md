# Scripts

This folder contains utility and migration scripts for the Expenses Tracker.

## Migration Scripts

Database migration scripts for schema changes:

- **`migrate_add_expense_logs.py`** - Adds expense logging functionality
- **`migrate_add_fixed_payments.py`** - Adds fixed payment tracking
- **`migrate_add_individual_only.py`** - Adds individual-only expense flag

**Usage:**
```bash
python scripts/migrate_<name>.py
```

⚠️ **Important**: Always backup your database before running migrations!
```bash
cp data/expenses.db data/expenses.db.backup
```

## Utility Scripts

- **`verify_before_commit.py`** - Pre-commit verification script
  - Checks for personal data leaks
  - Validates .gitignore
  - Ensures required files exist

**Usage:**
```bash
python scripts/verify_before_commit.py
```

Run this before committing to ensure no sensitive data is included.

## Creating New Migrations

When adding new database features:

1. Create a new migration script: `migrate_<feature_name>.py`
2. Include rollback instructions in comments
3. Test on a backup database first
4. Update this README with the new migration

## Safety Guidelines

✅ **DO:**
- Backup database before migrations
- Test migrations on sample data
- Document what each migration does
- Check migration script into git

❌ **DON'T:**
- Run migrations without backups
- Modify migration scripts after they've been run in production
- Commit database files or personal data
