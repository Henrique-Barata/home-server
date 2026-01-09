# Domain Concepts

## Users

The application tracks expenses for two fixed users:
- **Henrique**
- **Carlota**

Users are defined in configuration, not stored in database. This is intentional—the app is designed for a specific household, not multi-tenancy.

## Expense Categories

### Variable Expenses
Expenses that occur irregularly with varying amounts.

| Category | Table | Key Fields |
|----------|-------|------------|
| **Food** | `food_expenses` | name, amount, paid_by, date |
| **Utilities** | `utility_expenses` | name, amount, paid_by, date, utility_type |
| **Stuff** | `stuff_expenses` | name, amount, paid_by, date, stuff_type |
| **Other** | `other_expenses` | name, amount, paid_by, date |

### Fixed Expenses
Recurring monthly expenses with a defined amount.

- **Rent**: Monthly housing cost
- **Internet**: Monthly internet bill (can be managed as fixed or utility)

Fixed expenses use an **effective date** system:
- A new value takes effect from the specified date forward
- Previous values are preserved for historical accuracy
- Example: Rent increased from €800 to €850 effective May 2026

### Settlements
Balance payments between users.

When shared expenses result in one person paying more than their fair share, the other person can "settle" by paying the difference.

**Fields**: payer, receiver, amount, date, notes

## Paid By

Every expense records who paid. This enables:
- Per-person spending summaries
- Settlement calculations
- Fair expense splitting

## Stuff Types

User-defined categories for "Stuff" expenses.

**Examples**: Electronics, Clothing, Home Decor, Books

Users can add new types through the UI at `/stuff/types`.

## Time Model

- All expenses have an `expense_date` (when incurred)
- All records have a `created_at` timestamp (when logged)
- Dashboard groups by month/year
- Fixed expenses have `effective_date` (when new values apply)

## Currency

All amounts are assumed to be in **Euros (€)**. No multi-currency support.
