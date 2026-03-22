"""Factory for creating embedding providers."""

import logging

from backend.config import Settings, EmbeddingProviderType, LLMProviderType
from backend.core.embeddings_protocol import EmbeddingProvider
from backend.core.llm_protocol import LLM
from backend.providers.mock_provider import MockEmbeddingProvider
from backend.providers.gemini_provider import GeminiEmbeddingProvider
from backend.providers.mock_llm import MockLLM


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
        ValueError: If provider_type is invalid or required config is missing
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
    
    elif provider_enum == EmbeddingProviderType.GEMINI:
        return GeminiEmbeddingProvider(
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_MODEL,
        )
    
    # TODO: Add OpenAI provider later
    # elif provider_enum == EmbeddingProviderType.OPENAI:
    #     return OpenAIEmbeddingProvider(...)
    
    raise NotImplementedError(f"Provider {provider_enum.value} not yet implemented")


def get_llm_provider(
    provider_type: str = None,
    settings: Settings = None,
) -> LLM:
    """
    Factory function to get the configured LLM provider.

    Args:
        provider_type: Type of provider (overrides settings if provided)
        settings: Settings instance (uses Settings class if not provided)

    Returns:
        An instance implementing the LLM protocol

    Raises:
        ValueError: If provider_type is invalid or required config is missing
    """
    if settings is None:
        settings = Settings

    if provider_type is None:
        provider_type = settings.LLM_PROVIDER

    # Validate provider
    try:
        provider_enum = LLMProviderType(provider_type)
    except ValueError:
        raise ValueError(
            f"Invalid LLM provider type: {provider_type}. "
            f"Must be one of: {', '.join([p.value for p in LLMProviderType])}"
        )

    logger.info(f"Creating LLM provider: {provider_enum.value}")

    if provider_enum == LLMProviderType.MOCK:
        return MockLLM()
    
    # TODO: Add Gemini LLM provider
    # elif provider_enum == LLMProviderType.GEMINI:
    #     return GeminiLLMProvider(api_key=settings.LLM_API_KEY)
    
    # TODO: Add OpenAI LLM provider
    # elif provider_enum == LLMProviderType.OPENAI:
    #     return OpenAILLMProvider(api_key=settings.OPENAI_API_KEY)
    
    raise NotImplementedError(f"LLM provider {provider_enum.value} not yet implemented")
