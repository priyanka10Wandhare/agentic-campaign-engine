from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import CampaignState
from app.schemas import CampaignTransitionRequest, CampaignTransitionResponse
from app.services.campaign_workflow import (
    CampaignNotFoundError,
    InvalidTransitionError,
    transition_campaign_state,
)

api_router = APIRouter()


@api_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Health endpoint for readiness checks."""

    return {"status": "ok"}


@api_router.post(
    "/campaigns/{campaign_id}/transition",
    response_model=CampaignTransitionResponse,
    tags=["campaigns"],
)
def transition_campaign(
    campaign_id: int,
    payload: CampaignTransitionRequest,
    db: Session = Depends(get_db),
) -> CampaignTransitionResponse:
    """Transition a campaign using workflow service business rules."""

    try:
        result = transition_campaign_state(
            db=db,
            campaign_id=campaign_id,
            to_state=CampaignState(payload.to_state),
            message=payload.message,
        )
    except CampaignNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return CampaignTransitionResponse(
        id=result.campaign.id,
        state=CampaignState(result.campaign.state),
        changed=result.changed,
    )
