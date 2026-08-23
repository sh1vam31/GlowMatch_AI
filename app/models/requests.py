from pydantic import BaseModel
from typing import Optional, List


class RecommendRequest(BaseModel):
    query: str
    top_k: int = 5
    pregnancy_safe: bool = False
    fragrance_free: bool = False
    skin_types: List[str] = []
    concerns: List[str] = []
    price_ceiling_inr: Optional[int] = None
    category: Optional[str] = None


class RoutineRequest(BaseModel):
    skin_types: List[str] = []
    concerns: List[str] = []
    total_budget_inr: Optional[int] = None
    pregnancy_safe: bool = False
    fragrance_free: bool = False


class RoutineValidateRequest(BaseModel):
    product_ids: List[str]
