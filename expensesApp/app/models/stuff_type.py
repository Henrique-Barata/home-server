"""
Stuff Type Model
----------------
Custom categories for stuff/items expenses.
"""
from typing import List, Optional
from .database import db


class StuffType:
    """
    Custom category/type for stuff expenses.
    Users can create new types through the app.
    """
    
    TABLE_NAME = "stuff_types"
    
    def __init__(self, id: int = None, name: str = ""):
        self.id = id
        self.name = name
    
    @classmethod
    def from_row(cls, row: dict) -> 'StuffType':
        """Create instance from database row."""
        if not row:
            return None
        return cls(
            id=row.get('id'),
            name=row.get('name', '')
        )
    
    def save(self) -> int:
        """Save stuff type to database."""
        if self.id:
            return self._update()
        return self._insert()
    
    def _insert(self) -> int:
        """Insert new stuff type."""
        with db.transaction() as conn:
            cursor = conn.execute(
                f"INSERT INTO {self.TABLE_NAME} (name) VALUES (?)",
                (self.name,)
            )
            self.id = cursor.lastrowid
        return self.id
    
    def _update(self) -> int:
        """Update existing stuff type."""
        with db.transaction():
            db.execute(
                f"UPDATE {self.TABLE_NAME} SET name = ? WHERE id = ?",
                (self.name, self.id)
            )
        return self.id
    
    def delete(self):
        """Delete stuff type."""
        with db.transaction():
            db.execute(f"DELETE FROM {self.TABLE_NAME} WHERE id = ?", (self.id,))
    
    @classmethod
    def get_by_id(cls, type_id: int) -> Optional['StuffType']:
        """Get stuff type by ID."""
        row = db.fetch_one(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE id = ?",
            (type_id,)
        )
        return cls.from_row(row)
    
    @classmethod
    def get_by_name(cls, name: str) -> Optional['StuffType']:
        """Get stuff type by name."""
        row = db.fetch_one(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE name = ?",
            (name,)
        )
        return cls.from_row(row)
    
    @classmethod
    def get_all(cls) -> List['StuffType']:
        """Get all stuff types ordered by name."""
        rows = db.fetch_all(f"SELECT * FROM {cls.TABLE_NAME} ORDER BY name")
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_or_create(cls, name: str) -> 'StuffType':
        """Get existing stuff type or create new one."""
        existing = cls.get_by_name(name)
        if existing:
            return existing
        new_type = cls(name=name)
        new_type.save()
        return new_type
