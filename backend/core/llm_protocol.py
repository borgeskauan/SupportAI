"""Protocol definition for pluggable LLM providers."""

from typing import Protocol


class LLM(Protocol):
    """
    Generic prompt-response interface for LLM integration.

    Implementations can range from simple mock extraction (keyword analysis)
    to full LLM API calls (Gemini, OpenAI). This protocol is reusable for
    any text generation task: label generation, FAQ drafting, summarization, etc.

    Example implementations:
    - MockLLM: Keyword extraction from prompt text (no API)
    - GeminiLLM: Send to Google Gemini API
    - OpenAILLM: Send to OpenAI API
    """

    def generate(self, prompt: str) -> str:
        """
        Generate a response from a prompt.

        Args:
            prompt: Input prompt with full context/instructions
                   Example: "You are generating a label...
                           Cluster summaries:
                           1. Payment failed...
                           2. Refund issue..."

        Returns:
            Response string generated from the prompt
            Example: "Payment Issues"

        Raises:
            ValueError: If response generation fails
        """
        ...
