"""Provider protocol for embedding generation."""

from typing import Protocol


class EmbeddingProvider(Protocol):
    """
    Protocol for embedding providers.
    
    Any embedding provider (OpenAI, local, mock, etc.) must implement
    both methods to satisfy this protocol.
    """

    def embed(self, text: str) -> list[float]:
        """
        Generate an embedding for a single text input.

        Args:
            text: The text to embed

        Returns:
            A list of floats representing the embedding vector
        """
        ...

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple text inputs.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors (same length as input list)
        """
        ...
