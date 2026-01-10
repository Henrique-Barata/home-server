"""
Tests for Reimbursement Model and Routes
-----------------------------------------
Unit tests for reimbursement functionality.
"""
import pytest
from datetime import date

from app.models.reimbursement import Reimbursement


class TestReimbursement:
    """Tests for Reimbursement model."""
    
    def test_create_reimbursement(self, app, test_db):
        """Test creating a reimbursement."""
        with app.app_context():
            reimbursement = Reimbursement(
                name='Coffee refund',
                amount=5.50,
                reimbursed_to='TestUser1',
                reimbursement_date=date(2024, 1, 15),
                notes='Bought wrong coffee'
            )
            reimbursement_id = reimbursement.save()
            
            assert reimbursement_id is not None
            assert reimbursement.id == reimbursement_id
    
    def test_get_reimbursement_by_id(self, app, test_db):
        """Test retrieving a reimbursement by ID."""
        with app.app_context():
            reimbursement = Reimbursement(
                name='Lunch refund',
                amount=12.00,
                reimbursed_to='TestUser2',
                reimbursement_date=date(2024, 1, 16)
            )
            reimbursement_id = reimbursement.save()
            
            retrieved = Reimbursement.get_by_id(reimbursement_id)
            
            assert retrieved is not None
            assert retrieved.name == 'Lunch refund'
            assert retrieved.amount == 12.00
    
    def test_update_reimbursement(self, app, test_db):
        """Test updating a reimbursement."""
        with app.app_context():
            reimbursement = Reimbursement(
                name='Original',
                amount=10.00,
                reimbursed_to='TestUser1',
                reimbursement_date=date(2024, 1, 17)
            )
            reimbursement.save()
            
            reimbursement.amount = 15.00
            reimbursement.name = 'Updated'
            reimbursement.save()
            
            retrieved = Reimbursement.get_by_id(reimbursement.id)
            assert retrieved.name == 'Updated'
            assert retrieved.amount == 15.00
    
    def test_delete_reimbursement(self, app, test_db):
        """Test deleting a reimbursement."""
        with app.app_context():
            reimbursement = Reimbursement(
                name='To delete',
                amount=5.00,
                reimbursed_to='TestUser1',
                reimbursement_date=date(2024, 1, 18)
            )
            reimbursement_id = reimbursement.save()
            
            reimbursement.delete()
            
            retrieved = Reimbursement.get_by_id(reimbursement_id)
            assert retrieved is None
    
    def test_get_all_reimbursements(self, app, test_db):
        """Test getting all reimbursements."""
        with app.app_context():
            for i in range(3):
                Reimbursement(
                    name=f'Reimbursement {i}',
                    amount=10.00 * (i + 1),
                    reimbursed_to='TestUser1',
                    reimbursement_date=date(2024, 1, 10 + i)
                ).save()
            
            all_reimbursements = Reimbursement.get_all()
            assert len(all_reimbursements) == 3
    
    def test_get_by_person(self, app, test_db):
        """Test getting reimbursements by person."""
        with app.app_context():
            Reimbursement(
                name='For User1',
                amount=10.00,
                reimbursed_to='TestUser1',
                reimbursement_date=date(2024, 1, 10)
            ).save()
            
            Reimbursement(
                name='For User2',
                amount=20.00,
                reimbursed_to='TestUser2',
                reimbursement_date=date(2024, 1, 11)
            ).save()
            
            user1_reimbursements = Reimbursement.get_by_person('TestUser1')
            user2_reimbursements = Reimbursement.get_by_person('TestUser2')
            
            assert len(user1_reimbursements) == 1
            assert len(user2_reimbursements) == 1
            assert user1_reimbursements[0].name == 'For User1'
    
    def test_get_total_by_person(self, app, test_db):
        """Test getting total reimbursements by person."""
        with app.app_context():
            Reimbursement(
                name='R1',
                amount=50.00,
                reimbursed_to='TestUser1',
                reimbursement_date=date(2024, 1, 10)
            ).save()
            
            Reimbursement(
                name='R2',
                amount=30.00,
                reimbursed_to='TestUser1',
                reimbursement_date=date(2024, 1, 11)
            ).save()
            
            total = Reimbursement.get_total_by_person('TestUser1')
            assert total == 80.00


class TestReimbursementRoutes:
    """Integration tests for reimbursement routes."""
    
    def test_reimbursement_index_accessible(self, authenticated_client):
        """Test reimbursement index page is accessible."""
        response = authenticated_client.get('/reimbursement/')
        assert response.status_code == 200
    
    def test_reimbursement_add_page(self, authenticated_client):
        """Test reimbursement add page is accessible."""
        response = authenticated_client.get('/reimbursement/add')
        assert response.status_code == 200
    
    def test_add_reimbursement_via_form(self, app, authenticated_client, test_db):
        """Test adding a reimbursement via form."""
        with app.app_context():
            response = authenticated_client.post('/reimbursement/add', data={
                'name': 'Test Reimbursement',
                'amount': '25.00',
                'reimbursed_to': 'TestUser1',
                'reimbursement_date': '2024-01-15',
                'notes': 'Test notes'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Verify reimbursement was created
            all_r = Reimbursement.get_all()
            assert len(all_r) == 1
            assert all_r[0].name == 'Test Reimbursement'
    
    def test_add_reimbursement_validation_empty_name(self, authenticated_client):
        """Test validation rejects empty name."""
        response = authenticated_client.post('/reimbursement/add', data={
            'name': '',
            'amount': '25.00',
            'reimbursed_to': 'TestUser1',
            'reimbursement_date': '2024-01-15'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'error' in response.data.lower() or b'required' in response.data.lower()
    
    def test_add_reimbursement_validation_invalid_amount(self, authenticated_client):
        """Test validation rejects invalid amount."""
        response = authenticated_client.post('/reimbursement/add', data={
            'name': 'Test',
            'amount': 'not-a-number',
            'reimbursed_to': 'TestUser1',
            'reimbursement_date': '2024-01-15'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should show an error
        assert b'error' in response.data.lower() or b'invalid' in response.data.lower()
    
    def test_by_person_page(self, app, authenticated_client, test_db):
        """Test by_person page shows person's reimbursements."""
        with app.app_context():
            # Create a reimbursement
            Reimbursement(
                name='For User1',
                amount=50.00,
                reimbursed_to='TestUser1',
                reimbursement_date=date(2024, 1, 15)
            ).save()
            
            response = authenticated_client.get('/reimbursement/person/TestUser1')
            assert response.status_code == 200
            assert b'TestUser1' in response.data
