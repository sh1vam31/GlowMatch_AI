from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.models.query_context import QueryContext, DetectedAttributes


class RecommendationItem(BaseModel):
    product_id: str
    name: str
    brand: str
    price_inr: int
    score: float
    reason: str
    grounded: bool
    safety_notes: List[str] = []


class RecommendResponse(BaseModel):
    input_type: str  # "text" or "image+text"
    query_context: QueryContext
    recommendations: List[RecommendationItem] = []
    warnings: List[str] = []
    disclaimer: str
    cached: bool = False
    degraded: bool = False
    latency_ms: float
    cost_inr: float = 0.0
    latency_breakdown_ms: Optional[Dict[str, float]] = None
