"""
Tests for Search Functionality
-------------------------------
Unit tests for expense search feature.
"""
import pytest
from datetime import date

from app.models.expense import FoodExpense, StuffExpense
from app.models.travel import Travel, TravelExpense
from app.models.reimbursement import Reimbursement
from app.routes.search import search_all


class TestSearchFunction:
    """Tests for search_all function."""
    
    def test_search_returns_empty_for_short_query(self, app, test_db):
        """Test search returns empty for very short queries."""
        with app.app_context():
            result = search_all('a')
            assert result['results'] == []
            assert result['total'] == 0
    
    def test_search_returns_empty_for_empty_query(self, app, test_db):
        """Test search returns empty for empty query."""
        with app.app_context():
            result = search_all('')
            assert result['results'] == []
    
    def test_search_finds_food_expense_by_name(self, app, test_db):
        """Test search finds food expenses by name."""
        with app.app_context():
            FoodExpense(
                name='Weekly Groceries',
                amount=100.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 15)
            ).save()
            
            result = search_all('groceries')
            
            assert result['total'] >= 1
            assert any(r['name'] == 'Weekly Groceries' for r in result['results'])
    
    def test_search_finds_expense_by_person(self, app, test_db):
        """Test search finds expenses by person name."""
        with app.app_context():
            FoodExpense(
                name='Lunch',
                amount=15.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 16)
            ).save()
            
            result = search_all('TestUser1')
            
            assert result['total'] >= 1
    
    def test_search_finds_travel_by_name(self, app, test_db):
        """Test search finds travels by trip name."""
        with app.app_context():
            Travel(
                name='Paris Adventure',
                start_date=date(2024, 5, 1),
                end_date=date(2024, 5, 10),
                notes='Spring trip'
            ).save()
            
            result = search_all('Paris')
            
            assert result['total'] >= 1
            assert any('Paris' in r['name'] for r in result['results'])
    
    def test_search_finds_travel_expense(self, app, test_db):
        """Test search finds travel expenses."""
        with app.app_context():
            travel = Travel(
                name='Rome Trip',
                start_date=date(2024, 6, 1),
                end_date=date(2024, 6, 7)
            )
            travel.save()
            
            TravelExpense(
                travel_id=travel.id,
                name='Colosseum Tickets',
                amount=30.00,
                paid_by='TestUser1',
                category='Activities & Entertainment',
                expense_date=date(2024, 6, 3)
            ).save()
            
            result = search_all('Colosseum')
            
            assert result['total'] >= 1
    
    def test_search_finds_reimbursement(self, app, test_db):
        """Test search finds reimbursements."""
        with app.app_context():
            Reimbursement(
                name='Coffee Machine Refund',
                amount=50.00,
                reimbursed_to='TestUser1',
                reimbursement_date=date(2024, 2, 15)
            ).save()
            
            result = search_all('Coffee Machine')
            
            assert result['total'] >= 1
    
    def test_search_filters_by_type(self, app, test_db):
        """Test search filters by expense type."""
        with app.app_context():
            FoodExpense(
                name='Unique Item Food',
                amount=10.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 20)
            ).save()
            
            StuffExpense(
                name='Unique Item Stuff',
                amount=20.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 21),
                stuff_type='General'
            ).save()
            
            # Search all types
            all_result = search_all('Unique Item')
            assert all_result['total'] >= 2
            
            # Search only food
            food_result = search_all('Unique Item', types=['food'])
            assert all(r['type'] == 'food' for r in food_result['results'])
    
    def test_search_calculates_total_amount(self, app, test_db):
        """Test search calculates total amount of results."""
        with app.app_context():
            FoodExpense(
                name='Total Test 1',
                amount=50.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 25)
            ).save()
            
            FoodExpense(
                name='Total Test 2',
                amount=75.00,
                paid_by='TestUser1',
                expense_date=date(2024, 1, 26)
            ).save()
            
            result = search_all('Total Test')
            
            assert result['total_amount'] == 125.00


class TestSearchRoutes:
    """Integration tests for search routes."""
    
    def test_search_page_accessible(self, authenticated_client):
        """Test search page is accessible."""
        response = authenticated_client.get('/search/')
        assert response.status_code == 200
        assert b'Search' in response.data
    
    def test_search_with_query(self, app, authenticated_client, test_db):
        """Test search with a query parameter."""
        with app.app_context():
            FoodExpense(
                name='Searchable Pizza',
                amount=25.00,
                paid_by='TestUser1',
                expense_date=date(2024, 3, 15)
            ).save()
            
            response = authenticated_client.get('/search/?q=Pizza')
            
            assert response.status_code == 200
            assert b'Pizza' in response.data
    
    def test_search_no_results(self, authenticated_client):
        """Test search with no results."""
        response = authenticated_client.get('/search/?q=NonexistentThing12345')
        
        assert response.status_code == 200
        assert b'No results' in response.data or b'0' in response.data
    
    def test_search_with_type_filter(self, app, authenticated_client, test_db):
        """Test search with type filter."""
        with app.app_context():
            response = authenticated_client.get('/search/?q=test&type=food')
            
            assert response.status_code == 200
    
    def test_search_with_date_filter(self, app, authenticated_client, test_db):
        """Test search with date range filter."""
        with app.app_context():
            response = authenticated_client.get(
                '/search/?q=test&date_from=2024-01-01&date_to=2024-12-31'
            )
            
            assert response.status_code == 200
    
    def test_search_with_person_filter(self, app, authenticated_client, test_db):
        """Test search with person filter."""
        with app.app_context():
            response = authenticated_client.get('/search/?q=test&person=TestUser1')
            
            assert response.status_code == 200
