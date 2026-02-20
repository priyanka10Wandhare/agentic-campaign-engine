from fastapi import APIRouter, Depends, Header, HTTPException, status
import structlog
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Campaign, CampaignStatus, OutreachRequest, OutreachRequestStatus
from app.schemas import OutreachSendResponse
from app.tasks.outreach import send_outreach

api_router = APIRouter()
logger = structlog.get_logger(__name__)


@api_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Health endpoint for readiness checks."""

    return {"status": "ok"}


@api_router.post("/campaigns/{campaign_id}/send-outreach", response_model=OutreachSendResponse, tags=["campaigns"])
def send_campaign_outreach(
    campaign_id: int,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
) -> OutreachSendResponse:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    if campaign.status == CampaignStatus.SENT:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Outreach already sent")

    existing = db.scalar(
        select(OutreachRequest).where(
            OutreachRequest.campaign_id == campaign_id,
            OutreachRequest.idempotency_key == idempotency_key,
        )
    )
    if existing is not None:
        logger.info(
            "outreach.send.idempotent_replay",
            campaign_id=campaign_id,
            request_id=existing.id,
            idempotency_key=idempotency_key,
            task_id=existing.task_id,
        )
        return OutreachSendResponse(
            campaign_id=campaign_id,
            request_id=existing.id,
            task_id=existing.task_id or "",
            status=existing.status,
            idempotent_replay=True,
        )

    in_flight = db.scalar(
        select(OutreachRequest).where(
            OutreachRequest.campaign_id == campaign_id,
            OutreachRequest.status.in_([OutreachRequestStatus.QUEUED, OutreachRequestStatus.SENDING]),
        )
    )
    if in_flight is not None:
        logger.warning(
            "outreach.send.duplicate_blocked",
            campaign_id=campaign_id,
            request_id=in_flight.id,
            task_id=in_flight.task_id,
            idempotency_key=idempotency_key,
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Outreach already queued or sending")

    outreach_request = OutreachRequest(
        campaign_id=campaign_id,
        idempotency_key=idempotency_key,
        status=OutreachRequestStatus.QUEUED,
    )
    campaign.status = CampaignStatus.SENDING
    db.add(outreach_request)
    db.commit()
    db.refresh(outreach_request)

    task = send_outreach.delay(campaign_id=campaign_id, request_id=outreach_request.id)
    outreach_request.task_id = task.id
    db.commit()

    logger.info(
        "outreach.send.queued",
        campaign_id=campaign_id,
        request_id=outreach_request.id,
        task_id=task.id,
        idempotency_key=idempotency_key,
    )

    return OutreachSendResponse(
        campaign_id=campaign_id,
        request_id=outreach_request.id,
        task_id=task.id,
        status=outreach_request.status,
    )
