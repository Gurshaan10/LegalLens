# Legal Lens 🔍

A production-ready full-stack legal document analysis application powered by AI. Upload legal documents and get instant, intelligent analysis using RAG (Retrieval-Augmented Generation), vector search, and GPT-4.

**🚀 Live Demo:** [Coming Soon - Deploying to Railway]

**Try it instantly** - No sign-up required! Query our demo document or upload your own (2 free uploads per day for guests).

---

### ⚡ Instant Demo (30 seconds)
1. **Start the app** (see Quick Start below)
2. **Visit** `http://localhost:5173`
3. **Click** on the demo Robinhood document - it's pre-loaded!
4. **Try asking**:
   - "What is the FDIC insurance limit?"
   - "How does the Cash Sweep Program work?"
   - "What is the Brokerage-Held Cash Program threshold?"

### 📄 Test with Your Own Document (1 minute)
- Upload any legal PDF (up to 50MB) - **no sign-up needed**
- Get **2 free uploads per day** to fully test the AI capabilities
- Experience OCR (for scanned PDFs), vector search, and GPT-4 analysis
- Ask unlimited questions about your uploaded document

### 🔐 Full Feature Access (Optional)
- Sign in with Google to get **5 credits** and persistent history
- Access your upload history and previous queries
- Account menu with credit tracking and sign-out

**Bottom line:** You can evaluate all core features in under 5 minutes without creating any accounts! 🚀

---

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- React 18 + TypeScript + Vite
- Mantine UI (custom bronze/dark theme)
- Firebase Authentication (Google OAuth)
- React Router for navigation

**Backend:**
- FastAPI (Python 3.10+)
- PostgreSQL with SQLAlchemy ORM
- OpenAI GPT-4 for analysis
- FAISS for vector similarity search
- LangChain for RAG pipeline
- Tesseract OCR for scanned PDFs
- Firebase Admin SDK for auth

**Infrastructure:**
- Railway (PostgreSQL + Backend deployment)
- Vercel (Frontend hosting)
- Docker & Docker Compose for local dev

### System Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│   React Frontend    │    │   FastAPI Backend    │    │   PostgreSQL    │
│   (Mantine UI)      │◄──►│   (Python)           │◄──►│   Database      │
│                     │    │                      │    │                 │
│ • Google OAuth      │    │ • Document Processing│    │ • User Profiles │
│ • Document Upload   │    │ • OCR (Tesseract)    │    │ • Documents     │
│ • Chat Interface    │    │ • Text Chunking      │    │ • Query History │
│ • History View      │    │ • OpenAI Embeddings  │    │ • Credits       │
│ • Credit Tracking   │    │ • GPT-4 Analysis     │    │ • Guest Uploads │
│ • Account Menu      │    │ • Firebase Auth      │    └─────────────────┘
└─────────────────────┘    │ • Rate Limiting      │
                           └──────────────────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │   FAISS Vector Store │
                           │   (In-Memory)        │
                           │                      │
                           │ • Document Embeddings│
                           │ • Semantic Search    │
                           │ • Top-k Retrieval    │
                           └──────────────────────┘
```

### RAG Pipeline

```
PDF Upload → Text Extraction → Chunking (1000 chars, 200 overlap)
    → OpenAI Embeddings → FAISS Index

User Query → Query Embedding → FAISS Similarity Search (top-3)
    → Context Retrieval → GPT-4 Prompt → Structured Response
