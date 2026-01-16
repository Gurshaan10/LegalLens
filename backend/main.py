#main.py

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from pypdf import PdfReader
import os
from openai import OpenAI
from dotenv import load_dotenv
import uuid
from pydantic import BaseModel, Field
import logging
from io import BytesIO
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import tempfile
import time
from sqlalchemy.orm import Session
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from datetime import datetime, timedelta
from typing import Optional

# Import database components
from database import get_db, create_tables, get_user_by_firebase_uid
from models import Document, DocumentQuery, User, GuestUpload
from db_services import save_document, save_query, get_document_history, get_document_queries, get_user_activity_summary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Debug environment variables
logger.info("Current working directory: %s", os.getcwd())
logger.info("Environment variables loaded: %s", bool(os.getenv("OPENAI_API_KEY")))
logger.info("API Key starts with: %s", os.getenv("OPENAI_API_KEY")[:5] if os.getenv("OPENAI_API_KEY") else "Not found")

if not client.api_key:
    logger.error("OpenAI API key not found in environment variables!")
    raise ValueError("OpenAI API key not found in environment variables")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://legal-lens01.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Store document embeddings in memory
document_stores = {}

# Create database tables on startup
create_tables()

@app.on_event("startup")
async def load_demo_document():
    """Load demo document on application startup"""
    try:
        if not os.path.exists(DEMO_DOCUMENT_PATH):
            logger.warning(f"Demo document not found at {DEMO_DOCUMENT_PATH}")
            return

        logger.info(f"Loading demo document from {DEMO_DOCUMENT_PATH}")

        with open(DEMO_DOCUMENT_PATH, "rb") as f:
            contents = f.read()

        pdf_file = BytesIO(contents)
        reader = PdfReader(pdf_file)

        # Extract text
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        if not text.strip():
            # Try OCR for scanned PDFs
            text = extract_text_with_ocr(contents)

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        # Create embeddings and store them
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_texts(chunks, embeddings)

        document_stores[DEMO_DOCUMENT_ID] = {
            "filename": "Robinhood Cash Sweep Program (Demo)",
            "vectorstore": vectorstore,
            "chunks": chunks,
            "text": text,
            "is_demo": True,
            "created_at": datetime.utcnow(),  # Track creation time
            "is_guest_upload": False  # Demo documents never expire
        }

        logger.info(f"Demo document loaded successfully with {len(chunks)} chunks")
    except Exception as e:
        logger.error(f"Failed to load demo document: {e}")

# Initialize Firebase Admin SDK (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("FIREBASE_ADMIN_CREDENTIAL") or "firebase-admin.json")
    firebase_admin.initialize_app(cred)

# Demo document configuration
DEMO_DOCUMENT_ID = "demo-robinhood-document"
DEMO_DOCUMENT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test-documents", "robinhood.pdf")

# Document cleanup scheduler
def cleanup_old_documents():
    """Remove documents older than 24 hours for guests, 7 days for users"""
    cutoff_guest = datetime.utcnow() - timedelta(hours=24)
    cutoff_user = datetime.utcnow() - timedelta(days=7)

    to_delete = []
    for doc_id, doc_data in document_stores.items():
        # Skip demo documents
        if doc_data.get("is_demo"):
            continue

        created = doc_data.get("created_at")
        if not created:
            continue

        is_guest = doc_data.get("is_guest_upload", False)
        cutoff = cutoff_guest if is_guest else cutoff_user

        if created < cutoff:
            to_delete.append(doc_id)

    for doc_id in to_delete:
        del document_stores[doc_id]
        logger.info(f"Cleaned up document: {doc_id}")

    if to_delete:
        logger.info(f"Cleanup complete: Removed {len(to_delete)} old documents")

# Initialize cleanup scheduler
import threading
def run_cleanup_scheduler():
    """Run cleanup every hour"""
    while True:
        try:
            time.sleep(3600)  # Sleep for 1 hour
            cleanup_old_documents()
        except Exception as e:
            logger.error(f"Cleanup scheduler error: {e}")

