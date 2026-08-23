from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

import certifi

import asyncio

mongo_client: AsyncIOMotorClient = None


def get_mongo_client() -> AsyncIOMotorClient:
    global mongo_client
    if settings.MONGO_URI:
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if mongo_client is None or (current_loop and mongo_client.get_io_loop() != current_loop):
            try:
                mongo_client = AsyncIOMotorClient(settings.MONGO_URI, tlsCAFile=certifi.where())
            except Exception:
                mongo_client = AsyncIOMotorClient(settings.MONGO_URI, tlsAllowInvalidCertificates=True)
    return mongo_client


def get_db():
    client = get_mongo_client()
    if client:
        return client[settings.MONGO_DB]
    return None


async def check_mongo_health() -> dict:
    if not settings.MONGO_URI:
        return {"connected": False, "status": "unset (MONGO_URI not configured)"}
    try:
        client = get_mongo_client()
        await client.admin.command('ping')
        return {"connected": True, "database": settings.MONGO_DB}
    except Exception as e:
        logger.warning(f"MongoDB ping failed: {e}")
        return {"connected": False, "error": str(e)}
