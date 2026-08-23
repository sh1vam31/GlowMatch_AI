from typing import List, Tuple

from app.config import settings
from app.models.product import Product
import logging

logger = logging.getLogger(__name__)

_reranker_model = None


def get_reranker():
    global _reranker_model
    if _reranker_model is None:
        from sentence_transformers import CrossEncoder
        logger.info(f"Loading CrossEncoder model '{settings.RERANKER_MODEL}'...")
        _reranker_model = CrossEncoder(settings.RERANKER_MODEL)
    return _reranker_model


def rerank_cross_encoder(query: str, products: List[Product], top_k: int = 10) -> List[Tuple[Product, float]]:
    if not products or not query.strip():
        return [(p, 0.0) for p in products[:top_k]]

    try:
        model = get_reranker()
        pairs = [(query, p.text_for_embedding or p.name) for p in products]
        scores = model.predict(pairs, batch_size=16)
        scored_products = list(zip(products, [float(s) for s in scores]))
        scored_products.sort(key=lambda x: x[1], reverse=True)
        return scored_products[:top_k]
    except Exception as e:
        logger.warning(f"CrossEncoder reranking skipped due to memory constraint: {e}")
        return [(p, 1.0 - (i * 0.05)) for i, p in enumerate(products[:top_k])]
