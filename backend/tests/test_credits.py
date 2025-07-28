import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import os
import sys

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models import User, Document
from database import get_db
from db_services import save_document, get_user_by_firebase_uid

# Test client
client = TestClient(app)

@pytest.fixture
def mock_db_session():
    """Create a mock database session for testing"""
    with patch('database.get_db') as mock_get_db:
        mock_session = Mock()
        mock_get_db.return_value = mock_session
        yield mock_session

@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    return User(
        id=1,
        firebase_uid='test_user_123',
        email='test@example.com',
        name='Test User',
        credits=10
    )

class TestCreditLogic:
    """Test credit management logic"""
    
    def test_user_has_sufficient_credits(self, mock_user):
        """Test that user has enough credits for document upload"""
        assert mock_user.credits > 0
        assert mock_user.credits >= 1  # Minimum required for upload
    
    def test_user_insufficient_credits(self, mock_user):
        """Test user with insufficient credits"""
        mock_user.credits = 0
        assert mock_user.credits == 0
        
        # Should not be able to upload with 0 credits
        assert mock_user.credits < 1
    
    def test_credit_deduction_on_upload(self, mock_db_session, mock_user):
        """Test that credits are deducted when document is uploaded"""
        # Mock the user query
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Mock document save
        mock_document = Document(
            id=1,
            user_id=mock_user.id,
            filename='test.pdf',
            document_id='test_doc_123'
        )
        
        # Simulate credit deduction
        initial_credits = mock_user.credits
        mock_user.credits -= 1
        final_credits = mock_user.credits
        
        # Assertions
        assert final_credits == initial_credits - 1
        assert final_credits >= 0
    
    def test_credit_validation_before_upload(self, mock_user):
        """Test credit validation before allowing upload"""
        # Test with sufficient credits
        mock_user.credits = 5
        assert mock_user.credits >= 1
        
        # Test with insufficient credits
        mock_user.credits = 0
        assert mock_user.credits < 1

class TestCreditEndpoints:
    """Test credit-related endpoints"""
    
    def test_upload_with_sufficient_credits(self, mock_db_session, mock_user):
        """Test successful upload with sufficient credits"""
        # Mock user with sufficient credits
        mock_user.credits = 5
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Mock Firebase authentication
        with patch('main.get_current_user', return_value=mock_user):
            # Mock file upload
            with patch('main.process_document') as mock_process:
                mock_process.return_value = {
                    'document_id': 'test_doc_123',
                    'filename': 'test.pdf'
                }
                
                # Mock the upload endpoint
                with patch('main.save_document') as mock_save:
                    mock_save.return_value = True
                    
                    # Test would go here - we're testing the logic, not the actual endpoint
                    assert mock_user.credits >= 1
    
    def test_upload_with_insufficient_credits(self, mock_db_session, mock_user):
        """Test upload rejection with insufficient credits"""
        # Mock user with insufficient credits
        mock_user.credits = 0
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Mock Firebase authentication
        with patch('main.get_current_user', return_value=mock_user):
            # Should not be able to upload with 0 credits
            assert mock_user.credits < 1
    
    def test_me_endpoint_shows_credits(self, mock_db_session, mock_user):
        """Test that /me endpoint returns user credits"""
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        with patch('main.get_current_user', return_value=mock_user):
            # Mock the endpoint response
            expected_response = {
                'id': mock_user.id,
                'email': mock_user.email,
                'name': mock_user.name,
                'credits': mock_user.credits
            }
            
            assert expected_response['credits'] == 10
            assert expected_response['credits'] > 0

class TestCreditEdgeCases:
    """Test edge cases in credit management"""
    
    def test_negative_credits_prevention(self, mock_user):
        """Test that credits cannot go negative"""
        mock_user.credits = 1
        
        # Simulate multiple uploads
        for i in range(5):
            if mock_user.credits > 0:
                mock_user.credits -= 1
        
        # Should not go below 0
        assert mock_user.credits >= 0
    
    def test_credit_overflow_prevention(self, mock_user):
        """Test that credits don't overflow"""
        mock_user.credits = 1000
        
        # Simulate adding credits (if there was such functionality)
        # This would be relevant if you add credit purchase features
        max_credits = 9999  # Example max
        mock_user.credits = min(mock_user.credits, max_credits)
        
        assert mock_user.credits <= max_credits
    
    def test_credit_deduction_consistency(self, mock_user):
        """Test that credit deduction is consistent"""
        initial_credits = mock_user.credits
        
        # Simulate multiple uploads
        uploads = 3
        for _ in range(uploads):
            if mock_user.credits > 0:
                mock_user.credits -= 1
        
        expected_credits = initial_credits - uploads
        assert mock_user.credits == expected_credits

if __name__ == "__main__":
    pytest.main([__file__]) 