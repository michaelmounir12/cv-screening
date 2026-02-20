"""
URLs for resume screening API.
"""
from django.urls import path

from apps.resume_screening.views import (
    JobPostingCreateView,
    MatchResumesView,
    ResumeDetailView,
    ResumeUploadView,
)

urlpatterns = [
    path('resumes/upload/', ResumeUploadView.as_view(), name='resume-upload'),
    path('resumes/<uuid:resume_id>/', ResumeDetailView.as_view(), name='resume-detail'),
    path('jobs/', JobPostingCreateView.as_view(), name='job-create'),
    path('match/', MatchResumesView.as_view(), name='match-resumes'),
]
