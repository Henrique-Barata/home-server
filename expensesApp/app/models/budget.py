"""
Budget Model
------------
Monthly budget limits for expense categories.
Supports tracking spending against defined limits.
"""
import logging
from datetime import date
from typing import List, Optional, Dict
from .database import db

logger = logging.getLogger(__name__)


# Valid expense categories for budgets
BUDGET_CATEGORIES = [
    'Food',
    'Utilities',
    'Stuff',
    'Other',
    'Fixed',
    'Travel'
]


class Budget:
    """
    Monthly budget for an expense category.
    
    Attributes:
        id: Unique identifier
        category: Expense category (Food, Utilities, Stuff, Other, Fixed, Travel)
        monthly_limit: Budget limit in euros
        year: Year the budget applies to
        month: Month the budget applies to (1-12)
        notes: Optional notes about the budget
    """
    
    TABLE_NAME = "budgets"
    
    def __init__(
        self,
        id: int = None,
        category: str = "",
        monthly_limit: float = 0.0,
        year: int = None,
        month: int = None,
        notes: str = ""
    ):
        self.id = id
        self.category = category
        self.monthly_limit = monthly_limit
        self.year = year or date.today().year
        self.month = month or date.today().month
        self.notes = notes
    
    @classmethod
    def from_row(cls, row: dict) -> Optional['Budget']:
        """Create Budget instance from database row."""
        if not row:
            return None
        return cls(
            id=row.get('id'),
            category=row.get('category', ''),
            monthly_limit=row.get('monthly_limit', 0.0),
            year=row.get('year'),
            month=row.get('month'),
            notes=row.get('notes', '')
        )
    
    def save(self) -> int:
        """Save budget to database. Returns ID."""
        if self.id:
            return self._update()
        return self._insert()
    
    def _insert(self) -> int:
        """Insert new budget."""
        with db.transaction() as conn:
            cursor = conn.execute(
                f"""INSERT INTO {self.TABLE_NAME} 
                    (category, monthly_limit, year, month, notes)
                    VALUES (?, ?, ?, ?, ?)""",
                (self.category, self.monthly_limit, self.year, self.month, self.notes)
            )
            self.id = cursor.lastrowid
            logger.info(f"Created budget: {self.category} for {self.year}/{self.month:02d} - €{self.monthly_limit}")
        return self.id
    
    def _update(self) -> int:
        """Update existing budget."""
        with db.transaction():
            db.execute(
                f"""UPDATE {self.TABLE_NAME}
                    SET category = ?, monthly_limit = ?, year = ?, month = ?, notes = ?
                    WHERE id = ?""",
                (self.category, self.monthly_limit, self.year, self.month, self.notes, self.id)
            )
            logger.info(f"Updated budget ID {self.id}: {self.category} for {self.year}/{self.month:02d} - €{self.monthly_limit}")
        return self.id
    
    def delete(self):
        """Delete budget from database."""
        with db.transaction():
            db.execute(f"DELETE FROM {self.TABLE_NAME} WHERE id = ?", (self.id,))
            logger.info(f"Deleted budget ID {self.id}: {self.category} for {self.year}/{self.month:02d}")
    
    @classmethod
    def get_by_id(cls, budget_id: int) -> Optional['Budget']:
        """Get budget by ID."""
        row = db.fetch_one(
            f"SELECT * FROM {cls.TABLE_NAME} WHERE id = ?",
            (budget_id,)
        )
        return cls.from_row(row)
    
    @classmethod
    def get_by_category_and_month(
        cls,
        category: str,
        year: int,
        month: int
    ) -> Optional['Budget']:
        """Get budget for a specific category and month."""
        row = db.fetch_one(
            f"""SELECT * FROM {cls.TABLE_NAME}
                WHERE category = ? AND year = ? AND month = ?""",
            (category, year, month)
        )
        return cls.from_row(row)
    
    @classmethod
    def get_all_for_month(cls, year: int, month: int) -> List['Budget']:
        """Get all budgets for a specific month."""
        rows = db.fetch_all(
            f"""SELECT * FROM {cls.TABLE_NAME}
                WHERE year = ? AND month = ?
                ORDER BY category""",
            (year, month)
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def get_all(cls, limit: int = 100) -> List['Budget']:
        """Get all budgets ordered by date descending."""
        rows = db.fetch_all(
            f"""SELECT * FROM {cls.TABLE_NAME}
                ORDER BY year DESC, month DESC, category
                LIMIT ?""",
            (limit,)
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    def copy_month_budgets(
        cls,
        from_year: int,
        from_month: int,
        to_year: int,
        to_month: int
    ) -> int:
        """
        Copy all budgets from one month to another.
        Returns the number of budgets copied.
        Skips categories that already have a budget in the target month.
        """
        source_budgets = cls.get_all_for_month(from_year, from_month)
        copied_count = 0
        
        for budget in source_budgets:
            # Check if budget already exists for this category in target month
            existing = cls.get_by_category_and_month(budget.category, to_year, to_month)
            if not existing:
                new_budget = cls(
                    category=budget.category,
                    monthly_limit=budget.monthly_limit,
                    year=to_year,
                    month=to_month,
                    notes=budget.notes
                )
                new_budget.save()
                copied_count += 1
        
        logger.info(f"Copied {copied_count} budgets from {from_year}/{from_month:02d} to {to_year}/{to_month:02d}")
        return copied_count


class BudgetStatus:
    """
    Represents the spending status against a budget.
    Calculated from budget and actual spending.
    """
    
    def __init__(
        self,
        category: str,
        monthly_limit: float,
        spent: float,
        year: int,
        month: int,
        budget_id: int = None
    ):
        self.category = category
        self.monthly_limit = monthly_limit
        self.spent = spent
        self.year = year
        self.month = month
        self.budget_id = budget_id
    
    @property
    def remaining(self) -> float:
        """Amount remaining in budget (can be negative if overspent)."""
        return self.monthly_limit - self.spent
    
    @property
    def percentage_used(self) -> float:
        """Percentage of budget used (0-100+)."""
        if self.monthly_limit <= 0:
            return 100.0 if self.spent > 0 else 0.0
        return (self.spent / self.monthly_limit) * 100
    
    @property
    def is_over_budget(self) -> bool:
        """True if spending exceeds budget."""
        return self.spent > self.monthly_limit
    
    @property
    def is_warning(self) -> bool:
        """True if spending is over 80% of budget but not over."""
        return 80 <= self.percentage_used < 100
    
    @property
    def status_class(self) -> str:
        """CSS class for status display."""
        if self.is_over_budget:
            return "budget-over"
        elif self.is_warning:
            return "budget-warning"
        return "budget-ok"


def get_category_spending(category: str, year: int, month: int) -> float:
    """
    Get total spending for a category in a specific month.
    This aggregates from the appropriate expense table(s).
    """
    from .expense import FoodExpense, UtilityExpense, StuffExpense, OtherExpense
    from .fixed_expense import FixedExpense
    from .travel import TravelExpense
    
    category_map = {
        'Food': FoodExpense,
        'Utilities': UtilityExpense,
        'Stuff': StuffExpense,
        'Other': OtherExpense,
        'Fixed': FixedExpense,
    }
    
    if category in category_map:
        return category_map[category].get_total_by_month(year, month)
    elif category == 'Travel':
        return TravelExpense.get_total_by_month(year, month)
    else:
        logger.warning(f"Unknown budget category: {category}")
        return 0.0


def get_budget_status_for_month(year: int, month: int) -> List[BudgetStatus]:
    """
    Get budget status for all categories in a month.
    Returns BudgetStatus objects for each category with a budget.
    """
    budgets = Budget.get_all_for_month(year, month)
    statuses = []
    
    for budget in budgets:
        spent = get_category_spending(budget.category, year, month)
        statuses.append(BudgetStatus(
            category=budget.category,
            monthly_limit=budget.monthly_limit,
            spent=spent,
            year=year,
            month=month,
            budget_id=budget.id
        ))
    
    return statuses


def get_all_categories_status(year: int, month: int) -> Dict[str, BudgetStatus]:
    """
    Get budget status for ALL categories (including those without budgets).
    Returns a dict mapping category name to BudgetStatus.
    Categories without budgets will have monthly_limit=0.
    """
    budgets = {b.category: b for b in Budget.get_all_for_month(year, month)}
    statuses = {}
    
    for category in BUDGET_CATEGORIES:
        budget = budgets.get(category)
        spent = get_category_spending(category, year, month)
        
        statuses[category] = BudgetStatus(
            category=category,
            monthly_limit=budget.monthly_limit if budget else 0.0,
            spent=spent,
            year=year,
            month=month,
            budget_id=budget.id if budget else None
        )
    
    return statuses
