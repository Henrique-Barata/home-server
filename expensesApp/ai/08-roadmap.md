# Roadmap & Known Gaps

## Potential Improvements

### High Value / Low Effort

| Feature | Description | Files Affected |
|---------|-------------|----------------|
| **CSRF Protection** | Add Flask-WTF for form security | All route files, templates |
| **Mobile CSS** | Responsive design improvements | `static/css/style.css` |
| **Password Hashing** | Use werkzeug security for password | `config.py`, `models/user.py` |
| **Quick Add** | Add expense from dashboard without navigating | `routes/dashboard.py`, new template |

### Medium Effort

| Feature | Description | Complexity |
|---------|-------------|------------|
| **Recurring Expenses** | Auto-create monthly variable expenses | New model, scheduler needed |
| **Category Budgets** | Set monthly limits per category | New model, dashboard integration |
| **Charts/Graphs** | Visual expense breakdown | JavaScript library, new routes |
| **Bulk Import** | Import from CSV/Excel | New route, parser logic |
| **Date Range Filter** | Filter expenses by custom date range | Dashboard enhancements |

### High Effort

| Feature | Description | Consideration |
|---------|-------------|---------------|
| **Multi-Household** | Support multiple households | Major refactor, tenant isolation |
| **User Accounts** | Separate accounts per person | Auth rewrite, permission system |
| **REST API** | JSON API for mobile/integration | New architecture layer |
| **Receipt Upload** | Attach images to expenses | File storage, new model |

## Technical Debt to Address

### Priority 1 (Security)
- [ ] Add CSRF tokens to all forms
- [ ] Hash password instead of plaintext comparison
- [ ] Add input sanitization/validation library

### Priority 2 (Maintainability)
- [ ] Add test suite (pytest)
- [ ] Add database migration tool (Alembic)
- [ ] Add logging for debugging

### Priority 3 (Quality of Life)
- [ ] Add error pages (404, 500)
- [ ] Add keyboard shortcuts
- [ ] Improve form validation feedback

## Migration Path Notes

### Adding New Expense Category
1. Create model in `app/models/`
2. Add table in `init_db.py`
3. Create blueprint in `app/routes/`
4. Register blueprint in `app/__init__.py`
5. Add templates in `app/templates/{category}/`
6. Update dashboard to include new category
7. Update export to include new category

### Changing Database Schema
1. Create migration script (`migrate_*.py`)
2. Check if change exists before applying
3. Update model to match new schema
4. Update `init_db.py` for fresh installs
5. Document migration in this file

## Version History

| Date | Change | Files |
|------|--------|-------|
| Initial | Core expense tracking | All |
| + Expense Logs | Added audit trail | `migrate_add_expense_logs.py`, `models/expense_log.py` |
| + Fixed Payments | Track paid status for fixed expenses | `migrate_add_fixed_payments.py`, `models/fixed_expense.py` |
