"""
Email logs and dashboard statistics routes.
"""

from fastapi import APIRouter

from database import (
    creators_collection,
    email_logs_collection,
)


router = APIRouter(
    prefix="/api/emails",
    tags=["emails"],
)


def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("/stats")
async def get_email_stats():

    total_creators = await creators_collection().count_documents({})

    emails_sent = await email_logs_collection().count_documents(
        {
            "status": "sent"
        }
    )

    failed_emails = await email_logs_collection().count_documents(
        {
            "status": "failed"
        }
    )


    return {
        "total_creators": total_creators,
        "emails_sent": emails_sent,
        "failed_emails": failed_emails,
        "open_rate": 0,
    }



@router.get("/logs")
async def get_email_logs():

    cursor = (
        email_logs_collection()
        .find({})
        .sort("_id", -1)
        .limit(20)
    )

    logs = [
        serialize(doc)
        async for doc in cursor
    ]


    return {
        "logs": logs,
        "total": len(logs),
    }