# Database Migrations Guide

This application uses **Alembic** for database migrations. Since the app uses raw SQL queries (Active Record pattern) instead of SQLAlchemy ORM, migrations must be written manually.

## Quick Start

### For New Installations

If you're setting up a fresh database:

```bash
# Run all migrations to create the schema
alembic upgrade head
```

### For Existing Databases

If you have an existing database created with `init_db.py`:

```bash
# Stamp the database as already having the initial migration
alembic stamp 001_initial
```

This tells Alembic that your database is already at this version.

## Common Commands

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Upgrade to latest version
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Create a new migration
alembic revision -m "add new feature"
```

## Creating New Migrations

Since we don't use SQLAlchemy ORM, autogenerate won't work. Create migrations manually:

```bash
alembic revision -m "add new column to food_expenses"
```

Then edit the generated file in `alembic/versions/`:

```python
def upgrade() -> None:
    op.add_column('food_expenses', 
        sa.Column('new_column', sa.Text())
    )

def downgrade() -> None:
    op.drop_column('food_expenses', 'new_column')
```

## SQLite Limitations

SQLite has limited ALTER TABLE support. For complex changes, use batch mode:

```python
def upgrade() -> None:
    with op.batch_alter_table('food_expenses') as batch_op:
        batch_op.add_column(sa.Column('new_col', sa.Text()))
        batch_op.drop_column('old_col')
```

## Migration Best Practices

1. **Always test migrations** on a copy of production data before deploying
2. **Backup your database** before running migrations
3. **Write both upgrade and downgrade** functions
4. **Keep migrations small and focused** on one change
5. **Never edit a migration** that has been applied to production

## Backup Before Migration

```bash
# Create backup
cp data/expenses.db data/expenses_backup_$(date +%Y%m%d).db

# Run migration
alembic upgrade head

# If something goes wrong, restore
cp data/expenses_backup_*.db data/expenses.db
```

## Troubleshooting

### "Table already exists"
Your database already has the tables. Use `alembic stamp` to mark it as migrated:
```bash
alembic stamp 001_initial
```

### "Can't locate revision"
The alembic_version table might be corrupted. Check:
```sql
SELECT * FROM alembic_version;
```

### Foreign key errors
SQLite requires special handling for foreign keys. Enable with:
```python
op.execute("PRAGMA foreign_keys=ON")
```
