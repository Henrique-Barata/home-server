"""
Tests for Travel Model and Routes
----------------------------------
Unit tests for travel functionality.
"""
import pytest
from datetime import date

from app.models.travel import Travel, TravelExpense, TRAVEL_EXPENSE_CATEGORIES


class TestTravel:
    """Tests for Travel model."""
    
    def test_create_travel(self, app, test_db):
        """Test creating a travel."""
        with app.app_context():
            travel = Travel(
                name='Summer Vacation',
                start_date=date(2024, 7, 1),
                end_date=date(2024, 7, 15),
                notes='Beach trip'
            )
            travel_id = travel.save()
            
            assert travel_id is not None
            assert travel.id == travel_id
    
    def test_get_travel_by_id(self, app, test_db):
        """Test retrieving a travel by ID."""
        with app.app_context():
            travel = Travel(
                name='Weekend Trip',
                start_date=date(2024, 3, 15),
                end_date=date(2024, 3, 17)
            )
            travel_id = travel.save()
            
            retrieved = Travel.get_by_id(travel_id)
            
            assert retrieved is not None
            assert retrieved.name == 'Weekend Trip'
    
    def test_update_travel(self, app, test_db):
        """Test updating a travel."""
        with app.app_context():
            travel = Travel(
                name='Original Trip',
                start_date=date(2024, 4, 1),
                end_date=date(2024, 4, 5)
            )
            travel.save()
            
            travel.name = 'Updated Trip'
            travel.notes = 'New notes'
            travel.save()
            
            retrieved = Travel.get_by_id(travel.id)
            assert retrieved.name == 'Updated Trip'
            assert retrieved.notes == 'New notes'
    
    def test_delete_travel(self, app, test_db):
        """Test deleting a travel."""
        with app.app_context():
            travel = Travel(
                name='To Delete',
                start_date=date(2024, 5, 1),
                end_date=date(2024, 5, 3)
            )
            travel_id = travel.save()
            
            travel.delete()
            
            retrieved = Travel.get_by_id(travel_id)
            assert retrieved is None
    
    def test_get_all_travels(self, app, test_db):
        """Test getting all travels."""
        with app.app_context():
            for i in range(3):
                Travel(
                    name=f'Trip {i}',
                    start_date=date(2024, 1 + i, 1),
                    end_date=date(2024, 1 + i, 5)
                ).save()
            
            all_travels = Travel.get_all()
            assert len(all_travels) == 3
    
    def test_get_travel_by_year(self, app, test_db):
        """Test getting travels by year."""
        with app.app_context():
            Travel(
                name='Trip 2024',
                start_date=date(2024, 6, 1),
                end_date=date(2024, 6, 5)
            ).save()
            
            Travel(
                name='Trip 2023',
                start_date=date(2023, 6, 1),
                end_date=date(2023, 6, 5)
            ).save()
            
            travels_2024 = Travel.get_by_year(2024)
            travels_2023 = Travel.get_by_year(2023)
            
            assert len(travels_2024) == 1
            assert len(travels_2023) == 1
            assert travels_2024[0].name == 'Trip 2024'
    
    def test_travel_duration(self, app, test_db):
        """Test travel duration calculation."""
        with app.app_context():
            travel = Travel(
                name='Week Trip',
                start_date=date(2024, 7, 1),
                end_date=date(2024, 7, 7)
            )
            travel.save()
            
            assert travel.duration == 7  # Including both start and end


