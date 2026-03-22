"""Mock LLM implementation using keyword extraction."""

import logging
import re
from collections import Counter
from typing import Optional


logger = logging.getLogger(__name__)


class MockLLM:
    """
    Mock LLM that generates labels by extracting keywords from prompt text.

    No external API calls—fully deterministic keyword analysis.
    Useful for development, testing, and demonstrating label structure.
    """

    # Common English stopwords to exclude from keyword extraction
    STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "have", "has", "do", "does", "did", "will", "would", "could", "should",
        "may", "might", "must", "can", "this", "that", "these", "those",
        "i", "you", "he", "she", "it", "we", "they", "what", "which", "who",
        "when", "where", "why", "how", "all", "each", "every", "both", "few",
        "more", "most", "some", "any", "no", "not", "only", "own", "same", "as",
        "if", "because", "as", "while", "although", "after", "before", "during",
        "about", "above", "below", "through", "between", "into", "out", "off",
        "customer", "case", "issue", "problem", "support", "cases", "issues",
        "solved", "resolved", "solution", "answer", "received", "email",
        "confirmation", "receipt", "user", "account", "payment", "order"
    }

    def __init__(self):
        """Initialize mock LLM."""
        pass

    def generate(self, prompt: str) -> str:
        """
        Generate a label by extracting keywords from prompt text.

        Args:
            prompt: Full prompt including cluster summaries

        Returns:
            Synthetic 4-8 word label
        """
        try:
            # Extract numbered cluster summaries from prompt
            summaries = self._extract_summaries(prompt)

            if not summaries:
                logger.warning("No summaries found in prompt, returning generic label")
                return "Support Issues"

            # Extract keywords
            keywords = self._extract_keywords(summaries)

            if not keywords:
                logger.warning("No keywords extracted from summaries, returning generic label")
                return "Support Issues"

            # Generate label from keywords
            label = self._generate_label_from_keywords(keywords)
            return label

        except Exception as e:
            logger.error(f"Error in MockLLM.generate: {e}")
            return "Support Issues"

    def _extract_summaries(self, prompt: str) -> list[str]:
        """
        Extract numbered cluster summaries from prompt.

        Args:
            prompt: Full prompt text

        Returns:
            List of summary strings (e.g., ["Payment failed...", "Refund issue..."])
        """
        # Match numbered lines: "1. summary text", "2. summary text", etc.
        pattern = r"^\d+\.\s+(.+)$"
        summaries = []

        for line in prompt.split("\n"):
            match = re.match(pattern, line)
            if match:
                summary = match.group(1).strip()
                if summary:
                    summaries.append(summary)

        return summaries

    def _extract_keywords(self, summaries: list[str], top_n: int = 6) -> list[str]:
        """
        Extract top keywords from summaries (excluding stopwords).

        Args:
            summaries: List of cluster summary strings
            top_n: Number of top keywords to extract

        Returns:
            List of keywords, ordered by frequency
        """
        # Combine all summaries
        text = " ".join(summaries).lower()

        # Split into words, remove non-alphanumeric
        words = re.findall(r"\b[a-z]+\b", text)

        # Filter: must be 3+ chars and not a stopword
        filtered = [
            w for w in words
            if len(w) >= 3 and w not in self.STOPWORDS
        ]

        if not filtered:
            return []

        # Count frequency
        counter = Counter(filtered)

        # Return top N by frequency
        return [word for word, _ in counter.most_common(top_n)]

    def _generate_label_from_keywords(self, keywords: list[str]) -> str:
        """
        Generate a human-readable label from keywords.

        Args:
            keywords: List of keywords ordered by frequency

        Returns:
            4-8 word label
        """
        if not keywords:
            return "Support Issues"

        # Use top keywords to build label
        # Strategy: capitalize and join with " - " or " / "
        # Try to keep to 4-8 words

        # Sort by frequency (already done) and combine
        words = keywords[:4]  # Up to 4 top keywords

        # Capitalize each word
        words = [w.capitalize() for w in words]

        # Join with " - "
        label = " - ".join(words)

        # If too short, add more words (up to 8 total)
        if len(label.split()) < 4 and len(keywords) > 4:
            more_words = keywords[4:8]
            more_words = [w.capitalize() for w in more_words]
            label = label + " - " + " - ".join(more_words)

        # Ensure within 4-8 words
        word_count = len(label.split())
        if word_count > 8:
            # Truncate to 8 words
            label = " ".join(label.split()[:8])

        return label
