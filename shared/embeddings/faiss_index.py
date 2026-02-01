# shared/embeddings/faiss_index.py
"""
FAISS index management for fast similarity search.
"""

import os
import pickle
import numpy as np
import faiss
from typing import List, Tuple, Optional
from pathlib import Path
from shared.config import settings


class FAISSIndex:
    """
    FAISS index for storing and searching embeddings.
    Uses L2 distance (same as cosine similarity for normalized vectors).
    """
    
    def __init__(self, dimension: int = None):
        """
        Initialize FAISS index.
        
        Args:
            dimension: Embedding dimension (defaults to settings.EMBEDDING_DIM)
        """
        self.dimension = dimension or settings.EMBEDDING_DIM
        self.index = faiss.IndexFlatL2(self.dimension)
        self.id_map = []  # Maps FAISS index → job_id
    
    def add(self, embeddings: np.ndarray, ids: List[str]):
        """
        Add embeddings to index.
        
        Args:
            embeddings: numpy array of shape (n, dimension)
            ids: List of IDs (job_id, work_unit_id, etc.)
        """
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        self.id_map.extend(ids)
    
    def search(
        self, 
        query_embedding: np.ndarray, 
        k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Search for k most similar embeddings.
        
        Args:
            query_embedding: Query vector of shape (dimension,)
            k: Number of results to return
            
        Returns:
            List of (id, distance) tuples, sorted by similarity
        """
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Normalize query
        faiss.normalize_L2(query_embedding)
        
        # Search
        distances, indices = self.index.search(query_embedding, k)
        
        # Map indices to IDs
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.id_map):  # Valid index
                results.append((self.id_map[idx], float(dist)))
        
        return results
    
    def save(self, path: Optional[Path] = None):
        """
        Save index to disk.
        
        Args:
            path: Path to save (defaults to settings.FAISS_INDEX_PATH)
        """
        save_path = path or settings.FAISS_INDEX_PATH
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_file = str(save_path) + ".index"
        faiss.write_index(self.index, index_file)
        
        # Save ID map
        map_file = str(save_path) + ".map"
        with open(map_file, 'wb') as f:
            pickle.dump(self.id_map, f)
        
        print(f"[OK] FAISS index saved to {save_path}")
    
    def load(self, path: Optional[Path] = None):
        """
        Load index from disk.
        
        Args:
            path: Path to load from (defaults to settings.FAISS_INDEX_PATH)
        """
        load_path = path or settings.FAISS_INDEX_PATH
        load_path = Path(load_path)
        
        index_file = str(load_path) + ".index"
        map_file = str(load_path) + ".map"
        
        if not os.path.exists(index_file):
            raise FileNotFoundError(f"FAISS index not found: {index_file}")
        
        # Load FAISS index
        self.index = faiss.read_index(index_file)
        
        # Load ID map
        with open(map_file, 'rb') as f:
            self.id_map = pickle.load(f)
        
        print(f"[OK] FAISS index loaded from {load_path} ({len(self.id_map)} vectors)")
    
    def __len__(self):
        """Get number of vectors in index"""
        return self.index.ntotal
    
    def clear(self):
        """Clear all vectors from index"""
        self.index.reset()
        self.id_map = []
