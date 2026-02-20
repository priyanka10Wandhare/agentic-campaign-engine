from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, get_tenant_id
from app.schemas.campaign import CampaignCreate, CampaignRead
from app.services import CampaignService

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("", response_model=CampaignRead, status_code=201)
def create_campaign(
    payload: CampaignCreate,
    db: Session = Depends(get_db_session),
    tenant_id: int = Depends(get_tenant_id),
) -> CampaignRead:
    return CampaignService.create_campaign(db, payload, tenant_id)


@router.get("", response_model=list[CampaignRead])
def list_campaigns(
    db: Session = Depends(get_db_session),
    tenant_id: int = Depends(get_tenant_id),
) -> list[CampaignRead]:
    return CampaignService.list_campaigns(db, tenant_id)
