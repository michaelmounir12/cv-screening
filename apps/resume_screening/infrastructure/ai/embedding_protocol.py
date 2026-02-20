"""
Abstract embedding protocol - clean abstraction for embedding providers.
"""
from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np


class EmbeddingProvider(ABC):
    """Abstract interface for text embedding providers."""
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return embedding dimension."""
        ...
    
    @abstractmethod
    def encode(
        self,
        texts: Union[str, List[str]],
        *,
        batch_size: int = 32,
        show_progress: bool = False,
        normalize: bool = True,
    ) -> np.ndarray:
        """
        Encode text(s) to embedding vectors.
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for encoding
            show_progress: Show progress bar
            normalize: L2-normalize vectors (for cosine similarity)
            
        Returns:
            np.ndarray of shape (n, dimension), float32
        """
        ...
    
    @abstractmethod
    def encode_single(self, text: str, *, normalize: bool = True) -> List[float]:
        """Encode a single text. Returns list of floats."""
        ...
