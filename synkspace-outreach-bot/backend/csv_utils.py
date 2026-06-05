"""
CSV parsing utilities.
Handles SynkSpace tracker + generic influencer CSV files.
"""

import io
import re
from typing import Any

import pandas as pd


# -----------------------------
# Column cleaning
# -----------------------------

def clean_column(col: str) -> str:
    col = col.lower().strip()
    col = re.sub(r"[^a-z0-9]+", "_", col)
    col = col.strip("_")
    return col


# -----------------------------
# Supported column names
# -----------------------------

ALIASES = {

    # NAME
    "name": "name",
    "creator_name": "name",
    "influencer_name": "name",
    "full_name": "name",

    # EMAIL
    "email": "email",
    "email_address": "email",
    "e_mail": "email",
    "mail": "email",
    "contact_email": "email",
    "creator_email": "email",
    "business_email": "email",
    "public_email": "email",
    "email_id": "email",

    # SynkSpace sheet column
    "email_link": "email",
    "email_links": "email",
    "email_or_link": "email",

    # INSTAGRAM / PROFILE
    "instagram": "instagram",
    "instagram_handle": "instagram",
    "insta": "instagram",
    "ig": "instagram",
    "handle": "instagram",
    "handle_profile": "instagram",
    "profile": "instagram",
    "profile_link": "instagram",

    # PLATFORM
    "platform": "platform",

    # CATEGORY
    "category": "category",
    "niche": "category",
    "genre": "category",
    "content_type": "category",

    # FOLLOWERS
    "followers": "followers",
    "est_followers": "followers",

    # CITY
    "city": "city",
    "location": "city",

    # EXTRA SYNKSPACE COLUMNS
    "contact_method": "contact_method",
    "why_synkspace_fit": "notes",
    "priority": "priority",
    "status": "status",
}


REQUIRED = {"name"}


# -----------------------------
# CSV parser
# -----------------------------

def parse_csv_bytes(contents: bytes) -> tuple[pd.DataFrame, list[str]]:

    try:
        # read raw file because tracker has title rows
        raw = pd.read_csv(
            io.BytesIO(contents),
            header=None
        )

        header_row = None

        # find actual header row
        for i, row in raw.iterrows():

            values = [
                clean_column(str(x))
                for x in row.values
            ]

            if (
                "name" in values
                or "creator_name" in values
                or "influencer_name" in values
            ):
                header_row = i
                break


        if header_row is None:
            return pd.DataFrame(), [
                "Could not detect CSV header row"
            ]


        df = pd.read_csv(
            io.BytesIO(contents),
            header=header_row
        )


    except Exception as exc:
        return pd.DataFrame(), [
            f"CSV parse failed: {exc}"
        ]


    # rename columns
    renamed = {}

    for col in df.columns:
        cleaned = clean_column(col)
        renamed[col] = ALIASES.get(cleaned, cleaned)

    df = df.rename(columns=renamed)


    print("FINAL CSV COLUMNS:", list(df.columns))


    missing = REQUIRED - set(df.columns)

    if missing:
        return df, [
            f"CSV missing required columns: {', '.join(missing)}"
        ]


    return df.fillna(""), []


# -----------------------------
# Convert row to template data
# -----------------------------

def row_to_context(row: pd.Series) -> dict[str, Any]:

    instagram = str(
        row.get("instagram", "")
    ).strip()


    return {

        "name": str(
            row.get("name", "")
        ).strip(),

        "email": str(
            row.get("email", "")
        ).lower().strip(),

        "instagram": instagram,

        "handle": instagram,

        "category": str(
            row.get("category", "")
        ).strip(),

        "city": str(
            row.get("city", "")
        ).strip(),

        "platform": str(
            row.get("platform", "Instagram")
        ).strip(),
    }


# -----------------------------
# MongoDB document
# -----------------------------

def row_to_creator_doc(row: pd.Series) -> dict[str, Any]:

    ctx = row_to_context(row)


    return {

        "name": ctx["name"],

        "email": ctx["email"],

        "instagram": ctx["instagram"],

        "handle": ctx["handle"],

        "category": ctx["category"],

        "city": ctx["city"],

        "platform": ctx["platform"],


        # extra analytics fields

        "followers": str(
            row.get("followers", "")
        ),

        "priority": str(
            row.get("priority", "")
        ),

        "notes": str(
            row.get("notes", "")
        ),

        "status": str(
            row.get("status", "Not Contacted")
        ),
    }