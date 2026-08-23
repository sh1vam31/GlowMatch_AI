from sentence_transformers import SentenceTransformer
from app.config import settings

_embedder_instance = None


def get_embedder() -> SentenceTransformer:
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedder_instance
