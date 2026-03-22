"""Gemini LLM provider for Google's generative AI."""

import logging

from google import genai

from backend.core.llm_protocol import LLM


logger = logging.getLogger(__name__)


class GeminiLLM(LLM):
    """
    LLM provider using Google's Gemini API.
    
    Requires GEMINI_API_KEY environment variable to be set.
    Uses generative model for label generation and content creation.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
    ):
        """
        Initialize the Gemini LLM provider.

        Args:
            api_key: Google Gemini API key
            model: Model name (default: gemini-2.0-flash)

        Raises:
            ValueError: If api_key is empty or None
        """
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiLLM")

        self.model = model
        self.client = genai.Client(api_key=api_key)
        logger.info(f"Initialized GeminiLLM with model={model}")

    def generate(self, prompt: str) -> str:
        """
        Generate text using Gemini API.

        Args:
            prompt: Prompt text to send to the model

        Returns:
            Generated text response from the model

        Raises:
            ValueError: If prompt is empty
            Exception: If API call fails
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {e}")
            raise
