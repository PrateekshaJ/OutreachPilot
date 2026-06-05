"""
Creator management routes — CSV upload and listing.
"""

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, File, HTTPException, UploadFile

from csv_utils import parse_csv_bytes, row_to_creator_doc
from database import creators_collection


router = APIRouter(
    prefix="/api/creators",
    tags=["creators"],
)


def _serialize_creator(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc



@router.get("")
async def list_creators():
    """Return all creators stored in MongoDB."""

    cursor = (
        creators_collection()
        .find()
        .sort("created_at", -1)
    )

    creators = [
        _serialize_creator(doc)
        async for doc in cursor
    ]

    return {
        "creators": creators,
        "total": len(creators),
    }




@router.post("/upload")
async def upload_creators_csv(file: UploadFile):

    contents = await file.read()

    df, errors = parse_csv_bytes(contents)


    if errors:
        raise HTTPException(
            status_code=400,
            detail=errors[0],
        )


    inserted = 0
    updated = 0
    skipped = 0


    for _, row in df.iterrows():

        creator_doc = row_to_creator_doc(row)

        email = creator_doc.get("email", "").strip().lower()


        if not email:
            skipped += 1
            continue


        now = datetime.now(timezone.utc)


        existing = await creators_collection().find_one(
            {
                "email": email
            }
        )


        if existing:

            await creators_collection().update_one(
                {
                    "_id": existing["_id"]
                },
                {
                    "$set": {
                        **creator_doc,
                        "updated_at": now,
                    }
                }
            )

            updated += 1


        else:

            creator_doc["created_at"] = now
            creator_doc["updated_at"] = now


            await creators_collection().insert_one(
                creator_doc
            )

            inserted += 1



    return {
        "message": "Creators processed successfully",
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "total_processed": inserted + updated,
    }





@router.delete("/{creator_id}")
async def delete_creator(creator_id: str):

    if not ObjectId.is_valid(creator_id):

        raise HTTPException(
            status_code=400,
            detail="Invalid creator ID",
        )


    result = await creators_collection().delete_one(
        {
            "_id": ObjectId(creator_id)
        }
    )


    if result.deleted_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Creator not found",
        )


    return {
        "message": "Creator deleted successfully"
    }