from app.config import settings

_embedder_instance = None


def get_embedder():
    global _embedder_instance
    if _embedder_instance is None:
        from sentence_transformers import SentenceTransformer
        _embedder_instance = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedder_instance
