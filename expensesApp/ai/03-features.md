# Core Features

## 1. Dashboard

**Route**: `/`

The main view displaying:
- Monthly expense summary table (12 months)
- Columns: Fixed, Utilities, Food, Stuff, Other, Total
- Sortable by any column
- Year selector (view different years)
- Per-person yearly totals

### Sub-views
- **Month Detail** (`/dashboard/month/<year>/<month>`): All expenses for a specific month
- **Person Detail** (`/dashboard/person/<name>`): Expenses by a specific person
- **Settlement** (`/dashboard/settlement`): Record balance payments between users

---

## 2. Fixed Expenses

**Route Prefix**: `/fixed`

Fixed recurring monthly expenses (e.g., Rent, Internet).

### Key Behaviors
- **Effective date system**: Changes take effect from a specified month forward
- Historical values are preserved for accurate reporting
- Tracks paid/unpaid status per month

### Operations
- Add new fixed expense type
- Add/update value with effective date
- Mark month as paid/unpaid
- View payment history

---

## 3. Utilities

**Route Prefix**: `/utilities`

Variable monthly expenses for household services.

### Types
- Electricity
- Gas
- Water
- Internet (can overlap with Fixed if needed)

### Fields
- Name/description
- Amount
- Paid by (Henrique/Carlota)
- Expense date
- Utility type

---

## 4. Food Expenses

**Route Prefix**: `/food`

Grocery and dining expenses.

### Fields
- Name/description
- Amount
- Paid by
- Expense date

---

## 5. Stuff Expenses

**Route Prefix**: `/stuff`

Items and purchases with custom categorization.

### Features
- User-defined categories (StuffType)
- Manage categories via `/stuff/types`

### Fields
- Name/description
- Amount
- Paid by
- Expense date
- Stuff type (category)

---

## 6. Other Expenses

**Route Prefix**: `/other`

Miscellaneous expenses that don't fit other categories.

### Fields
- Name/description
- Amount
- Paid by
- Expense date

---

## 7. Expense Log (Audit Trail)

**Route Prefix**: `/log`

Chronological log of all expense operations.

### Tracked Actions
- `added` - New expense created
- `updated` - Expense modified
- `deleted` - Expense removed
- `marked_paid` - Fixed expense paid
- `marked_unpaid` - Fixed expense unpaid

### Fields Logged
- Action type
- Expense type (food, utility, etc.)
- Expense ID
- Amount
- Paid by
- Description
- Timestamp

---

## 8. Excel Export

**Route Prefix**: `/export`

Generate Excel files for external analysis.

### Features
- Google Sheets compatible format
- Multiple worksheets:
  - Monthly Summary
  - Per-person breakdown
  - Detailed expense lists
- Year filtering
- Styled headers and currency formatting

---

## 9. Authentication

**Route Prefix**: `/auth`

Simple password-based authentication.

### Behavior
- Single shared password (not per-user)
- Session-based (Flask-Login)
- 24-hour session lifetime
- All routes except `/auth/login` require authentication
