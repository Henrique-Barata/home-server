"""
Tests for Expense Models
------------------------
Unit tests for the expense model classes.
"""
import pytest
from datetime import date, datetime

from app.models.expense import (
    Expense, FoodExpense, UtilityExpense, StuffExpense, OtherExpense
)


class TestFoodExpense:
    """Tests for FoodExpense model."""
    
    def test_create_food_expense(self, app, test_db):
        """Test creating a food expense."""
        with app.app_context():
            expense = FoodExpense(
                name='Groceries',
                amount=50.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 15)
            )
            expense_id = expense.save()
            
            assert expense_id is not None
            assert expense.id == expense_id
    
    def test_get_food_expense_by_id(self, app, test_db):
        """Test retrieving a food expense by ID."""
        with app.app_context():
            # Create expense
            expense = FoodExpense(
                name='Lunch',
                amount=15.50,
                paid_by='TestUser2',
                expense_date=date(2024, 1, 16)
            )
            expense_id = expense.save()
            
            # Retrieve it
            retrieved = FoodExpense.get_by_id(expense_id)
            
            assert retrieved is not None
            assert retrieved.name == 'Lunch'
            assert retrieved.amount == 15.50
            assert retrieved.paid_by == 'TestUser2'
    
    def test_update_food_expense(self, app, test_db):
        """Test updating a food expense."""
        with app.app_context():
            # Create expense
            expense = FoodExpense(
                name='Dinner',
                amount=25.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 17)
            )
            expense.save()
            
            # Update it
            expense.amount = 30.00
            expense.name = 'Fancy Dinner'
            expense.save()
            
            # Verify update
            retrieved = FoodExpense.get_by_id(expense.id)
            assert retrieved.name == 'Fancy Dinner'
            assert retrieved.amount == 30.00
    
    def test_delete_food_expense(self, app, test_db):
        """Test deleting a food expense."""
        with app.app_context():
            # Create expense
            expense = FoodExpense(
                name='Snacks',
                amount=10.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 18)
            )
            expense_id = expense.save()
            
            # Delete it
            expense.delete()
            
            # Verify deletion
            retrieved = FoodExpense.get_by_id(expense_id)
            assert retrieved is None
    
    def test_get_all_food_expenses(self, app, test_db):
        """Test getting all food expenses."""
        with app.app_context():
            # Create multiple expenses
            for i in range(3):
                expense = FoodExpense(
                    name=f'Food {i}',
                    amount=10.00 * (i + 1),
                    paid_by='TestUser1',
                    expense_date=date(2024, 1, 10 + i)
                )
                expense.save()
            
            # Get all
            all_expenses = FoodExpense.get_all()
            assert len(all_expenses) == 3
    
    def test_get_food_expenses_by_month(self, app, test_db):
        """Test getting food expenses by month."""
        with app.app_context():
            # Create expenses in different months
            FoodExpense(
                name='January Food',
                amount=100.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 15)
            ).save()
            
            FoodExpense(
                name='February Food',
                amount=200.00,
                paid_by='TestUser1',
                expense_date=date(2024, 2, 15)
            ).save()
            
            # Get by month
            jan_expenses = FoodExpense.get_by_month(2024, 1)
            feb_expenses = FoodExpense.get_by_month(2024, 2)
            
            assert len(jan_expenses) == 1
            assert jan_expenses[0].name == 'January Food'
            assert len(feb_expenses) == 1
            assert feb_expenses[0].name == 'February Food'
    
    def test_get_total_by_month(self, app, test_db):
        """Test getting total amount by month."""
        with app.app_context():
            # Create expenses
            FoodExpense(
                name='Food 1',
                amount=50.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 10)
            ).save()
            
            FoodExpense(
                name='Food 2',
                amount=75.00,
                paid_by='TestUser2',
                expense_date=date(2024, 1, 20)
            ).save()
            
            total = FoodExpense.get_total_by_month(2024, 1)
            assert total == 125.00
    
    def test_individual_only_expense(self, app, test_db):
        """Test individual_only flag on expenses."""
        with app.app_context():
            # Create individual expense
            expense = FoodExpense(
                name='Personal Snack',
                amount=5.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 15),
                individual_only=True
            )
            expense.save()
            
            retrieved = FoodExpense.get_by_id(expense.id)
            assert retrieved.individual_only is True


class TestUtilityExpense:
    """Tests for UtilityExpense model."""
    
    def test_create_utility_expense(self, app, test_db):
        """Test creating a utility expense with type."""
        with app.app_context():
            expense = UtilityExpense(
                name='Electricity Bill',
                amount=100.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 5),
                utility_type='Electricity'
            )
            expense_id = expense.save()
            
            retrieved = UtilityExpense.get_by_id(expense_id)
            assert retrieved.utility_type == 'Electricity'
    
    def test_get_by_utility_type(self, app, test_db):
        """Test getting expenses by utility type."""
        with app.app_context():
            UtilityExpense(
                name='Electric',
                amount=80.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 5),
                utility_type='Electricity'
            ).save()
            
            UtilityExpense(
                name='Water',
                amount=30.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 10),
                utility_type='Water'
            ).save()
            
            electric = UtilityExpense.get_by_type('Electricity')
            water = UtilityExpense.get_by_type('Water')
            
            assert len(electric) == 1
            assert len(water) == 1
            assert electric[0].name == 'Electric'


class TestStuffExpense:
    """Tests for StuffExpense model."""
    
    def test_create_stuff_expense(self, app, test_db):
        """Test creating a stuff expense with type."""
        with app.app_context():
            expense = StuffExpense(
                name='New Chair',
                amount=150.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 20),
                stuff_type='Furniture'
            )
            expense.save()
            
            retrieved = StuffExpense.get_by_id(expense.id)
            assert retrieved.stuff_type == 'Furniture'
            assert retrieved.name == 'New Chair'


class TestExpenseFromRow:
    """Tests for creating expenses from database rows."""
    
    def test_from_row_returns_none_for_none(self, app):
        """Test from_row returns None when given None."""
        with app.app_context():
            assert FoodExpense.from_row(None) is None
            assert UtilityExpense.from_row(None) is None
    
    def test_from_row_creates_expense(self, app):
        """Test from_row creates expense from dict."""
        with app.app_context():
            row = {
                'id': 1,
                'name': 'Test',
                'amount': 25.00,
                'paid_by': 'TestUser1',
                'expense_date': date(2024, 1, 15),
                'created_at': datetime.now(),
                'individual_only': 0
            }
            
            expense = FoodExpense.from_row(row)
            assert expense.id == 1
            assert expense.name == 'Test'
            assert expense.amount == 25.00
