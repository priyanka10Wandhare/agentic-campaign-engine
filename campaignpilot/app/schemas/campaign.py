from pydantic import BaseModel, ConfigDict

from app.models import CampaignState


class CampaignCreate(BaseModel):
    name: str
    state: CampaignState = CampaignState.DRAFT


class CampaignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    tenant_id: int
    state: CampaignState
