from sentence_transformers import SentenceTransformer

# Load model once at module level to avoid reloading
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str) -> list[float]:
    """Generate embedding vector for a text string."""
    return model.encode(text).tolist()


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embedding vectors for a list of texts."""
    return model.encode(texts).tolist()