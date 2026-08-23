import re
from typing import Optional, List, Tuple
from app.models.query_context import QueryContext

CATEGORY_SYNONYMS = {
    "cleanser": ["cleanser", "cleansers", "face wash", "facewash", "cleansing gel", "cleansing foam", "wash"],
    "moisturizer": ["moisturizer", "moisturisers", "moisturizing", "cream", "lotion", "gel cream", "hydrator"],
    "serum": ["serum", "serums", "essence", "ampoule", "drops"],
    "sunscreen": ["sunscreen", "sunscreens", "sunblock", "spf", "sun lotion", "sun cream"],
    "treatment": ["treatment", "treatments", "peel", "retinoid", "acid"],
    "mask": ["mask", "masks", "sheet mask", "clay mask"],
    "eye": ["eye cream", "eye gel", "eye serum", "eye treatment"],
    "toner": ["toner", "toners", "astringent"],
    "foundation": ["foundation", "skin tint", "bb cream", "cc cream", "concealer"]
}

SKIN_TYPE_SYNONYMS = ["oily", "dry", "combination", "normal", "sensitive"]
CONCERN_SYNONYMS = ["acne", "aging", "dryness", "dullness", "redness", "pigmentation", "pores", "texture", "pimples", "breakouts"]


def parse_query_text(text: str) -> Tuple[Optional[str], Optional[int], List[str], List[str]]:
    """Extracts category, price_ceiling_inr, skin_types, and concerns from free text."""
    if not text:
        return None, None, [], []

    lower_text = text.lower()

    # 1. Category extraction
    detected_category = None
    for cat, synonyms in CATEGORY_SYNONYMS.items():
        for syn in synonyms:
            if re.search(r'\b' + re.escape(syn) + r'\b', lower_text):
                detected_category = cat
                break
        if detected_category:
            break

    # 2. Price ceiling extraction (e.g., "under 800", "below 500", "< 1000", "under r.s 800", "under rs 800", "under ₹800")
    price_ceiling = None
    price_match = re.search(r'(?:under|below|less than|<|within|rs\.?|₹|\b)\s*(\d{3,5})\b', lower_text)
    if price_match:
        try:
            val = int(price_match.group(1))
            if 100 <= val <= 20000:
                price_ceiling = val
        except ValueError:
            pass

    # 3. Skin type extraction
    detected_skin_types = []
    for st in SKIN_TYPE_SYNONYMS:
        if re.search(r'\b' + re.escape(st) + r'\b', lower_text):
            detected_skin_types.append(st)

    # 4. Concern extraction
    detected_concerns = []
    for c in CONCERN_SYNONYMS:
        if re.search(r'\b' + re.escape(c) + r'\b', lower_text):
            canonical_concern = "acne" if c in ["pimples", "breakouts"] else c
            if canonical_concern not in detected_concerns:
                detected_concerns.append(canonical_concern)

    return detected_category, price_ceiling, detected_skin_types, detected_concerns


def enrich_query_context(ctx: QueryContext) -> QueryContext:
    """Enriches QueryContext with parsed entities from free_text if not explicitly set."""
    if not ctx.free_text:
        return ctx

    cat, price, skin_types, concerns = parse_query_text(ctx.free_text)

    if not ctx.category and cat:
        ctx.category = cat
    if ctx.price_ceiling_inr is None and price:
        ctx.price_ceiling_inr = price

    # Only enrich skin_types and concerns if not explicitly specified by user
    if not ctx.skin_types and skin_types:
        ctx.skin_types = skin_types

    if not ctx.concerns and concerns:
        ctx.concerns = concerns

    return ctx
