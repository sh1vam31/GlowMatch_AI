from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
from app.config import settings
from app.db.mongo import check_mongo_health
from app.db.vectors import check_qdrant_health
from app.db.cache import check_cache_health, get_cache

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger("glowmatch")

import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    cache = get_cache()
    logger.info(f"GlowMatch AI backend started in {settings.ENV} mode.")
    logger.info(f"Cache status: {cache.metrics()}")

    def _warmup():
        try:
            from app.retrieval.embedder import get_embedder
            logger.info("Pre-warming lightweight embedding model in background...")
            get_embedder()
            logger.info("Embedding model pre-warmed successfully!")
        except Exception as e:
            logger.warning(f"Model pre-warming deferred: {e}")

    asyncio.get_event_loop().run_in_executor(None, _warmup)
    yield

app = FastAPI(
    title="GlowMatch AI",
    description="Unified beauty recommendation engine",
    version="0.1.0",
    lifespan=lifespan
)

from app.api import recommend
app.include_router(recommend.router, prefix="/api")


@app.get("/health")
async def health_check():
    mongo_status = await check_mongo_health()
    qdrant_status = check_qdrant_health()
    cache_status = check_cache_health()

    return {
        "status": "ok",
        "env": settings.ENV,
        "mongo": mongo_status,
        "qdrant": qdrant_status,
        "cache": cache_status
    }


from fastapi.responses import FileResponse

@app.get("/")
async def serve_ui():
    static_index = os.path.abspath("static/index.html")
    if os.path.exists(static_index):
        return FileResponse(static_index)
    return {"message": "GlowMatch AI Engine Live", "docs": "/docs", "health": "/health"}


# Mount static and assets directories
static_path = os.path.abspath("static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    assets_path = os.path.join(static_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