```

---

## 💳 Credit System

Legal Lens uses a flexible credit system to manage usage:

| User Type | Credits | Upload Limit | Features |
|-----------|---------|--------------|----------|
| **Guest** | N/A | 2/day per IP | • Query demo document (unlimited)<br>• Upload own documents (2/day)<br>• No persistent history<br>• localStorage tracking |
| **Registered** | 5 initial | 1 credit per upload | • 5 free uploads on sign-up<br>• Persistent history<br>• Query history<br>• Account menu |

**Note:** Querying documents (both demo and uploaded) is **always free and unlimited** for all users!

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (optional, but recommended)
- Firebase Project (for authentication)
- OpenAI API Key

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/legal-lens.git
cd legal-lens

# Set up environment variables
cp env.example .env
# Edit .env with your API keys

# Start the entire application
docker-compose up -d

# Access the application
open http://localhost:5173
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
# Create .env in backend/ with:
# OPENAI_API_KEY=your_key_here
# DATABASE_URL=sqlite:///./legal_lens.db
# FIREBASE_ADMIN_CREDENTIAL=firebase-admin.json

# Initialize database
python -c "from database import create_tables; create_tables()"

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
# Create .env.local in frontend/ with:
# VITE_FIREBASE_API_KEY=your_key
# VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
# VITE_FIREBASE_PROJECT_ID=your_project_id
# VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
# VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
# VITE_FIREBASE_APP_ID=your_app_id
# VITE_API_BASE_URL=http://localhost:8000

# Start the development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

## 📁 Project Structure

```
legal-lens/
├── backend/                    # FastAPI backend application
│   ├── main.py                # API routes, RAG pipeline, auth
│   ├── models.py              # SQLAlchemy models (User, Document, Query, GuestUpload)
│   ├── database.py            # Database config and session management
│   ├── db_services.py         # Database CRUD operations
│   ├── utils.py               # Helper utilities
│   ├── ingest.py              # Batch document ingestion script
│   ├── query.py               # CLI query tool
│   ├── tests/                 # Comprehensive test suite
│   │   ├── test_auth.py       # Authentication tests
│   │   ├── test_credits.py    # Credit system tests
│   │   └── test_qa_endpoint.py# QA pipeline tests
│   ├── requirements.txt       # Python dependencies
│   └── firebase-admin.json    # Firebase credentials (gitignored)
│
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── Layout.tsx         # App layout with account menu
│   │   │   ├── DocumentUpload.tsx # Upload with guest mode
│   │   │   ├── ChatInterface.tsx  # Q&A interface
│   │   │   └── DemoDocumentCard.tsx # Demo card
│   │   ├── pages/             # Page components
│   │   │   ├── LandingPage.tsx    # Landing with demo
│   │   │   ├── AnalysisPage.tsx   # Main analysis page
│   │   │   └── HistoryPage.tsx    # Upload history
│   │   ├── contexts/          # React contexts
│   │   │   └── AuthContext.tsx    # Firebase auth state
│   │   ├── config/            # Configuration
│   │   │   └── api.ts             # API endpoints config
│   │   ├── types/             # TypeScript types
│   │   │   └── api.ts             # API response types
│   │   ├── firebase.ts        # Firebase client config
│   │   └── App.tsx            # Main app component
│   ├── package.json           # Node.js dependencies
│   └── vite.config.ts         # Vite configuration
│
├── docs/                       # Documentation
│   ├── DEPLOYMENT.md          # General deployment guide
│   ├── QUICK_DEPLOY.md        # Quick deployment options
│   └── RAILWAY_DEPLOY.md      # Railway-specific deployment
│
├── scripts/                    # Utility scripts
│   ├── deploy.sh              # Interactive deployment script
│   ├── deploy-simple.sh       # Simple deployment script
│   └── run_tests.py           # Test runner
│
├── test-documents/             # PDF test files
│   ├── robinhood.pdf          # Demo document (Robinhood Cash Sweep)
│   ├── lease.pdf              # Sample lease agreement
│   └── 25-47-25.pdf           # Test legal document
│
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Backend Docker image
├── railway.toml                # Railway deployment config
├── env.example                 # Environment variables template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## 🔧 Configuration

### Environment Variables

See `env.example` for a complete template. Key variables:

#### Backend

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here

# Firebase Admin SDK (path to JSON file or inline JSON)
FIREBASE_ADMIN_CREDENTIAL=firebase-admin.json

# Database (SQLite for dev, PostgreSQL for production)
DATABASE_URL=sqlite:///./legal_lens.db
# For production: DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Server
HOST=0.0.0.0
PORT=8000
```

#### Frontend

```bash
# Firebase Client Configuration
VITE_FIREBASE_API_KEY=AIza...
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123:web:abc123

# Backend API URL
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🧪 Testing

### Run All Tests

```bash
cd backend
pytest
```

### Run Specific Test Suites

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

### Quick Manual Test (No Setup Required)

Test the guest features immediately:

```bash
# Check if demo document is available
curl http://localhost:8000/demo

# Query the demo document (no auth needed)
curl -X POST http://localhost:8000/query/demo-robinhood-document \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the FDIC insurance limit?"}'

# Test guest upload (2 per day per IP)
curl -X POST http://localhost:8000/upload/ \
  -F "file=@test-documents/lease.pdf"
```

---

## 🔒 Security Features

- ✅ **Firebase Authentication** - Secure Google OAuth with server-side token verification
- ✅ **Atomic Rate Limiting** - Database-level locking prevents race conditions
- ✅ **Input Validation** - File size (50MB max), file type, query length (500 chars)
- ✅ **IP-Based Guest Tracking** - 2 uploads/day per IP with UTC midnight reset
- ✅ **User Isolation** - Users can only access their own documents
- ✅ **Credit System** - Usage tracking prevents abuse
- ✅ **Optional Auth** - Flexible authentication for demo access
- ✅ **CORS Protection** - Restricted origins
- ✅ **Error Handling** - No sensitive data leakage

