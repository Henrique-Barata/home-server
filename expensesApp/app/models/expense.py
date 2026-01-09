"""
Expense Models
--------------
Base and specific expense models with CRUD operations.
Uses simple SQL abstraction for efficiency.
"""
from datetime import date, datetime
from typing import List, Optional
from .database import db


class Expense:
    """
    Base expense class with common functionality.
    Subclasses define specific table and fields.
    """
    
    TABLE_NAME = "expenses"  # Override in subclasses
    
    def __init__(self, id: int = None, name: str = "", amount: float = 0.0,
                 paid_by: str = "", expense_date: date = None, created_at: datetime = None,
                 individual_only: bool = False):
        self.id = id
        self.name = name
        self.amount = amount
        self.paid_by = paid_by
        self.expense_date = expense_date or date.today()
        self.created_at = created_at or datetime.now()
        self.individual_only = individual_only
    
    @classmethod
    def from_row(cls, row: dict) -> 'Expense':
        """Create instance from database row."""
        if not row:
            return None
        return cls(
            id=row.get('id'),
            name=row.get('name', ''),
            amount=row.get('amount', 0.0),
            paid_by=row.get('paid_by', ''),
            expense_date=row.get('expense_date'),
            created_at=row.get('created_at'),
            individual_only=bool(row.get('individual_only', 0))
        )
    
    def save(self) -> int:
        """Save expense to database. Returns ID."""
        if self.id:
            return self._update()
        return self._insert()
    
    def _insert(self) -> int:
        """Insert new expense."""
        with db.transaction() as conn:
            cursor = conn.execute(
                f"""INSERT INTO {self.TABLE_NAME} 
                    (name, amount, paid_by, expense_date, created_at, individual_only)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                (self.name, self.amount, self.paid_by, self.expense_date, self.created_at, 
                 int(self.individual_only))
            )
            self.id = cursor.lastrowid
        return self.id
    
    def _update(self) -> int:
        """Update existing expense."""
        with db.transaction():
            db.execute(
                f"""UPDATE {self.TABLE_NAME}
                    SET name = ?, amount = ?, paid_by = ?, expense_date = ?, individual_only = ?
                    WHERE id = ?""",
                (self.name, self.amount, self.paid_by, self.expense_date, 
                 int(self.individual_only), self.id)
            )
        return self.id
    
    def delete(self):
        """Delete expense from database."""
        with db.transaction():
            db.execute(f"DELETE FROM {self.TABLE_NAME} WHERE id = ?", (self.id,))
    
    @classmethod
    def get_by_id(cls, expense_id: int) -> Optional['Expense']:
        """Get expense by ID."""
        row = db.fetch_one(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE id = ?",
            (expense_id,)
        )
        return cls.from_row(row)
    
    @classmethod
    def get_all(cls, order_by: str = "expense_date DESC") -> List['Expense']:
        """Get all expenses ordered by date."""
        rows = db.fetch_all(f"SELECT * FROM {cls.TABLE_NAME} ORDER BY {order_by}")
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_by_month(cls, year: int, month: int) -> List['Expense']:
        """Get expenses for a specific month."""
        rows = db.fetch_all(
            f"""SELECT * FROM {cls.TABLE_NAME}
                WHERE strftime('%Y', expense_date) = ?
                AND strftime('%m', expense_date) = ?
                ORDER BY expense_date DESC""",
            (str(year), f"{month:02d}")
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_total_by_month(cls, year: int, month: int) -> float:
        """Get total amount for a specific month."""
        result = db.fetch_one(
            f"""SELECT COALESCE(SUM(amount), 0) as total FROM {cls.TABLE_NAME}
                WHERE strftime('%Y', expense_date) = ?
                AND strftime('%m', expense_date) = ?""",
            (str(year), f"{month:02d}")
        )
        return result['total'] if result else 0.0
    
    @classmethod
    def get_total_by_person(cls, person: str) -> float:
        """Get total amount paid by a person."""
        result = db.fetch_one(
            f"SELECT COALESCE(SUM(amount), 0) as total FROM {cls.TABLE_NAME} WHERE paid_by = ?",
            (person,)
        )
        return result['total'] if result else 0.0
    
    @classmethod
    def get_total_by_person_and_month(cls, person: str, year: int, month: int) -> float:
        """Get total amount paid by a person in a specific month."""
        result = db.fetch_one(
            f"""SELECT COALESCE(SUM(amount), 0) as total FROM {cls.TABLE_NAME}
                WHERE paid_by = ?
                AND strftime('%Y', expense_date) = ?
                AND strftime('%m', expense_date) = ?""",
            (person, str(year), f"{month:02d}")
        )
        return result['total'] if result else 0.0
    
    @classmethod
    def get_total_by_month_shared_only(cls, year: int, month: int) -> float:
        """Get total amount for a specific month (excluding individual-only expenses)."""
        result = db.fetch_one(
            f"""SELECT COALESCE(SUM(amount), 0) as total FROM {cls.TABLE_NAME}
                WHERE strftime('%Y', expense_date) = ?
                AND strftime('%m', expense_date) = ?
                AND individual_only = 0""",
            (str(year), f"{month:02d}")
        )
        return result['total'] if result else 0.0
    
    @classmethod
    def get_total_by_person_and_month_shared_only(cls, person: str, year: int, month: int) -> float:
        """Get total amount paid by a person in a specific month (excluding individual-only expenses)."""
        result = db.fetch_one(
            f"""SELECT COALESCE(SUM(amount), 0) as total FROM {cls.TABLE_NAME}
                WHERE paid_by = ?
                AND strftime('%Y', expense_date) = ?
                AND strftime('%m', expense_date) = ?
                AND individual_only = 0""",
            (person, str(year), f"{month:02d}")
        )
        return result['total'] if result else 0.0


class FoodExpense(Expense):
    """Food expense model."""
    TABLE_NAME = "food_expenses"


class OtherExpense(Expense):
    """Other/miscellaneous expense model."""
    TABLE_NAME = "other_expenses"


class UtilityExpense(Expense):
    """
    Utility expense model with utility type.
    Types: Electricity, Gas, Water, Internet
    """
    TABLE_NAME = "utility_expenses"
    
    def __init__(self, utility_type: str = "", **kwargs):
        super().__init__(**kwargs)
        self.utility_type = utility_type
    
    @classmethod
    def from_row(cls, row: dict) -> 'UtilityExpense':
        """Create instance from database row."""
        if not row:
            return None
        expense = super().from_row(row)
        expense.utility_type = row.get('utility_type', '')
        return expense
    
    def _insert(self) -> int:
        """Insert new utility expense."""
        with db.transaction() as conn:
            cursor = conn.execute(
                f"""INSERT INTO {self.TABLE_NAME} 
                    (name, amount, paid_by, expense_date, created_at, utility_type, individual_only)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (self.name, self.amount, self.paid_by, self.expense_date, 
                 self.created_at, self.utility_type, int(self.individual_only))
            )
            self.id = cursor.lastrowid
        return self.id
    
    def _update(self) -> int:
        """Update existing utility expense."""
        with db.transaction():
            db.execute(
                f"""UPDATE {self.TABLE_NAME}
                    SET name = ?, amount = ?, paid_by = ?, expense_date = ?, utility_type = ?, individual_only = ?
                    WHERE id = ?""",
                (self.name, self.amount, self.paid_by, self.expense_date, 
                 self.utility_type, int(self.individual_only), self.id)
            )
        return self.id
    
    @classmethod
    def get_by_type(cls, utility_type: str) -> List['UtilityExpense']:
        """Get all expenses of a specific utility type."""
        rows = db.fetch_all(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE utility_type = ? ORDER BY expense_date DESC",
            (utility_type,)
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_total_by_type_and_month(cls, utility_type: str, year: int, month: int) -> float:
        """Get total for a utility type in a specific month."""
        result = db.fetch_one(
            f"""SELECT COALESCE(SUM(amount), 0) as total FROM {cls.TABLE_NAME}
                WHERE utility_type = ?
                AND strftime('%Y', expense_date) = ?
                AND strftime('%m', expense_date) = ?""",
            (utility_type, str(year), f"{month:02d}")
        )
        return result['total'] if result else 0.0


class StuffExpense(Expense):
    """
    Stuff/items expense with custom type/category.
    """
    TABLE_NAME = "stuff_expenses"
    
    def __init__(self, stuff_type: str = "", **kwargs):
        super().__init__(**kwargs)
        self.stuff_type = stuff_type
    
    @classmethod
    def from_row(cls, row: dict) -> 'StuffExpense':
        """Create instance from database row."""
        if not row:
            return None
        expense = super().from_row(row)
        expense.stuff_type = row.get('stuff_type', '')
        return expense
    
    def _insert(self) -> int:
        """Insert new stuff expense."""
        with db.transaction() as conn:
            cursor = conn.execute(
                f"""INSERT INTO {self.TABLE_NAME} 
                    (name, amount, paid_by, expense_date, created_at, stuff_type, individual_only)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (self.name, self.amount, self.paid_by, self.expense_date, 
                 self.created_at, self.stuff_type, int(self.individual_only))
            )
            self.id = cursor.lastrowid
        return self.id
    
    def _update(self) -> int:
        """Update existing stuff expense."""
        with db.transaction():
            db.execute(
                f"""UPDATE {self.TABLE_NAME}
                    SET name = ?, amount = ?, paid_by = ?, expense_date = ?, stuff_type = ?, individual_only = ?
                    WHERE id = ?""",
                (self.name, self.amount, self.paid_by, self.expense_date, 
                 self.stuff_type, int(self.individual_only), self.id)
            )
        return self.id
    
    @classmethod
    def get_by_type(cls, stuff_type: str) -> List['StuffExpense']:
        """Get all expenses of a specific stuff type."""
        rows = db.fetch_all(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE stuff_type = ? ORDER BY expense_date DESC",
            (stuff_type,)
        )
        return [cls.from_row(row) for row in rows]
