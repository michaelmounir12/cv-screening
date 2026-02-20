"""
PDF text extraction service using PyMuPDF with pdfplumber fallback.
"""
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PdfTextExtractionService:
    """Extracts text from PDF files."""
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Uses PyMuPDF first (faster), falls back to pdfplumber for complex layouts.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
            
        Raises:
            ValueError: If file is not a PDF or extraction fails
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        if path.suffix.lower() != '.pdf':
            raise ValueError(f"Invalid file type. Expected PDF, got: {path.suffix}")
        
        text = PdfTextExtractionService._extract_with_pymupdf(file_path)
        if text and text.strip():
            return text.strip()
        
        text = PdfTextExtractionService._extract_with_pdfplumber(file_path)
        if text:
            return text.strip()
        
        return ""
    
    @staticmethod
    def _extract_with_pymupdf(file_path: str) -> str:
        """Extract text using PyMuPDF (fitz)."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
            return "\n".join(text_parts)
        except ImportError:
            logger.warning("PyMuPDF not installed, skipping")
            return ""
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {e}")
            return ""
    
    @staticmethod
    def _extract_with_pdfplumber(file_path: str) -> str:
        """Extract text using pdfplumber (fallback)."""
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            return "\n".join(text_parts) if text_parts else ""
        except ImportError:
            logger.warning("pdfplumber not installed, skipping")
            return ""
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
            return ""
