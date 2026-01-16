# Legal Lens 🔍

A full-stack legal document analysis web application powered by AI. Upload legal documents and get instant, intelligent analysis using advanced NLP and vector search capabilities.

**Try it instantly** - No sign-up required! Query our demo document or upload your own (2 free uploads per day for guests).

## 👋 For Portfolio Reviewers & Hiring Managers

Want to see Legal Lens in action without setting up accounts? Here's how:

### Instant Demo (30 seconds)
1. **Start the app** (see Quick Start below)
2. **Query the demo document** at `http://localhost:8000/demo` - it's pre-loaded!
3. **Try asking**: "What is the monthly rent?" or "What are the tenant's responsibilities?"

### Test with Your Own Document (1 minute)
- Upload any legal PDF (up to 5MB) - **no sign-up needed**
- Get 2 free uploads per day to fully test the AI capabilities
- Experience the OCR, vector search, and GPT-4 analysis

### Full Feature Access (Optional)
- Sign in with Google to get **5 credits** and persistent history
- Perfect for evaluating the complete authentication and credit system

**Bottom line:** You can evaluate all core features in under 2 minutes without creating any accounts! 🚀

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │   PostgreSQL    │
│   (Mantine UI)  │◄──►│   (Python)      │◄──►│   Database      │
│                 │    │                 │    │                 │
│ • Google OAuth  │    │ • Document      │    │ • User Profiles │
│ • Document Upload│    │   Processing    │    │ • Document      │
│ • Chat Interface │    │ • OCR (Tesseract)│   │   Metadata      │
│ • History View  │    │ • OpenAI GPT-4  │    │ • Query History │
│ • Credit System │    │ • Vector Search │    │ • Credit System │
└─────────────────┘    │ • Firebase Auth │    └─────────────────┘
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Vector Store  │
                       │   (FAISS)       │
                       │                 │
                       │ • Document      │
                       │   Embeddings    │
                       │ • Semantic      │
                       │   Search        │
                       └─────────────────┘
```

## 💳 Credit System

Legal Lens uses a flexible credit system to manage usage:

| User Type | Credits | Limits | Features |
|-----------|---------|--------|----------|
| **Guest** | N/A | 2 uploads/day (per IP) | • Query demo document (unlimited)<br>• Upload own documents (2/day)<br>• No persistent history |
| **Registered** | 5 initial credits | 1 credit per upload | • 5 free uploads on sign-up<br>• Persistent history<br>• Full account features |

**Note:** Querying documents (both demo and uploaded) is always free and unlimited for all users!

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (optional)
- Firebase Project (for authentication features)
- OpenAI API Key

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd Legal_Lens

# Start the entire application
docker-compose up -d

# Access the application
open http://localhost:3000
```

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your Firebase config

# Start the development server
npm start
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Firebase Configuration
FIREBASE_ADMIN_CREDENTIAL=path_to_firebase_admin.json

# Database Configuration
DATABASE_URL=sqlite:///./legal_lens.db

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

#### Frontend (.env)
```bash
# Firebase Configuration
REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
REACT_APP_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
REACT_APP_FIREBASE_APP_ID=your_app_id

# Backend API
REACT_APP_API_URL=http://localhost:8000
```

## 📚 API Documentation

### Public Endpoints (No Auth Required)

#### GET /demo
Get demo document information.

**Response:**
```json
{
  "document_id": "demo-lease-document",
  "filename": "Sample Lease Agreement (Demo)",
  "available": true,
  "chunks": 109,
  "is_demo": true
}
```

#### POST /query/demo-lease-document
Query the demo document (unlimited, no auth needed).

**Body:**
```json
{
  "query": "What is the monthly rent amount?"
}
```

**Response:**
```json
{
  "answer": "The monthly rent amount is $3,300.00..."
}
```

#### POST /upload/ (Guest Mode)
Upload up to 2 documents per day without authentication.

**Headers:**
```
Content-Type: multipart/form-data
```

**Body:**
```
file: <pdf_file>
```

**Response:**
```json
{
  "document_id": "uuid-string",
  "is_guest": true,
  "credits_remaining": null
}
```

**Rate Limiting:** 2 uploads per IP per day. Returns 429 error when exceeded:
```json
{
  "detail": "Daily upload limit reached for guest users. Please sign in to get more credits."
}
```

### Authentication Endpoints

#### GET /me
Get current user profile and credits.

**Headers:**
```
Authorization: Bearer <firebase_id_token>
```

**Response:**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "firebase_uid": "firebase-uid",
  "credits": 5,
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-15T10:30:00Z"
}
```

### Document Management

#### POST /upload/ (Authenticated)
Upload a legal document for analysis. Requires authentication and deducts 1 credit.

**Headers:**
```
Authorization: Bearer <firebase_id_token>
Content-Type: multipart/form-data
```

**Body:**
```
file: <pdf_file>
```

**Response:**
```json
{
  "document_id": "uuid-string",
  "is_guest": false,
  "credits_remaining": 4
}
```

### Query Endpoints

#### POST /query/{document_id}
Query a specific document (works with or without authentication).

**Headers (Optional):**
```
Authorization: Bearer <firebase_id_token>
Content-Type: application/json
```

**Body:**
```json
{
  "query": "What are the key terms in this contract?"
}
```

**Response:**
```json
{
  "answer": "This contract contains the following key terms..."
}
```

### History Endpoints

#### GET /history/
Get user's document upload history.

**Headers:**
```
Authorization: Bearer <firebase_id_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "filename": "contract.pdf",
    "document_id": "doc-uuid",
    "uploaded_at": "2024-01-15T10:30:00Z",
    "title": "Employment Contract"
  }
]
```

#### GET /history/{document_id}/queries
Get query history for a specific document.

**Headers:**
```
Authorization: Bearer <firebase_id_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "query": "What are the key terms?",
    "response": "The key terms include...",
    "created_at": "2024-01-15T10:35:00Z"
  }
]
```

## 🧪 Testing

### Quick Test (No Setup Required)

Test the guest features immediately without authentication:

```bash
# Check if demo document is available
curl http://localhost:8000/demo

