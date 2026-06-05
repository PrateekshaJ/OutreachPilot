"""
Email log and dashboard statistics routes.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/emails", tags=["emails"])


@router.get("/stats")
async def get_email_stats():
    """
    Return dashboard statistics for the outreach platform.
    Temporary version without database dependency.
    """

    return {
        "total_creators": 0,
        "emails_sent": 0,
        "failed_emails": 0,
        "open_rate": 0
    }


@router.get("/logs")
async def list_email_logs():
    """
    Return email logs.
    Temporary version without database dependency.
    """

    return {
        "logs": [],
        "total": 0
    }