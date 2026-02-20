"""
Views for resume screening API.
Thin layer - no business logic, delegates to services.
"""
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.resume_screening.application.services.job_service import JobPostingService
from apps.resume_screening.application.services.matching_service import MatchingService
from apps.resume_screening.application.services.resume_upload_service import ResumeUploadService
from apps.resume_screening.infrastructure.repositories.resume_repository import ResumeRepository
from apps.resume_screening.serializers import (
    JobPostingCreateSerializer,
    MatchResultSerializer,
    ResumeDetailSerializer,
    ResumeUploadSerializer,
)


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


class JobPostingCreateView(APIView):
    """Create job posting with embedding generation."""
    parser_classes = [JSONParser]
    
    def post(self, request: Request) -> Response:
        serializer = JobPostingCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = JobPostingService().create_job(
                title=serializer.validated_data["title"],
                description=serializer.validated_data["description"],
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"error": "Job creation failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MatchResumesView(APIView):
    """Match job to resumes - returns top 5 by cosine similarity."""
    parser_classes = [JSONParser]
    
    def post(self, request: Request) -> Response:
        """
        Body: {"job_id": "uuid"} or {"description": "job description text"}
        Returns top 5 matching resumes.
        """
        job_id = request.data.get("job_id")
        description = request.data.get("description")
        
        if not job_id and not description:
            return Response(
                {"error": "Provide either job_id or description"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if job_id and description:
            return Response(
                {"error": "Provide only one of job_id or description"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            service = MatchingService()
            k = min(int(request.data.get("k", 5)), 20)
            if job_id:
                from uuid import UUID
                results = service.find_top_resumes(UUID(str(job_id)), k=k)
            else:
                results = service.find_top_resumes_by_description(description, k=k)
            return Response({"matches": results})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response(
                {"error": "Matching failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
