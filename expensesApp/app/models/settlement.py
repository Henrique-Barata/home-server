"""
Settlement Model
----------------
Track balance payments between users.
When one person pays another to balance shared expenses.
"""
from datetime import date, datetime
from typing import List, Optional
from .database import db


class Settlement:
    """
    Settlement model for balance payments between users.
    
    Example: Carlota pays Henrique €50 to balance out shared expenses.
    """
    
    TABLE_NAME = "settlements"
    
    def __init__(self, id: int = None, payer: str = "", receiver: str = "",
                 amount: float = 0.0, settlement_date: date = None,
                 notes: str = "", created_at: datetime = None):
        self.id = id
        self.payer = payer  # Who paid
        self.receiver = receiver  # Who received
        self.amount = amount
        self.settlement_date = settlement_date or date.today()
        self.notes = notes
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_row(cls, row: dict) -> 'Settlement':
        """Create instance from database row."""
        if not row:
            return None
        return cls(
            id=row.get('id'),
            payer=row.get('payer', ''),
            receiver=row.get('receiver', ''),
            amount=row.get('amount', 0.0),
            settlement_date=row.get('settlement_date'),
            notes=row.get('notes', ''),
            created_at=row.get('created_at')
        )
    
    def save(self) -> int:
        """Save settlement to database."""
        if self.id:
            return self._update()
        return self._insert()
    
    def _insert(self) -> int:
        """Insert new settlement."""
        with db.transaction() as conn:
            cursor = conn.execute(
                f"""INSERT INTO {self.TABLE_NAME} 
                    (payer, receiver, amount, settlement_date, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                (self.payer, self.receiver, self.amount, 
                 self.settlement_date, self.notes, self.created_at)
            )
            self.id = cursor.lastrowid
        return self.id
    
    def _update(self) -> int:
        """Update existing settlement."""
        with db.transaction():
            db.execute(
                f"""UPDATE {self.TABLE_NAME}
                    SET payer = ?, receiver = ?, amount = ?, 
                        settlement_date = ?, notes = ?
                    WHERE id = ?""",
                (self.payer, self.receiver, self.amount,
                 self.settlement_date, self.notes, self.id)
            )
        return self.id
    
    def delete(self):
        """Delete settlement."""
        with db.transaction():
            db.execute(f"DELETE FROM {self.TABLE_NAME} WHERE id = ?", (self.id,))
    
    @classmethod
    def get_by_id(cls, settlement_id: int) -> Optional['Settlement']:
        """Get settlement by ID."""
        row = db.fetch_one(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE id = ?",
            (settlement_id,)
        )
        return cls.from_row(row)
    
    @classmethod
    def get_all(cls) -> List['Settlement']:
        """Get all settlements ordered by date."""
        rows = db.fetch_all(
            f"SELECT * FROM {cls.TABLE_NAME} ORDER BY settlement_date DESC"
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_by_month(cls, year: int, month: int) -> List['Settlement']:
        """Get settlements for a specific month."""
        rows = db.fetch_all(
            f"""SELECT * FROM {cls.TABLE_NAME}
                WHERE strftime('%Y', settlement_date) = ?
                AND strftime('%m', settlement_date) = ?
                ORDER BY settlement_date DESC""",
            (str(year), f"{month:02d}")
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_total_paid_by(cls, payer: str, year: int = None) -> float:
        """Get total amount paid by a person (optionally filtered by year)."""
        if year:
            row = db.fetch_one(
                f"""SELECT COALESCE(SUM(amount), 0) as total FROM {cls.TABLE_NAME}
                    WHERE payer = ? AND strftime('%Y', settlement_date) = ?""",
                (payer, str(year))
            )
        else:
            row = db.fetch_one(
                f"SELECT COALESCE(SUM(amount), 0) as total FROM {cls.TABLE_NAME} WHERE payer = ?",
                (payer,)
            )
        return row['total'] if row else 0.0
    
    @classmethod
    def get_total_received_by(cls, receiver: str, year: int = None) -> float:
        """Get total amount received by a person (optionally filtered by year)."""
        if year:
            row = db.fetch_one(
                f"""SELECT COALESCE(SUM(amount), 0) as total FROM {cls.TABLE_NAME}
                    WHERE receiver = ? AND strftime('%Y', settlement_date) = ?""",
                (receiver, str(year))
            )
        else:
            row = db.fetch_one(
                f"SELECT COALESCE(SUM(amount), 0) as total FROM {cls.TABLE_NAME} WHERE receiver = ?",
                (receiver,)
            )
        return row['total'] if row else 0.0
    
    @classmethod
    def get_balance_between(cls, person1: str, person2: str, year: int = None) -> float:
        """
        Calculate net balance between two people.
        Positive = person1 owes person2
        Negative = person2 owes person1
        """
        paid_1_to_2 = 0.0
        paid_2_to_1 = 0.0
        
        if year:
            row = db.fetch_one(
                f"""SELECT COALESCE(SUM(amount), 0) as total FROM {cls.TABLE_NAME}
                    WHERE payer = ? AND receiver = ? AND strftime('%Y', settlement_date) = ?""",
                (person1, person2, str(year))
            )
            paid_1_to_2 = row['total'] if row else 0.0
            
            row = db.fetch_one(
                f"""SELECT COALESCE(SUM(amount), 0) as total FROM {cls.TABLE_NAME}
                    WHERE payer = ? AND receiver = ? AND strftime('%Y', settlement_date) = ?""",
                (person2, person1, str(year))
            )
            paid_2_to_1 = row['total'] if row else 0.0
        else:
            row = db.fetch_one(
                f"""SELECT COALESCE(SUM(amount), 0) as total FROM {cls.TABLE_NAME}
                    WHERE payer = ? AND receiver = ?""",
                (person1, person2)
            )
            paid_1_to_2 = row['total'] if row else 0.0
            
            row = db.fetch_one(
                f"""SELECT COALESCE(SUM(amount), 0) as total FROM {cls.TABLE_NAME}
                    WHERE payer = ? AND receiver = ?""",
                (person2, person1)
            )
            paid_2_to_1 = row['total'] if row else 0.0
        
        return paid_2_to_1 - paid_1_to_2
