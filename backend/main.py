#main.py

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.vectorstores.faiss import FAISS
from pypdf import PdfReader
import os
from openai import OpenAI
from dotenv import load_dotenv
import uuid
from pydantic import BaseModel
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
from datetime import datetime

# Import database components
from database import get_db, create_tables, get_user_by_firebase_uid
from models import Document, DocumentQuery, User
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
    allow_origins=["http://localhost:5173"],
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

# Initialize Firebase Admin SDK (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("FIREBASE_ADMIN_CREDENTIAL") or "firebase-admin.json")
    firebase_admin.initialize_app(cred)

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
    query: str

class HistoryResponse(BaseModel):
    documents: list
    total_documents: int
    total_size_bytes: int

def get_current_user(authorization: str = Header(...), db=Depends(get_db)):
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
        user = User(firebase_uid=firebase_uid, email=email, credits=1)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_login = datetime.utcnow()
        db.commit()
    return user

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    logger.info(f"Receiving file: {file.filename}")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        contents = await file.read()
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
        
        # Generate a unique ID for this document
        document_id = str(uuid.uuid4())
        document_stores[document_id] = {
            "filename": file.filename,
            "vectorstore": vectorstore,
            "chunks": chunks,
            "text": text
        }
        logger.info(f"Document stored with ID: {document_id}")

        # Save to database
        try:
            meta = {
                "pages": len(reader.pages),
                "chunks": len(chunks),
                "processing_method": "ocr" if not text.strip() else "text_extraction"
            }
            
            db_document = save_document(
                db=db,
                filename=document_id,
                original_filename=file.filename,
                file_size=len(contents),
                text_content=text[:10000],  # Store first 10k chars for preview
                text_length=len(text),      # Store actual total text length
                user_id=user.id,
                meta=meta
            )
            logger.info(f"Document saved to database with ID: {db_document.id}")
        except Exception as e:
            logger.error(f"Failed to save to database: {e}")
            # Continue without database save for now

        # Check user.credits > 0, decrement, and associate document with user_id
        if user.credits > 0:
            user.credits -= 1
            db.commit()

        return {"document_id": document_id}
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/{document_id}")
async def query_document(document_id: str, query: Query, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    logger.info(f"Querying document {document_id} with query: {query.dict()}")
    
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
    return {
        "id": user.id,
        "firebase_uid": user.firebase_uid,
        "email": user.email,
        "credits": user.credits,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
