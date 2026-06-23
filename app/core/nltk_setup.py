"""Auto-download NLTK resources required by unstructured.

The unstructured library (used by UnstructuredMarkdownLoader) depends
on NLTK resources for tokenization and tagging:
- punkt_tab: sentence tokenizer (newer format, required by recent nltk)
- averaged_perceptron_tagger_eng: POS tagger

These are NOT installed by pip install nltk — they must be downloaded
separately. This module ensures they're available on first import,
making the app work in any environment (local, CI, Render, Docker)
without manual setup steps.

The download is idempotent: nltk.download() skips if the resource is
already present, so importing this module multiple times is safe.
"""
import logging

import nltk

logger = logging.getLogger("supportbot.nltk_setup")

# Resources required by unstructured (and their newer format names).
REQUIRED_RESOURCES = [
    "punkt",
    "punkt_tab",
    "averaged_perceptron_tagger",
    "averaged_perceptron_tagger_eng",
]


def ensure_nltk_resources() -> None:
    """Download required NLTK resources if not already present.

    Safe to call multiple times — nltk.download() is idempotent.
    Uses quiet=True to avoid spamming stdout on every startup.
    """
    for resource in REQUIRED_RESOURCES:
        try:
            # Check if already downloaded to avoid network calls.
            try:
                nltk.data.find(f"tokenizers/{resource}")
                continue  # Already present.
            except LookupError:
                pass
            try:
                nltk.data.find(f"taggers/{resource}")
                continue  # Already present.
            except LookupError:
                pass

            # Not found — download it.
            logger.info("nltk_downloading", extra={"resource": resource})
            nltk.download(resource, quiet=True)
        except Exception as e:
            # Don't crash startup if NLTK download fails — log and continue.
            # The endpoint will fail with a clear error if the resource is
            # actually needed and still missing.
            logger.warning(
                "nltk_download_failed",
                extra={"resource": resource, "error": str(e)},
            )


# Run on import so any module importing from app.* gets NLTK ready.
ensure_nltk_resources()
