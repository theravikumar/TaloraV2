# shared/embeddings/generator.py
"""
Embedding generation using sentence-transformers.
Singleton pattern for efficient model loading.
"""

import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
from shared.config import settings


class EmbeddingGenerator:
    """
    Singleton embedding generator.
    Loads model once and reuses for all embeddings.
    """
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            print(f"Loading embedding model: {settings.EMBEDDING_MODEL}...")
            self._model = SentenceTransformer(
                settings.EMBEDDING_MODEL,
                device=settings.EMBEDDING_DEVICE,
            )
            print(f"[OK] Model loaded on {settings.EMBEDDING_DEVICE}")
    
    def embed(self, text: str) -> np.ndarray:
        """
        Generate embedding for single text.
        
        Args:
            text: Text to embed
            
        Returns:
            numpy array of shape (embedding_dim,)
        """
        embedding = self._model.encode(
            text,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return embedding
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts (efficient).
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 100,
        )
        return embeddings
    
    @property
    def embedding_dim(self) -> int:
        """Get embedding dimension"""
        return self._model.get_sentence_embedding_dimension()
    
    def test(self) -> bool:
        """Test if embeddings work correctly"""
        try:
            test_text = "This is a test sentence."
            embedding = self.embed(test_text)
            
            # Verify shape
            expected_dim = settings.EMBEDDING_DIM
            actual_dim = embedding.shape[0]
            
            if actual_dim != expected_dim:
                print(f"Warning: Expected {expected_dim}D embeddings, got {actual_dim}D")
                return False
            
            print(f"[OK] Embeddings working ({actual_dim}D)")
            return True
            
        except Exception as e:
            print(f"[ERROR] Embedding test failed: {e}")
            return False


# Singleton instance
embedding_generator = EmbeddingGenerator()
