"""
Resume repository - handles all database operations for Resume.
"""
from typing import Optional, List
from uuid import UUID

from apps.resume_screening.models import Resume


class ResumeRepository:
    """Repository for Resume model - encapsulates data access."""
    
    @staticmethod
    def create(
        *,
        resume_id: UUID,
        filename: str,
        file_path: str,
        raw_text: str = "",
    ) -> Resume:
        """Create a new Resume record."""
        return Resume.objects.create(
            id=resume_id,
            filename=filename,
            file_path=file_path,
            raw_text=raw_text,
        )
    
    @staticmethod
    def get_by_id(resume_id) -> Optional[Resume]:
        """Get Resume by UUID."""
        try:
            return Resume.objects.get(pk=resume_id)
        except Resume.DoesNotExist:
            return None
    
    @staticmethod
    def update_raw_text(resume_id: UUID, raw_text: str) -> Optional[Resume]:
        """Update raw_text for a Resume."""
        resume = ResumeRepository.get_by_id(resume_id)
        if resume:
            resume.raw_text = raw_text
            resume.save(update_fields=['raw_text'])
        return resume
    
    @staticmethod
    def update_embedding(resume_id: UUID, embedding: list) -> Optional[Resume]:
        """Update embedding for a Resume."""
        resume = ResumeRepository.get_by_id(resume_id)
        if resume:
            resume.embedding = embedding
            resume.save(update_fields=['embedding'])
        return resume
    
    @staticmethod
    def get_by_ids(resume_ids: list) -> List[Resume]:
        """Get resumes by list of UUIDs, preserving order."""
        if not resume_ids:
            return []
        found = {str(r.id): r for r in Resume.objects.filter(id__in=resume_ids)}
        return [found[str(rid)] for rid in resume_ids if str(rid) in found]
    
    @staticmethod
    def list_all(skip: int = 0, limit: int = 100) -> List[Resume]:
        """List resumes with pagination."""
        return list(Resume.objects.all()[skip:skip + limit])
    
    @staticmethod
    def delete(resume_id: UUID) -> bool:
        """Delete a Resume by UUID."""
        deleted, _ = Resume.objects.filter(pk=resume_id).delete()
        return deleted > 0
