"""Configuration for the SupportAI backend."""

import os
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv


# Load environment variables from .env file
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)


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
    
    # Gemini API configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-embedding-001")
    
    # Clustering configuration
    CLUSTERING_MIN_CLUSTER_SIZE = int(os.getenv("CLUSTERING_MIN_CLUSTER_SIZE", "3"))
    CLUSTERING_SIMILARITY_THRESHOLD = float(os.getenv("CLUSTERING_SIMILARITY_THRESHOLD", "0.90"))
    
    # Data directory
    DATA_DIR = os.getenv("DATA_DIR", "backend/data")

    @classmethod
    def validate_provider(cls) -> None:
        """Validate that the configured provider is supported and properly configured."""
        valid_providers = {provider.value for provider in EmbeddingProviderType}
        if cls.EMBEDDING_PROVIDER not in valid_providers:
            raise ValueError(
                f"Invalid EMBEDDING_PROVIDER: {cls.EMBEDDING_PROVIDER}. "
                f"Must be one of: {', '.join(valid_providers)}"
            )
        
        # Validate provider-specific configuration
        if cls.EMBEDDING_PROVIDER == EmbeddingProviderType.GEMINI.value:
            if not cls.GEMINI_API_KEY:
                raise ValueError(
                    "GEMINI_API_KEY environment variable is required when "
                    "EMBEDDING_PROVIDER=gemini. Set it in .env file or as environment variable."
                )
