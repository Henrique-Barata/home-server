# New Features: Individual Expenses & Reimbursements

## Overview

Two new features have been added to the Expenses App:

1. **Individual Expenses** - Expenses that are NOT divided among participants
2. **Reimbursements** - Track refunds and money received back

## Individual Expenses

### What is an Individual Expense?

An individual expense is an expense that:
- **Counts toward the total** balance
- **Is NOT divided** among other participants
- **Only affects the payer's account**

### Use Cases

- Personal items purchased for yourself
- Reimbursements for someone else's purchase
- Items that shouldn't be split
- Deposits or advances

### How It Works

When you add an individual expense:

```
Example: Alice buys a $50 personal item

Without individual_only flag:
- Alice's balance: -$25 (her share)
- Bob's balance: +$25 (his share to pay)
- Total: $50 split equally

With individual_only flag:
- Alice's balance: -$50 (full amount)
- Bob's balance: $0 (not affected)
- Total: $50 (not split)
```

### Using Individual Expenses

1. Go to any expense type (Food, Utilities, Stuff, Other)
2. Click "Add Expense"
3. Check the "Personal/Individual Expense" checkbox
4. Fill in the details and submit

The expense will be recorded but **not divided** among participants.

## Reimbursements

### What is a Reimbursement?

A reimbursement is when:
- Someone receives money back from a return or refund
- The original shared expense **stays in place**
- The reimbursement **reduces** the account of the person who got the money

### Use Cases

- Returning items and getting refunds
- Getting money back for overpaid shared expenses
- Refunds from suppliers
- Money returned from previous overpayments

### How It Works

**Example: Alice buys a table for $100 (shared expense)**

```
Step 1: Original Shared Expense
- Item: Table for $100
- Shared between: Alice & Bob
- Alice owes: $50
- Bob owes: $50

Step 2: Table is Returned, $100 Refund
- Alice adds a $100 reimbursement to herself
- Alice's account: $50 - $100 = -$50 (she received $50 more than her share)
- Bob's account: $50 (unchanged from original split)

Step 3: Settlement
- Bob owes Alice $100 total
  - $50 for his share of the table
  - $50 because Alice got the refund but Bob benefited from the table

Or alternatively:
- Alice keeps the $100
- Bob pays Alice $50 (his share of the table purchase)
```

### Managing Reimbursements

**Adding a Reimbursement:**
1. Go to "Reimbursements" menu
2. Click "Add Reimbursement"
3. Fill in:
   - **Description**: What was reimbursed (e.g., "Table refund")
   - **Amount**: Amount received
   - **Who Received the Money**: Which person got the refund
   - **Date**: When the refund was received
   - **Original Expense Type** (optional): What type the original was
   - **Notes** (optional): Additional details
4. Submit

**Viewing Reimbursements:**
- See all reimbursements in the Reimbursements list
- View summary by person showing total reimbursed

**Editing/Deleting:**
- Use Edit button to modify details
- Use Delete button to remove reimbursements

## Calculation Examples

### Example 1: Individual Expense

```
Items purchased:
1. Shared groceries: $60 (Alice)
   - Alice: -$30, Bob: +$30

2. Alice's personal item: $40 (Alice, Individual)
   - Alice: -$40, Bob: $0

Total balance:
- Alice: -$70
- Bob: +$30
Settlement: Bob pays Alice $30
```

### Example 2: Reimbursement After Return

```
1. Shared kitchen furniture: $200 (Alice)
   - Alice: -$100, Bob: +$100

2. Refund received: $200 (Alice reimbursed)
   - Alice: -$100 + $200 = +$100
   - Bob: +$100 (unchanged)

3. Settlement:
   - Bob owes Alice: $200 (his $100 + Alice got refund)
   - Or: Alice keeps $100, Bob pays $100
```

## Database Schema

### Individual Expenses
Already exists in all expense tables:
```
- individual_only: INTEGER (0 or 1)
  Default: 0 (shared)
  When 1: Not divided among participants
```

