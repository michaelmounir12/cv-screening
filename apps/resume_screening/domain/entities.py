"""
Domain entities (business objects).
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class Resume:
    """Resume domain entity."""
    id: Optional[int] = None
    file_path: str = ""
    file_name: str = ""
    extracted_text: Optional[str] = None
    processed: bool = False
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class JobPosting:
    """Job posting domain entity."""
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    requirements: List[str] = None
    embedding: Optional[List[float]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ScreeningResult:
    """Screening result domain entity."""
    id: Optional[int] = None
    resume_id: int = 0
    job_posting_id: int = 0
    similarity_score: float = 0.0
    match_details: Dict[str, Any] = None
    created_at: Optional[datetime] = None
