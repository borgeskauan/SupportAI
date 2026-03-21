"""Factory for creating embedding providers."""

import logging

from backend.config import Settings, EmbeddingProviderType
from backend.core.embeddings_protocol import EmbeddingProvider
from backend.providers.mock_provider import MockEmbeddingProvider


logger = logging.getLogger(__name__)


def get_embedding_provider(
    provider_type: str = None,
    settings: Settings = None,
) -> EmbeddingProvider:
    """
    Factory function to get the configured embedding provider.

    Args:
        provider_type: Type of provider (overrides settings if provided)
        settings: Settings instance (uses Settings class if not provided)

    Returns:
        An instance implementing the EmbeddingProvider protocol

    Raises:
        ValueError: If provider_type is invalid
    """
    if settings is None:
        settings = Settings

    if provider_type is None:
        provider_type = settings.EMBEDDING_PROVIDER

    # Validate provider
    try:
        provider_enum = EmbeddingProviderType(provider_type)
    except ValueError:
        raise ValueError(
            f"Invalid provider type: {provider_type}. "
            f"Must be one of: {', '.join([p.value for p in EmbeddingProviderType])}"
        )

    logger.info(f"Creating embedding provider: {provider_enum.value}")

    if provider_enum == EmbeddingProviderType.MOCK:
        return MockEmbeddingProvider(dimension=settings.EMBEDDING_DIMENSION)
    
    # TODO: Add OpenAI provider in Task 2.2b
    # elif provider_enum == EmbeddingProviderType.OPENAI:
    #     return OpenAIEmbeddingProvider(...)
    
    # TODO: Add Gemini provider in Task 2.2c
    # elif provider_enum == EmbeddingProviderType.GEMINI:
    #     return GeminiEmbeddingProvider(...)
    
    raise NotImplementedError(f"Provider {provider_enum.value} not yet implemented")
