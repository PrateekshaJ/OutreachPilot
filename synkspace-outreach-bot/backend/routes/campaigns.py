"""
Campaign management routes — create, list, preview, and send outreach campaigns.
"""

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from csv_utils import parse_csv_bytes, row_to_context
from database import campaigns_collection, creators_collection, email_logs_collection
from email_sender import email_sender
from models.campaign import CampaignCreate, CampaignSendRequest
from template_engine import TEMPLATE_MAP, template_engine

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


def _serialize_campaign(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


def _validate_template_type(template_type: str) -> str:
    if template_type not in TEMPLATE_MAP and template_type != "custom":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid template type. Choose from: {', '.join([*TEMPLATE_MAP, 'custom'])}",
        )
    return template_type


def _parse_csv_recipients(contents: bytes) -> list[dict]:
    df, errors = parse_csv_bytes(contents)
    if errors:
        raise HTTPException(status_code=400, detail=errors[0] if len(errors) == 1 else errors)

    recipients: list[dict] = []
    row_errors: list[str] = []

    for index, row in df.iterrows():
        context = row_to_context(row)
        if not context["email"] or "@" not in context["email"]:
            row_errors.append(f"Row {index + 2}: invalid email")
            continue
        recipients.append(context)

    if not recipients:
        raise HTTPException(
            status_code=400,
            detail=row_errors[0] if row_errors else "CSV contains no valid recipients.",
        )

    return recipients


@router.get("/templates")
async def list_templates():
    """Return available email templates for the campaign dropdown."""
    return {"templates": template_engine.list_templates()}


@router.get("")
async def list_campaigns():
    """Return all campaigns."""
    cursor = campaigns_collection().find().sort("created_at", -1)
    campaigns = [_serialize_campaign(doc) async for doc in cursor]
    return {"campaigns": campaigns, "total": len(campaigns)}


