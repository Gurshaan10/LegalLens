import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import os
import sys
import json

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models import User, Document, DocumentQuery
from database import get_db

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

@pytest.fixture
def mock_document():
    """Create a mock document for testing"""
    return Document(
        id=1,
        user_id=1,
        filename='test_document.pdf',
        document_id='test_doc_123',
        title='Test Document'
    )

class TestQAEndpoint:
    """Test the QA endpoint functionality"""
    
    def test_qa_endpoint_success(self, mock_db_session, mock_user, mock_document):
        """Test successful QA query"""
        # Mock database queries
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [
            mock_user,  # get_current_user
            mock_document  # get_document
        ]
        
        # Mock OpenAI API call
        mock_openai_response = {
            'choices': [{
                'message': {
                    'content': 'This is a legal document containing standard terms and conditions.'
                }
            }]
        }
        
        with patch('main.get_current_user', return_value=mock_user):
            with patch('openai.ChatCompletion.create', return_value=mock_openai_response):
                with patch('main.load_vector_store') as mock_load_vector:
                    mock_load_vector.return_value = Mock()
                    
                    response = client.post(
                        '/query/test_doc_123',
                        headers={'Authorization': 'Bearer valid_token'},
                        json={'query': 'What type of document is this?'}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert 'response' in data
                    assert 'query_id' in data
    
    def test_qa_endpoint_document_not_found(self, mock_db_session, mock_user):
        """Test QA endpoint when document doesn't exist"""
        # Mock user exists but document doesn't
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [
            mock_user,  # get_current_user
            None  # get_document - document not found
        ]
        
        with patch('main.get_current_user', return_value=mock_user):
            response = client.post(
                '/query/nonexistent_doc',
                headers={'Authorization': 'Bearer valid_token'},
                json={'query': 'What type of document is this?'}
            )
            
            assert response.status_code == 404
    
    def test_qa_endpoint_unauthorized(self):
        """Test QA endpoint without authorization"""
        response = client.post(
            '/query/test_doc_123',
            json={'query': 'What type of document is this?'}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_qa_endpoint_invalid_query(self, mock_db_session, mock_user, mock_document):
        """Test QA endpoint with invalid query format"""
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [
            mock_user,
            mock_document
        ]
        
        with patch('main.get_current_user', return_value=mock_user):
            # Test with missing query
            response = client.post(
                '/query/test_doc_123',
                headers={'Authorization': 'Bearer valid_token'},
                json={}
            )
            
            assert response.status_code == 422
    
    def test_qa_endpoint_openai_error(self, mock_db_session, mock_user, mock_document):
        """Test QA endpoint when OpenAI API fails"""
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [
            mock_user,
            mock_document
        ]
        
        with patch('main.get_current_user', return_value=mock_user):
            with patch('openai.ChatCompletion.create', side_effect=Exception("OpenAI API Error")):
                with patch('main.load_vector_store') as mock_load_vector:
                    mock_load_vector.return_value = Mock()
                    
                    response = client.post(
                        '/query/test_doc_123',
                        headers={'Authorization': 'Bearer valid_token'},
                        json={'query': 'What type of document is this?'}
                    )
                    
                    assert response.status_code == 500
    
    def test_qa_endpoint_vector_store_error(self, mock_db_session, mock_user, mock_document):
        """Test QA endpoint when vector store fails to load"""
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [
            mock_user,
            mock_document
        ]
        
        with patch('main.get_current_user', return_value=mock_user):
            with patch('main.load_vector_store', side_effect=Exception("Vector store error")):
                response = client.post(
                    '/query/test_doc_123',
                    headers={'Authorization': 'Bearer valid_token'},
                    json={'query': 'What type of document is this?'}
                )
                
                assert response.status_code == 500

class TestQAResponseFormat:
    """Test QA response format and content"""
    
    def test_qa_response_structure(self, mock_db_session, mock_user, mock_document):
        """Test that QA response has correct structure"""
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [
            mock_user,
            mock_document
        ]
        
        mock_openai_response = {
            'choices': [{
                'message': {
                    'content': 'This document contains standard legal terms and conditions.'
                }
            }]
        }
        
        with patch('main.get_current_user', return_value=mock_user):
            with patch('openai.ChatCompletion.create', return_value=mock_openai_response):
                with patch('main.load_vector_store') as mock_load_vector:
                    mock_load_vector.return_value = Mock()
                    
                    response = client.post(
                        '/query/test_doc_123',
                        headers={'Authorization': 'Bearer valid_token'},
                        json={'query': 'What type of document is this?'}
                    )
                    
                    data = response.json()
                    
                    # Check response structure
                    assert 'response' in data
                    assert 'query_id' in data
                    assert isinstance(data['response'], str)
                    assert isinstance(data['query_id'], str)
    
    def test_qa_response_content_validation(self, mock_db_session, mock_user, mock_document):
        """Test that QA response contains expected content"""
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [
            mock_user,
            mock_document
        ]
        
        expected_content = "This is a legal document analysis response."
        mock_openai_response = {
            'choices': [{
                'message': {
                    'content': expected_content
                }
            }]
        }
        
        with patch('main.get_current_user', return_value=mock_user):
            with patch('openai.ChatCompletion.create', return_value=mock_openai_response):
                with patch('main.load_vector_store') as mock_load_vector:
                    mock_load_vector.return_value = Mock()
                    
                    response = client.post(
                        '/query/test_doc_123',
                        headers={'Authorization': 'Bearer valid_token'},
                        json={'query': 'What type of document is this?'}
                    )
                    
                    data = response.json()
                    assert data['response'] == expected_content

class TestQAIntegration:
    """Integration tests for QA functionality"""
    
    def test_qa_query_saved_to_database(self, mock_db_session, mock_user, mock_document):
        """Test that QA queries are saved to database"""
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [
            mock_user,
            mock_document
        ]
        
        mock_openai_response = {
            'choices': [{
                'message': {
                    'content': 'Legal document analysis response.'
                }
            }]
        }
        
        with patch('main.get_current_user', return_value=mock_user):
            with patch('openai.ChatCompletion.create', return_value=mock_openai_response):
                with patch('main.load_vector_store') as mock_load_vector:
                    mock_load_vector.return_value = Mock()
                    
                    response = client.post(
                        '/query/test_doc_123',
                        headers={'Authorization': 'Bearer valid_token'},
                        json={'query': 'What type of document is this?'}
                    )
                    
                    # Verify that database operations were called
                    assert mock_db_session.add.called
                    assert mock_db_session.commit.called
    
    def test_qa_multiple_queries_same_document(self, mock_db_session, mock_user, mock_document):
        """Test multiple queries on the same document"""
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [
            mock_user,
            mock_document
        ]
        
        mock_openai_response = {
            'choices': [{
                'message': {
                    'content': 'Legal document analysis response.'
                }
            }]
        }
        
        with patch('main.get_current_user', return_value=mock_user):
            with patch('openai.ChatCompletion.create', return_value=mock_openai_response):
                with patch('main.load_vector_store') as mock_load_vector:
                    mock_load_vector.return_value = Mock()
                    
                    # First query
                    response1 = client.post(
                        '/query/test_doc_123',
                        headers={'Authorization': 'Bearer valid_token'},
                        json={'query': 'What type of document is this?'}
                    )
                    
                    # Second query
                    response2 = client.post(
                        '/query/test_doc_123',
                        headers={'Authorization': 'Bearer valid_token'},
                        json={'query': 'What are the key terms?'}
                    )
                    
                    assert response1.status_code == 200
                    assert response2.status_code == 200
                    
                    data1 = response1.json()
                    data2 = response2.json()
                    
                    # Both should have different query IDs
                    assert data1['query_id'] != data2['query_id']

if __name__ == "__main__":
    pytest.main([__file__]) 