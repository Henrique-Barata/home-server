"""
Tests for User Model and Authentication
----------------------------------------
Unit tests for user authentication and password hashing.
"""
import pytest
from werkzeug.security import generate_password_hash

from app.models.user import User


class TestUser:
    """Tests for User model."""
    
    def test_user_get_valid_id(self, app):
        """Test getting user with valid ID."""
        with app.app_context():
            user = User.get('local_user')
            assert user is not None
            assert user.id == 'local_user'
    
    def test_user_get_invalid_id(self, app):
        """Test getting user with invalid ID returns None."""
        with app.app_context():
            user = User.get('invalid_user')
            assert user is None
    
    def test_user_is_authenticated(self, app):
        """Test user is_authenticated property."""
        with app.app_context():
            user = User('local_user')
            assert user.is_authenticated is True
    
    def test_authenticate_with_correct_plaintext_password(self, app):
        """Test authentication with correct plaintext password."""
        with app.app_context():
            # TestConfig has APP_PASSWORD = 'test-password'
            user = User.authenticate('test-password')
            assert user is not None
            assert user.id == 'local_user'
    
    def test_authenticate_with_wrong_password(self, app):
        """Test authentication with wrong password fails."""
        with app.app_context():
            user = User.authenticate('wrong-password')
            assert user is None
    
    def test_authenticate_with_empty_password(self, app):
        """Test authentication with empty password fails."""
        with app.app_context():
            user = User.authenticate('')
            assert user is None
    
    def test_authenticate_with_none_password(self, app):
        """Test authentication with None password fails."""
        with app.app_context():
            user = User.authenticate(None)
            assert user is None
    
    def test_is_hashed_password_detects_pbkdf2(self, app):
        """Test _is_hashed_password detects PBKDF2 hashes."""
        with app.app_context():
            hashed = generate_password_hash('test', method='pbkdf2:sha256')
            assert User._is_hashed_password(hashed) is True
    
    def test_is_hashed_password_rejects_plaintext(self, app):
        """Test _is_hashed_password rejects plaintext."""
        with app.app_context():
            assert User._is_hashed_password('plain-password') is False
            assert User._is_hashed_password('') is False
            assert User._is_hashed_password(None) is False
    
    def test_hash_password_creates_valid_hash(self, app):
        """Test hash_password creates a valid hash."""
        with app.app_context():
            password = 'my-secure-password'
            hashed = User.hash_password(password)
            
            assert hashed is not None
            assert hashed.startswith('pbkdf2:sha256:')
            assert User._is_hashed_password(hashed) is True


class TestUserAuthentication:
    """Integration tests for user authentication flows."""
    
    def test_login_page_accessible(self, client):
        """Test login page is accessible without authentication."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'password' in response.data.lower()
    
    def test_login_with_correct_password(self, client):
        """Test login with correct password redirects."""
        response = client.post('/login', data={
            'password': 'test-password'
        }, follow_redirects=False)
        
        # Should redirect on success
        assert response.status_code == 302
    
    def test_login_with_wrong_password_shows_error(self, client):
        """Test login with wrong password shows error."""
        response = client.post('/login', data={
            'password': 'wrong-password'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'incorrect' in response.data.lower() or b'error' in response.data.lower()
    
    def test_logout_redirects_to_login(self, authenticated_client):
        """Test logout redirects to login page."""
        response = authenticated_client.get('/logout', follow_redirects=False)
        
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_protected_page_requires_login(self, client):
        """Test protected pages redirect to login."""
        response = client.get('/', follow_redirects=False)
        
        assert response.status_code == 302
        assert 'login' in response.location.lower()
    
    def test_authenticated_user_can_access_dashboard(self, authenticated_client):
        """Test authenticated user can access dashboard."""
        response = authenticated_client.get('/')
        
        assert response.status_code == 200
