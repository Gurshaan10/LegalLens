import pytest
import jwt
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import os
import sys

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models import User
from database import get_db, engine
from sqlalchemy.orm import sessionmaker

# Test client
client = TestClient(app)

# Mock Firebase Admin SDK
@pytest.fixture
def mock_firebase_admin():
    with patch('firebase_admin.auth') as mock_auth:
        yield mock_auth

@pytest.fixture
def mock_db_session():
    """Create a mock database session for testing"""
    with patch('database.get_db') as mock_get_db:
        mock_session = Mock()
        mock_get_db.return_value = mock_session
        yield mock_session

class TestAuthentication:
    """Test authentication flows"""
    
    def test_get_current_user_valid_token(self, mock_firebase_admin, mock_db_session):
        """Test successful user authentication with valid Firebase token"""
        # Mock Firebase token verification
        mock_firebase_admin.verify_id_token.return_value = {
            'uid': 'test_user_123',
            'email': 'test@example.com',
            'name': 'Test User'
        }
        
        # Mock database session
        mock_user = User(
            id=1,
            firebase_uid='test_user_123',
            email='test@example.com',
            name='Test User',
            credits=10
        )
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Create a mock request with authorization header
        mock_request = Mock()
        mock_request.headers = {'Authorization': 'Bearer valid_token_123'}
        
        # Test the function
        from main import get_current_user
        result = get_current_user(mock_request, mock_db_session)
        
        # Assertions
        assert result == mock_user
        mock_firebase_admin.verify_id_token.assert_called_once_with('valid_token_123')
    
    def test_get_current_user_invalid_token(self, mock_firebase_admin):
        """Test authentication failure with invalid token"""
        # Mock Firebase token verification failure
        mock_firebase_admin.verify_id_token.side_effect = Exception("Invalid token")
        
        # Create a mock request with invalid authorization header
        mock_request = Mock()
        mock_request.headers = {'Authorization': 'Bearer invalid_token'}
        
        # Test the function
        from main import get_current_user
        with pytest.raises(Exception):
            get_current_user(mock_request, Mock())
    
    def test_get_current_user_missing_header(self):
        """Test authentication failure with missing authorization header"""
        # Create a mock request without authorization header
        mock_request = Mock()
        mock_request.headers = {}
        
        # Test the function
        from main import get_current_user
        with pytest.raises(Exception):
            get_current_user(mock_request, Mock())
    
    def test_get_current_user_new_user_creation(self, mock_firebase_admin, mock_db_session):
        """Test creating a new user when they don't exist in database"""
        # Mock Firebase token verification
        mock_firebase_admin.verify_id_token.return_value = {
            'uid': 'new_user_456',
            'email': 'new@example.com',
            'name': 'New User'
        }
        
        # Mock database session - user doesn't exist initially
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Mock the new user that will be created
        mock_new_user = User(
            id=2,
            firebase_uid='new_user_456',
            email='new@example.com',
            name='New User',
            credits=1
        )
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None
        
        # Create a mock request
        mock_request = Mock()
        mock_request.headers = {'Authorization': 'Bearer valid_token_456'}
        
        # Test the function
        from main import get_current_user
        result = get_current_user(mock_request, mock_db_session)
        
        # Assertions
        assert result is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_me_endpoint_success(self, mock_firebase_admin, mock_db_session):
        """Test successful /me endpoint"""
        # Mock Firebase token verification
        mock_firebase_admin.verify_id_token.return_value = {
            'uid': 'test_user_123',
            'email': 'test@example.com'
        }
        
        # Mock user in database
        mock_user = User(
            id=1,
            firebase_uid='test_user_123',
            email='test@example.com',
            name='Test User',
            credits=10
        )
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Mock the get_current_user dependency
        with patch('main.get_current_user', return_value=mock_user):
            response = client.get('/me', headers={'Authorization': 'Bearer valid_token'})
            
            assert response.status_code == 200
            data = response.json()
            assert data['email'] == 'test@example.com'
            assert data['credits'] == 10
    
    def test_me_endpoint_unauthorized(self):
        """Test /me endpoint without authorization"""
        response = client.get('/me')
        assert response.status_code == 422  # Validation error for missing Authorization header

if __name__ == "__main__":
    pytest.main([__file__]) 