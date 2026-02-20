"""
Celery tasks for index maintenance.
"""
import logging
from uuid import UUID

from apps.resume_screening.celery_app import app
from apps.resume_screening.application.services.embedding_generation_service import EmbeddingGenerationService
from apps.resume_screening.infrastructure.repositories.resume_repository import ResumeRepository

logger = logging.getLogger(__name__)


@app.task(name='resume_screening.rebuild_vector_index')
def rebuild_vector_index_task() -> dict:
    """
    Rebuild FAISS vector index from all resumes with embeddings.
    Use after bulk imports or index corruption.
    """
    try:
        service = EmbeddingGenerationService()
        resumes = ResumeRepository.list_all(skip=0, limit=10000)
        count = 0
        for r in resumes:
            if r.embedding and r.raw_text:
                try:
                    service.generate_and_index_resume(r.id)
                    count += 1
                except Exception as e:
                    logger.warning(f"Skip resume {r.id}: {e}")
        return {"status": "success", "indexed": count}
    except Exception as e:
        logger.exception(f"Index rebuild failed: {e}")
        return {"status": "error", "message": str(e)}
