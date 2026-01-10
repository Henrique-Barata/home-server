"""
Travel Model
------------
Models for tracking travel trips and their associated expenses.
Each travel can have multiple expense categories and expenses.
"""
import logging
from datetime import date, datetime
from typing import List, Optional, Dict
from .database import db

logger = logging.getLogger(__name__)


# Travel expense categories
TRAVEL_EXPENSE_CATEGORIES = [
    'Transportation',
    'Accommodation', 
    'Food & Dining',
    'Activities & Entertainment',
    'Miscellaneous'
]


class Travel:
    """
    Model for tracking travel trips.
    
    A travel represents a trip with a name, start/end dates,
    and multiple expense categories with expenses.
    """
    
    TABLE_NAME = "travels"
    
    def __init__(self, id: int = None, name: str = "", 
                 start_date: date = None, end_date: date = None,
                 notes: str = "", created_at: datetime = None):
        self.id = id
        self.name = name
        self.start_date = start_date or date.today()
        self.end_date = end_date or date.today()
        self.notes = notes
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_row(cls, row: dict) -> 'Travel':
        """Create instance from database row."""
        if not row:
            return None
        return cls(
            id=row.get('id'),
            name=row.get('name', ''),
            start_date=row.get('start_date'),
            end_date=row.get('end_date'),
            notes=row.get('notes', ''),
            created_at=row.get('created_at')
        )
    
    def save(self) -> int:
        """Save travel to database. Returns ID."""
        if self.id:
            return self._update()
        return self._insert()
    
    def _insert(self) -> int:
        """Insert new travel."""
        with db.transaction() as conn:
            cursor = conn.execute(
                f"""INSERT INTO {self.TABLE_NAME} 
                    (name, start_date, end_date, notes, created_at)
                    VALUES (?, ?, ?, ?, ?)""",
                (self.name, self.start_date, self.end_date, self.notes, self.created_at)
            )
            self.id = cursor.lastrowid
        logger.info(f"Created travel {self.id}: {self.name}")
        return self.id
    
    def _update(self) -> int:
        """Update existing travel."""
        with db.transaction():
            db.execute(
                f"""UPDATE {self.TABLE_NAME}
                    SET name = ?, start_date = ?, end_date = ?, notes = ?
                    WHERE id = ?""",
                (self.name, self.start_date, self.end_date, self.notes, self.id)
            )
        logger.info(f"Updated travel {self.id}: {self.name}")
        return self.id
    
    def delete(self):
        """Delete travel and all associated expenses from database."""
        with db.transaction():
            # Delete associated expenses first (cascade)
            db.execute(
                f"DELETE FROM {TravelExpense.TABLE_NAME} WHERE travel_id = ?",
                (self.id,)
            )
            db.execute(f"DELETE FROM {self.TABLE_NAME} WHERE id = ?", (self.id,))
        logger.info(f"Deleted travel {self.id}: {self.name}")
    
    @classmethod
    def get_by_id(cls, travel_id: int) -> Optional['Travel']:
        """Get travel by ID."""
        row = db.fetch_one(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE id = ?",
            (travel_id,)
        )
        return cls.from_row(row)
    
    @classmethod
    def get_all(cls, order_by: str = "start_date DESC") -> List['Travel']:
        """Get all travels ordered by date."""
        rows = db.fetch_all(f"SELECT * FROM {cls.TABLE_NAME} ORDER BY {order_by}")
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_by_year(cls, year: int) -> List['Travel']:
        """Get travels for a specific year."""
        rows = db.fetch_all(
            f"""SELECT * FROM {cls.TABLE_NAME} 
               WHERE strftime('%Y', start_date) = ? 
               ORDER BY start_date DESC""",
            (str(year),)
        )
        return [cls.from_row(row) for row in rows]
    
    def get_expenses(self) -> List['TravelExpense']:
        """Get all expenses for this travel."""
        return TravelExpense.get_by_travel(self.id)
    
    def get_expenses_by_category(self) -> Dict[str, List['TravelExpense']]:
        """Get expenses grouped by category."""
        expenses = self.get_expenses()
        result = {cat: [] for cat in TRAVEL_EXPENSE_CATEGORIES}
        for expense in expenses:
            if expense.category in result:
                result[expense.category].append(expense)
            else:
                result[expense.category] = [expense]
        return result
    
    def get_total(self) -> float:
        """Get total amount of all expenses for this travel."""
        result = db.fetch_one(
            f"""SELECT COALESCE(SUM(amount), 0) as total 
                FROM {TravelExpense.TABLE_NAME} WHERE travel_id = ?""",
            (self.id,)
        )
        return result['total'] if result else 0.0
    
    def get_totals_by_category(self) -> Dict[str, float]:
        """Get total amounts by category."""
        rows = db.fetch_all(
            f"""SELECT category, COALESCE(SUM(amount), 0) as total 
                FROM {TravelExpense.TABLE_NAME} 
                WHERE travel_id = ? 
                GROUP BY category""",
            (self.id,)
        )
        result = {cat: 0.0 for cat in TRAVEL_EXPENSE_CATEGORIES}
        for row in rows:
            result[row['category']] = row['total']
        return result
    
    def get_totals_by_person(self) -> Dict[str, float]:
        """Get total amounts by person who paid."""
        rows = db.fetch_all(
            f"""SELECT paid_by, COALESCE(SUM(amount), 0) as total 
                FROM {TravelExpense.TABLE_NAME} 
                WHERE travel_id = ? 
                GROUP BY paid_by""",
            (self.id,)
        )
        return {row['paid_by']: row['total'] for row in rows}
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'notes': self.notes,
            'total': self.get_total(),
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else str(self.created_at)
        }


