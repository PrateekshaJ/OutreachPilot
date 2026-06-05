"""
MongoDB database connection helpers.
"""

from motor.motor_asyncio import AsyncIOMotorClient

from config import settings


client = AsyncIOMotorClient(settings.mongodb_uri)

database = client[settings.mongodb_db]


def creators_collection():
    return database["creators"]


def campaigns_collection():
    return database["campaigns"]


def email_logs_collection():
    return database["email_logs"]