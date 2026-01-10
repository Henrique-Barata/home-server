"""
Expense Log Model
-----------------
Tracks all expense additions, updates, and deletions for audit trail.
"""
from datetime import datetime, date
from typing import List, Optional
from .database import db


class ExpenseLog:
    """Model for logging all expense operations."""
    
    TABLE_NAME = "expense_logs"
    
    # Action types
    ACTION_ADDED = "added"
    ACTION_UPDATED = "updated"
    ACTION_DELETED = "deleted"
    ACTION_PAID = "marked_paid"
    ACTION_UNPAID = "marked_unpaid"
    
    def __init__(self, id: int = None, action: str = "", expense_type: str = "",
                 expense_id: int = None, paid_by: str = "", amount: float = 0.0,
                 expense_date: date = None, description: str = "", 
                 created_at: datetime = None):
        self.id = id
        self.action = action
        self.expense_type = expense_type
        self.expense_id = expense_id
        self.paid_by = paid_by
        self.amount = amount
        self.expense_date = expense_date
        self.description = description
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_row(cls, row: dict) -> 'ExpenseLog':
        """Create instance from database row."""
        if not row:
            return None
        return cls(
            id=row.get('id'),
            action=row.get('action', ''),
            expense_type=row.get('expense_type', ''),
            expense_id=row.get('expense_id'),
            paid_by=row.get('paid_by', ''),
            amount=row.get('amount', 0.0),
            expense_date=row.get('expense_date'),
            description=row.get('description', ''),
            created_at=row.get('created_at')
        )
    
    def save(self) -> int:
        """Save the log entry."""
        with db.transaction() as conn:
            cursor = conn.execute(
                f"""INSERT INTO {self.TABLE_NAME} 
                    (action, expense_type, expense_id, paid_by, amount, expense_date, description, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (self.action, self.expense_type, self.expense_id, self.paid_by, 
                 self.amount, self.expense_date, self.description, self.created_at)
            )
            self.id = cursor.lastrowid
        return self.id
    
    @classmethod
    def log_expense(cls, action: str, expense_type: str, paid_by: str, 
                   amount: float, expense_date: date, description: str = "",
                   expense_id: int = None) -> int:
        """Helper method to quickly log an expense action."""
        log = cls(
            action=action,
            expense_type=expense_type,
            expense_id=expense_id,
            paid_by=paid_by,
            amount=amount,
            expense_date=expense_date,
            description=description
        )
        return log.save()
    
    @classmethod
    def get_all(cls) -> List['ExpenseLog']:
        """Get all log entries ordered by date descending."""
        rows = db.fetch_all(
            f"SELECT * FROM {cls.TABLE_NAME} ORDER BY created_at DESC"
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_recent(cls, limit: int = 50) -> List['ExpenseLog']:
        """Get recent log entries."""
        rows = db.fetch_all(
            f"SELECT * FROM {cls.TABLE_NAME} ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_by_date_range(cls, start_date: date, end_date: date) -> List['ExpenseLog']:
        """Get log entries within a date range."""
        rows = db.fetch_all(
            f"""SELECT * FROM {cls.TABLE_NAME} 
               WHERE DATE(created_at) BETWEEN ? AND ?
               ORDER BY created_at DESC""",
            (start_date, end_date)
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_by_type(cls, expense_type: str) -> List['ExpenseLog']:
        """Get log entries for a specific expense type."""
        rows = db.fetch_all(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE expense_type = ? ORDER BY created_at DESC",
            (expense_type,)
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_by_person(cls, person: str) -> List['ExpenseLog']:
        """Get log entries for a specific person."""
        rows = db.fetch_all(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE paid_by = ? ORDER BY created_at DESC",
            (person,)
        )
        return [cls.from_row(row) for row in rows]    
    @classmethod
    def log_reimbursement(cls, action: str, reimbursement_id: int, reimbursed_to: str,
                         amount: float, description: str = "") -> int:
        """
        Log a reimbursement action.
        
        Args:
            action: 'add', 'update', or 'delete'
            reimbursement_id: ID of the reimbursement
            reimbursed_to: Person who received the reimbursement
            amount: Amount of reimbursement
            description: Optional description
        
        Returns:
            Log entry ID
        """
        log = cls(
            action=action,
            expense_type="reimbursement",
            expense_id=reimbursement_id,
            paid_by=reimbursed_to,  # Person who received money
            amount=amount,
            description=description
        )
        return log.save()