import random

from celery import Task
from celery.exceptions import MaxRetriesExceededError
import structlog

from app.core.database import SessionLocal, init_db
from app.core.logging import configure_logging
from app.models import AuditLog, Campaign, CampaignStatus, OutreachRequest, OutreachRequestStatus

configure_logging()
logger = structlog.get_logger(__name__)


class OutreachTask(Task):
    max_retries = 3


@OutreachTask.bind
def send_outreach(self: OutreachTask, campaign_id: int, request_id: int) -> dict[str, str]:
    init_db()
    db = SessionLocal()
    try:
        campaign = db.get(Campaign, campaign_id)
        request = db.get(OutreachRequest, request_id)

        if campaign is None or request is None:
            logger.error(
                "outreach.send.missing_entities",
                campaign_id=campaign_id,
                request_id=request_id,
            )
            return {"status": "missing"}

        request.status = OutreachRequestStatus.SENDING
        campaign.status = CampaignStatus.SENDING
        db.commit()

        if random.random() < 0.3:
            countdown = 2 ** (self.request.retries + 1)
            logger.warning(
                "outreach.send.retry",
                campaign_id=campaign_id,
                request_id=request_id,
                retry=self.request.retries + 1,
                countdown_seconds=countdown,
            )
            raise self.retry(exc=RuntimeError("Simulated outreach failure"), countdown=countdown)

        request.status = OutreachRequestStatus.SENT
        campaign.status = CampaignStatus.SENT
        db.add(
            AuditLog(
                campaign_id=campaign.id,
                action="outreach_sent",
                details={"request_id": request.id, "task_id": request.task_id},
            )
        )
        db.commit()

        logger.info(
            "outreach.send.success",
            campaign_id=campaign_id,
            request_id=request_id,
            task_id=request.task_id,
        )
        return {"status": "sent"}
    except MaxRetriesExceededError:
        campaign = db.get(Campaign, campaign_id)
        request = db.get(OutreachRequest, request_id)
        if campaign is not None:
            campaign.status = CampaignStatus.FAILED
        if request is not None:
            request.status = OutreachRequestStatus.FAILED

        db.add(
            AuditLog(
                campaign_id=campaign_id,
                action="outreach_failed_max_retries",
                details={"request_id": request_id, "max_retries": self.max_retries},
            )
        )
        db.commit()

        logger.error(
            "outreach.send.max_retries_exceeded",
            campaign_id=campaign_id,
            request_id=request_id,
            max_retries=self.max_retries,
        )
        return {"status": "failed"}
    finally:
        db.close()
