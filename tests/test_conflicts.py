import pytest
from app.models.product import Product
from app.models.query_context import QueryContext
from app.reco.conflicts import validate_routine


def make_product(product_id: str, name: str, category: str, ingredients_parsed: list[str], raw: str = "") -> Product:
    return Product(
        product_id=product_id,
        name=name,
        brand="Test Brand",
        category=category,
        price_usd=10.0,
        price_inr=830,
        description="Test product description",
        ingredients_raw=raw or ", ".join(ingredients_parsed),
        ingredients_parsed=ingredients_parsed
    )


def test_rule_retinoid_x_aha_bha():
    p1 = make_product("p1", "Retinol Serum", "serum", ["retinol"])
    p2 = make_product("p2", "Glycolic Toner", "toner", ["glycolic acid"])
    ctx = QueryContext()
    res = validate_routine([p1, p2], ctx)
    rule_ids = [h.rule_id for h in res.hits]
    assert "retinoid_x_aha_bha" in rule_ids
    assert res.is_valid is True  # SEPARATE is not BLOCK


def test_rule_retinoid_x_benzoyl_peroxide():
    p1 = make_product("p1", "Retinol Cream", "treatment", ["retinol"])
    p2 = make_product("p2", "BP Wash", "cleanser", ["benzoyl peroxide"])
    ctx = QueryContext()
    res = validate_routine([p1, p2], ctx)
    rule_ids = [h.rule_id for h in res.hits]
    assert "retinoid_x_benzoyl_peroxide" in rule_ids


def test_rule_aha_x_bha_stacking():
    p1 = make_product("p1", "AHA Serum", "serum", ["lactic acid"])
    p2 = make_product("p2", "BHA Liquid", "toner", ["salicylic acid"])
    ctx = QueryContext()
    res = validate_routine([p1, p2], ctx)
    rule_ids = [h.rule_id for h in res.hits]
    assert "aha_x_bha_stacking" in rule_ids


def test_rule_vitamin_c_x_aha_bha():
    p1 = make_product("p1", "Vit C Serum", "serum", ["ascorbic acid"])
    p2 = make_product("p2", "AHA Lotion", "moisturizer", ["glycolic acid"])
    ctx = QueryContext()
    res = validate_routine([p1, p2], ctx)
    rule_ids = [h.rule_id for h in res.hits]
    assert "vitamin_c_x_aha_bha" in rule_ids


def test_rule_vitamin_c_x_niacinamide():
    p1 = make_product("p1", "Vit C Drops", "serum", ["ascorbic acid"])
    p2 = make_product("p2", "Niacinamide Serum", "serum", ["niacinamide"])
    ctx = QueryContext()
    res = validate_routine([p1, p2], ctx)
    hit = next((h for h in res.hits if h.rule_id == "vitamin_c_x_niacinamide"), None)
    assert hit is not None
    assert hit.severity == "INFO"


def test_rule_multi_exfoliant():
    p1 = make_product("p1", "AHA Gel", "treatment", ["glycolic acid"])
    p2 = make_product("p2", "BHA Lotion", "treatment", ["salicylic acid"])
    ctx = QueryContext()
    res = validate_routine([p1, p2], ctx)
    rule_ids = [h.rule_id for h in res.hits]
    assert "multi_exfoliant" in rule_ids


def test_rule_pregnancy_retinoid():
    p1 = make_product("p1", "Retinol Night Oil", "treatment", ["retinol"])
    ctx = QueryContext(pregnancy_safe=True)
    res = validate_routine([p1], ctx)
    assert res.is_valid is False
    assert "p1" in res.blocked_product_ids
    rule_ids = [h.rule_id for h in res.hits]
    assert "pregnancy_retinoid" in rule_ids


def test_rule_pregnancy_hydroquinone():
    p1 = make_product("p1", "Spot Fader", "treatment", ["hydroquinone"])
    ctx = QueryContext(pregnancy_safe=True)
    res = validate_routine([p1], ctx)
    assert res.is_valid is False
    assert "p1" in res.blocked_product_ids
    rule_ids = [h.rule_id for h in res.hits]
    assert "pregnancy_hydroquinone" in rule_ids


def test_rule_sensitive_fragrance():
    p1 = make_product("p1", "Scented Cream", "moisturizer", ["parfum"])
    ctx = QueryContext(skin_types=["sensitive"])
    res = validate_routine([p1], ctx)
    rule_ids = [h.rule_id for h in res.hits]
    assert "sensitive_fragrance" in rule_ids


def test_rule_sensitive_alcohol():
    p1 = make_product("p1", "Matte Toner", "toner", ["alcohol denat"])
    ctx = QueryContext(skin_types=["sensitive"])
    res = validate_routine([p1], ctx)
    rule_ids = [h.rule_id for h in res.hits]
    assert "sensitive_alcohol" in rule_ids


def test_rule_acne_comedogenic():
    p1 = make_product("p1", "Rich Balm", "moisturizer", ["coconut oil"])
    ctx = QueryContext(concerns=["acne"])
    res = validate_routine([p1], ctx)
    rule_ids = [h.rule_id for h in res.hits]
    assert "acne_comedogenic" in rule_ids


def test_rule_duplicate_category():
    p1 = make_product("p1", "Cleanser A", "cleanser", ["water"])
    p2 = make_product("p2", "Cleanser B", "cleanser", ["water"])
    ctx = QueryContext()
    res = validate_routine([p1, p2], ctx)
    rule_ids = [h.rule_id for h in res.hits]
    assert "duplicate_category" in rule_ids