class TravelExpense:
    """
    Model for individual expenses within a travel.
    
    Each expense belongs to a travel and a category.
    """
    
    TABLE_NAME = "travel_expenses"
    
    def __init__(self, id: int = None, travel_id: int = None,
                 name: str = "", amount: float = 0.0, paid_by: str = "",
                 category: str = "", expense_date: date = None,
                 notes: str = "", created_at: datetime = None):
        self.id = id
        self.travel_id = travel_id
        self.name = name
        self.amount = amount
        self.paid_by = paid_by
        self.category = category
        self.expense_date = expense_date or date.today()
        self.notes = notes
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_row(cls, row: dict) -> 'TravelExpense':
        """Create instance from database row."""
        if not row:
            return None
        return cls(
            id=row.get('id'),
            travel_id=row.get('travel_id'),
            name=row.get('name', ''),
            amount=row.get('amount', 0.0),
            paid_by=row.get('paid_by', ''),
            category=row.get('category', ''),
            expense_date=row.get('expense_date'),
            notes=row.get('notes', ''),
            created_at=row.get('created_at')
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
                    (travel_id, name, amount, paid_by, category, expense_date, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (self.travel_id, self.name, self.amount, self.paid_by, 
                 self.category, self.expense_date, self.notes, self.created_at)
            )
            self.id = cursor.lastrowid
        logger.info(f"Created travel expense {self.id}: {self.name} (€{self.amount:.2f})")
        return self.id
    
    def _update(self) -> int:
        """Update existing expense."""
        with db.transaction():
            db.execute(
                f"""UPDATE {self.TABLE_NAME}
                    SET name = ?, amount = ?, paid_by = ?, category = ?, 
                        expense_date = ?, notes = ?
                    WHERE id = ?""",
                (self.name, self.amount, self.paid_by, self.category,
                 self.expense_date, self.notes, self.id)
            )
        logger.info(f"Updated travel expense {self.id}: {self.name}")
        return self.id
    
    def delete(self):
        """Delete expense from database."""
        with db.transaction():
            db.execute(f"DELETE FROM {self.TABLE_NAME} WHERE id = ?", (self.id,))
        logger.info(f"Deleted travel expense {self.id}: {self.name}")
    
    @classmethod
    def get_by_id(cls, expense_id: int) -> Optional['TravelExpense']:
        """Get expense by ID."""
        row = db.fetch_one(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE id = ?",
            (expense_id,)
        )
        return cls.from_row(row)
    
    @classmethod
    def get_by_travel(cls, travel_id: int) -> List['TravelExpense']:
        """Get all expenses for a travel."""
        rows = db.fetch_all(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE travel_id = ? ORDER BY expense_date DESC",
            (travel_id,)
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_by_travel_and_category(cls, travel_id: int, category: str) -> List['TravelExpense']:
        """Get expenses for a travel in a specific category."""
        rows = db.fetch_all(
            f"""SELECT * FROM {cls.TABLE_NAME} 
                WHERE travel_id = ? AND category = ? 
                ORDER BY expense_date DESC""",
            (travel_id, category)
        )
        return [cls.from_row(row) for row in rows]
    
    def get_travel(self) -> Optional[Travel]:
        """Get the parent travel for this expense."""
        if self.travel_id:
            return Travel.get_by_id(self.travel_id)
        return None
    
    @classmethod
    def get_total_by_month(cls, year: int, month: int) -> float:
        """Get total travel expenses for a specific month."""
        result = db.fetch_one(
            f"""SELECT COALESCE(SUM(amount), 0) as total FROM {cls.TABLE_NAME}
                WHERE strftime('%Y', expense_date) = ?
                AND strftime('%m', expense_date) = ?""",
            (str(year), f"{month:02d}")
        )
        return result['total'] if result else 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'travel_id': self.travel_id,
            'name': self.name,
            'amount': self.amount,
            'paid_by': self.paid_by,
            'category': self.category,
            'expense_date': str(self.expense_date),
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else str(self.created_at)
        }
