import os
import json
import glob
import pandas as pd
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("build_cooccurrence")


def main():
    raw_dir = os.path.abspath("data/raw")
    output_path = os.path.abspath("data/processed/cooccurrence.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    review_files = glob.glob(os.path.join(raw_dir, "reviews_*.csv")) + glob.glob(os.path.join(raw_dir, "*review*.csv"))
    
    cooccurrence = defaultdict(lambda: defaultdict(int))

    if not review_files:
        logger.warning(f"No review shards found in {raw_dir}. Writing empty co-occurrence matrix.")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return

    logger.info(f"Found {len(review_files)} review files. Building item-item co-occurrence matrix...")
    
    author_products = defaultdict(set)
    for r_file in review_files:
        logger.info(f"Processing {r_file}...")
        try:
            df = pd.read_csv(r_file, usecols=lambda c: c.lower() in ["author_id", "product_id"])
            if "author_id" in df.columns and "product_id" in df.columns:
                for _, row in df.iterrows():
                    aid = str(row["author_id"])
                    pid = str(row["product_id"])
                    if aid and pid and aid != "nan" and pid != "nan":
                        author_products[aid].add(pid)
        except Exception as e:
            logger.warning(f"Failed to parse {r_file}: {e}")

    logger.info(f"Processing reviews from {len(author_products)} unique authors...")
    for aid, prods in author_products.items():
        prod_list = list(prods)
        if len(prod_list) > 1 and len(prod_list) <= 50:  # Ignore extreme spammers
            for i in range(len(prod_list)):
                for j in range(i + 1, len(prod_list)):
                    p1, p2 = prod_list[i], prod_list[j]
                    cooccurrence[p1][p2] += 1
                    cooccurrence[p2][p1] += 1

    # Convert defaultdict to standard dict
    output_data = {k: dict(v) for k, v in cooccurrence.items()}
    
    logger.info(f"Saving co-occurrence matrix ({len(output_data)} products) to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f)
        
    logger.info("Phase 1 Step 05 completed successfully.")


if __name__ == "__main__":
    main()
