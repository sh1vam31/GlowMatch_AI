import os
import sys
import httpx
import logging
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("download_data")

SHADES_URL = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2021/2021-03-30/allShades.csv"


def download_shades(raw_dir: str):
    output_path = os.path.join(raw_dir, "allShades.csv")
    logger.info(f"Downloading foundation shades dataset from {SHADES_URL}...")
    response = httpx.get(SHADES_URL, follow_redirects=True, timeout=30.0)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(response.content)
    logger.info(f"Successfully saved foundation shades to {output_path}")


def download_sephora_kaggle(raw_dir: str):
    logger.info("Downloading Sephora dataset from Kaggle (nadyinky/sephora-products-and-skincare-reviews)...")

    # Set env vars from settings
    username = settings.KAGGLE_USERNAME or os.environ.get("KAGGLE_USERNAME", "")
    key = settings.KAGGLE_KEY or os.environ.get("KAGGLE_KEY", "")

    if username and key:
        os.environ["KAGGLE_USERNAME"] = username
        os.environ["KAGGLE_KEY"] = key

        # Also write ~/.kaggle/kaggle.json
        kaggle_dir = os.path.expanduser("~/.kaggle")
        os.makedirs(kaggle_dir, exist_ok=True)
        kaggle_json_path = os.path.join(kaggle_dir, "kaggle.json")
        if not os.path.exists(kaggle_json_path):
            import json
            with open(kaggle_json_path, "w") as f:
                json.dump({"username": username, "key": key}, f)
            os.chmod(kaggle_json_path, 0o600)
            logger.info(f"Wrote Kaggle credentials to {kaggle_json_path}")

    kaggle_json_exists = os.path.exists(os.path.expanduser("~/.kaggle/kaggle.json"))
    has_env_credentials = bool(os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"))

    if not (kaggle_json_exists or has_env_credentials):
        logger.error("\n" + "="*70)
        logger.error("KAGGLE API CREDENTIALS MISSING!")
        logger.error("Please obtain a Kaggle API token to download the product dataset:")
        logger.error("1. Go to https://www.kaggle.com and sign in.")
        logger.error("2. Go to Settings -> Account -> Click 'Create New Token'.")
        logger.error("3. Add your credentials to .env:")
        logger.error("   KAGGLE_USERNAME=your_username")
        logger.error("   KAGGLE_KEY=your_key")
        logger.error("   OR place the downloaded kaggle.json file in ~/.kaggle/kaggle.json")
        logger.error("="*70 + "\n")
        sys.exit(1)

    if settings.KAGGLE_USERNAME and settings.KAGGLE_KEY:
        os.environ["KAGGLE_USERNAME"] = settings.KAGGLE_USERNAME
        os.environ["KAGGLE_KEY"] = settings.KAGGLE_KEY

    try:
        import kagglehub
        path = kagglehub.dataset_download("nadyinky/sephora-products-and-skincare-reviews")
        logger.info(f"Downloaded Kaggle dataset to: {path}")

        # Copy downloaded files to data/raw/
        import shutil
        for file_name in os.listdir(path):
            src_file = os.path.join(path, file_name)
            if os.path.isfile(src_file):
                dst_file = os.path.join(raw_dir, file_name)
                shutil.copy2(src_file, dst_file)
                logger.info(f"Copied {file_name} to {dst_file}")
    except Exception as e:
        logger.error(f"Failed to download Kaggle dataset: {e}")
        sys.exit(1)


def main():
    raw_dir = os.path.abspath("data/raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    download_shades(raw_dir)
    download_sephora_kaggle(raw_dir)
    logger.info("Phase 1 Step 01 completed successfully.")


if __name__ == "__main__":
    main()
