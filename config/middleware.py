"""
Logging and error handling middleware.
"""
import logging
import time
import traceback
import uuid

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)
REQUEST_ATTR = "_request_id"


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log each request with timing and request ID."""
    
    def process_request(self, request):
        request_id = str(uuid.uuid4())[:8]
        setattr(request, REQUEST_ATTR, request_id)
        request._start_time = time.monotonic()
        logger.info(
            "request_start",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "client_ip": self._get_client_ip(request),
            },
        )
        return None
    
    def process_response(self, request, response):
        request_id = getattr(request, REQUEST_ATTR, None)
        duration = 0
        if hasattr(request, "_start_time"):
            duration = round((time.monotonic() - request._start_time) * 1000)
        logger.info(
            "request_end",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": duration,
            },
        )
        if request_id and hasattr(response, "headers"):
            response["X-Request-ID"] = request_id
        return response
    
    def _get_client_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")


class ExceptionHandlingMiddleware(MiddlewareMixin):
    """
    Catch unhandled exceptions and return structured JSON error response.
    """
    
    def process_exception(self, request, exception):
        request_id = getattr(request, REQUEST_ATTR, None)
        tb = traceback.format_exc()
        logger.exception(
            "unhandled_exception",
            extra={
                "request_id": request_id,
                "path": request.path,
                "exception_type": type(exception).__name__,
                "exception_msg": str(exception),
            },
            exc_info=True,
        )
        status = 500
        if hasattr(exception, "status_code"):
            status = exception.status_code
        from django.conf import settings
        body = {
            "error": "Internal server error",
            "detail": str(exception) if settings.DEBUG else "An unexpected error occurred",
            "request_id": request_id,
        }
        if settings.DEBUG:
            body["traceback"] = tb
        return JsonResponse(body, status=status)