# Query the demo document (no auth needed)
curl -X POST http://localhost:8000/query/demo-lease-document \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the monthly rent amount?"}'

# Test guest upload (2 per day per IP)
curl -X POST http://localhost:8000/upload/ \
  -F "file=@your-document.pdf"

# Test rate limiting (3rd upload should fail)
curl -X POST http://localhost:8000/upload/ \
  -F "file=@your-document.pdf"
```

### Run All Tests
```bash
cd backend
pytest
```

### Run Specific Test Categories
```bash
# Authentication tests
pytest tests/test_auth.py -v

# Credit management tests
pytest tests/test_credits.py -v

# QA endpoint tests
pytest tests/test_qa_endpoint.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

### Test Categories

- **Authentication Tests**: Firebase token verification, user creation, optional auth
- **Credit Tests**: Credit deduction, validation, edge cases
- **Guest Access Tests**: IP-based rate limiting, demo document access
- **QA Tests**: Document querying, AI responses, error handling
- **Integration Tests**: End-to-end workflows

## 📊 Sample Queries

### Contract Analysis
```
"What are the key obligations in this contract?"
"Who are the parties involved?"
"What are the termination conditions?"
"Are there any unusual clauses I should be aware of?"
```

### Lease Agreement
```
"What are the rent payment terms?"
"What are the tenant's responsibilities?"
"Are there any maintenance obligations?"
"What happens if I break the lease early?"
```

### Legal Notice
```
"What is this notice about?"
"What actions are required?"
"What are the deadlines mentioned?"
"Who should I contact for more information?"
```

### Terms of Service
```
"What are the main terms of service?"
"What are my rights as a user?"
"What are the company's obligations?"
"Are there any privacy implications?"
```

## 🔒 Security Features

- **Firebase Authentication**: Secure Google OAuth integration for registered users
- **Token Verification**: Server-side Firebase ID token validation
- **IP-Based Rate Limiting**: Prevents abuse from guest users (2 uploads/day per IP)
- **User Isolation**: Registered users can only access their own documents
- **Credit System**: Prevents abuse and controls usage for authenticated users
- **Optional Auth**: Flexible authentication for demo and guest access
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Secure error responses without data leakage

## 🎯 Key Features

### Guest-Friendly Access
- **Demo Document**: Pre-loaded sample lease agreement - try unlimited queries instantly
- **Guest Uploads**: 2 free document uploads per day without sign-up (IP-based)
- **Easy Testing**: Perfect for portfolio viewers and hiring managers
- **Optional Registration**: Sign up to get 5 credits and persistent history

### Document Processing
- **PDF Support**: Native PDF parsing and text extraction
- **OCR Capability**: Handles scanned documents with Tesseract
- **Chunking**: Intelligent text splitting for optimal AI processing
- **Vector Embeddings**: FAISS-based semantic search

### AI Analysis
- **Legal Specialization**: Trained specifically for legal documents
- **Context-Aware**: Uses document content for relevant responses
- **Structured Output**: Formatted responses with bullet points and sections
- **Multi-Language**: Supports various legal document types

### User Experience
- **Real-time Upload**: Animated loading with magnifying glass
- **Chat Interface**: Natural conversation with documents
- **History Tracking**: Complete audit trail of uploads and queries (registered users)
- **Credit Management**: Transparent usage tracking

## 🛠️ Development

### Project Structure
```
Legal_Lens/
├── backend/
│   ├── main.py              # FastAPI application with guest access
│   ├── models.py            # SQLAlchemy models (User, Document, GuestUpload)
│   ├── database.py          # Database configuration
│   ├── db_services.py       # Database operations
│   ├── tests/               # Test suite
│   ├── requirements.txt     # Python dependencies
│   └── lease.pdf           # (in parent dir) Demo document
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   ├── contexts/       # React contexts
│   │   └── App.tsx         # Main application
│   └── package.json        # Node.js dependencies
├── docker-compose.yml      # Docker orchestration
└── README.md              # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📈 Performance

- **Document Processing**: ~30 seconds for 50-page PDFs
- **Query Response**: ~2-5 seconds for AI analysis
- **Concurrent Users**: Supports 100+ simultaneous users
- **File Size Limit**: 5MB per document
- **Supported Formats**: PDF only

## 🚨 Troubleshooting

### Common Issues

**Backend won't start:**
- Check if all environment variables are set
- Verify Firebase Admin SDK credentials
- Ensure OpenAI API key is valid

**Frontend authentication fails:**
- Verify Firebase configuration
- Check CORS settings in backend
- Ensure backend is running on correct port

**Document upload fails:**
- Check file size (max 5MB)
- Ensure file is PDF format
- Verify user has sufficient credits

**AI responses are generic:**
- Check OpenAI API key and quota
- Verify document was processed correctly
- Check vector store was created properly

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support, please open an issue on GitHub or contact the development team.

---

**Legal Lens** - Making legal document analysis accessible and intelligent. 🔍⚖️ 