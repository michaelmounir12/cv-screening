"""
URLs for resume screening API.
"""
from django.urls import path

from apps.resume_screening.views import ResumeUploadView, ResumeDetailView

urlpatterns = [
    path('resumes/upload/', ResumeUploadView.as_view(), name='resume-upload'),
    path('resumes/<uuid:resume_id>/', ResumeDetailView.as_view(), name='resume-detail'),
]
