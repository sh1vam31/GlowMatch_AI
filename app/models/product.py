from pydantic import BaseModel
from typing import Optional, List


class Product(BaseModel):
    product_id: str
    name: str
    brand: str
    category: str  # cleanser|moisturizer|serum|sunscreen|treatment|mask|eye|toner|foundation|other
    price_usd: float
    price_inr: int  # price_usd * USD_TO_INR, rounded
    description: str
    ingredients_raw: Optional[str] = None
    ingredients_parsed: List[str] = []  # normalized INCI tokens, lowercased
    skin_types: List[str] = []  # oily|dry|combination|normal|sensitive
    concerns: List[str] = []  # acne|aging|dryness|dullness|redness|pigmentation|pores|texture
    rating: Optional[float] = None
    review_count: int = 0
    is_fragrance_free: bool = False
    safety_flags: List[str] = []  # e.g. pregnancy_avoid
    text_for_embedding: str = ""