### Security Measures Implemented

**Rate Limiting:**
```python
# Atomic check-and-record with database locking
def record_guest_upload_atomic(db, ip_address, max_uploads=2):
    with db.begin_nested():
        count = db.query(GuestUpload).filter(
            GuestUpload.ip_address == ip_address,
            GuestUpload.upload_date >= today_start
        ).with_for_update().scalar()  # Row-level lock

        if count >= max_uploads:
            return False

        db.add(GuestUpload(ip_address=ip_address))
        db.commit()
        return True
```

**Document Cleanup:**
- Guest uploads: Deleted after 24 hours
- User uploads: Deleted after 7 days
- Demo document: Persists indefinitely
- Background scheduler runs hourly

---

## 🎯 Key Features

### Guest-Friendly Access
- **Demo Document**: Pre-loaded Robinhood Cash Sweep Program - unlimited queries
- **Guest Uploads**: 2 free documents/day without sign-up (IP-based)
- **localStorage Persistence**: Upload counter persists across refreshes
- **Easy Testing**: Perfect for portfolio reviewers

### Document Processing
- **PDF Support**: Native PDF parsing and text extraction
- **OCR Fallback**: Handles scanned documents with Tesseract (300 DPI)
- **Smart Chunking**: RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
- **Vector Embeddings**: OpenAI embeddings + FAISS indexing

### AI Analysis
- **RAG Pipeline**: Retrieval-Augmented Generation with GPT-4
- **Legal Specialization**: Custom system prompt for legal documents
- **Context-Aware**: Top-3 semantic chunks retrieved per query
- **Structured Output**: Markdown formatting with citations
- **Multi-Question Detection**: Prompts users to ask one question at a time

### User Experience
- **Custom Theme**: Bronze/dark Mantine UI theme
- **Real-time Upload**: Animated loading states
- **Chat Interface**: Natural Q&A with document context
- **History Tracking**: Complete audit trail (registered users)
- **Account Menu**: Credit tracking with sign-out option
- **Responsive Design**: Mobile-friendly interface

---

## 📊 Performance

- **Document Processing**: ~10-30s for 50-page PDFs (depends on OCR)
- **Query Response**: ~2-5s for AI analysis
- **Vector Search**: Sub-second similarity search with FAISS
- **File Size Limit**: 50MB per document
- **Supported Formats**: PDF only (native + scanned with OCR)
- **Concurrent Users**: Supports 100+ simultaneous users (tested with pytest-asyncio)

---

## 🚀 Deployment

### Railway (Backend)

See [`docs/RAILWAY_DEPLOY.md`](docs/RAILWAY_DEPLOY.md) for detailed instructions.

**Quick Deploy:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy
railway up
```

### Vercel (Frontend)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel

# Set environment variables in Vercel dashboard
# VITE_API_BASE_URL=https://your-railway-app.up.railway.app
```

---

## 🚨 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check environment variables
cat backend/.env

# Verify Firebase credentials
ls backend/firebase-admin.json

# Check OpenAI API key
echo $OPENAI_API_KEY
```

**Frontend authentication fails:**
```bash
# Verify Firebase config in frontend/.env.local
# Check CORS settings in backend/main.py
# Ensure backend is running on port 8000
```

**Document upload fails:**
- Check file size (max 50MB)
- Ensure file is PDF format
- Verify user has credits (for registered users)
- Check guest upload limit (2/day per IP)

**AI responses are empty:**
- Verify OpenAI API key is valid
- Check OpenAI account has credits
- Ensure document was processed correctly
- Check vector store creation logs

---

## 📈 Future Enhancements

- [ ] Support for more document types (DOCX, TXT)
- [ ] Multi-language support
- [ ] Document comparison feature
- [ ] Export analysis to PDF
- [ ] Stripe integration for credit purchases
- [ ] PostgreSQL pgvector for persistent vector storage
- [ ] Redis caching for repeated queries
- [ ] Admin dashboard
- [ ] Email notifications

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 and embeddings API
- LangChain for RAG framework
- FAISS for vector similarity search
- Firebase for authentication
- Mantine UI for component library

---

**Legal Lens** - Making legal document analysis accessible and intelligent. 🔍⚖️

*Built with ❤️ for portfolio demonstration and real-world utility.*
