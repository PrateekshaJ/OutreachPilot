"""
Pydantic models for campaign resources.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

TemplateType = Literal[
    "founding_creator",
    "follow_up",
    "brand_invite",
    "event_invite",
    "custom",
]


class CampaignCreate(BaseModel):
    """Legacy JSON endpoint — create a campaign with a custom HTML template."""
    name: str
    subject: str
    html_template: str
    template_type: TemplateType = "custom"


class CampaignResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    subject: str
    template_type: str = "custom"
    html_template: Optional[str] = None
    status: str
    total_recipients: int = 0
    sent_count: int = 0
    failed_count: int = 0
    created_at: datetime
    sent_at: Optional[datetime] = None

    model_config = {"populate_by_name": True}


class CampaignSendRequest(BaseModel):
    """Optional filter to send only to creators in a specific category."""
    category: Optional[str] = None