### Reimbursements
New table: `reimbursements`
```
- id: INTEGER PRIMARY KEY
- name: TEXT (description)
- amount: REAL (amount reimbursed)
- reimbursed_to: TEXT (person who got money)
- original_expense_type: TEXT (food, utilities, stuff, other)
- original_expense_id: INTEGER (if known)
- reimbursement_date: DATE
- notes: TEXT
- created_at: TIMESTAMP
```

## Implementation Details

### Files Added

1. **Models**
   - `/app/models/reimbursement.py` - Reimbursement model with CRUD operations

2. **Routes**
   - `/app/routes/reimbursement.py` - Reimbursement route handlers

3. **Templates**
   - `/app/templates/reimbursement/index.html` - List view
   - `/app/templates/reimbursement/form.html` - Add/Edit form

4. **Migrations**
   - `/scripts/migrate_add_reimbursements.py` - Add reimbursement table

### Files Updated

1. **Models**
   - `/app/models/__init__.py` - Export Reimbursement
   - `/app/models/expense_log.py` - Add reimbursement logging

2. **Routes**
   - `/app/__init__.py` - Register reimbursement blueprint

3. **Git**
   - `/.gitignore` - Updated ignore rules (logs, PID files, etc)

## Setup Instructions

### 1. Run Migration

```bash
cd /Users/henrique.barata/CODE/home-server/expensesApp

# Activate virtual environment
source venv/bin/activate

# Run migration
python scripts/migrate_add_reimbursements.py
```

Output:
```
✅ Reimbursements table created successfully!
```

### 2. Update App Files

The new files have been created and the app already has:
- Reimbursement model
- Reimbursement routes
- Reimbursement templates
- Updated main app initialization

### 3. Restart Application

```bash
# Stop the app if running
# Start it again - new features available
```

## UI/UX Improvements

### Individual Expenses
- Checkbox available on all expense forms
- Visual indicator in lists showing individual expenses
- Doesn't appear in shared expense calculations

### Reimbursements
- New "Reimbursements" section in main menu
- Clean form for adding/editing
- Summary view showing total reimbursed per person
- Links to relevant documentation

## Accounting Logic

### Individual Expenses in Calculations

**Original formula** (all shared):
```
Person's balance = Amount paid - Amount owed
Amount owed = Total expenses / Number of people
```

**New formula** (with individual):
```
Person's balance = Amount paid (all) - Amount owed (shared only)
Amount owed = Sum of shared expenses / Number of people
```

### Reimbursements in Settlements

```
Final balance = Original balance - Reimbursement received + Reimbursement paid
Settlement = Who owes whom based on final balance
```

## Validation Rules

- **Individual expenses**: Amount > 0
- **Reimbursements**: 
  - Amount > 0
  - Person must exist
  - Date <= today
  - Description required

## Logging

All reimbursement actions are logged:
- `log_reimbursement(action, reimbursement_id, person, amount, description)`
- Supports: add, update, delete
- Accessible via: Dashboard → Activity Log

## Future Enhancements

Possible future improvements:
1. **Partial reimbursements** - Record partial returns
2. **Linked reimbursements** - Auto-link to original expense
3. **Automatic settlement** - Calculate impact on settlements
4. **Reimbursement reports** - Summary reports by person/period
5. **Recurring reimbursements** - Setup automatic reimbursements
6. **Batch reimbursements** - Handle multiple items at once

## Troubleshooting

### Reimbursements table doesn't exist

```bash
python scripts/migrate_add_reimbursements.py
```

### Individual expense flag not showing

Check that:
1. Database migration was run
2. Browser cache is cleared
3. Application was restarted

### Reimbursements not appearing in reports

Ensure:
1. Date is correct
2. Person name matches exactly
3. Migration has been run

## Questions & Support

For questions about:
- **Individual expenses**: See the checkbox on expense forms with explanation
- **Reimbursements**: Click the 💡 info box on the reimbursement form
- **Settlement calculations**: See Dashboard → Settlement section
