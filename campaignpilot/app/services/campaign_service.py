from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Campaign
from app.schemas.campaign import CampaignCreate


class CampaignService:
    @staticmethod
    def create_campaign(db: Session, payload: CampaignCreate, tenant_id: int) -> Campaign:
        campaign = Campaign(name=payload.name, tenant_id=tenant_id, state=payload.state)
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign

    @staticmethod
    def list_campaigns(db: Session, tenant_id: int) -> list[Campaign]:
        stmt = select(Campaign).where(Campaign.tenant_id == tenant_id).order_by(Campaign.id.asc())
        return list(db.scalars(stmt).all())
