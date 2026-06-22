"""Smoke test for the Google Gemini embeddings integration."""
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def test_embed():
    """Embed a simple query and print the embedding dimension."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No GEMINI_API_KEY")
        return

    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=api_key
        )
        res = embeddings.embed_query("Hello world")
        print(f"Success! Dimension: {len(res)}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_embed()
