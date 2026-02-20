"""
URLs for resume screening API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from apps.resume_screening.views import ResumeViewSet

router = DefaultRouter()
# router.register(r'resumes', ResumeViewSet, basename='resume')

urlpatterns = [
    path('', include(router.urls)),
]
