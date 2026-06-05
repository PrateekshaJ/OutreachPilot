"""
Pydantic models for creator resources.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class CreatorBase(BaseModel):
    name: str
    email: EmailStr
    instagram: str = ""
    category: str = ""


class CreatorCreate(CreatorBase):
    pass


class CreatorResponse(CreatorBase):
    id: str = Field(alias="_id")
    created_at: datetime

    model_config = {"populate_by_name": True}
