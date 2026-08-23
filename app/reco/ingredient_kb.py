import os
import yaml
from typing import Dict, List, Any
from app.models.product import Product

_kb_cache = None


def load_ingredient_kb() -> Dict[str, Any]:
    global _kb_cache
    if _kb_cache is None:
        yaml_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "knowledge", "ingredient_rules.yaml")
        if not os.path.exists(yaml_path):
            yaml_path = os.path.abspath("data/knowledge/ingredient_rules.yaml")
        
        with open(yaml_path, "r", encoding="utf-8") as f:
            _kb_cache = yaml.safe_load(f)
    return _kb_cache


def get_ingredient_groups() -> Dict[str, List[str]]:
    kb = load_ingredient_kb()
    return kb.get("ingredient_groups", {})


def get_conflicts() -> List[Dict[str, Any]]:
    kb = load_ingredient_kb()
    return kb.get("conflicts", [])


def get_flags() -> Dict[str, List[str]]:
    kb = load_ingredient_kb()
    return kb.get("flags", {})


def product_has_group(product: Product, group_name: str) -> bool:
    groups = get_ingredient_groups()
    target_ingredients = groups.get(group_name, [])
    if not target_ingredients:
        return False
    
    parsed = [ing.lower().strip() for ing in product.ingredients_parsed]
    raw = (product.ingredients_raw or "").lower()

    for item in target_ingredients:
        item_lower = item.lower()
        if any(item_lower in ing for ing in parsed) or item_lower in raw:
            return True
    return False
