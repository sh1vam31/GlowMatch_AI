import os
import json
import logging
from sentence_transformers import SentenceTransformer
from qdrant_client.models import VectorParams, Distance, PointStruct
from app.config import settings
from app.db.vectors import get_qdrant_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("index_products")


def main():
    jsonl_path = os.path.abspath("data/processed/products.jsonl")
    if not os.path.exists(jsonl_path):
        logger.error(f"Processed products file not found at {jsonl_path}. Run 02_normalize_catalog.py first.")
        return

    logger.info(f"Loading products from {jsonl_path}...")
    products = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                products.append(json.loads(line))

    logger.info(f"Loaded {len(products)} products.")
    logger.info(f"Loading embedding model '{settings.EMBEDDING_MODEL}'...")
    embedder = SentenceTransformer(settings.EMBEDDING_MODEL)

    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION

    # Re-create collection
    logger.info(f"Re-creating Qdrant collection '{collection_name}' with vector size {settings.EMBEDDING_DIM}...")
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=settings.EMBEDDING_DIM, distance=Distance.COSINE)
    )

    batch_size = 100
    points = []

    logger.info("Generating embeddings and uploading vectors to Qdrant...")
    for i in range(0, len(products), batch_size):
        batch = products[i:i+batch_size]
        texts = [p.get("text_for_embedding", p["name"]) for p in batch]
        embeddings = embedder.encode(texts, show_progress_bar=False, normalize_embeddings=True)

        for j, (p, emb) in enumerate(zip(batch, embeddings)):
            idx = i + j
            points.append(PointStruct(
                id=idx,
                vector=emb.tolist(),
                payload={
                    "product_id": p["product_id"],
                    "name": p["name"],
                    "brand": p["brand"],
                    "category": p["category"],
                    "price_inr": p["price_inr"],
                    "skin_types": p["skin_types"],
                    "concerns": p["concerns"],
                    "is_fragrance_free": p["is_fragrance_free"],
                    "safety_flags": p["safety_flags"]
                }
            ))

        if len(points) >= 500:
            client.upsert(collection_name=collection_name, points=points)
            logger.info(f"Indexed {i + len(batch)} / {len(products)} products...")
            points = []

    if points:
        client.upsert(collection_name=collection_name, points=points)

    logger.info(f"Successfully indexed all {len(products)} products into Qdrant collection '{collection_name}'.")


if __name__ == "__main__":
    main()
