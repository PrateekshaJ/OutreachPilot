"""
Shared CSV parsing utilities for creator uploads and campaign sends.
"""

import io
from typing import Any

import pandas as pd


# Only creator name is compulsory
REQUIRED_COLUMNS = {"name"}


# Map messy CSV headers → clean backend fields
COLUMN_MAP = {
    "name": "name",
    "handle / profile": "handle",
    "handle": "handle",
    "instagram": "handle",
    "platform": "platform",
    "category": "category",
    "t.follower": "followers",
    "followers": "followers",
    "city": "city",
    "contact method": "contact_method",
    "email / link": "email",
    "email/link": "email",
    "email": "email",
    "why synkspace fit": "notes",
    "priority": "priority",
    "status": "status",
}


def parse_csv_bytes(contents: bytes) -> tuple[pd.DataFrame, list[str]]:
    """
    Parse CSV bytes into normalized creator dataframe.
    """

    errors: list[str] = []

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as exc:
        return pd.DataFrame(), [
            f"Failed to parse CSV: {exc}"
        ]


    # clean column names
    df.columns = [
        col.strip().lower()
        for col in df.columns
    ]


    # rename columns
    df = df.rename(
        columns={
            col: COLUMN_MAP.get(col, col)
            for col in df.columns
        }
    )


    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        errors.append(
            f"CSV missing required columns: {', '.join(missing)}"
        )

        return df, errors


    return df.fillna(""), errors



def row_to_context(row: pd.Series) -> dict[str, Any]:
    """
    Build template variables for emails.
    """

    handle = str(
        row.get("handle", "")
    ).strip()


    return {
        "name": str(
            row.get("name", "")
        ).strip(),

        "email": str(
            row.get("email", "")
        ).strip(),

        "category": str(
            row.get("category", "")
        ).strip(),

        "city": str(
            row.get("city", "")
        ).strip(),

        "handle": handle,

        "instagram": handle,

        "platform": str(
            row.get("platform", "Instagram")
        ).strip(),

        "followers": str(
            row.get("followers", "")
        ).strip(),

        "priority": str(
            row.get("priority", "")
        ).strip(),

        "notes": str(
            row.get("notes", "")
        ).strip(),
    }



def row_to_creator_doc(row: pd.Series) -> dict[str, Any]:
    """
    Build MongoDB creator document.
    """

    context = row_to_context(row)

    return {
        **context,
        "status": str(
            row.get("status", "Not Contacted")
        ),
    }