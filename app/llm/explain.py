import logging
from app.models.product import Product
from app.models.query_context import QueryContext
from app.llm.provider import get_llm_provider
from app.llm.grounding import validate_grounding

logger = logging.getLogger(__name__)


def generate_template_reason(product: Product, ctx: QueryContext) -> str:
    """Generates an accurate, product-specific grounded reason based on actual product fields."""
    parts = []
    
    cat_display = product.category if product.category != "other" else "skincare formulation"
    parts.append(f"Formulated as a {cat_display} priced at ₹{product.price_inr}.")

    if product.skin_types:
        parts.append(f"Suitable for {', '.join(product.skin_types[:2])} skin.")

    if product.concerns:
        parts.append(f"Addresses {', '.join(product.concerns[:2])}.")

    if product.is_fragrance_free:
        parts.append("Fragrance-free formulation.")

    if product.ingredients_parsed:
        top_ings = [ing.title() for ing in product.ingredients_parsed[:2]]
        parts.append(f"Key ingredients include {', '.join(top_ings)}.")

    return " ".join(parts)


async def generate_explanation(product: Product, ctx: QueryContext) -> tuple[str, bool]:
    """Generates product explanation. Returns (reason_string, is_grounded_bool)."""
    provider = get_llm_provider()
    
    if getattr(provider, "api_key", None):
        prompt = (
            f"Write a 1-2 sentence grounded, non-medical recommendation reason for the following beauty product:\n"
            f"Name: {product.name}\nBrand: {product.brand}\nCategory: {product.category}\nPrice: ₹{product.price_inr}\n"
            f"Ingredients: {', '.join(product.ingredients_parsed[:5])}\n"
            f"User Query: {ctx.free_text or 'recommendation'}\n"
            f"Rules: Do NOT make medical claims. Reference price ₹{product.price_inr} or key ingredients accurately."
        )
        res = await provider.complete_json(prompt)
        reason = res.get("explanation", res.get("reason", ""))
        if reason:
            g_res = validate_grounding(reason, product, ctx.detected)
            if g_res.is_grounded:
                return reason, True

    # Fallback to template-based deterministic grounded reason
    fallback_reason = generate_template_reason(product, ctx)
    return fallback_reason, True
