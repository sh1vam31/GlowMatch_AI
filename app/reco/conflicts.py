from typing import List
from app.models.product import Product
from app.models.query_context import QueryContext
from app.models.routine import RoutineValidation, RuleHit, Severity
from app.reco.ingredient_kb import get_conflicts, product_has_group


def validate_routine(products: List[Product], ctx: QueryContext) -> RoutineValidation:
    """Returns every triggered rule with severity, products involved, and
    suggested remediation. Pure function — no LLM, no I/O, no network.
    Fully unit-testable with hand-built Product fixtures."""
    
    hits: List[RuleHit] = []
    blocked_product_ids: List[str] = []

    # Rule 1: Retinoid x AHA/BHA
    retinoid_prods = [p for p in products if product_has_group(p, "retinoid")]
    aha_bha_prods = [p for p in products if product_has_group(p, "aha") or product_has_group(p, "bha")]
    if retinoid_prods and aha_bha_prods:
        p_ids = list(set([p.product_id for p in retinoid_prods + aha_bha_prods]))
        hits.append(RuleHit(
            rule_id="retinoid_x_aha_bha",
            severity="SEPARATE",
            product_ids=p_ids,
            message="Commonly recommended to use on alternate nights or in separate AM/PM routines to reduce irritation.",
            remediation="Use retinoid in PM and AHA/BHA in AM or alternate nights."
        ))

    # Rule 2: Retinoid x Benzoyl Peroxide
    bp_prods = [p for p in products if product_has_group(p, "benzoyl_peroxide")]
    if retinoid_prods and bp_prods:
        p_ids = list(set([p.product_id for p in retinoid_prods + bp_prods]))
        hits.append(RuleHit(
            rule_id="retinoid_x_benzoyl_peroxide",
            severity="SEPARATE",
            product_ids=p_ids,
            message="Benzoyl peroxide can degrade certain retinoids when applied together; use at separate times.",
            remediation="Apply Benzoyl Peroxide in AM and Retinoid in PM."
        ))

    # Rule 3: AHA x BHA Stacking
    aha_prods = [p for p in products if product_has_group(p, "aha")]
    bha_prods = [p for p in products if product_has_group(p, "bha")]
    if aha_prods and bha_prods:
        p_ids = list(set([p.product_id for p in aha_prods + bha_prods]))
        hits.append(RuleHit(
            rule_id="aha_x_bha_stacking",
            severity="CAUTION",
            product_ids=p_ids,
            message="Combining multiple direct hydroxy acids in the same routine increases risk of over-exfoliation.",
            remediation="Limit direct acids to one product per application."
        ))

    # Rule 4: Vitamin C x AHA/BHA
    vit_c_prods = [p for p in products if product_has_group(p, "vitamin_c_acidic")]
    if vit_c_prods and aha_bha_prods:
        p_ids = list(set([p.product_id for p in vit_c_prods + aha_bha_prods]))
        hits.append(RuleHit(
            rule_id="vitamin_c_x_aha_bha",
            severity="CAUTION",
            product_ids=p_ids,
            message="Stacking low-pH L-ascorbic acid with direct AHAs/BHAs may cause barrier irritation.",
            remediation="Use Vitamin C in AM and AHAs/BHAs in PM."
        ))

    # Rule 5: Vitamin C x Niacinamide (INFO)
    niacinamide_prods = [p for p in products if product_has_group(p, "niacinamide")]
    if vit_c_prods and niacinamide_prods:
        p_ids = list(set([p.product_id for p in vit_c_prods + niacinamide_prods]))
        hits.append(RuleHit(
            rule_id="vitamin_c_x_niacinamide",
            severity="INFO",
            product_ids=p_ids,
            message="Vitamin C with niacinamide is often flagged as a conflict; current formulation consensus is that it's generally fine.",
            remediation=None
        ))

    # Rule 6: Multi-exfoliant (>=2 exfoliating products)
    exfoliating_dict = {p.product_id: p for p in (aha_prods + bha_prods)}
    exfoliating_prods = list(exfoliating_dict.values())
    if len(exfoliating_prods) >= 2:
        p_ids = list(exfoliating_dict.keys())
        hits.append(RuleHit(
            rule_id="multi_exfoliant",
            severity="CAUTION",
            product_ids=p_ids,
            message="Multiple exfoliating products detected in routine; monitor for cumulative dryness or skin barrier strain.",
            remediation="Stagger use across different days."
        ))

    # Rule 7: Pregnancy Retinoid (BLOCK)
    if ctx.pregnancy_safe:
        for p in products:
            if product_has_group(p, "retinoid"):
                blocked_product_ids.append(p.product_id)
                hits.append(RuleHit(
                    rule_id="pregnancy_retinoid",
                    severity="BLOCK",
                    product_ids=[p.product_id],
                    message=f"Product '{p.name}' contains retinoids which are contra-indicated during pregnancy.",
                    remediation="Remove product from pregnancy-safe routine."
                ))

    # Rule 8: Pregnancy Hydroquinone (BLOCK)
    if ctx.pregnancy_safe:
        for p in products:
            if product_has_group(p, "hydroquinone") or "hydroquinone" in (p.ingredients_raw or "").lower():
                blocked_product_ids.append(p.product_id)
                hits.append(RuleHit(
                    rule_id="pregnancy_hydroquinone",
                    severity="BLOCK",
                    product_ids=[p.product_id],
                    message=f"Product '{p.name}' contains hydroquinone which is not recommended during pregnancy.",
                    remediation="Remove product from pregnancy-safe routine."
                ))

    # Rule 9: Sensitive Fragrance
    if "sensitive" in ctx.skin_types:
        fragrance_prods = [p for p in products if product_has_group(p, "fragrance")]
        if fragrance_prods:
            hits.append(RuleHit(
                rule_id="sensitive_fragrance",
                severity="CAUTION",
                product_ids=[p.product_id for p in fragrance_prods],
                message="Added fragrance / parfum detected for sensitive skin profile.",
                remediation="Consider fragrance-free alternative."
            ))

    # Rule 10: Sensitive Alcohol
    if "sensitive" in ctx.skin_types:
        alcohol_prods = [p for p in products if product_has_group(p, "drying_alcohol")]
        if alcohol_prods:
            hits.append(RuleHit(
                rule_id="sensitive_alcohol",
                severity="CAUTION",
                product_ids=[p.product_id for p in alcohol_prods],
                message="Drying alcohol detected for sensitive skin profile.",
                remediation="Consider alcohol-free formulation."
            ))

    # Rule 11: Acne Comedogenic
    if "acne" in ctx.concerns or "acne" in ctx.skin_types:
        comedogenic_prods = [p for p in products if product_has_group(p, "comedogenic")]
        if comedogenic_prods:
            hits.append(RuleHit(
                rule_id="acne_comedogenic",
                severity="CAUTION",
                product_ids=[p.product_id for p in comedogenic_prods],
                message="Potentially comedogenic ingredient detected for acne-prone skin profile.",
                remediation="Select non-comedogenic product."
            ))

    # Rule 12: Duplicate Category
    categories = [p.category for p in products if p.category]
    category_counts = {}
    for cat in categories:
        category_counts[cat] = category_counts.get(cat, 0) + 1
    for cat, count in category_counts.items():
        if count > 1:
            dup_prods = [p.product_id for p in products if p.category == cat]
            hits.append(RuleHit(
                rule_id="duplicate_category",
                severity="INFO",
                product_ids=dup_prods,
                message=f"Multiple products in '{cat}' category detected in the same routine slot.",
                remediation="Consider streamlining redundant products."
            ))

    is_valid = len(blocked_product_ids) == 0
    return RoutineValidation(
        is_valid=is_valid,
        hits=hits,
        blocked_product_ids=list(set(blocked_product_ids))
    )
