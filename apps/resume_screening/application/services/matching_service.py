"""
Matching service - job-to-resume similarity search with Redis caching.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID

from apps.resume_screening.infrastructure.ai.embedding_service import EmbeddingService
from apps.resume_screening.infrastructure.ai.vector_index_service import get_vector_index
from apps.resume_screening.infrastructure.repositories.job_repository import JobPostingRepository
from apps.resume_screening.infrastructure.repositories.resume_repository import ResumeRepository
from apps.resume_screening.infrastructure.services.cache_service import get_cached_search, set_cached_search

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
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Find top-k resumes matching a job posting.
        Results are cached in Redis when use_cache=True.
        
        Args:
            job_id: Job posting UUID
            k: Number of results (default 5)
            use_cache: Whether to use Redis cache
            
        Returns:
            List of dicts with resume_id, filename, similarity_score, raw_text_preview
        """
        if use_cache:
            cached = get_cached_search(str(job_id), k, None)
            if cached is not None:
                return cached
        
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
                "extracted_skills": resume.extracted_skills or [],
            })
        if use_cache and output:
            set_cached_search(str(job_id), k, output, None)
        return output
    
    def find_top_resumes_by_description(
        self,
        description: str,
        k: int = TOP_K,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Find top-k resumes matching a job description string (no stored job).
        Results are cached when use_cache=True.
        """
        if use_cache:
            cached = get_cached_search(None, k, description)
            if cached is not None:
                return cached
        query_embedding = self._embedding_service.encode_job_description(description)
        results = self._vector_index.search(query_embedding, k=k)
        if not results:
            return []
        
        resume_ids = [UUID(rid) for rid, _ in results]
        resumes = ResumeRepository.get_by_ids(resume_ids)
        
        output = [
            {
                "resume_id": str(r.id),
                "filename": r.filename,
                "similarity_score": round(score, 4),
                "raw_text_preview": r.raw_text[:500] + "..." if len(r.raw_text) > 500 else r.raw_text,
                "extracted_skills": r.extracted_skills or [],
            }
            for (_, score), r in zip(results, resumes)
            if r is not None
        ]
        if use_cache and output:
            set_cached_search(None, k, output, description)
        return output
