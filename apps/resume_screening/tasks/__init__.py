"""
Celery tasks.
"""
from .resume_tasks import extract_resume_text_task

__all__ = ['extract_resume_text_task']