class TestTravelExpense:
    """Tests for TravelExpense model."""
    
    def test_create_travel_expense(self, app, test_db):
        """Test creating a travel expense."""
        with app.app_context():
            # First create a travel
            travel = Travel(
                name='Test Trip',
                start_date=date(2024, 8, 1),
                end_date=date(2024, 8, 10)
            )
            travel.save()
            
            expense = TravelExpense(
                travel_id=travel.id,
                name='Hotel',
                amount=200.00,
                paid_by='TestUser1',
                category='Accommodation',
                expense_date=date(2024, 8, 1)
            )
            expense_id = expense.save()
            
            assert expense_id is not None
    
    def test_get_travel_expense_by_id(self, app, test_db):
        """Test retrieving a travel expense by ID."""
        with app.app_context():
            travel = Travel(
                name='Test Trip',
                start_date=date(2024, 8, 1),
                end_date=date(2024, 8, 10)
            )
            travel.save()
            
            expense = TravelExpense(
                travel_id=travel.id,
                name='Flight',
                amount=500.00,
                paid_by='TestUser2',
                category='Transportation',
                expense_date=date(2024, 8, 1)
            )
            expense.save()
            
            retrieved = TravelExpense.get_by_id(expense.id)
            assert retrieved is not None
            assert retrieved.name == 'Flight'
            assert retrieved.category == 'Transportation'
    
    def test_get_expenses_by_travel(self, app, test_db):
        """Test getting expenses for a travel."""
        with app.app_context():
            travel = Travel(
                name='Multi Expense Trip',
                start_date=date(2024, 9, 1),
                end_date=date(2024, 9, 5)
            )
            travel.save()
            
            TravelExpense(
                travel_id=travel.id,
                name='Hotel',
                amount=300.00,
                paid_by='TestUser1',
                category='Accommodation',
                expense_date=date(2024, 9, 1)
            ).save()
            
            TravelExpense(
                travel_id=travel.id,
                name='Dinner',
                amount=50.00,
                paid_by='TestUser1',
                category='Food & Dining',
                expense_date=date(2024, 9, 2)
            ).save()
            
            expenses = TravelExpense.get_by_travel(travel.id)
            assert len(expenses) == 2
    
    def test_travel_get_total(self, app, test_db):
        """Test getting total expenses for a travel."""
        with app.app_context():
            travel = Travel(
                name='Expense Totals',
                start_date=date(2024, 10, 1),
                end_date=date(2024, 10, 5)
            )
            travel.save()
            
            TravelExpense(
                travel_id=travel.id,
                name='E1',
                amount=100.00,
                paid_by='TestUser1',
                category='Transportation',
                expense_date=date(2024, 10, 1)
            ).save()
            
            TravelExpense(
                travel_id=travel.id,
                name='E2',
                amount=200.00,
                paid_by='TestUser2',
                category='Accommodation',
                expense_date=date(2024, 10, 2)
            ).save()
            
            total = travel.get_total()
            assert total == 300.00
    
    def test_travel_expense_categories(self):
        """Test travel expense categories are defined."""
        assert 'Transportation' in TRAVEL_EXPENSE_CATEGORIES
        assert 'Accommodation' in TRAVEL_EXPENSE_CATEGORIES
        assert 'Food & Dining' in TRAVEL_EXPENSE_CATEGORIES
    
    def test_get_total_by_month(self, app, test_db):
        """Test getting total travel expenses by month."""
        with app.app_context():
            travel = Travel(
                name='Monthly Test',
                start_date=date(2024, 11, 1),
                end_date=date(2024, 11, 30)
            )
            travel.save()
            
            TravelExpense(
                travel_id=travel.id,
                name='Nov Expense',
                amount=150.00,
                paid_by='TestUser1',
                category='Miscellaneous',
                expense_date=date(2024, 11, 15)
            ).save()
            
            nov_total = TravelExpense.get_total_by_month(2024, 11)
            dec_total = TravelExpense.get_total_by_month(2024, 12)
            
            assert nov_total == 150.00
            assert dec_total == 0.00


class TestTravelRoutes:
    """Integration tests for travel routes."""
    
    def test_travel_index_accessible(self, authenticated_client):
        """Test travel index page is accessible."""
        response = authenticated_client.get('/travel/')
        assert response.status_code == 200
    
    def test_travel_add_page(self, authenticated_client):
        """Test travel add page is accessible."""
        response = authenticated_client.get('/travel/add')
        assert response.status_code == 200
    
    def test_add_travel_via_form(self, app, authenticated_client, test_db):
        """Test adding a travel via form."""
        with app.app_context():
            response = authenticated_client.post('/travel/add', data={
                'name': 'Form Test Trip',
                'start_date': '2024-12-01',
                'end_date': '2024-12-10',
                'notes': 'Added via form'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            travels = Travel.get_all()
            assert len(travels) == 1
            assert travels[0].name == 'Form Test Trip'
    
    def test_travel_detail_page(self, app, authenticated_client, test_db):
        """Test travel detail page."""
        with app.app_context():
            travel = Travel(
                name='Detail Test',
                start_date=date(2024, 12, 15),
                end_date=date(2024, 12, 20)
            )
            travel.save()
            
            response = authenticated_client.get(f'/travel/{travel.id}')
            assert response.status_code == 200
            assert b'Detail Test' in response.data
    
    def test_add_expense_to_travel(self, app, authenticated_client, test_db):
        """Test adding an expense to a travel."""
        with app.app_context():
            travel = Travel(
                name='Expense Test Trip',
                start_date=date(2024, 12, 1),
                end_date=date(2024, 12, 5)
            )
            travel.save()
            
            response = authenticated_client.post(
                f'/travel/{travel.id}/expense/add',
                data={
                    'name': 'Test Expense',
                    'amount': '75.00',
                    'paid_by': 'TestUser1',
                    'category': 'Transportation',
                    'expense_date': '2024-12-02',
                    'notes': ''
                },
                follow_redirects=True
            )
            
            assert response.status_code == 200
            
            expenses = TravelExpense.get_by_travel(travel.id)
            assert len(expenses) == 1
            assert expenses[0].name == 'Test Expense'
