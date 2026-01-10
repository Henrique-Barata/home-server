"""
Tests for Budget Model and Routes
----------------------------------
Unit tests for budget functionality.
"""
import pytest
from datetime import date

from app.models.budget import (
    Budget, BudgetStatus, BUDGET_CATEGORIES,
    get_budget_status_for_month, get_all_categories_status
)


class TestBudget:
    """Tests for Budget model."""
    
    def test_create_budget(self, app, test_db):
        """Test creating a budget."""
        with app.app_context():
            budget = Budget(
                category='Food',
                monthly_limit=500.00,
                year=2024,
                month=1,
                notes='Test budget'
            )
            budget_id = budget.save()
            
            assert budget_id is not None
            assert budget.id == budget_id
    
    def test_get_budget_by_id(self, app, test_db):
        """Test retrieving a budget by ID."""
        with app.app_context():
            budget = Budget(
                category='Utilities',
                monthly_limit=200.00,
                year=2024,
                month=2
            )
            budget_id = budget.save()
            
            retrieved = Budget.get_by_id(budget_id)
            
            assert retrieved is not None
            assert retrieved.category == 'Utilities'
            assert retrieved.monthly_limit == 200.00
    
    def test_get_budget_by_category_and_month(self, app, test_db):
        """Test getting budget by category and month."""
        with app.app_context():
            Budget(
                category='Stuff',
                monthly_limit=300.00,
                year=2024,
                month=3
            ).save()
            
            found = Budget.get_by_category_and_month('Stuff', 2024, 3)
            not_found = Budget.get_by_category_and_month('Stuff', 2024, 4)
            
            assert found is not None
            assert found.monthly_limit == 300.00
            assert not_found is None
    
    def test_update_budget(self, app, test_db):
        """Test updating a budget."""
        with app.app_context():
            budget = Budget(
                category='Other',
                monthly_limit=100.00,
                year=2024,
                month=1
            )
            budget.save()
            
            budget.monthly_limit = 150.00
            budget.save()
            
            retrieved = Budget.get_by_id(budget.id)
            assert retrieved.monthly_limit == 150.00
    
    def test_delete_budget(self, app, test_db):
        """Test deleting a budget."""
        with app.app_context():
            budget = Budget(
                category='Travel',
                monthly_limit=1000.00,
                year=2024,
                month=6
            )
            budget_id = budget.save()
            
            budget.delete()
            
            retrieved = Budget.get_by_id(budget_id)
            assert retrieved is None
    
    def test_get_all_for_month(self, app, test_db):
        """Test getting all budgets for a month."""
        with app.app_context():
            # Create budgets for same month
            Budget(category='Food', monthly_limit=500, year=2024, month=5).save()
            Budget(category='Utilities', monthly_limit=200, year=2024, month=5).save()
            Budget(category='Other', monthly_limit=100, year=2024, month=5).save()
            
            # Create budget for different month
            Budget(category='Food', monthly_limit=600, year=2024, month=6).save()
            
            may_budgets = Budget.get_all_for_month(2024, 5)
            june_budgets = Budget.get_all_for_month(2024, 6)
            
            assert len(may_budgets) == 3
            assert len(june_budgets) == 1
    
    def test_copy_month_budgets(self, app, test_db):
        """Test copying budgets from one month to another."""
        with app.app_context():
            # Create source budgets
            Budget(category='Food', monthly_limit=500, year=2024, month=1).save()
            Budget(category='Utilities', monthly_limit=200, year=2024, month=1).save()
            
            # Copy to new month
            copied = Budget.copy_month_budgets(2024, 1, 2024, 2)
            
            assert copied == 2
            
            feb_budgets = Budget.get_all_for_month(2024, 2)
            assert len(feb_budgets) == 2
    
    def test_copy_month_budgets_skips_existing(self, app, test_db):
        """Test that copy doesn't override existing budgets."""
        with app.app_context():
            # Create source
            Budget(category='Food', monthly_limit=500, year=2024, month=1).save()
            
            # Create existing in target
            Budget(category='Food', monthly_limit=600, year=2024, month=2).save()
            
            # Try to copy
            copied = Budget.copy_month_budgets(2024, 1, 2024, 2)
            
            assert copied == 0
            
            # Verify original value preserved
            feb = Budget.get_by_category_and_month('Food', 2024, 2)
            assert feb.monthly_limit == 600


