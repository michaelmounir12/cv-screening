"""
Embedding generation service - generates and persists embeddings.
"""
from uuid import UUID

from apps.resume_screening.infrastructure.ai.embedding_service import EmbeddingService
from apps.resume_screening.infrastructure.ai.vector_index_service import get_vector_index
from apps.resume_screening.infrastructure.repositories.resume_repository import ResumeRepository


class EmbeddingGenerationService:
    """Service for generating resume embeddings and adding to vector index."""
    
    def generate_and_index_resume(self, resume_id: UUID) -> None:
        """
        Generate embedding for resume and add to FAISS index.
        Updates resume.embedding in DB.
        """
        resume = ResumeRepository.get_by_id(resume_id)
        if not resume:
            raise ValueError(f"Resume not found: {resume_id}")
        if not resume.raw_text or not resume.raw_text.strip():
            raise ValueError(f"Resume has no text to embed: {resume_id}")
        
        embedding_svc = EmbeddingService()
        embedding = embedding_svc.encode_resume_text(resume.raw_text)
        
        ResumeRepository.update_embedding(resume_id, embedding)
        
        vector_index = get_vector_index(dimension=embedding_svc.dimension)
        vector_index.add(resume_id, embedding)
