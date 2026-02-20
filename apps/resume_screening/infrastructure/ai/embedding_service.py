"""
Embedding service using SentenceTransformers.
"""
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from django.conf import settings
import os


class EmbeddingService:
    """Service for generating text embeddings."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            model_path = settings.HF_MODEL_NAME
            cache_dir = str(settings.HF_MODEL_CACHE_DIR)
            os.makedirs(cache_dir, exist_ok=True)
            self._model = SentenceTransformer(
                model_path,
                cache_folder=cache_dir
            )
    
    @property
    def model(self) -> SentenceTransformer:
        """Get the SentenceTransformer model."""
        if self._model is None:
            self.__init__()
        return self._model
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        return self.model.encode(texts, convert_to_numpy=True)
    
    def encode_single(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to encode
            
        Returns:
            List of float values representing the embedding
        """
        embedding = self.encode([text])
        return embedding[0].tolist()
