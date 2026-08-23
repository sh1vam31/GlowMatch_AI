import asyncio
import logging
from typing import List, Tuple
from app.config import settings
from app.models.query_context import QueryContext
from app.models.product import Product
from app.db.mongo import get_db
from app.retrieval.keyword import search_bm25
from app.retrieval.semantic import search_vector
from app.retrieval.fusion import rrf_fuse
from app.retrieval.reranker import rerank_cross_encoder
from app.reco.ingredient_kb import product_has_group

logger = logging.getLogger(__name__)


from app.bridge.attribute_to_query import enrich_query_context

async def fetch_filtered_products(ctx: QueryContext) -> List[Product]:
    ctx = enrich_query_context(ctx)
    db = get_db()
    raw_products = []

    if db is not None:
        query = {}
        if ctx.category:
            query["category"] = ctx.category.lower()
        if ctx.price_ceiling_inr:
            query["price_inr"] = {"$lte": ctx.price_ceiling_inr}
        if ctx.fragrance_free:
            query["is_fragrance_free"] = True
        if ctx.skin_types:
            query["skin_types"] = {"$in": [s.lower() for s in ctx.skin_types]}
        if ctx.concerns:
            query["concerns"] = {"$in": [c.lower() for c in ctx.concerns]}

        cursor = db["products"].find(query).limit(100)
        docs = await cursor.to_list(length=100)
        for doc in docs:
            doc.pop("_id", None)
            raw_products.append(Product(**doc))

        # Fallback 1: if strict criteria returned 0, relax skin_types/concerns to ensure candidate pool
        if not raw_products and (ctx.skin_types or ctx.concerns):
            query_relaxed = {}
            if ctx.category:
                query_relaxed["category"] = ctx.category.lower()
            if ctx.price_ceiling_inr:
                query_relaxed["price_inr"] = {"$lte": ctx.price_ceiling_inr}
            cursor = db["products"].find(query_relaxed).limit(100)
            docs = await cursor.to_list(length=100)
            for doc in docs:
                doc.pop("_id", None)
                raw_products.append(Product(**doc))

        # Fallback 2: if category + price filtered down to 0, relax price ceiling
        if not raw_products and ctx.category:
            query_cat = {"category": ctx.category.lower()}
            cursor = db["products"].find(query_cat).limit(100)
            docs = await cursor.to_list(length=100)
            for doc in docs:
                doc.pop("_id", None)
                raw_products.append(Product(**doc))
    
    # Filter in Python memory for strict pregnancy safety & fragrance requirements
    filtered = []
    unsafe_ingredients = {"retinol", "retinoid", "tretinoin", "adapalene", "hydroquinone", "tazarotene"}
    
    for p in raw_products:
        if ctx.fragrance_free and not p.is_fragrance_free:
            continue

        if ctx.pregnancy_safe:
            p_ings = {ing.lower() for ing in p.ingredients_parsed}
            if p_ings.intersection(unsafe_ingredients):
                continue
            if product_has_group(p, "retinoid") or product_has_group(p, "hydroquinone"):
                continue
            if "pregnancy_avoid" in p.safety_flags:
                continue

        if ctx.exclude_ingredients:
            raw_ing = (p.ingredients_raw or "").lower()
            if any(ex.lower() in raw_ing for ex in ctx.exclude_ingredients):
                continue

        filtered.append(p)

    return filtered


async def run(ctx: QueryContext) -> List[Tuple[Product, float]]:
    query_text = ctx.to_retrieval_text()
    strategy = settings.RETRIEVAL_STRATEGY.lower()

    # Skip heavy model downloading and inference on Render Free tier to avoid gateway timeouts
    import os
    if os.getenv("RENDER"):
        strategy = "bm25"

    candidates = await fetch_filtered_products(ctx)

    if not candidates:
        return []

    prod_dict = {p.product_id: p for p in candidates}

    # Step 2: Strategy execution
    if strategy == "bm25":
        bm25_ids = search_bm25(query_text, top_k=settings.TOP_K_RETRIEVE, candidate_products=candidates)
        return [(prod_dict[pid], 1.0 / (idx + 1)) for idx, pid in enumerate(bm25_ids[:settings.TOP_K_RETURN]) if pid in prod_dict]

    elif strategy == "vector":
        vector_ids = search_vector(query_text, top_k=settings.TOP_K_RETRIEVE)
        valid_ids = [pid for pid in vector_ids if pid in prod_dict]
        return [(prod_dict[pid], 1.0 / (idx + 1)) for idx, pid in enumerate(valid_ids[:settings.TOP_K_RETURN])]

    elif strategy == "hybrid_rrf":
        bm25_ids = search_bm25(query_text, top_k=settings.TOP_K_RETRIEVE, candidate_products=candidates)
        vector_ids = search_vector(query_text, top_k=settings.TOP_K_RETRIEVE)
        valid_vector_ids = [pid for pid in vector_ids if pid in prod_dict]

        fused = rrf_fuse([bm25_ids, valid_vector_ids], k=settings.RRF_K)
        return [(prod_dict[pid], score) for pid, score in fused[:settings.TOP_K_RETURN] if pid in prod_dict]

    elif strategy in ["hybrid_rrf_ce", "hybrid_rrf_llm"]:
        bm25_ids = search_bm25(query_text, top_k=settings.TOP_K_RETRIEVE, candidate_products=candidates)
        vector_ids = search_vector(query_text, top_k=settings.TOP_K_RETRIEVE)
        valid_vector_ids = [pid for pid in vector_ids if pid in prod_dict]

        fused = rrf_fuse([bm25_ids, valid_vector_ids], k=settings.RRF_K)
        fused_candidates = [prod_dict[pid] for pid, _ in fused[:20] if pid in prod_dict]

        if not fused_candidates:
            fused_candidates = candidates[:20]

        reranked = rerank_cross_encoder(query_text, fused_candidates, top_k=20)

        # Apply attribute boost to prioritize products matching requested skin_types or concerns
        boosted = []
        for p, score in reranked:
            b = 0.0
            if ctx.skin_types:
                p_st = [st.lower() for st in p.skin_types]
                if any(st.lower() in p_st for st in ctx.skin_types):
                    b += 1.5
            if ctx.concerns:
                p_c = [c.lower() for c in p.concerns]
                if any(c.lower() in p_c for c in ctx.concerns):
                    b += 1.5
            boosted.append((p, score + b))

        boosted.sort(key=lambda x: x[1], reverse=True)
        return boosted[:settings.TOP_K_RETURN]

    else:
        # Fallback
        return [(p, 1.0) for p in candidates[:settings.TOP_K_RETURN]]
