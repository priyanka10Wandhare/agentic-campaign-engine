from __future__ import annotations

from pydantic import BaseModel

from app.models import CampaignState


class CampaignTransitionRequest(BaseModel):
    to_state: CampaignState
    message: str | None = None


class CampaignTransitionResponse(BaseModel):
    id: int
    state: CampaignState
    changed: bool