class TestBudgetStatus:
    """Tests for BudgetStatus calculations."""
    
    def test_budget_status_remaining(self):
        """Test remaining amount calculation."""
        status = BudgetStatus(
            category='Food',
            monthly_limit=500.00,
            spent=350.00,
            year=2024,
            month=1
        )
        
        assert status.remaining == 150.00
    
    def test_budget_status_percentage(self):
        """Test percentage used calculation."""
        status = BudgetStatus(
            category='Food',
            monthly_limit=500.00,
            spent=250.00,
            year=2024,
            month=1
        )
        
        assert status.percentage_used == 50.0
    
    def test_budget_status_over_budget(self):
        """Test over budget detection."""
        over = BudgetStatus(
            category='Food',
            monthly_limit=500.00,
            spent=600.00,
            year=2024,
            month=1
        )
        under = BudgetStatus(
            category='Food',
            monthly_limit=500.00,
            spent=400.00,
            year=2024,
            month=1
        )
        
        assert over.is_over_budget is True
        assert under.is_over_budget is False
    
    def test_budget_status_warning(self):
        """Test warning threshold (80-100%)."""
        warning = BudgetStatus(
            category='Food',
            monthly_limit=100.00,
            spent=85.00,
            year=2024,
            month=1
        )
        ok = BudgetStatus(
            category='Food',
            monthly_limit=100.00,
            spent=50.00,
            year=2024,
            month=1
        )
        over = BudgetStatus(
            category='Food',
            monthly_limit=100.00,
            spent=110.00,
            year=2024,
            month=1
        )
        
        assert warning.is_warning is True
        assert ok.is_warning is False
        assert over.is_warning is False  # Over is not warning
    
    def test_budget_status_css_class(self):
        """Test CSS class assignment."""
        ok = BudgetStatus('Food', 100, 50, 2024, 1)
        warning = BudgetStatus('Food', 100, 85, 2024, 1)
        over = BudgetStatus('Food', 100, 120, 2024, 1)
        
        assert ok.status_class == 'budget-ok'
        assert warning.status_class == 'budget-warning'
        assert over.status_class == 'budget-over'
    
    def test_budget_status_zero_limit(self):
        """Test handling of zero budget limit."""
        status = BudgetStatus(
            category='Food',
            monthly_limit=0,
            spent=100.00,
            year=2024,
            month=1
        )
        
        assert status.percentage_used == 100.0  # Spent with no limit = 100%


class TestBudgetRoutes:
    """Integration tests for budget routes."""
    
    def test_budget_index_accessible(self, authenticated_client):
        """Test budget index page is accessible."""
        response = authenticated_client.get('/budget/')
        assert response.status_code == 200
        assert b'Budget' in response.data
    
    def test_budget_add_page(self, authenticated_client):
        """Test budget add page is accessible."""
        response = authenticated_client.get('/budget/add')
        assert response.status_code == 200
    
    def test_budget_quick_setup_page(self, authenticated_client):
        """Test quick setup page is accessible."""
        response = authenticated_client.get('/budget/quick-setup')
        assert response.status_code == 200
    
    def test_add_budget_via_form(self, app, authenticated_client, test_db):
        """Test adding a budget via form."""
        with app.app_context():
            response = authenticated_client.post('/budget/add', data={
                'category': 'Food',
                'monthly_limit': '500.00',
                'year': '2024',
                'month': '1',
                'notes': 'Test'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Verify budget was created
            budget = Budget.get_by_category_and_month('Food', 2024, 1)
            assert budget is not None
            assert budget.monthly_limit == 500.00
