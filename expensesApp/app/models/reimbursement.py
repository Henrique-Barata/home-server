"""
Reimbursement Model
-------------------
Model for tracking reimbursements (refunds) of expenses.
A reimbursement reduces the account of the person who received the money back.
Unlike shared expenses, reimbursements are NOT divided among participants.
"""
from datetime import date, datetime
from typing import List, Optional
from .database import db


class Reimbursement:
    """
    Model for tracking reimbursements.
    
    A reimbursement represents money returned when an item is refunded.
    It reduces the reimbursed_to person's account balance.
    """
    
    TABLE_NAME = "reimbursements"
    
    def __init__(self, id: int = None, name: str = "", amount: float = 0.0,
                 reimbursed_to: str = "", original_expense_type: str = None,
                 original_expense_id: int = None, reimbursement_date: date = None,
                 notes: str = "", created_at: datetime = None):
        self.id = id
        self.name = name
        self.amount = amount
        self.reimbursed_to = reimbursed_to
        self.original_expense_type = original_expense_type
        self.original_expense_id = original_expense_id
        self.reimbursement_date = reimbursement_date or date.today()
        self.notes = notes
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_row(cls, row: dict) -> 'Reimbursement':
        """Create instance from database row."""
        if not row:
            return None
        return cls(
            id=row.get('id'),
            name=row.get('name', ''),
            amount=row.get('amount', 0.0),
            reimbursed_to=row.get('reimbursed_to', ''),
            original_expense_type=row.get('original_expense_type'),
            original_expense_id=row.get('original_expense_id'),
            reimbursement_date=row.get('reimbursement_date'),
            notes=row.get('notes', ''),
            created_at=row.get('created_at')
        )
    
    def save(self) -> int:
        """Save reimbursement to database. Returns ID."""
        if self.id:
            return self._update()
        return self._insert()
    
    def _insert(self) -> int:
        """Insert new reimbursement."""
        with db.transaction() as conn:
            cursor = conn.execute(
                f"""INSERT INTO {self.TABLE_NAME} 
                    (name, amount, reimbursed_to, original_expense_type, 
                     original_expense_id, reimbursement_date, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (self.name, self.amount, self.reimbursed_to, self.original_expense_type,
                 self.original_expense_id, self.reimbursement_date, self.notes, self.created_at)
            )
            self.id = cursor.lastrowid
        return self.id
    
    def _update(self) -> int:
        """Update existing reimbursement."""
        with db.transaction():
            db.execute(
                f"""UPDATE {self.TABLE_NAME}
                    SET name = ?, amount = ?, reimbursed_to = ?, 
                        original_expense_type = ?, original_expense_id = ?,
                        reimbursement_date = ?, notes = ?
                    WHERE id = ?""",
                (self.name, self.amount, self.reimbursed_to, 
                 self.original_expense_type, self.original_expense_id,
                 self.reimbursement_date, self.notes, self.id)
            )
        return self.id
    
    def delete(self):
        """Delete reimbursement from database."""
        with db.transaction():
            db.execute(f"DELETE FROM {self.TABLE_NAME} WHERE id = ?", (self.id,))
    
    @classmethod
    def get_by_id(cls, reimbursement_id: int) -> Optional['Reimbursement']:
        """Get reimbursement by ID."""
        row = db.fetch_one(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE id = ?",
            (reimbursement_id,)
        )
        return cls.from_row(row)
    
    @classmethod
    def get_all(cls, order_by: str = "reimbursement_date DESC") -> List['Reimbursement']:
        """Get all reimbursements ordered by date."""
        rows = db.fetch_all(f"SELECT * FROM {cls.TABLE_NAME} ORDER BY {order_by}")
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_by_month(cls, year: int, month: int) -> List['Reimbursement']:
        """Get reimbursements for a specific month."""
        rows = db.fetch_all(
            f"""SELECT * FROM {cls.TABLE_NAME} 
               WHERE strftime('%Y', reimbursement_date) = ? 
               AND strftime('%m', reimbursement_date) = ?
               ORDER BY reimbursement_date DESC""",
            (str(year).zfill(4), str(month).zfill(2))
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_by_person(cls, person: str, order_by: str = "reimbursement_date DESC") -> List['Reimbursement']:
        """Get all reimbursements for a specific person."""
        rows = db.fetch_all(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE reimbursed_to = ? ORDER BY {order_by}",
            (person,)
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_total_reimbursed(cls, person: str) -> float:
        """Get total amount reimbursed to a person."""
        result = db.fetch_one(
            f"SELECT SUM(amount) as total FROM {cls.TABLE_NAME} WHERE reimbursed_to = ?",
            (person,)
        )
        return result.get('total', 0) if result else 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'reimbursed_to': self.reimbursed_to,
            'original_expense_type': self.original_expense_type,
            'original_expense_id': self.original_expense_id,
            'reimbursement_date': str(self.reimbursement_date),
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else str(self.created_at)
        }
