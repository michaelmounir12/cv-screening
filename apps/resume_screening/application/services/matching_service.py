"""
Matching service - job-to-resume similarity search.
"""
from typing import List, Dict, Any
from uuid import UUID

from apps.resume_screening.infrastructure.ai.embedding_service import EmbeddingService
from apps.resume_screening.infrastructure.ai.vector_index_service import get_vector_index
from apps.resume_screening.infrastructure.repositories.job_repository import JobPostingRepository
from apps.resume_screening.infrastructure.repositories.resume_repository import ResumeRepository

TOP_K = 5


class MatchingService:
    """Service for matching job descriptions to resumes via vector similarity."""
    
    def __init__(self):
        self._embedding_service = EmbeddingService()
        self._vector_index = get_vector_index(dimension=self._embedding_service.dimension)
    
    def find_top_resumes(
        self,
        job_id: UUID,
        k: int = TOP_K,
    ) -> List[Dict[str, Any]]:
        """
        Find top-k resumes matching a job posting.
        
        Args:
            job_id: Job posting UUID
            k: Number of results (default 5)
            
        Returns:
            List of dicts with resume_id, filename, similarity_score, raw_text_preview
        """
        job = JobPostingRepository.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")
        
        if job.embedding:
            query_embedding = job.embedding
        else:
            query_embedding = self._embedding_service.encode_job_description(job.description)
            JobPostingRepository.update_embedding(job_id, query_embedding)
        
        results = self._vector_index.search(query_embedding, k=k)
        if not results:
            return []
        
        resume_ids = [UUID(rid) for rid, _ in results]
        resumes = ResumeRepository.get_by_ids(resume_ids)
        
        output = []
        for (resume_id_str, score), resume in zip(results, resumes):
            if resume is None:
                continue
            output.append({
                "resume_id": str(resume.id),
                "filename": resume.filename,
                "similarity_score": round(score, 4),
                "raw_text_preview": resume.raw_text[:500] + "..." if len(resume.raw_text) > 500 else resume.raw_text,
            })
        return output
    
    def find_top_resumes_by_description(
        self,
        description: str,
        k: int = TOP_K,
    ) -> List[Dict[str, Any]]:
        """
        Find top-k resumes matching a job description string (no stored job).
        """
        query_embedding = self._embedding_service.encode_job_description(description)
        results = self._vector_index.search(query_embedding, k=k)
        if not results:
            return []
        
        resume_ids = [UUID(rid) for rid, _ in results]
        resumes = ResumeRepository.get_by_ids(resume_ids)
        
        return [
            {
                "resume_id": str(r.id),
                "filename": r.filename,
                "similarity_score": round(score, 4),
                "raw_text_preview": r.raw_text[:500] + "..." if len(r.raw_text) > 500 else r.raw_text,
            }
            for (_, score), r in zip(results, resumes)
            if r is not None
        ]
