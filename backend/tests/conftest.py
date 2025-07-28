import pytest
import os
import sys
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models import User, Document, DocumentQuery
from database import get_db

@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

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

@pytest.fixture
def mock_document_query():
    """Create a mock document query for testing"""
    return DocumentQuery(
        id=1,
        document_id='test_doc_123',
        user_id=1,
        query='What type of document is this?',
        response='This is a legal document.',
        query_id='query_123'
    )

@pytest.fixture
def mock_firebase_admin():
    """Mock Firebase Admin SDK"""
    with patch('firebase_admin.auth') as mock_auth:
        yield mock_auth

@pytest.fixture
def mock_openai():
    """Mock OpenAI API"""
    with patch('openai.ChatCompletion.create') as mock_create:
        yield mock_create

@pytest.fixture
def mock_vector_store():
    """Mock vector store operations"""
    with patch('main.load_vector_store') as mock_load:
        mock_store = Mock()
        mock_load.return_value = mock_store
        yield mock_store

@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing"""
    return b'%PDF-1.4\n%\xd3\xeb\xe9\xe1\n1 0 obj\n<<\n/Title (Test Document)\n/Producer (Test)\n>>\nendobj\n'

@pytest.fixture
def valid_auth_headers():
    """Valid authorization headers for testing"""
    return {'Authorization': 'Bearer valid_test_token_123'}

@pytest.fixture
def invalid_auth_headers():
    """Invalid authorization headers for testing"""
    return {'Authorization': 'Bearer invalid_token'}

@pytest.fixture
def no_auth_headers():
    """No authorization headers for testing"""
    return {}

# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "auth: marks tests as authentication tests"
    )
    config.addinivalue_line(
        "markers", "credits: marks tests as credit management tests"
    )
    config.addinivalue_line(
        "markers", "qa: marks tests as QA endpoint tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )

# Test utilities
class TestUtils:
    """Utility functions for testing"""
    
    @staticmethod
    def create_mock_file(filename="test.pdf", content=b"test content"):
        """Create a mock file for testing uploads"""
        from io import BytesIO
        return BytesIO(content), filename
    
    @staticmethod
    def create_mock_form_data(file_content, filename="test.pdf"):
        """Create mock form data for file uploads"""
        from fastapi import UploadFile
        file_obj, filename = TestUtils.create_mock_file(filename, file_content)
        return UploadFile(filename=filename, file=file_obj)
    
    @staticmethod
    def assert_response_structure(response_data, expected_keys):
        """Assert that response has expected structure"""
        for key in expected_keys:
            assert key in response_data, f"Missing key: {key}"
    
    @staticmethod
    def assert_error_response(response, expected_status_code, expected_error_type=None):
        """Assert error response structure"""
        assert response.status_code == expected_status_code
        if expected_error_type:
            data = response.json()
            assert 'detail' in data 