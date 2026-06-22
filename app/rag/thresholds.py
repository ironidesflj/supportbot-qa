"""Default similarity thresholds per embedding model.

Different Gemini/OpenAI embedding models produce cosine similarity
scores with different distributions. Using a single hardcoded threshold
leads to either too many false positives (irrelevant context returned)
or too many false negatives (valid context discarded).

This module provides sane defaults per model, while still allowing
override via the SIMILARITY_THRESHOLD env var.
"""
from app.core.config import settings


# Empirically tuned defaults per model (cosine similarity).
# These can be overridden by the SIMILARITY_THRESHOLD env var.
DEFAULT_THRESHOLDS = {
    # Gemini family — tends to spread scores lower (0.4-0.7 for good matches)
    "models/gemini-embedding-001": 0.40,
    "models/gemini-embedding-002": 0.40,
    "models/gemini-embedding-exp-03-07": 0.40,
    "models/text-embedding-004": 0.75,  # legacy, higher scores
    # OpenAI family — tends to compress scores higher (0.7-0.9 for good matches)
    "text-embedding-3-small": 0.70,
    "text-embedding-3-large": 0.70,
    "text-embedding-ada-002": 0.75,
}

DEFAULT_FALLBACK_THRESHOLD = 0.30


def get_effective_threshold() -> float:
    """Return the similarity threshold to use.

    Priority:
    1. SIMILARITY_THRESHOLD env var if explicitly set (non-default)
    2. Per-model default from DEFAULT_THRESHOLDS
    3. DEFAULT_FALLBACK_THRESHOLD

    The check for env var override is done by comparing against the
    Settings default; if the user set a value different from the default,
    we honor it.
    """
    # If the user overrode SIMILARITY_THRESHOLD in env, honor it.
    # Settings default is 0.40 (set in P2.2). If the loaded value differs,
    # it means the user set it explicitly.
    if settings.SIMILARITY_THRESHOLD != 0.40:
        return settings.SIMILARITY_THRESHOLD
    # Otherwise, use per-model default if available.
    return DEFAULT_THRESHOLDS.get(
        settings.EMBEDDING_MODEL, DEFAULT_FALLBACK_THRESHOLD
    )
