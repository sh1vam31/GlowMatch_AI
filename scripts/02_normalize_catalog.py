import os
import json
import pandas as pd
import asyncio
import logging
from app.config import settings
from app.db.mongo import get_db
from app.reco.ingredient_kb import load_ingredient_kb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("normalize_catalog")

CATEGORY_MAPPING = {
    "cleanser": "cleanser",
    "cleansers": "cleanser",
    "face wash": "cleanser",
    "moisturizer": "moisturizer",
    "moisturizers": "moisturizer",
    "cream": "moisturizer",
    "lotion": "moisturizer",
    "serum": "serum",
    "serums": "serum",
    "essence": "serum",
    "treatment": "treatment",
    "treatments": "treatment",
    "sunscreen": "sunscreen",
    "sunscreens": "sunscreen",
    "spf": "sunscreen",
    "mask": "mask",
    "masks": "mask",
    "eye": "eye",
    "eye cream": "eye",
    "toner": "toner",
    "toners": "toner",
    "foundation": "foundation",
    "foundations": "foundation"
}


def infer_category(primary_cat: str, secondary_cat: str, product_name: str) -> str:
    combined = f"{primary_cat} {secondary_cat} {product_name}".lower()
    for key, mapped in CATEGORY_MAPPING.items():
        if key in combined:
            return mapped
    return "other"


def parse_ingredients(raw_ingredients: str) -> list[str]:
    if not raw_ingredients or pd.isna(raw_ingredients):
        return []
    # Split by comma or semicolon
    tokens = [t.strip().lower() for t in raw_ingredients.replace(";", ",").split(",")]
    # Clean empty or extremely long noise strings
    cleaned = [t for t in tokens if t and len(t) < 80]
    return cleaned


def infer_skin_types(row: pd.Series) -> list[str]:
    types = []
    text = f"{row.get('highlights', '')} {row.get('description', '')}".lower()
    for st in ["oily", "dry", "combination", "normal", "sensitive"]:
        if st in text or row.get(st) == 1 or row.get(st) is True:
            types.append(st)
    if not types:
        types = ["normal", "combination"]
    return types


def infer_concerns(row: pd.Series) -> list[str]:
    concerns = []
    text = f"{row.get('highlights', '')} {row.get('description', '')} {row.get('product_name', '')}".lower()
    for c in ["acne", "aging", "dryness", "dullness", "redness", "pigmentation", "pores", "texture"]:
        if c in text:
            concerns.append(c)
    return concerns


def extract_safety_flags(parsed_ingredients: list[str], raw_text: str) -> list[str]:
    kb = load_ingredient_kb()
    flags_config = kb.get("flags", {})
    groups_config = kb.get("ingredient_groups", {})
    triggered_flags = set()

    for flag_name, group_list in flags_config.items():
        for group in group_list:
            target_ings = groups_config.get(group, [group])
            for target in target_ings:
                target_lower = target.lower()
                if any(target_lower in ing for ing in parsed_ingredients) or target_lower in raw_text.lower():
                    triggered_flags.add(flag_name)

    return list(triggered_flags)


async def main_async():
    raw_path = os.path.abspath("data/raw/product_info.csv")
    processed_dir = os.path.abspath("data/processed")
    os.makedirs(processed_dir, exist_ok=True)
    jsonl_output = os.path.join(processed_dir, "products.jsonl")

    if not os.path.exists(raw_path):
        logger.error(f"Raw product file not found at {raw_path}. Run 01_download_data.py first.")
        return

    logger.info(f"Reading product info from {raw_path}...")
    df = pd.read_csv(raw_path)

    products = []
    for idx, row in df.iterrows():
        p_id = str(row.get("product_id", f"P{idx:06d}"))
        name = str(row.get("product_name", ""))
        brand = str(row.get("brand_name", ""))
        desc = str(row.get("description", "")) if not pd.isna(row.get("description")) else ""
        
        try:
            price_usd = float(row.get("price_usd", 0.0))
        except Exception:
            price_usd = 0.0

        price_inr = int(round(price_usd * settings.USD_TO_INR))
        category = infer_category(str(row.get("primary_category", "")), str(row.get("secondary_category", "")), name)
        
        ingredients_raw = str(row.get("ingredients", "")) if not pd.isna(row.get("ingredients")) else ""
        parsed_ings = parse_ingredients(ingredients_raw)
        
        skin_types = infer_skin_types(row)
        concerns = infer_concerns(row)
        
        try:
            rating = float(row.get("rating", 0.0)) if not pd.isna(row.get("rating")) else None
        except Exception:
            rating = None

        try:
            review_count = int(row.get("reviews", 0)) if not pd.isna(row.get("reviews")) else 0
        except Exception:
            review_count = 0

        is_fragrance_free = "fragrance" not in ingredients_raw.lower() and "parfum" not in ingredients_raw.lower()
        safety_flags = extract_safety_flags(parsed_ings, ingredients_raw)

        text_for_embedding = f"{brand} {name} category: {category} for {' '.join(skin_types)} skin addressing {' '.join(concerns)}. {desc[:300]}"

        product_dict = {
            "product_id": p_id,
            "name": name,
            "brand": brand,
            "category": category,
            "price_usd": price_usd,
            "price_inr": price_inr,
            "description": desc,
            "ingredients_raw": ingredients_raw,
            "ingredients_parsed": parsed_ings,
            "skin_types": skin_types,
            "concerns": concerns,
            "rating": rating,
            "review_count": review_count,
            "is_fragrance_free": is_fragrance_free,
            "safety_flags": safety_flags,
            "text_for_embedding": text_for_embedding
        }
        products.append(product_dict)

    logger.info(f"Normalized {len(products)} products. Writing to {jsonl_output}...")
    with open(jsonl_output, "w", encoding="utf-8") as f:
        for p in products:
            f.write(json.dumps(p) + "\n")

    # Insert into MongoDB if connected
    db = get_db()
    if db is not None:
        logger.info("Inserting products into MongoDB collection 'products'...")
        coll = db["products"]
        await coll.delete_many({})
        if products:
            await coll.insert_many(products)
        logger.info(f"Successfully inserted {len(products)} products into MongoDB.")
    else:
        logger.warning("MongoDB not connected; skipping Mongo insertion.")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
