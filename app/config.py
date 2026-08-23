from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # MongoDB
    MONGO_URI: str = ""
    MONGO_DB: str = "glowmatch"

    # Qdrant
    QDRANT_MODE: str = "embedded"  # embedded or cloud
    QDRANT_PATH: str = "./qdrant_data"
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "products"

    # Cache
    REDIS_URL: str = ""

    # Models
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIM: int = 384
    RERANKER_MODEL: str = "BAAI/bge-reranker-base"
    LLM_MODEL: str = "gemini-2.5-flash-lite"
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "groq/compound"
    GROK_API_KEY: str = ""
    GROK_MODEL: str = "grok-2-latest"
    LLM_PROVIDER: str = "auto"  # auto | groq | grok | gemini

    # Retrieval behaviour
    RETRIEVAL_STRATEGY: str = "hybrid_rrf_ce"
    TOP_K_RETRIEVE: int = 20
    TOP_K_RETURN: int = 5
    RRF_K: int = 60
    ENABLE_LLM_RERANK: bool = False

    # Caching TTLs (seconds)
    CACHE_TTL_QUERY: int = 3600
    CACHE_TTL_EMBEDDING: int = 86400
    CACHE_TTL_LLM: int = 86400
    CACHE_TTL_ATTRIBUTES: int = 3600

    # Vision
    MAX_IMAGE_BYTES: int = 8388608
    ENABLE_WHITE_BALANCE: bool = True

    # Public deployment protection
    RATE_LIMIT_PER_MIN: int = 10
    RATE_LIMIT_PER_DAY: int = 100
    LLM_DAILY_BUDGET: int = 800
    ALLOWED_ORIGINS: str = "http://localhost:8000"
    DEGRADE_ON_BUDGET_EXHAUSTED: bool = True

    # Misc
    USD_TO_INR: int = 83
    LOG_LEVEL: str = "INFO"
    ENV: str = "development"

    # Data download
    KAGGLE_USERNAME: str = ""
    KAGGLE_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
