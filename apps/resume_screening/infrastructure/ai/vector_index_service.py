"""
FAISS vector index service with persistence and id mapping.
Uses IndexFlatIP for cosine similarity (vectors must be L2-normalized).
"""
import json
import logging
import threading
from pathlib import Path
from typing import List, Tuple
from uuid import UUID

import faiss
import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)

INDEX_FILENAME = "resume_index.faiss"
IDS_FILENAME = "resume_index_ids.json"
INDEX_LOCK = threading.RLock()


class VectorIndexService:
    """
    FAISS-backed vector index for resume embeddings.
    Maps index positions to resume UUIDs. Persists index and mapping to disk.
    """
    
    def __init__(
        self,
        dimension: int = 384,
        index_dir: Path = None,
    ):
        self.dimension = dimension
        self.index_dir = Path(index_dir or settings.FAISS_INDEX_PATH)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self._index: faiss.IndexFlatIP | None = None
        self._id_list: List[str] = []
        self._id_to_position: dict[str, int] = {}
    
    @property
    def index_path(self) -> Path:
        return self.index_dir / INDEX_FILENAME
    
    @property
    def ids_path(self) -> Path:
        return self.index_dir / IDS_FILENAME
    
    def _ensure_loaded(self) -> None:
        with INDEX_LOCK:
            if self._index is not None:
                return
            if self.index_path.exists():
                self._index = faiss.read_index(str(self.index_path))
                if self.ids_path.exists():
                    with open(self.ids_path) as f:
                        self._id_list = json.load(f)
                    self._id_to_position = {rid: i for i, rid in enumerate(self._id_list)}
                else:
                    self._id_list = []
                    self._id_to_position = {}
            else:
                self._index = faiss.IndexFlatIP(self.dimension)
                self._id_list = []
                self._id_to_position = {}
            logger.info(f"Vector index loaded: {len(self._id_list)} resumes")
    
    def add(self, resume_id: UUID, embedding: List[float]) -> None:
        """
        Add resume embedding. If resume_id already exists, replaces it via rebuild.
        """
        if len(embedding) != self.dimension:
            raise ValueError(f"Embedding dimension {len(embedding)} != {self.dimension}")
        
        vec = np.array([embedding], dtype=np.float32)
        rid = str(resume_id)
        
        with INDEX_LOCK:
            self._ensure_loaded()
            if rid in self._id_to_position:
                self._rebuild_without_and_add(rid, vec)
            else:
                self._index.add(vec)
                self._id_list.append(rid)
                self._id_to_position[rid] = len(self._id_list) - 1
            self._persist()
    
    def _rebuild_without_and_add(self, exclude_rid: str, new_vec: np.ndarray) -> None:
        """Rebuild index without exclude_rid, then add new_vec."""
        if exclude_rid not in self._id_to_position:
            return
        exclude_pos = self._id_to_position[exclude_rid]
        n = self._index.ntotal
        vectors = np.zeros((n - 1, self.dimension), dtype=np.float32)
        new_id_list = []
        j = 0
        for i in range(n):
            if i == exclude_pos:
                continue
            vectors[j] = self._index.reconstruct(i)
            new_id_list.append(self._id_list[i])
            j += 1
        self._index.reset()
        self._index.add(vectors)
        self._index.add(new_vec)
        new_id_list.append(exclude_rid)
        self._id_list = new_id_list
        self._id_to_position = {r: i for i, r in enumerate(self._id_list)}
    
    def search(
        self,
        query_embedding: List[float],
        k: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Search for top-k similar resumes by cosine similarity.
        Returns List[(resume_id_str, score)] ordered by score descending.
        """
        if len(query_embedding) != self.dimension:
            raise ValueError(f"Query dimension {len(query_embedding)} != {self.dimension}")
        
        with INDEX_LOCK:
            self._ensure_loaded()
            n = self._index.ntotal
            if n == 0:
                return []
            
            k = min(k, n)
            vec = np.array([query_embedding], dtype=np.float32)
            scores, indices = self._index.search(vec, k)
            
            return [
                (self._id_list[int(idx)], float(scores[0][i]))
                for i, idx in enumerate(indices[0])
                if 0 <= idx < len(self._id_list)
            ]
    
    def contains(self, resume_id: UUID) -> bool:
        with INDEX_LOCK:
            self._ensure_loaded()
            return str(resume_id) in self._id_to_position
    
    def count(self) -> int:
        with INDEX_LOCK:
            self._ensure_loaded()
            return self._index.ntotal
    
    def _persist(self) -> None:
        faiss.write_index(self._index, str(self.index_path))
        with open(self.ids_path, 'w') as f:
            json.dump(self._id_list, f)


def get_vector_index(dimension: int = 384) -> VectorIndexService:
    """Factory for vector index service."""
    return VectorIndexService(dimension=dimension)