@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Return a single campaign by ID."""
    if not ObjectId.is_valid(campaign_id):
        raise HTTPException(status_code=400, detail="Invalid campaign ID.")

    doc = await campaigns_collection().find_one({"_id": ObjectId(campaign_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    return _serialize_campaign(doc)


@router.post("")
async def create_campaign(payload: CampaignCreate):
    """Create a new outreach campaign with a custom HTML template (legacy flow)."""
    now = datetime.now(timezone.utc)
    doc = {
        "name": payload.name,
        "subject": payload.subject,
        "template_type": payload.template_type,
        "html_template": payload.html_template,
        "status": "draft",
        "total_recipients": 0,
        "sent_count": 0,
        "failed_count": 0,
        "created_at": now,
        "sent_at": None,
    }
    result = await campaigns_collection().insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return {"message": "Campaign created", "campaign": doc}


@router.post("/preview")
async def preview_campaign(
    file: UploadFile = File(...),
    template_type: str = Form(...),
    html_template: str = Form(""),
):
    """
    Render a preview of the selected template using the first valid CSV row.
    """
    _validate_template_type(template_type)

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    contents = await file.read()
    recipients = _parse_csv_recipients(contents)
    first_row = recipients[0]

    try:
        html_body = template_engine.render_campaign(
            template_type=template_type,
            context=first_row,
            html_template=html_template or None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "preview_html": html_body,
        "recipient": {
            "name": first_row["name"],
            "email": first_row["email"],
            "category": first_row["category"],
            "city": first_row["city"],
            "handle": first_row["handle"],
            "platform": first_row["platform"],
        },
        "total_recipients": len(recipients),
    }


@router.post("/launch")
async def launch_campaign(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    subject: str = Form(...),
    template_type: str = Form(...),
    html_template: str = Form(""),
    category_filter: str = Form(""),
):
    """
    Create and send a campaign using a CSV file, template type, and subject line.
    """
    _validate_template_type(template_type)

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    contents = await file.read()
    recipients = _parse_csv_recipients(contents)

    if category_filter.strip():
        recipients = [r for r in recipients if r["category"] == category_filter.strip()]
        if not recipients:
            raise HTTPException(
                status_code=400,
                detail=f"No recipients found with category '{category_filter}'.",
            )

    now = datetime.now(timezone.utc)
    campaign_doc = {
        "name": name.strip(),
        "subject": subject.strip(),
        "template_type": template_type,
        "html_template": html_template if template_type == "custom" else None,
        "status": "sending",
        "total_recipients": len(recipients),
        "sent_count": 0,
        "failed_count": 0,
        "created_at": now,
        "sent_at": None,
    }
    result = await campaigns_collection().insert_one(campaign_doc)
    campaign_id = str(result.inserted_id)

    background_tasks.add_task(
        _send_campaign_to_recipients,
        campaign_id,
        recipients,
        subject.strip(),
        template_type,
        html_template if template_type == "custom" else None,
    )

    return {
        "message": "Campaign launched",
        "campaign_id": campaign_id,
        "total_recipients": len(recipients),
    }


async def _send_campaign_to_recipients(
    campaign_id: str,
    recipients: list[dict],
    subject: str,
    template_type: str,
    html_template: str | None,
) -> None:
    """Background task — send templated emails to CSV recipients."""
    sent_count = 0
    failed_count = 0

    for recipient in recipients:
        log_doc = {
            "campaign_id": campaign_id,
            "email": recipient["email"],
            "name": recipient["name"],
            "status": "pending",
            "error": None,
            "sent_at": None,
            "created_at": datetime.now(timezone.utc),
        }

        try:
            html_body = template_engine.render_campaign(
                template_type=template_type,
                context=recipient,
                html_template=html_template,
            )
            await email_sender.send_html_email(
                to_email=recipient["email"],
                subject=subject,
                html_body=html_body,
            )
            log_doc["status"] = "sent"
            log_doc["sent_at"] = datetime.now(timezone.utc)
            sent_count += 1
        except Exception as exc:
            log_doc["status"] = "failed"
            log_doc["error"] = str(exc)
            failed_count += 1

        await email_logs_collection().insert_one(log_doc)

    await campaigns_collection().update_one(
        {"_id": ObjectId(campaign_id)},
        {
            "$set": {
                "status": "completed",
                "sent_count": sent_count,
                "failed_count": failed_count,
                "sent_at": datetime.now(timezone.utc),
            }
        },
    )


async def _send_campaign_emails(campaign_id: str, category_filter: str | None) -> None:
    """Background task — legacy send using MongoDB-stored creators and custom HTML."""
    campaign = await campaigns_collection().find_one({"_id": ObjectId(campaign_id)})
    if not campaign:
        return

    query: dict = {}
    if category_filter:
        query["category"] = category_filter

    creators = await creators_collection().find(query).to_list(length=None)
    sent_count = 0
    failed_count = 0

    template_type = campaign.get("template_type", "custom")
    html_template = campaign.get("html_template")

    for creator in creators:
        context = {
            "name": creator.get("name", ""),
            "email": creator.get("email", ""),
            "category": creator.get("category", ""),
            "city": creator.get("city", ""),
            "handle": creator.get("handle", "") or creator.get("instagram", ""),
            "platform": creator.get("platform", "Instagram"),
            "instagram": creator.get("instagram", ""),
        }

        log_doc = {
            "campaign_id": campaign_id,
            "creator_id": str(creator["_id"]),
            "email": creator["email"],
            "name": creator.get("name", ""),
            "status": "pending",
            "error": None,
            "sent_at": None,
            "created_at": datetime.now(timezone.utc),
        }

        try:
            html_body = template_engine.render_campaign(
                template_type=template_type,
                context=context,
                html_template=html_template,
            )
            await email_sender.send_html_email(
                to_email=creator["email"],
                subject=campaign["subject"],
                html_body=html_body,
            )
            log_doc["status"] = "sent"
            log_doc["sent_at"] = datetime.now(timezone.utc)
            sent_count += 1
        except Exception as exc:
            log_doc["status"] = "failed"
            log_doc["error"] = str(exc)
            failed_count += 1

        await email_logs_collection().insert_one(log_doc)

    await campaigns_collection().update_one(
        {"_id": ObjectId(campaign_id)},
        {
            "$set": {
                "status": "completed",
                "total_recipients": len(creators),
                "sent_count": sent_count,
                "failed_count": failed_count,
                "sent_at": datetime.now(timezone.utc),
            }
        },
    )


@router.post("/{campaign_id}/send")
async def send_campaign(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    payload: CampaignSendRequest | None = None,
):
    """Queue a legacy campaign for sending to MongoDB-stored creators."""
    if not ObjectId.is_valid(campaign_id):
        raise HTTPException(status_code=400, detail="Invalid campaign ID.")

    campaign = await campaigns_collection().find_one({"_id": ObjectId(campaign_id)})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    if campaign.get("status") == "sending":
        raise HTTPException(status_code=409, detail="Campaign is already being sent.")

    category_filter = payload.category if payload else None

    await campaigns_collection().update_one(
        {"_id": ObjectId(campaign_id)},
        {"$set": {"status": "sending"}},
    )

    background_tasks.add_task(_send_campaign_emails, campaign_id, category_filter)

    return {
        "message": "Campaign send started",
        "campaign_id": campaign_id,
        "category_filter": category_filter,
    }
