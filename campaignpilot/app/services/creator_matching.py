import json

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import AuditLog, Campaign, CampaignStatus
from app.services.embeddings import generate_embedding


def match_campaign_creators(campaign_id: int, db: Session) -> dict[str, object]:
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign_embedding = generate_embedding(campaign.brief)

    query = text(
        """
        SELECT *
        FROM match_creators(
            :tenant_id,
            CAST(:embedding AS vector(1536)),
            :limit
        );
        """
    )
    matched_creators = db.execute(
        query,
        {
            "tenant_id": campaign.tenant_id,
            "embedding": json.dumps(campaign_embedding),
            "limit": 5,
        },
    ).mappings().all()

    campaign.status = CampaignStatus.MATCHED.value
    db.add(
        AuditLog(
            tenant_id=campaign.tenant_id,
            campaign_id=campaign.id,
            action="campaign.creators_matched",
            details=f"Matched {len(matched_creators)} creators for campaign {campaign.id}",
        )
    )
    db.commit()

    return {
        "campaign_id": campaign.id,
        "status": campaign.status,
        "matched_creators": [dict(row) for row in matched_creators],
    }
