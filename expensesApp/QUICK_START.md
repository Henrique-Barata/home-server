# Quick Start: Individual Expenses & Reimbursements

## TL;DR

Two new features added to Expenses App:

### 1. **Individual Expenses** 
Expenses that count toward total but are NOT divided among participants.
- Use when someone buys something just for themselves
- Already in database, just use the checkbox on expense forms

### 2. **Reimbursements**
Track money received back from returns/refunds.
- New Reimbursements menu
- Records what was reimbursed and to whom
- Affects account balances

---

## Quick Setup (5 minutes)

### Step 1: Run Migration
```bash
cd /Users/henrique.barata/CODE/home-server/expensesApp
source venv/bin/activate
python scripts/migrate_add_reimbursements.py
```

Output: `✅ Reimbursements table created successfully!`

### Step 2: Restart App
```bash
cd /Users/henrique.barata/CODE/home-server
./start_server.sh --start
```

### Step 3: Done!
New features are now available.

---

## Using Individual Expenses

**Add an Individual Expense:**
1. Go to Food/Utilities/Stuff/Other
2. Click "Add Expense"
3. ✅ Check "Personal/Individual Expense"
4. Fill details and submit

**Effect:**
- Amount goes to that person's balance
- NOT divided among others
- Shows in totals but separate accounting

---

## Using Reimbursements

**Add a Reimbursement:**
1. Click "Reimbursements" in menu
2. Click "Add Reimbursement"
3. Fill in:
   - **Description**: What was reimbursed (e.g., "Table refund")
   - **Amount**: Money received
   - **Person**: Who got the money
   - **Date**: When received
4. Submit

**Effect:**
- Reduces that person's account by the amount
- Original shared expense stays the same
- Other people may need to pay them

---

## Real Example

**Scenario:** Alice buys a table for $100 (shared with Bob), returns it for $100 refund

### Step 1: Shared Expense (already recorded)
```
- Expense: Table $100
- Split: Alice $50, Bob $50
```

### Step 2: Add Reimbursement
```
- Name: "Table refund"
- Amount: $100
- To: Alice
- Date: Today
- Type: Stuff
```

### Step 3: New Balance
```
- Alice: Gets $100 back, now +$50 overall
- Bob: Still owes $50
- Settlement: Bob pays Alice $100 total
  (His $50 + Alice's refund)
```

---

## Files Overview

| File | Purpose |
|------|---------|
| `app/models/reimbursement.py` | Reimbursement data model |
| `app/routes/reimbursement.py` | Reimbursement pages/API |
| `app/templates/reimbursement/*` | Forms and lists |
| `scripts/migrate_*.py` | Database setup |
| `FEATURES_INDIVIDUAL_REIMBURSEMENT.md` | Full documentation |

---

## Key Features

✅ **Individual Expenses**
- Checkbox on all expense forms
- Doesn't divide amount
- Counts toward totals

✅ **Reimbursements**
- Add/Edit/Delete reimbursements
- Track refunds per person
- Linked to original expenses (optional)
- Full audit log

✅ **Calculation**
- Automatic balance updates
- Affects settlements
- Shows in summaries

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Reimbursement button missing | Run migration |
| Individual checkbox not showing | Restart app |
| Balance looks wrong | Check audit log |
| Can't add reimbursement | Fill required fields (name, amount, person) |

---

## Examples

### Example 1: Personal Item
```
Alice: Buys $30 coffee maker for herself
- Add as "Stuff" expense
- Check "Individual"
- Amount: $30 to Alice only
- Bob: Unaffected
```

### Example 2: Return
```
Alice: Returns $50 item, gets $50 back
- Reimbursement page
- Name: "Item return"
- Amount: $50
- To: Alice
- Alice's account: -$50
```

### Example 3: Both Combined
```
Shared meal: $60 (Alice pays) → Alice -$30, Bob +$30
Alice's drink: $10 individual → Alice -$10, Bob: $0
Alice returns something: Get $20 → Alice +$20

Final: Alice -$20, Bob +$30
Settlement: Bob pays Alice $30
```

---

## Menu Locations

**Individual Expenses:**
- Food → Add Expense (check Personal checkbox)
- Utilities → Add Expense (check Personal checkbox)
- Stuff → Add Expense (check Personal checkbox)
- Other → Add Expense (check Personal checkbox)

**Reimbursements:**
- New "Reimbursements" menu item
  - List view
  - Add Reimbursement
  - Edit/Delete

---

## Logging

All actions are logged automatically:
- Dashboard → Activity Log
- Shows add/edit/delete of reimbursements
- Shows who reimbursed and when

---

## Questions?

See detailed guide: `FEATURES_INDIVIDUAL_REIMBURSEMENT.md`

For questions about:
- **Calculations**: See examples in feature doc
- **Usage**: See forms (they have help text)
- **Settings**: Check config.yaml for any options

---

## Next Time

When you start the app again, both features are ready to use:
```bash
./start_server.sh --start
```

The app will:
1. Load reimbursements from database
2. Calculate balances including individual expenses
3. Show reimbursement menu
4. Ready for use!
