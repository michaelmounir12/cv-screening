"""
FAISS vector similarity search service.
"""
from typing import List, Tuple
import numpy as np
import faiss
from django.conf import settings
import os


class FAISSService:
    """Service for FAISS vector similarity search."""
    
    def __init__(self, dimension: int = 384):
        """
        Initialize FAISS service.
        
        Args:
            dimension: Dimension of the embeddings (default 384 for all-MiniLM-L6-v2)
        """
        self.dimension = dimension
        self.index = None
        self.index_path = settings.FAISS_INDEX_PATH
        os.makedirs(self.index_path, exist_ok=True)
    
    def create_index(self, index_type: str = 'IndexFlatL2') -> None:
        """
        Create a new FAISS index.
        
        Args:
            index_type: Type of index ('IndexFlatL2', 'IndexIVFFlat', etc.)
        """
        if index_type == 'IndexFlatL2':
            self.index = faiss.IndexFlatL2(self.dimension)
        elif index_type == 'IndexIVFFlat':
            # Requires training data - simplified for now
            self.index = faiss.IndexFlatL2(self.dimension)
        else:
            raise ValueError(f"Unsupported index type: {index_type}")
    
    def add_vectors(self, vectors: np.ndarray) -> None:
        """
        Add vectors to the index.
        
        Args:
            vectors: numpy array of shape (n, dimension)
        """
        if self.index is None:
            self.create_index()
        
        # Ensure vectors are float32
        vectors = vectors.astype('float32')
        self.index.add(vectors)
    
    def search(self, query_vector: np.ndarray, k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query vector of shape (dimension,) or (1, dimension)
            k: Number of results to return
            
        Returns:
            Tuple of (distances, indices)
        """
        if self.index is None:
            raise ValueError("Index not initialized. Call create_index() first.")
        
        # Ensure query_vector is 2D
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        
        query_vector = query_vector.astype('float32')
        
        distances, indices = self.index.search(query_vector, k)
        return distances[0], indices[0]
    
    def save_index(self, filename: str) -> None:
        """Save index to disk."""
        if self.index is None:
            raise ValueError("No index to save.")
        filepath = self.index_path / filename
        faiss.write_index(self.index, str(filepath))
    
    def load_index(self, filename: str) -> None:
        """Load index from disk."""
        filepath = self.index_path / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Index file not found: {filepath}")
        self.index = faiss.read_index(str(filepath))
