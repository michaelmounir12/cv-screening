"""
Job posting service - CRUD with embedding generation.
"""
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4

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
    
    def get_job(self, job_id: UUID) -> Optional[Dict[str, Any]]:
        job = JobPostingRepository.get_by_id(job_id)
        if not job:
            return None
        return {
            "id": str(job.id),
            "title": job.title,
            "description": job.description,
            "created_at": job.created_at.isoformat(),
        }
    
    def list_jobs(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        jobs = JobPostingRepository.list_all(skip=skip, limit=limit)
        return [
            {"id": str(j.id), "title": j.title, "description": j.description[:200] + "..." if len(j.description) > 200 else j.description, "created_at": j.created_at.isoformat()}
            for j in jobs
        ]
    
    def update_job(self, job_id: UUID, *, title: str = None, description: str = None) -> Optional[Dict[str, Any]]:
        job = JobPostingRepository.get_by_id(job_id)
        if not job:
            return None
        embedding = None
        if description is not None:
            embedding_svc = EmbeddingService()
            embedding = embedding_svc.encode_job_description(description)
        JobPostingRepository.update(job_id, title=title, description=description, embedding=embedding)
        job = JobPostingRepository.get_by_id(job_id)
        return {"id": str(job.id), "title": job.title, "description": job.description, "created_at": job.created_at.isoformat()}
    
    def delete_job(self, job_id: UUID) -> bool:
        return JobPostingRepository.delete(job_id)
