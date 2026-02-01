# api/database/models.py
"""
SQLAlchemy ORM Models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from api.database.postgres import Base


def generate_uuid():
    """Generate UUID for SQLite compatibility"""
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)  # Null for guests
    filename = Column(String(255), nullable=False)
    pdf_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), unique=True, index=True)  # SHA256
    parsed_data = Column(JSON, nullable=False)  # {name, skills, work_units}
    is_active = Column(Boolean, default=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    match_results = relationship("MatchResult", back_populates="resume", cascade="all, delete-orphan")


class MatchResult(Base):
    __tablename__ = "match_results"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), index=True)
    job_id = Column(String(100), nullable=False)
    match_score = Column(Float, nullable=False)
    matched_requirements = Column(JSON)  # List of matched requirements
    gaps = Column(JSON)  # List of missing requirements
    matched_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="match_results")


class ParsingJob(Base):
    __tablename__ = "parsing_jobs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(100), index=True)  # For guests
    user_id = Column(String(36), ForeignKey("users.id"))  # For registered
    filename = Column(String(255))
    status = Column(String(20), nullable=False, index=True)  # pending, processing, completed, failed
    result = Column(JSON)  # Parsed resume or error
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
