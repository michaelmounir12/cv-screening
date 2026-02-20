"""
Job posting repository - handles all database operations for JobPosting.
"""
from typing import List, Optional
from uuid import UUID

from apps.resume_screening.models import JobPosting


class JobPostingRepository:
    """Repository for JobPosting model."""
    
    @staticmethod
    def create(
        *,
        job_id: UUID,
        title: str,
        description: str,
        embedding: List[float] = None,
    ) -> JobPosting:
        return JobPosting.objects.create(
            id=job_id,
            title=title,
            description=description,
            embedding=embedding,
        )
    
    @staticmethod
    def get_by_id(job_id) -> Optional[JobPosting]:
        try:
            return JobPosting.objects.get(pk=job_id)
        except JobPosting.DoesNotExist:
            return None
    
    @staticmethod
    def update_embedding(job_id: UUID, embedding: List[float]) -> Optional[JobPosting]:
        job = JobPostingRepository.get_by_id(job_id)
        if job:
            job.embedding = embedding
            job.save(update_fields=['embedding'])
        return job
    
    @staticmethod
    def list_all(skip: int = 0, limit: int = 100) -> List[JobPosting]:
        return list(JobPosting.objects.all()[skip:skip + limit])
