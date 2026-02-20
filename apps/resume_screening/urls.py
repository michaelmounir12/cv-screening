"""
URLs for resume screening API.
"""
from django.urls import path

from apps.resume_screening.views import (
    BatchResumeUploadView,
    JobPostingCreateView,
    JobPostingDetailView,
    JobPostingListView,
    MatchResumesView,
    RankingView,
    ResumeDetailView,
    ResumeUploadView,
    SemanticSearchView,
)

urlpatterns = [
    path('resumes/upload/', ResumeUploadView.as_view(), name='resume-upload'),
    path('resumes/upload/batch/', BatchResumeUploadView.as_view(), name='resume-batch-upload'),
    path('resumes/<uuid:resume_id>/', ResumeDetailView.as_view(), name='resume-detail'),
    path('jobs/', JobPostingCreateView.as_view(), name='job-create'),
    path('jobs/list/', JobPostingListView.as_view(), name='job-list'),
    path('jobs/<uuid:job_id>/', JobPostingDetailView.as_view(), name='job-detail'),
    path('match/', MatchResumesView.as_view(), name='match-resumes'),
    path('rank/', RankingView.as_view(), name='rank-resumes'),
    path('search/', SemanticSearchView.as_view(), name='semantic-search'),
]
