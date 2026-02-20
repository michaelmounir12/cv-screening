"""
SQLAlchemy models for resume screening.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from apps.core.database import Base


class ResumeModel(Base):
    """SQLAlchemy model for Resume."""
    __tablename__ = 'resumes'
    
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    extracted_text = Column(Text, nullable=True)
    processed = Column(Boolean, default=False)
    embedding = Column(JSON, nullable=True)  # Store as JSON array
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class JobPostingModel(Base):
    """SQLAlchemy model for Job Posting."""
    __tablename__ = 'job_postings'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(JSON, nullable=True)  # List of requirements
    embedding = Column(JSON, nullable=True)  # Store as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ScreeningResultModel(Base):
    """SQLAlchemy model for Screening Result."""
    __tablename__ = 'screening_results'
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'), nullable=False)
    job_posting_id = Column(Integer, ForeignKey('job_postings.id'), nullable=False)
    similarity_score = Column(Float, nullable=False)
    match_details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
