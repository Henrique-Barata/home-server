"""
Fixed Expense Model
-------------------
Fixed expenses that apply monthly with effective dates for changes.
"""
from datetime import date
from typing import List, Optional
from .database import db


class FixedExpense:
    """
    Fixed expense model for recurring monthly expenses like Rent.
    
    Changes are tracked with effective dates:
    - A change made in April with effective date May 1st affects May onwards
    - Historical values are preserved for accurate reporting
    """
    
    TABLE_NAME = "fixed_expenses"
    
    def __init__(self, id: int = None, expense_type: str = "", 
                 amount: float = 0.0, effective_date: date = None,
                 paid_by: str = "", created_at: date = None):
        self.id = id
        self.expense_type = expense_type
        self.amount = amount
        self.effective_date = effective_date or date.today().replace(day=1)
        self.paid_by = paid_by
        self.created_at = created_at or date.today()
    
    @classmethod
    def from_row(cls, row: dict) -> 'FixedExpense':
        """Create instance from database row."""
        if not row:
            return None
        return cls(
            id=row.get('id'),
            expense_type=row.get('expense_type', ''),
            amount=row.get('amount', 0.0),
            effective_date=row.get('effective_date'),
            paid_by=row.get('paid_by', ''),
            created_at=row.get('created_at')
        )
    
    def save(self) -> int:
        """
        Save fixed expense. Always inserts a new record to maintain history.
        """
        with db.transaction() as conn:
            cursor = conn.execute(
                f"""INSERT INTO {self.TABLE_NAME} 
                    (expense_type, amount, effective_date, paid_by, created_at)
                    VALUES (?, ?, ?, ?, ?)""",
                (self.expense_type, self.amount, self.effective_date, self.paid_by, self.created_at)
            )
            self.id = cursor.lastrowid
        return self.id
    
    def delete(self):
        """Delete fixed expense record."""
        with db.transaction():
            db.execute(f"DELETE FROM {self.TABLE_NAME} WHERE id = ?", (self.id,))
    
    @classmethod
    def get_by_id(cls, expense_id: int) -> Optional['FixedExpense']:
        """Get fixed expense by ID."""
        row = db.fetch_one(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE id = ?",
            (expense_id,)
        )
        return cls.from_row(row)
    
    @classmethod
    def get_all(cls) -> List['FixedExpense']:
        """Get all fixed expense records ordered by date."""
        rows = db.fetch_all(
            f"SELECT * FROM {cls.TABLE_NAME} ORDER BY expense_type, effective_date DESC"
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_by_type(cls, expense_type: str) -> List['FixedExpense']:
        """Get all records for a specific expense type."""
        rows = db.fetch_all(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE expense_type = ? ORDER BY effective_date DESC",
            (expense_type,)
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_current_by_type(cls, expense_type: str) -> Optional['FixedExpense']:
        """Get the current (most recent effective) value for a type."""
        row = db.fetch_one(
            f"""SELECT * FROM {cls.TABLE_NAME} 
                WHERE expense_type = ? AND effective_date <= ?
                ORDER BY effective_date DESC LIMIT 1""",
            (expense_type, date.today())
        )
        return cls.from_row(row)
    
    @classmethod
    def get_value_for_month(cls, expense_type: str, year: int, month: int) -> float:
        """
        Get the applicable value for a specific month.
        Returns the most recent value effective on or before the first of that month.
        """
        target_date = date(year, month, 1)
        row = db.fetch_one(
            f"""SELECT amount FROM {cls.TABLE_NAME} 
                WHERE expense_type = ? AND effective_date <= ?
                ORDER BY effective_date DESC LIMIT 1""",
            (expense_type, target_date)
        )
        return row['amount'] if row else 0.0
    
    @classmethod
    def get_total_by_month(cls, year: int, month: int) -> float:
        """
        Get the total of all fixed expenses for a specific month.
        Sums the applicable value for each expense type.
        """
        all_types = FixedExpenseType.get_all_types()
        total = 0.0
        for expense_type in all_types:
            total += cls.get_value_for_month(expense_type, year, month)
        return total
    
    @classmethod
    def get_all_current(cls) -> dict:
        """
        Get current values for all fixed expense types.
        Returns dict of {expense_type: amount}
        """
        all_types = FixedExpenseType.get_all_types()
        
        result = {}
        for expense_type in all_types:
            current = cls.get_current_by_type(expense_type)
            result[expense_type] = current.amount if current else 0.0
        return result
    
    @classmethod
    def get_all_types_history(cls) -> dict:
        """
        Get history for all fixed expense types.
        Returns dict of {expense_type: [FixedExpense, ...]}
        """
        all_types = FixedExpenseType.get_all_types()
        
        result = {}
        for expense_type in all_types:
            result[expense_type] = cls.get_by_type(expense_type)
        return result
    
    @classmethod
    def delete_by_type(cls, expense_type: str):
        """Delete all fixed expenses of a specific type."""
        with db.transaction():
            db.execute(f"DELETE FROM {cls.TABLE_NAME} WHERE expense_type = ?", (expense_type,))
    
    @classmethod
    def mark_paid(cls, fixed_expense_id: int, year: int, month: int, paid_by: str):
        """Mark a fixed expense as paid for a specific month."""
        with db.transaction() as conn:
            # Check if record exists
            existing = db.fetch_one(
                """SELECT id FROM fixed_expense_payments 
                   WHERE fixed_expense_id = ? AND year = ? AND month = ?""",
                (fixed_expense_id, year, month)
            )
            
            if existing:
                # Update existing record
                db.execute(
                    """UPDATE fixed_expense_payments 
                       SET is_paid = 1, paid_by = ?, paid_date = ?
                       WHERE fixed_expense_id = ? AND year = ? AND month = ?""",
                    (paid_by, date.today(), fixed_expense_id, year, month)
                )
            else:
                # Insert new record
                db.execute(
                    """INSERT INTO fixed_expense_payments 
                       (fixed_expense_id, year, month, is_paid, paid_by, paid_date)
                       VALUES (?, ?, ?, 1, ?, ?)""",
                    (fixed_expense_id, year, month, paid_by, date.today())
                )
    
    @classmethod
    def mark_unpaid(cls, fixed_expense_id: int, year: int, month: int):
        """Mark a fixed expense as unpaid for a specific month."""
        with db.transaction():
            db.execute(
                """UPDATE fixed_expense_payments 
                   SET is_paid = 0, paid_by = NULL, paid_date = NULL
                   WHERE fixed_expense_id = ? AND year = ? AND month = ?""",
                (fixed_expense_id, year, month)
            )
    
    @classmethod
    def get_payment_status(cls, fixed_expense_id: int, year: int, month: int) -> dict:
        """Get payment status for a fixed expense in a specific month."""
        row = db.fetch_one(
            """SELECT is_paid, paid_by, paid_date FROM fixed_expense_payments 
               WHERE fixed_expense_id = ? AND year = ? AND month = ?""",
            (fixed_expense_id, year, month)
        )
        return {
            'is_paid': row['is_paid'] if row else 0,
            'paid_by': row['paid_by'] if row else None,
            'paid_date': row['paid_date'] if row else None
        }
    
    @classmethod
    def get_all_payments_for_month(cls, year: int, month: int) -> dict:
        """Get payment status for all fixed expenses in a month."""
        rows = db.fetch_all(
            """SELECT fixed_expense_id, is_paid, paid_by, paid_date 
               FROM fixed_expense_payments 
               WHERE year = ? AND month = ?""",
            (year, month)
        )
        result = {}
        for row in rows:
            result[row['fixed_expense_id']] = {
                'is_paid': row['is_paid'],
                'paid_by': row['paid_by'],
                'paid_date': row['paid_date']
            }
        return result
    
    @classmethod
    def get_all_payments_for_expense(cls, fixed_expense_id: int) -> list:
        """Get all payment records for a specific fixed expense across all months."""
        rows = db.fetch_all(
            """SELECT year, month, is_paid, paid_by, paid_date 
               FROM fixed_expense_payments 
               WHERE fixed_expense_id = ?
               ORDER BY year DESC, month DESC""",
            (fixed_expense_id,)
        )
        return [dict(row) for row in rows]


class FixedExpenseType:
    """
    Model to store custom fixed expense types.
    Default types (Rent, Internet) are hardcoded, custom ones stored in DB.
    """
    
    TABLE_NAME = "fixed_expense_types"
    DEFAULT_TYPES = ["Rent", "Internet"]
    
    def __init__(self, id: int = None, name: str = ""):
        self.id = id
        self.name = name
    
    @classmethod
    def from_row(cls, row: dict) -> 'FixedExpenseType':
        """Create instance from database row."""
        if not row:
            return None
        return cls(
            id=row.get('id'),
            name=row.get('name', '')
        )
    
    def save(self) -> int:
        """Save the expense type."""
        with db.transaction() as conn:
            cursor = conn.execute(
                f"INSERT INTO {self.TABLE_NAME} (name) VALUES (?)",
                (self.name,)
            )
            self.id = cursor.lastrowid
        return self.id
    
    @classmethod
    def get_all_types(cls) -> list:
        """Get all expense types (default + custom)."""
        rows = db.fetch_all(f"SELECT name FROM {cls.TABLE_NAME} ORDER BY name")
        custom_types = [row['name'] for row in rows]
        
        # Combine default and custom, remove duplicates while preserving order
        all_types = list(cls.DEFAULT_TYPES)
        for t in custom_types:
            if t not in all_types:
                all_types.append(t)
        
        return all_types
    
    @classmethod
    def delete_by_name(cls, name: str):
        """Delete a custom expense type by name."""
        if name in cls.DEFAULT_TYPES:
            return  # Don't delete default types
        with db.transaction():
            db.execute(f"DELETE FROM {cls.TABLE_NAME} WHERE name = ?", (name,))
