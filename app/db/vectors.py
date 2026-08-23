from qdrant_client import QdrantClient
from app.config import settings
import logging
import os

logger = logging.getLogger(__name__)

qdrant_client: QdrantClient = None


def get_qdrant_client() -> QdrantClient:
    global qdrant_client
    if qdrant_client is None:
        if settings.QDRANT_MODE == "cloud" and settings.QDRANT_URL:
            logger.info(f"Connecting to Qdrant Cloud at {settings.QDRANT_URL}")
            qdrant_client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY
            )
        else:
            logger.info(f"Initializing Qdrant embedded mode at path {settings.QDRANT_PATH}")
            os.makedirs(settings.QDRANT_PATH, exist_ok=True)
            qdrant_client = QdrantClient(path=settings.QDRANT_PATH)
    return qdrant_client


def check_qdrant_health() -> dict:
    try:
        client = get_qdrant_client()
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        return {
            "connected": True,
            "mode": settings.QDRANT_MODE,
            "collection": settings.QDRANT_COLLECTION,
            "collections_found": collection_names
        }
    except Exception as e:
        logger.warning(f"Qdrant check failed: {e}")
        return {"connected": False, "error": str(e)}
