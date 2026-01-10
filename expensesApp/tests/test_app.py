"""
Tests for Application Factory
------------------------------
Tests for app creation and configuration.
"""
import pytest

from app import create_app
from app.config import Config, DevelopmentConfig


class TestAppFactory:
    """Tests for application factory."""
    
    def test_app_is_created(self, app):
        """Test application is created successfully."""
        assert app is not None
    
    def test_app_is_testing(self, app):
        """Test application is in testing mode."""
        assert app.testing is True
    
    def test_config_is_loaded(self, app):
        """Test configuration is loaded."""
        assert app.config['SECRET_KEY'] is not None
    
    def test_blueprints_registered(self, app):
        """Test all blueprints are registered."""
        expected_blueprints = [
            'auth', 'dashboard', 'food', 'utilities', 
            'fixed', 'stuff', 'other', 'log', 'export',
            'reimbursement', 'travel', 'budget', 'search'
        ]
        
        for bp_name in expected_blueprints:
            assert bp_name in app.blueprints, f"Blueprint '{bp_name}' not registered"
    
    def test_login_manager_configured(self, app):
        """Test Flask-Login is configured."""
        assert app.login_manager is not None
        assert app.login_manager.login_view == 'auth.login'


class TestRoutes:
    """Basic route tests."""
    
    def test_index_redirects_to_login(self, client):
        """Test index redirects to login when not authenticated."""
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.location.lower()
    
    def test_login_page_accessible(self, client):
        """Test login page is accessible."""
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_dashboard_accessible_when_authenticated(self, authenticated_client):
        """Test dashboard is accessible when authenticated."""
        response = authenticated_client.get('/')
        assert response.status_code == 200
    
    def test_food_index_accessible(self, authenticated_client):
        """Test food index is accessible."""
        response = authenticated_client.get('/food/')
        assert response.status_code == 200
    
    def test_utilities_index_accessible(self, authenticated_client):
        """Test utilities index is accessible."""
        response = authenticated_client.get('/utilities/')
        assert response.status_code == 200
    
    def test_fixed_index_accessible(self, authenticated_client):
        """Test fixed index is accessible."""
        response = authenticated_client.get('/fixed/')
        assert response.status_code == 200
    
    def test_stuff_index_accessible(self, authenticated_client):
        """Test stuff index is accessible."""
        response = authenticated_client.get('/stuff/')
        assert response.status_code == 200
    
    def test_other_index_accessible(self, authenticated_client):
        """Test other index is accessible."""
        response = authenticated_client.get('/other/')
        assert response.status_code == 200
    
    def test_404_for_invalid_route(self, authenticated_client):
        """Test 404 for invalid routes."""
        response = authenticated_client.get('/nonexistent-page-12345')
        assert response.status_code == 404
