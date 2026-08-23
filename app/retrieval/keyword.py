from rank_bm25 import BM25Okapi
from typing import List, Dict, Any
from app.models.product import Product

_bm25_index = None
_bm25_products: List[Product] = []


def initialize_bm25(products: List[Product]):
    global _bm25_index, _bm25_products
    _bm25_products = products
    corpus = [p.text_for_embedding.lower().split() for p in products]
    if corpus:
        _bm25_index = BM25Okapi(corpus)


def search_bm25(query: str, top_k: int = 50, candidate_products: List[Product] = None) -> List[str]:
    target_prods = candidate_products if candidate_products is not None else _bm25_products
    if not target_prods:
        return []

    corpus = [p.text_for_embedding.lower().split() for p in target_prods]
    if not corpus:
        return []

    bm25 = BM25Okapi(corpus)
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    
    indexed_scores = [(idx, score) for idx, score in enumerate(scores)]
    indexed_scores.sort(key=lambda x: x[1], reverse=True)
    
    top_indices = indexed_scores[:top_k]
    return [target_prods[idx].product_id for idx, score in top_indices if score > 0]
