"""
Django models for resume screening.
"""
import uuid
from django.db import models


class Resume(models.Model):
    """Resume model for uploaded PDF files."""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    raw_text = models.TextField(blank=True)
    embedding = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'resume_screening_resumes'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.filename} ({self.id})"
