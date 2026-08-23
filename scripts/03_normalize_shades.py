import os
import json
import pandas as pd
import numpy as np
import asyncio
import logging
from skimage import color
from app.config import settings
from app.db.mongo import get_db
from app.vision.ita import calculate_ita, get_ita_band

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("normalize_shades")


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    hex_str = str(hex_str).lstrip("#").strip()
    if len(hex_str) != 6:
        return (200, 150, 120)  # Default fallback skin tone RGB
    try:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return (r, g, b)
    except Exception:
        return (200, 150, 120)


def rgb_to_lab(r: int, g: int, b: int) -> tuple[float, float, float]:
    rgb_arr = np.array([[[r / 255.0, g / 255.0, b / 255.0]]], dtype=np.float64)
    lab_arr = color.rgb2lab(rgb_arr)
    l, a, b_val = lab_arr[0, 0]
    return (float(l), float(a), float(b_val))


async def main_async():
    raw_path = os.path.abspath("data/raw/allShades.csv")
    processed_dir = os.path.abspath("data/processed")
    os.makedirs(processed_dir, exist_ok=True)
    jsonl_output = os.path.join(processed_dir, "shades.jsonl")

    if not os.path.exists(raw_path):
        logger.error(f"Raw shades file not found at {raw_path}. Run 01_download_data.py first.")
        return

    logger.info(f"Reading foundation shades from {raw_path}...")
    df = pd.read_csv(raw_path)

    shades = []
    for idx, row in df.iterrows():
        s_id = f"S{idx:06d}"
        brand = str(row.get("brand", ""))
        product = str(row.get("product", ""))
        shade_name = str(row.get("name", str(row.get("specific", f"Shade {idx}"))))
        hex_val = str(row.get("hex", "#D29B77")).upper()
        if not hex_val.startswith("#"):
            hex_val = "#" + hex_val

        r, g, b_val = hex_to_rgb(hex_val)
        l_star, a_star, b_star = rgb_to_lab(r, g, b_val)
        ita = calculate_ita(l_star, b_star)
        ita_band = get_ita_band(ita)

        shade_dict = {
            "shade_id": s_id,
            "brand": brand,
            "product": product,
            "shade_name": shade_name,
            "hex": hex_val,
            "lab_l": round(l_star, 2),
            "lab_a": round(a_star, 2),
            "lab_b": round(b_star, 2),
            "ita": round(ita, 2),
            "ita_band": ita_band
        }
        shades.append(shade_dict)

    logger.info(f"Normalized {len(shades)} foundation shades. Writing to {jsonl_output}...")
    with open(jsonl_output, "w", encoding="utf-8") as f:
        for s in shades:
            f.write(json.dumps(s) + "\n")

    # Insert into MongoDB if connected
    db = get_db()
    if db is not None:
        logger.info("Inserting shades into MongoDB collection 'shades'...")
        coll = db["shades"]
        await coll.delete_many({})
        if shades:
            await coll.insert_many(shades)
        logger.info(f"Successfully inserted {len(shades)} shades into MongoDB.")
    else:
        logger.warning("MongoDB not connected; skipping Mongo insertion.")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
