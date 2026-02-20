"""
Batch resume upload service.
"""
from typing import Dict, Any, List

from apps.resume_screening.application.services.resume_upload_service import ResumeUploadService
from apps.resume_screening.tasks.resume_tasks import extract_resume_text_task


class BatchResumeUploadService:
    """Service for batch resume uploads."""
    
    MAX_BATCH_SIZE = 50
    
    @classmethod
    def upload_batch(cls, files: List) -> Dict[str, Any]:
        """
        Upload multiple resumes. Returns list of created resume summaries.
        Queues each for extraction + embedding in Celery.
        """
        if not files:
            raise ValueError("No files provided")
        if len(files) > cls.MAX_BATCH_SIZE:
            raise ValueError(f"Batch size exceeds maximum ({cls.MAX_BATCH_SIZE})")
        
        results = []
        errors = []
        for i, file in enumerate(files):
            try:
                result = ResumeUploadService.upload_resume(file)
                results.append(result)
            except ValueError as e:
                errors.append({"index": i, "filename": getattr(file, "name", "unknown"), "error": str(e)})
        
        return {
            "uploaded": len(results),
            "failed": len(errors),
            "resumes": results,
            "errors": errors,
        }
