"""
Semantic search - free-text search over resumes using embeddings.
"""
from typing import List, Dict, Any
from uuid import UUID

from apps.resume_screening.infrastructure.ai.embedding_service import EmbeddingService
from apps.resume_screening.infrastructure.ai.vector_index_service import get_vector_index
from apps.resume_screening.infrastructure.repositories.resume_repository import ResumeRepository


class SemanticSearchService:
    """Semantic search over resumes using natural language queries."""
    
    def __init__(self):
        self._embedding_service = EmbeddingService()
        self._vector_index = get_vector_index(dimension=self._embedding_service.dimension)
    
    def search(
        self,
        query: str,
        k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search resumes by semantic similarity to query text.
        
        Args:
            query: Natural language search query
            k: Number of results
            
        Returns:
            List of dicts with resume_id, filename, similarity_score, raw_text_preview, extracted_skills
        """
        if not query or not query.strip():
            return []
        
        query_embedding = self._embedding_service.encode_single(query.strip()[:2000])
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
                "extracted_skills": r.extracted_skills or [],
            }
            for (_, score), r in zip(results, resumes)
            if r is not None
        ]
