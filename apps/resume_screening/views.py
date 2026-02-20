"""
Views for resume screening API.
Thin layer - no business logic, delegates to services.
"""
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.resume_screening.application.services.resume_upload_service import ResumeUploadService
from apps.resume_screening.infrastructure.repositories.resume_repository import ResumeRepository
from apps.resume_screening.serializers import ResumeDetailSerializer, ResumeUploadSerializer


class ResumeUploadView(APIView):
    """Upload PDF resume - delegates to ResumeUploadService."""
    
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request: Request) -> Response:
        """
        Accept PDF file upload.
        
        Expected: multipart/form-data with 'file' key
        """
        file = request.FILES.get("file")
        
        if not file:
            return Response(
                {"error": "No file provided. Use 'file' form field for PDF upload."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            result = ResumeUploadService.upload_resume(file)
            serializer = ResumeUploadSerializer(result)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": "Upload failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResumeDetailView(APIView):
    """Retrieve resume by ID."""
    
    def get(self, request: Request, resume_id: str) -> Response:
        """Get resume details including extracted text."""
        resume = ResumeRepository.get_by_id(resume_id)
        
        if not resume:
            return Response(
                {"error": "Resume not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        serializer = ResumeDetailSerializer({
            "id": resume.id,
            "filename": resume.filename,
            "file_path": resume.file_path,
            "raw_text": resume.raw_text,
            "created_at": resume.created_at,
        })
        return Response(serializer.data)
