from typing import List, Tuple
from collections import defaultdict


def rrf_fuse(rankings: List[List[str]], k: int = 60) -> List[Tuple[str, float]]:
    """rankings: ranked product_id lists from each retriever.
    score(d) = Σ 1 / (k + rank(d)), rank is 1-indexed.
    Returns ids sorted by descending score."""
    scores = defaultdict(float)

    for rank_list in rankings:
        for idx, doc_id in enumerate(rank_list):
            rank = idx + 1  # 1-indexed
            scores[doc_id] += 1.0 / (k + rank)

    sorted_results = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_results
