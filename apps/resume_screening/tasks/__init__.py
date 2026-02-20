"""
Celery tasks.
"""
from .resume_tasks import extract_resume_text_task, generate_resume_embedding_task
from .index_tasks import rebuild_vector_index_task

__all__ = ['extract_resume_text_task', 'generate_resume_embedding_task', 'rebuild_vector_index_task']
