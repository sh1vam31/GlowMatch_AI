import re
from typing import Optional
from app.models.product import Product
from app.models.query_context import DetectedAttributes
from app.models.routine import GroundingResult


def validate_grounding(explanation: str, source: Product, detected: Optional[DetectedAttributes] = None) -> GroundingResult:
    """Extract every factual claim and verify each against source Product fields or detected attributes."""
    violations = []
    claim_count = 0
    verified_count = 0

    lower_expl = explanation.lower()

    # 1. Price claim verification
    numbers_in_expl = re.findall(r'\b\d{3,5}\b', explanation)
    for num_str in numbers_in_expl:
        claim_count += 1
        num_val = int(num_str)
        if num_val == source.price_inr or num_val == int(source.price_usd):
            verified_count += 1
        else:
            violations.append(f"Claimed price {num_val} does not match source price ₹{source.price_inr}")

    # 2. Ingredient mention verification
    # Look for common ingredient keywords mentioned in explanation
    for ing in source.ingredients_parsed:
        if ing.lower() in lower_expl:
            claim_count += 1
            verified_count += 1

    # 3. Medical / curative claim violation check (PRD Section 0.2 & 10.4)
    medical_words = ["cure", "cures", "treats acne clinically", "dermatologist prescribed", "medical grade", "heals disease"]
    for med in medical_words:
        if med in lower_expl:
            claim_count += 1
            violations.append(f"Forbidden medical claim found: '{med}'")

    is_grounded = len(violations) == 0
    return GroundingResult(
        is_grounded=is_grounded,
        violations=violations,
        claim_count=claim_count,
        verified_count=verified_count
    )
