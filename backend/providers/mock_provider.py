"""Mock embedding provider for testing and development."""

import hashlib
import logging

from backend.core.embeddings_protocol import EmbeddingProvider


logger = logging.getLogger(__name__)


class MockEmbeddingProvider:
    """
    Mock embedding provider that generates deterministic vectors.
    
    Uses hash-based generation to produce consistent embeddings
    for the same input text without external API calls.
    """

    def __init__(self, dimension: int = 768):
        """
        Initialize the mock provider.

        Args:
            dimension: Size of the embedding vectors (default 768)
        """
        self.dimension = dimension
        logger.info(f"Initialized MockEmbeddingProvider with dimension={dimension}")

    def embed(self, text: str) -> list[float]:
        """
        Generate a deterministic embedding for a single text.

        Uses SHA-256 hash of input text to seed a deterministic
        vector generation.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.dimension

        # Generate deterministic values from hash
        hash_obj = hashlib.sha256(text.encode("utf-8"))
        hash_bytes = hash_obj.digest()

        # Use hash bytes to seed random-like values
        vector = []
        for i in range(self.dimension):
            # Use different parts of hash for each dimension
            byte_idx = (i * 2) % len(hash_bytes)
            next_byte_idx = (i * 2 + 1) % len(hash_bytes)
            
            # Combine two bytes and normalize to [-1, 1]
            combined = (hash_bytes[byte_idx] + hash_bytes[next_byte_idx]) / 255.0
            normalized = (combined - 1.0) / 2.0  # Scale to approximately [-0.5, 0.5]
            vector.append(normalized)

        return vector

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        return [self.embed(text) for text in texts]
