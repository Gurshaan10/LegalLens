from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    firebase_uid = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    credits = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    # Relationships
    documents = relationship("Document", back_populates="user")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # For user association
    document_type = Column(String, nullable=True)  # lease, contract, etc.
    text_content = Column(Text, nullable=True)  # Extracted text
    text_length = Column(Integer, nullable=True)
    processing_status = Column(String, default="completed")  # processing, completed, failed
    meta = Column(JSON, nullable=True)  # Additional info like page count, etc.
    
    # Relationships
    queries = relationship("DocumentQuery", back_populates="document", cascade="all, delete-orphan")
    user = relationship("User", back_populates="documents")

class DocumentQuery(Base):
    __tablename__ = "document_queries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    query_date = Column(DateTime, default=datetime.utcnow)
    response_time_ms = Column(Integer, nullable=True)  # For performance tracking
    user_id = Column(String, nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="queries")

class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)
    session_date = Column(DateTime, default=datetime.utcnow)
    documents_processed = Column(Integer, default=0)
    total_queries = Column(Integer, default=0)
    session_duration_minutes = Column(Integer, nullable=True)
    meta = Column(JSON, nullable=True) 