"""Configuration for the SupportAI backend."""

import os
from enum import Enum


class EmbeddingProviderType(str, Enum):
    """Supported embedding providers."""

    MOCK = "mock"
    OPENAI = "openai"
    GEMINI = "gemini"


class Settings:
    """Application settings, loaded from environment variables."""

    # Embedding configuration
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", EmbeddingProviderType.MOCK.value)
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "768"))
    
    # OpenAI API configuration (for future use)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Gemini API configuration (for future use)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Data directory
    DATA_DIR = os.getenv("DATA_DIR", "backend/data")

    @classmethod
    def validate_provider(cls) -> None:
        """Validate that the configured provider is supported."""
        valid_providers = {provider.value for provider in EmbeddingProviderType}
        if cls.EMBEDDING_PROVIDER not in valid_providers:
            raise ValueError(
                f"Invalid EMBEDDING_PROVIDER: {cls.EMBEDDING_PROVIDER}. "
                f"Must be one of: {', '.join(valid_providers)}"
            )
