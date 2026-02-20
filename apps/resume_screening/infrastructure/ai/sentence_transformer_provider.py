"""
SentenceTransformer embedding provider - production implementation.
Uses all-MiniLM-L6-v2 (384 dimensions).
"""
import logging
from typing import List, Union

import numpy as np
from django.conf import settings

from .embedding_protocol import EmbeddingProvider

logger = logging.getLogger(__name__)

# Model config - all-MiniLM-L6-v2 outputs 384-dim vectors
MINILM_DIMENSION = 384
DEFAULT_MAX_SEQ_LENGTH = 256
DEFAULT_TRUNCATE = True


class SentenceTransformerProvider(EmbeddingProvider):
    """SentenceTransformer-based embedding provider."""
    
    def __init__(
        self,
        model_name: str = None,
        cache_dir: str = None,
        max_seq_length: int = DEFAULT_MAX_SEQ_LENGTH,
        truncate: bool = DEFAULT_TRUNCATE,
    ):
        self._model = None
        self._model_name = model_name or getattr(
            settings, 'HF_MODEL_NAME', 'sentence-transformers/all-MiniLM-L6-v2'
        )
        self._cache_dir = str(cache_dir or getattr(settings, 'HF_MODEL_CACHE_DIR', 'models_cache'))
        self._max_seq_length = max_seq_length
        self._truncate = truncate
    
    @property
    def model(self):
        """Lazy-load model to avoid loading at import time."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            import os
            os.makedirs(self._cache_dir, exist_ok=True)
            self._model = SentenceTransformer(
                self._model_name,
                cache_folder=self._cache_dir,
            )
            self._model.max_seq_length = self._max_seq_length
            logger.info(f"Loaded embedding model: {self._model_name}")
        return self._model
    
    @property
    def dimension(self) -> int:
        return MINILM_DIMENSION
    
    def encode(
        self,
        texts: Union[str, List[str]],
        *,
        batch_size: int = 32,
        show_progress: bool = False,
        normalize: bool = True,
    ) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
        if not texts:
            return np.zeros((0, self.dimension), dtype=np.float32)
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=normalize,
            truncate=self._truncate,
        )
        return embeddings.astype(np.float32)
    
    def encode_single(self, text: str, *, normalize: bool = True) -> List[float]:
        arr = self.encode([text], normalize=normalize)
        return arr[0].tolist()
