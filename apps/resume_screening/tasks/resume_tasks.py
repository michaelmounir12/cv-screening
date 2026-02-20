"""
Celery tasks for resume processing.
"""
import logging
from uuid import UUID

from apps.resume_screening.celery_app import app
from apps.resume_screening.infrastructure.repositories.resume_repository import ResumeRepository
from apps.resume_screening.infrastructure.services.pdf_extraction_service import PdfTextExtractionService

logger = logging.getLogger(__name__)


@app.task(name='resume_screening.extract_resume_text')
def extract_resume_text_task(resume_id: str) -> dict:
    """
    Background task: extract text from PDF and update Resume record.
    
    Args:
        resume_id: UUID string of the resume
        
    Returns:
        Dict with status and extracted text length
    """
    try:
        resume = ResumeRepository.get_by_id(UUID(resume_id))
        if not resume:
            logger.error(f"Resume not found: {resume_id}")
            return {"status": "error", "message": "Resume not found"}
        
        raw_text = PdfTextExtractionService.extract_text(resume.file_path)
        
        ResumeRepository.update_raw_text(UUID(resume_id), raw_text)
        
        logger.info(f"Extracted {len(raw_text)} chars from resume {resume_id}")
        return {
            "status": "success",
            "resume_id": resume_id,
            "text_length": len(raw_text),
        }
    except FileNotFoundError as e:
        logger.error(f"File not found for resume {resume_id}: {e}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.exception(f"Failed to extract text from resume {resume_id}: {e}")
        return {"status": "error", "message": str(e)}
