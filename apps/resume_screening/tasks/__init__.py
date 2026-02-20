"""
Celery tasks.
"""
from .resume_tasks import extract_resume_text_task, generate_resume_embedding_task

__all__ = ['extract_resume_text_task', 'generate_resume_embedding_task']
