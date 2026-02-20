"""
Embedding service - factory and singleton access.
Provides clean abstraction over embedding providers.
"""
from typing import List, Union

import numpy as np

from .embedding_protocol import EmbeddingProvider
from .sentence_transformer_provider import SentenceTransformerProvider

# Default provider instance (lazy singleton)
_default_provider: EmbeddingProvider | None = None


def get_embedding_provider() -> EmbeddingProvider:
    """Get the default embedding provider (thread-safe for Celery/Django)."""
    global _default_provider
    if _default_provider is None:
        _default_provider = SentenceTransformerProvider()
    return _default_provider


def set_embedding_provider(provider: EmbeddingProvider) -> None:
    """Set custom provider (for testing)."""
    global _default_provider
    _default_provider = provider


class EmbeddingService:
    """
    Production embedding service facade.
    Delegates to configured EmbeddingProvider.
    """
    
    def __init__(self, provider: EmbeddingProvider = None):
        self._provider = provider or get_embedding_provider()
    
    @property
    def dimension(self) -> int:
        return self._provider.dimension
    
    def encode(
        self,
        texts: Union[str, List[str]],
        *,
        batch_size: int = 32,
        normalize: bool = True,
    ) -> np.ndarray:
        """Encode texts to normalized embeddings (for cosine similarity)."""
        return self._provider.encode(
            texts,
            batch_size=batch_size,
            show_progress=False,
            normalize=normalize,
        )
    
    def encode_single(self, text: str) -> List[float]:
        """Encode single text."""
        return self._provider.encode_single(text, normalize=True)
    
    def encode_resume_text(self, raw_text: str) -> List[float]:
        """
        Encode resume text with sensible truncation.
        Resumes can be long; we use first N chars for embedding.
        """
        if not raw_text or not raw_text.strip():
            raise ValueError("Resume text is empty")
        # Truncate to ~4K chars to stay within model limits
        truncated = raw_text[:4000].strip() if len(raw_text) > 4000 else raw_text
        return self.encode_single(truncated)
    
    def encode_job_description(self, description: str) -> List[float]:
        """Encode job description."""
        if not description or not description.strip():
            raise ValueError("Job description is empty")
        truncated = description[:2000].strip() if len(description) > 2000 else description
        return self.encode_single(truncated)
