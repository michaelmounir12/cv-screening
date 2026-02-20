"""
Resume upload service - application layer.
Orchestrates file storage, DB persistence, and background processing.
"""
import uuid
from pathlib import Path
from typing import Dict, Any

from django.conf import settings

from apps.resume_screening.infrastructure.repositories.resume_repository import ResumeRepository
from apps.resume_screening.tasks.resume_tasks import extract_resume_text_task


class ResumeUploadService:
    """Service for resume upload operations."""
    
    UPLOAD_SUBDIR = "resumes"
    ALLOWED_EXTENSIONS = {".pdf"}
    MAX_FILENAME_LENGTH = 255
    
    @classmethod
    def upload_resume(cls, file) -> Dict[str, Any]:
        """
        Handle resume upload: save file, create DB record, queue extraction.
        
        Args:
            file: Django UploadedFile (PDF)
            
        Returns:
            Dict with resume id, filename, file_path, status
            
        Raises:
            ValueError: If file validation fails
        """
        cls._validate_file(file)
        
        resume_id = uuid.uuid4()
        filename = cls._sanitize_filename(file.name)
        
        file_path = cls._save_file(file, resume_id, filename)
        
        resume = ResumeRepository.create(
            resume_id=resume_id,
            filename=filename,
            file_path=str(file_path),
            raw_text="",
        )
        
        extract_resume_text_task.delay(str(resume.id))
        
        return {
            "id": str(resume.id),
            "filename": resume.filename,
            "file_path": resume.file_path,
            "status": "processing",
            "created_at": resume.created_at.isoformat(),
        }
    
    @classmethod
    def _validate_file(cls, file) -> None:
        """Validate uploaded file."""
        if not file:
            raise ValueError("No file provided")
        
        if file.size == 0:
            raise ValueError("File is empty")
        
        ext = Path(file.name).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(f"Invalid file type. Allowed: {list(cls.ALLOWED_EXTENSIONS)}")
        
        if len(file.name) > cls.MAX_FILENAME_LENGTH:
            raise ValueError(f"Filename too long (max {cls.MAX_FILENAME_LENGTH} chars)")
    
    @classmethod
    def _sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename for storage."""
        name = Path(filename).stem
        ext = Path(filename).suffix.lower()
        safe_name = "".join(c for c in name if c.isalnum() or c in "._- ")[:200]
        return f"{safe_name}{ext}" if safe_name else f"resume{ext}"
    
    @classmethod
    def _save_file(cls, file, resume_id: uuid.UUID, filename: str) -> Path:
        """Save uploaded file to disk. Returns full path."""
        media_root = Path(settings.MEDIA_ROOT)
        upload_dir = media_root / cls.UPLOAD_SUBDIR
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{resume_id}_{filename}"
        
        with open(file_path, "wb") as dest:
            for chunk in file.chunks():
                dest.write(chunk)
        
        return file_path