# Start cleanup thread
cleanup_thread = threading.Thread(target=run_cleanup_scheduler, daemon=True)
cleanup_thread.start()
logger.info("Document cleanup scheduler started (runs every hour)")

# Helper functions for guest access
def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.
    For dev/portfolio: Uses request.client.host directly (ignores X-Forwarded-For to prevent spoofing).
    For production: Configure trusted proxies in FastAPI settings if needed.
    """
    return request.client.host if request.client else "unknown"

def check_guest_upload_limit(db: Session, ip_address: str, max_uploads: int = 2) -> bool:
    """Check if guest IP has reached daily upload limit (non-atomic, for query only)"""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    upload_count = db.query(GuestUpload).filter(
        GuestUpload.ip_address == ip_address,
        GuestUpload.upload_date >= today_start
    ).count()

    return upload_count < max_uploads

def record_guest_upload_atomic(db: Session, ip_address: str, document_id: str, max_uploads: int = 2) -> bool:
    """
    Atomically check and record guest upload.
    Returns True if upload was recorded successfully, False if limit exceeded.
    Uses database-level locking to prevent race conditions.
    """
    from sqlalchemy import func

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        # Use a savepoint for nested transaction
        db.begin_nested()

        # Count with row-level lock (FOR UPDATE prevents concurrent reads)
        upload_count = db.query(func.count(GuestUpload.id)).filter(
            GuestUpload.ip_address == ip_address,
            GuestUpload.upload_date >= today_start
        ).with_for_update().scalar()

        if upload_count >= max_uploads:
            db.rollback()
            return False

        # Insert new record
        guest_upload = GuestUpload(
            ip_address=ip_address,
            document_id=document_id
        )
        db.add(guest_upload)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error recording guest upload: {e}")
        return False

def record_guest_upload(db: Session, ip_address: str, document_id: str):
    """Record a guest upload in the database (legacy, non-atomic)"""
    guest_upload = GuestUpload(
        ip_address=ip_address,
        document_id=document_id
    )
    db.add(guest_upload)
    db.commit()

def extract_text_with_ocr(pdf_bytes: bytes) -> str:
    """Extract text from scanned PDF using OCR"""
    logger.info("Attempting OCR text extraction...")
    try:
        # Convert PDF to images
        images = convert_from_bytes(pdf_bytes, dpi=300)
        logger.info(f"Converted PDF to {len(images)} images")
        
        text = ""
        for i, image in enumerate(images):
            try:
                # Extract text using OCR
                page_text = pytesseract.image_to_string(image)
                logger.info(f"OCR Page {i+1}: {len(page_text)} characters")
                text += page_text + "\n"
            except Exception as e:
                logger.warning(f"OCR failed for page {i+1}: {e}")
                continue
        
        logger.info(f"OCR extraction complete: {len(text)} total characters")
        return text.strip()
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise e

class Query(BaseModel):
    query: str = Field(..., max_length=500, min_length=1, description="Query text (max 500 characters)")

class HistoryResponse(BaseModel):
    documents: list
    total_documents: int
    total_size_bytes: int

def get_current_user(authorization: str = Header(...), db=Depends(get_db)):
    """Get current authenticated user (required)"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    id_token = authorization.split(" ", 1)[1]
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        firebase_uid = decoded_token["uid"]
        email = decoded_token.get("email")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid Firebase ID token")
    # Get or create user in DB
    user = get_user_by_firebase_uid(db, firebase_uid)
    if not user:
        user = User(firebase_uid=firebase_uid, email=email, credits=5)  # 5 credits for registered users
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_login = datetime.utcnow()
        db.commit()
    return user

