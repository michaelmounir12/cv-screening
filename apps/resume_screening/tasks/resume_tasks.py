"""
Celery tasks for resume processing.
"""
from apps.resume_screening.celery_app import app
from apps.resume_screening.application.services.resume_service import ResumeService


@app.task(name='resume_screening.process_resume')
def process_resume_task(resume_id: int):
    """
    Background task to process a resume.
    
    Args:
        resume_id: ID of the resume to process
    """
    service = ResumeService()
    # Note: Celery tasks are sync, but we can use asyncio.run()
    import asyncio
    return asyncio.run(service.process_resume(resume_id))


@app.task(name='resume_screening.screen_resume')
def screen_resume_task(resume_id: int, job_posting_id: int):
    """
    Background task to screen a resume against a job posting.
    
    Args:
        resume_id: ID of the resume
        job_posting_id: ID of the job posting
    """
    service = ResumeService()
    import asyncio
    return asyncio.run(service.screen_resume(resume_id, job_posting_id))
