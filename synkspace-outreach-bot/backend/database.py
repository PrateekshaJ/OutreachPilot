"""
MongoDB connection and collection helpers.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import get_settings

_client: AsyncIOMotorClient | None = None


async def connect_db() -> None:
    """Initialize the MongoDB client on application startup."""
    global _client
    settings = get_settings()
    _client = AsyncIOMotorClient(settings.mongodb_uri)


async def close_db() -> None:
    """Close the MongoDB client on application shutdown."""
    global _client
    if _client is not None:
        _client.close()
        _client = None


def get_database() -> AsyncIOMotorDatabase:
    if _client is None:
        raise RuntimeError("Database client is not initialized.")
    settings = get_settings()
    return _client[settings.mongodb_db]


def creators_collection():
    return get_database()["creators"]


def campaigns_collection():
    return get_database()["campaigns"]


def email_logs_collection():
    return get_database()["email_logs"]