def get_optional_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> Optional[User]:
    """Get current user if authenticated, None otherwise (for optional auth endpoints)"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        id_token = authorization.split(" ", 1)[1]
        decoded_token = firebase_auth.verify_id_token(id_token)
        firebase_uid = decoded_token["uid"]
        email = decoded_token.get("email")

        user = get_user_by_firebase_uid(db, firebase_uid)
        if not user:
            user = User(firebase_uid=firebase_uid, email=email, credits=5)  # 5 credits for registered users
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user.last_login = datetime.utcnow()
            db.commit()
        return user
    except Exception as e:
        logger.warning(f"Failed to authenticate user: {e}")
        return None

@app.post("/upload/")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user)
):
    logger.info(f"Receiving file: {file.filename}")

    # Handle guest vs authenticated users
    is_guest = user is None
    client_ip = None  # Initialize for later use
    document_id = str(uuid.uuid4())  # Generate ID early for atomic recording

    if is_guest:
        client_ip = get_client_ip(request)
        logger.info(f"Guest upload from IP: {client_ip}")

        # Atomically check and record upload - prevents race conditions
        if not record_guest_upload_atomic(db, client_ip, document_id):
            raise HTTPException(
                status_code=429,
                detail="Daily upload limit reached for guest users. Please sign in to get more credits."
            )
        logger.info(f"Guest upload atomically recorded for IP: {client_ip}")
    else:
        logger.info(f"Authenticated upload from user: {user.email}")
        # Check if user has credits
        if user.credits <= 0:
            raise HTTPException(
                status_code=403,
                detail="Insufficient credits. You have used all your upload credits."
            )
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Add file size validation (50MB max)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes

    try:
        contents = await file.read()

        # Check file size
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum file size is 50MB."
            )
        logger.info(f"File read: {len(contents)} bytes")
        logger.info(f"File content type: {type(contents)}")
        logger.info(f"First 100 bytes: {contents[:100]}")
        
        pdf_file = BytesIO(contents)
        logger.info(f"BytesIO created, size: {pdf_file.getbuffer().nbytes}")
        
        reader = PdfReader(pdf_file)
        logger.info(f"PDF loaded successfully, pages: {len(reader.pages)}")
        
        # Check if PDF is encrypted
        if reader.is_encrypted:
            logger.warning("PDF is encrypted, attempting to decrypt...")
            try:
                reader.decrypt('')  # Try empty password
                logger.info("PDF decrypted successfully")
            except Exception as e:
                logger.error(f"Failed to decrypt PDF: {e}")
                raise HTTPException(status_code=400, detail="PDF is encrypted and cannot be processed")
        
        text = ""
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                logger.info(f"Page {i+1} extracted text length: {len(page_text)} characters")
                if len(page_text) > 0:
                    logger.info(f"Page {i+1} first 50 chars: {page_text[:50]}")
                text += page_text
            except Exception as e:
                logger.warning(f"Error extracting text from page {i+1}: {str(e)}")
                continue
        
        logger.info(f"Total extracted text length: {len(text)} characters")

        if not text.strip():
            # Try OCR for scanned PDFs
            logger.info("No text extracted, attempting OCR for scanned PDF...")
            try:
                text = extract_text_with_ocr(contents)
                if not text.strip():
                    raise HTTPException(status_code=400, detail="No text could be extracted from the PDF using OCR. The file might be corrupted or contain unreadable images.")
                logger.info(f"OCR successful, extracted {len(text)} characters")
            except Exception as e:
                logger.error(f"OCR extraction failed: {e}")
                raise HTTPException(status_code=400, detail=f"Failed to extract text from scanned PDF: {str(e)}")

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        logger.info(f"Created {len(chunks)} text chunks")

        if not chunks:
            raise HTTPException(status_code=400, detail="Failed to create text chunks from the document.")

        # Create embeddings and store them
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_texts(chunks, embeddings)
        logger.info("Created embeddings and vector store")
        
        # Use the pre-generated document_id (for guests, already recorded atomically)
        document_stores[document_id] = {
            "filename": file.filename,
            "vectorstore": vectorstore,
            "chunks": chunks,
            "text": text,
            "created_at": datetime.utcnow(),  # Track creation time for cleanup
            "is_guest_upload": is_guest  # Track if guest upload (24h TTL vs 7d for users)
        }
        logger.info(f"Document stored with ID: {document_id}")

        # Save to database
        try:
            meta = {
                "pages": len(reader.pages),
                "chunks": len(chunks),
                "processing_method": "ocr" if not text.strip() else "text_extraction",
                "is_guest_upload": is_guest
            }

            db_document = save_document(
                db=db,
                filename=document_id,
                original_filename=file.filename,
                file_size=len(contents),
                text_content=text[:10000],  # Store first 10k chars for preview
                text_length=len(text),      # Store actual total text length
                user_id=user.id if user else None,
                meta=meta
            )
            logger.info(f"Document saved to database with ID: {db_document.id}")
        except Exception as e:
            logger.error(f"Failed to save to database: {e}")
            # Continue without database save for now

        # Handle credit deduction for authenticated users (guest upload already recorded atomically)
        if not is_guest:
            # Deduct credit for authenticated users
            if user.credits > 0:
                user.credits -= 1
                db.commit()
                logger.info(f"User {user.email} credits remaining: {user.credits}")

        return {
            "document_id": document_id,
            "is_guest": is_guest,
            "credits_remaining": user.credits if user else None
        }
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/{document_id}")
async def query_document(
    document_id: str,
    query: Query,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user)
):
    logger.info(f"Querying document {document_id} with query: {query.dict()}")
    is_guest = user is None
    
    if document_id not in document_stores:
        logger.error(f"Document ID {document_id} not found in document_stores. Available IDs: {list(document_stores.keys())}")
        raise HTTPException(status_code=404, detail="Document not found")
        
    start_time = time.time()
    
    try:
        doc = document_stores[document_id]
        logger.info(f"Found document: {doc['filename']}")
        
        if not client.api_key:
            logger.error("OpenAI API key not configured")
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        logger.info("Sending request to OpenAI...")
        logger.info(f"Document text length: {len(doc['text'])} characters")
        logger.info(f"Query: {query.query}")
            
        # Get relevant chunks using vector similarity search
        try:
            docs = doc['vectorstore'].similarity_search_with_score(query.query, k=3)
            logger.info(f"Found {len(docs)} relevant chunks")
        except Exception as e:
            logger.error(f"Error during similarity search: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error during similarity search: {str(e)}")
        
        # Use the chunks as context for GPT
        try:
            context = "\n\n".join([d[0].page_content for d in docs])
            logger.info(f"Created context of length: {len(context)} characters")
        except Exception as e:
            logger.error(f"Error creating context from chunks: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error creating context: {str(e)}")
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are Legal Lens, a specialized AI assistant designed specifically for analyzing legal documents. Your expertise is in legal document analysis, contract review, and legal compliance.

IMPORTANT: You should ONLY provide analysis for legal documents such as:
- Contracts and agreements
- Leases and rental agreements
- Legal notices and correspondence
- Court documents and filings
- Legal forms and applications
- Terms of service and privacy policies
- Legal memoranda and briefs

If the document is NOT a legal document (e.g., resumes, personal letters, non-legal forms), politely inform the user that Legal Lens is designed specifically for legal document analysis and suggest they upload a legal document instead.

When analyzing legal documents, focus on:
- Key terms and conditions
- Legal obligations and rights
- Potential risks or concerns
- Compliance requirements
- Important deadlines or dates
- Legal implications and consequences

FORMATTING REQUIREMENTS:
- Use clear, structured responses with proper line breaks
- Use bullet points (•) for lists and key points
- Separate different sections with line breaks
- Use clear headings and subheadings without special formatting
- Organize information in a logical, easy-to-read format
- Use numbered lists when appropriate for step-by-step analysis
- Avoid using asterisks or special markdown symbols

Provide clear, professional legal analysis while being careful not to give legal advice. Always base your responses on the document content provided."""},
                    {"role": "user", "content": f"Document context:\n{context}\n\nQuestion: {query.query}"}
                ],
                temperature=0.0,
            )
            
            if not response.choices:
                raise HTTPException(status_code=500, detail="No response generated from OpenAI")
                
            answer = response.choices[0].message.content.strip()
            logger.info("Successfully generated response")
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Save query to database
            try:
                save_query(
                    db=db,
                    document_id=document_id,
                    query_text=query.query,
                    response_text=answer,
                    response_time_ms=response_time_ms
                )
                logger.info("Query saved to database")
            except Exception as e:
                logger.error(f"Failed to save query to database: {e}")
                # Continue without database save for now
            
            return {"answer": answer}
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/")
async def get_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get document upload history"""
    try:
        documents = get_document_history(db)
        summary = get_user_activity_summary(db)
        
        return {
            "documents": [
                {
                    "id": doc.id,
                    "filename": doc.original_filename,
                    "upload_date": doc.upload_date.isoformat(),
                    "file_size": doc.file_size,
                    "text_length": doc.text_length,
                    "processing_status": doc.processing_status,
                    "meta": doc.meta
                }
                for doc in documents
            ],
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{document_id}/queries")
async def get_document_queries_history(document_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get query history for a specific document"""
    try:
        queries = get_document_queries(db, document_id)
        
        return {
            "queries": [
                {
                    "id": query.id,
                    "query_text": query.query_text,
                    "response_text": query.response_text,
                    "query_date": query.query_date.isoformat(),
                    "response_time_ms": query.response_time_ms
                }
                for query in queries
            ]
        }
    except Exception as e:
        logger.error(f"Error getting document queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    response = {
        "id": user.id,
        "firebase_uid": user.firebase_uid,
        "email": user.email,
        "credits": user.credits,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None
    }
    logger.info(f"GET /me - User: {user.email}, Credits: {user.credits}")
    return response

