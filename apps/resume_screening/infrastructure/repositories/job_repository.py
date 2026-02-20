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
    
    @staticmethod
    def update(job_id: UUID, *, title: str = None, description: str = None, embedding: List[float] = None) -> Optional[JobPosting]:
        job = JobPostingRepository.get_by_id(job_id)
        if not job:
            return None
        update_fields = []
        if title is not None:
            job.title = title
            update_fields.append('title')
        if description is not None:
            job.description = description
            update_fields.append('description')
        if embedding is not None:
            job.embedding = embedding
            update_fields.append('embedding')
        if update_fields:
            job.save(update_fields=update_fields)
        return job
    
    @staticmethod
    def delete(job_id: UUID) -> bool:
        deleted, _ = JobPosting.objects.filter(pk=job_id).delete()
        return deleted > 0
