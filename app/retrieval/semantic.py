import functools
from typing import List
from app.db.vectors import get_qdrant_client
from app.retrieval.embedder import get_embedder
from app.config import settings
import logging

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1024)
def _get_cached_embedding(text: str) -> List[float]:
    embedder = get_embedder()
    return embedder.encode([text], normalize_embeddings=True)[0].tolist()


def search_vector(query_text: str, top_k: int = 20) -> List[str]:
    if not query_text.strip():
        return []

    try:
        query_vector = _get_cached_embedding(query_text)
        client = get_qdrant_client()
        results = client.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=query_vector,
            limit=top_k
        )
        return [hit.payload.get("product_id") for hit in results if hit.payload and "product_id" in hit.payload]
    except Exception as e:
        logger.warning(f"Vector search failed: {e}")
        return []