@app.get("/demo")
async def get_demo_document():
    """Get demo document information"""
    if DEMO_DOCUMENT_ID in document_stores:
        demo_doc = document_stores[DEMO_DOCUMENT_ID]
        return {
            "document_id": DEMO_DOCUMENT_ID,
            "filename": demo_doc["filename"],
            "available": True,
            "chunks": len(demo_doc.get("chunks", [])),
            "is_demo": True
        }
    return {
        "document_id": DEMO_DOCUMENT_ID,
        "available": False,
        "message": "Demo document not loaded"
    }

@app.get("/document/{document_id}")
async def get_document_info(document_id: str):
    """Get document information (works with or without authentication)"""
    if document_id not in document_stores:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = document_stores[document_id]
    return {
        "document_id": document_id,
        "filename": doc["filename"],
        "chunks": len(doc.get("chunks", [])),
        "text_length": len(doc.get("text", "")),
        "is_demo": doc.get("is_demo", False),
        "can_view": doc.get("is_demo", False)  # Only demo documents can be viewed/downloaded
    }

@app.get("/document/{document_id}/view")
async def view_document(document_id: str):
    """View/download document PDF (currently only demo document)"""
    from fastapi.responses import FileResponse

    # Only allow viewing demo document for now
    if document_id != DEMO_DOCUMENT_ID:
        raise HTTPException(status_code=403, detail="Document viewing is only available for demo documents")

    if not os.path.exists(DEMO_DOCUMENT_PATH):
        raise HTTPException(status_code=404, detail="Demo document file not found")

    return FileResponse(
        path=DEMO_DOCUMENT_PATH,
        media_type="application/pdf",
        filename="robinhood-cash-sweep-program.pdf",
        headers={
            "Content-Disposition": "inline; filename=robinhood-cash-sweep-program.pdf"
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
