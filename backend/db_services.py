from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Document, DocumentQuery, AnalysisSession
from datetime import datetime
import time

def save_document(
    db: Session,
    filename: str,
    original_filename: str,
    file_size: int,
    text_content: str = None,
    text_length: int = None,
    user_id: str = None,
    document_type: str = None,
    meta: dict = None
) -> Document:
    """Save a document to the database"""
    document = Document(
        filename=filename,
        original_filename=original_filename,
        file_size=file_size,
        text_content=text_content,
        text_length=text_length if text_length is not None else (len(text_content) if text_content else 0),
        user_id=user_id,
        document_type=document_type,
        meta=meta or {}
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

def save_query(
    db: Session,
    document_id: str,
    query_text: str,
    response_text: str,
    response_time_ms: int = None,
    user_id: str = None
) -> DocumentQuery:
    """Save a document query to the database"""
    query = DocumentQuery(
        document_id=document_id,
        query_text=query_text,
        response_text=response_text,
        response_time_ms=response_time_ms,
        user_id=user_id
    )
    db.add(query)
    db.commit()
    db.refresh(query)
    return query

def get_document_history(db: Session, user_id: str = None, limit: int = 50) -> list:
    """Get document upload history"""
    query = db.query(Document)
    if user_id:
        query = query.filter(Document.user_id == user_id)
    
    documents = query.order_by(Document.upload_date.desc()).limit(limit).all()
    return documents

def get_document_queries(db: Session, document_id: str, limit: int = 50) -> list:
    """Get all queries for a specific document"""
    queries = db.query(DocumentQuery)\
        .filter(DocumentQuery.document_id == document_id)\
        .order_by(DocumentQuery.query_date.desc())\
        .limit(limit)\
        .all()
    return queries

def get_document_by_id(db: Session, document_id: str) -> Document:
    """Get a document by its ID"""
    return db.query(Document).filter(Document.id == document_id).first()

def get_user_activity_summary(db: Session, user_id: str = None) -> dict:
    """Get summary of user activity"""
    query = db.query(Document)
    if user_id:
        query = query.filter(Document.user_id == user_id)
    
    total_documents = query.count()
    total_size = query.with_entities(func.sum(Document.file_size)).scalar() or 0
    
    # Get recent activity
    recent_documents = query.order_by(Document.upload_date.desc()).limit(5).all()
    
    return {
        "total_documents": total_documents,
        "total_size_bytes": total_size,
        "recent_documents": recent_documents
    } 