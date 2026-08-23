from pydantic import BaseModel
from typing import Optional, List, Literal
from app.models.product import Product

Severity = Literal["BLOCK", "SEPARATE", "CAUTION", "INFO"]


class RuleHit(BaseModel):
    rule_id: str
    severity: Severity
    product_ids: List[str]
    message: str
    remediation: Optional[str] = None


class RoutineValidation(BaseModel):
    is_valid: bool  # False only if any BLOCK fired
    hits: List[RuleHit] = []
    blocked_product_ids: List[str] = []


class RoutineSlot(BaseModel):
    slot: str  # cleanser|treatment|serum|moisturizer|sunscreen
    period: Literal["AM", "PM"]
    product: Optional[Product] = None
    reason: str = ""


class Routine(BaseModel):
    am: List[RoutineSlot] = []
    pm: List[RoutineSlot] = []
    total_price_inr: int = 0
    validation: RoutineValidation
    disclaimer: str = ""


class GroundingResult(BaseModel):
    is_grounded: bool
    violations: List[str] = []
    claim_count: int = 0
    verified_count: int = 0
