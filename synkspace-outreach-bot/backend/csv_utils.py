"""
Shared CSV parsing utilities for creator uploads and campaign sends.
"""

import io
from typing import Any

import pandas as pd

# Minimum columns required for any CSV import
REQUIRED_COLUMNS = {"name", "email"}

# Optional columns used for template personalization
OPTIONAL_COLUMNS = {"category", "city", "handle", "instagram", "platform"}


def parse_csv_bytes(contents: bytes) -> tuple[pd.DataFrame, list[str]]:
    """
    Parse CSV bytes into a normalized DataFrame.

    Returns the DataFrame and a list of validation errors (empty if valid).
    """
    errors: list[str] = []

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as exc:
        return pd.DataFrame(), [f"Failed to parse CSV: {exc}"]

    df.columns = [col.strip().lower() for col in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        errors.append(f"CSV is missing required columns: {', '.join(sorted(missing))}")
        return df, errors

    return df.fillna(""), errors


def row_to_context(row: pd.Series) -> dict[str, Any]:
    """Build a Jinja2 template context from a CSV row."""
    handle = str(row.get("handle", "") or row.get("instagram", "")).strip()
    platform = str(row.get("platform", "") or "Instagram").strip()

    return {
        "name": str(row.get("name", "")).strip(),
        "email": str(row.get("email", "")).strip().lower(),
        "category": str(row.get("category", "")).strip(),
        "city": str(row.get("city", "")).strip(),
        "handle": handle,
        "platform": platform,
        # Legacy aliases kept for backward compatibility
        "instagram": handle,
    }


def row_to_creator_doc(row: pd.Series) -> dict[str, Any]:
    """Build a MongoDB creator document from a CSV row."""
    context = row_to_context(row)
    return {
        "name": context["name"],
        "email": context["email"],
        "instagram": context["handle"],
        "category": context["category"],
        "city": context["city"],
        "handle": context["handle"],
        "platform": context["platform"],
    }
