"""
Job posting service - create jobs with embedding generation.
"""
from typing import Dict, Any
from uuid import uuid4

from apps.resume_screening.infrastructure.ai.embedding_service import EmbeddingService
from apps.resume_screening.infrastructure.repositories.job_repository import JobPostingRepository


class JobPostingService:
    """Service for job posting operations."""
    
    def create_job(self, title: str, description: str) -> Dict[str, Any]:
        """
        Create job posting and generate embedding.
        """
        job_id = uuid4()
        embedding_svc = EmbeddingService()
        embedding = embedding_svc.encode_job_description(description)
        
        job = JobPostingRepository.create(
            job_id=job_id,
            title=title,
            description=description,
            embedding=embedding,
        )
        return {
            "id": str(job.id),
            "title": job.title,
            "description": job.description,
            "created_at": job.created_at.isoformat(),
        }
