import time
import asyncio
import hashlib
import json
from fastapi import APIRouter
from app.models.requests import RecommendRequest
from app.models.responses import RecommendResponse, RecommendationItem
from app.models.query_context import QueryContext
from app.retrieval import pipeline
from app.observability.cost import DISCLAIMER_STRING
from app.llm.explain import generate_explanation
from app.db.cache import get_cache
from app.config import settings

router = APIRouter()


@router.post("/recommend", response_model=RecommendResponse)
async def recommend_products(req: RecommendRequest):
    start_time = time.time()
    cache = get_cache()

    raw_key = f"rec:{req.query}:{req.skin_types}:{req.concerns}:{req.price_ceiling_inr}:{req.pregnancy_safe}:{req.fragrance_free}:{req.top_k}"
    cache_key = "qrec:" + hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    cached_res = cache.get(cache_key)
    if cached_res:
        try:
            cached_data = json.loads(cached_res)
            cached_data["latency_ms"] = round((time.time() - start_time) * 1000, 2)
            cached_data["cached"] = True
            return RecommendResponse(**cached_data)
        except Exception:
            pass

    ctx = QueryContext(
        free_text=req.query,
        skin_types=req.skin_types,
        concerns=req.concerns,
        price_ceiling_inr=req.price_ceiling_inr,
        category=req.category,
        pregnancy_safe=req.pregnancy_safe,
        fragrance_free=req.fragrance_free,
        top_k=req.top_k
    )

    scored_products = await pipeline.run(ctx)

    explanation_tasks = [generate_explanation(prod, ctx) for prod, score in scored_products]
    explanations = await asyncio.gather(*explanation_tasks)

    recs = []
    for (prod, score), (reason, grounded) in zip(scored_products, explanations):
        recs.append(RecommendationItem(
            product_id=prod.product_id,
            name=prod.name,
            brand=prod.brand,
            price_inr=prod.price_inr,
            score=round(score, 4),
            reason=reason,
            grounded=grounded,
            safety_notes=prod.safety_flags
        ))

    latency_ms = round((time.time() - start_time) * 1000, 2)
    response_obj = RecommendResponse(
        input_type="text",
        query_context=ctx,
        recommendations=recs,
        latency_ms=latency_ms,
        disclaimer=DISCLAIMER_STRING
    )

    cache.set(cache_key, response_obj.model_dump_json(), ttl=settings.CACHE_TTL_QUERY)
    return response_obj
