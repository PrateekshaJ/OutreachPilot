"""
Creator management routes — CSV upload and listing.
"""

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, File, HTTPException, UploadFile

from csv_utils import parse_csv_bytes, row_to_creator_doc
from database import creators_collection

router = APIRouter(prefix="/api/creators", tags=["creators"])

# Upload page still expects these columns; handle/platform/city are optional extras
REQUIRED_COLUMNS = {"name", "email", "instagram", "category"}


def _serialize_creator(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("")
async def list_creators():
    """Return all creators stored in MongoDB."""
    cursor = creators_collection().find().sort("created_at", -1)
    creators = [_serialize_creator(doc) async for doc in cursor]
    return {"creators": creators, "total": len(creators)}


@router.post("/upload")
async def upload_creators_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file with columns: name, email, instagram, category.
    Optional: city, handle, platform.
    Existing creators (matched by email) are updated; new ones are inserted.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    contents = await file.read()
    df, parse_errors = parse_csv_bytes(contents)
    if parse_errors:
        raise HTTPException(status_code=400, detail=parse_errors[0])

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"CSV is missing required columns: {', '.join(sorted(missing))}",
        )

    inserted = 0
    updated = 0
    errors: list[str] = []

    for index, row in df.iterrows():
        creator_doc = row_to_creator_doc(row)
        email = creator_doc["email"]

        if not email or "@" not in email:
            errors.append(f"Row {index + 2}: invalid email '{email}'")
            continue

        creator_doc["updated_at"] = datetime.now(timezone.utc)

        existing = await creators_collection().find_one({"email": email})
        if existing:
            await creators_collection().update_one(
                {"_id": existing["_id"]},
                {"$set": creator_doc},
            )
            updated += 1
        else:
            creator_doc["created_at"] = datetime.now(timezone.utc)
            await creators_collection().insert_one(creator_doc)
            inserted += 1

    return {
        "message": "CSV processed successfully",
        "inserted": inserted,
        "updated": updated,
        "errors": errors,
        "total_processed": inserted + updated,
    }


@router.delete("/{creator_id}")
async def delete_creator(creator_id: str):
    """Delete a single creator by ID."""
    if not ObjectId.is_valid(creator_id):
        raise HTTPException(status_code=400, detail="Invalid creator ID.")

    result = await creators_collection().delete_one({"_id": ObjectId(creator_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Creator not found.")

    return {"message": "Creator deleted successfully"}
