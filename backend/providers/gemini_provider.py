"""Gemini embedding provider for Google's generative AI."""

import logging

from google import genai
from google.genai import types

from backend.core.embeddings_protocol import EmbeddingProvider


logger = logging.getLogger(__name__)


class GeminiEmbeddingProvider:
    """
    Embedding provider using Google's Gemini API.
    
    Requires GEMINI_API_KEY environment variable to be set.
    Uses SEMANTIC_SIMILARITY task type for optimal results with FAQ clustering.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-embedding-001",
    ):
        """
        Initialize the Gemini provider.

        Args:
            api_key: Google Gemini API key
            model: Model name (default: gemini-embedding-001)

        Raises:
            ValueError: If api_key is empty or None
        """
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiEmbeddingProvider")

        self.model = model
        self.client = genai.Client(api_key=api_key)
        logger.info(f"Initialized GeminiEmbeddingProvider with model={model}")

    def embed(self, text: str) -> list[float]:
        """
        Generate an embedding for a single text using Gemini API.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector

        Raises:
            ValueError: If text is empty
            Exception: If API call fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty for embedding")

        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts using Gemini API.

        Uses SEMANTIC_SIMILARITY task type for optimal results when clustering
        similar support issues for FAQ generation.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors (same length as input)

        Raises:
            ValueError: If texts list is empty
            Exception: If API call fails
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")

        try:
            logger.info(f"Requesting embeddings for {len(texts)} texts from Gemini API")
            
            response = self.client.models.embed_content(
                model=self.model,
                contents=texts,
                config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY"),
            )

            # Extract embedding vectors
            embeddings = [emb.values for emb in response.embeddings]
            
            logger.debug(
                f"Generated {len(embeddings)} embeddings, "
                f"dimension={len(embeddings[0]) if embeddings else 0}"
            )

            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate embeddings with Gemini API: {e}")
            raise
