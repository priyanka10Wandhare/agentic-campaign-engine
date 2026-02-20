from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.outreach_agent import OutreachAgentService
from app.core.database import get_db
from app.schemas.outreach import OutreachGenerationRequest, OutreachGenerationResponse

api_router = APIRouter()
outreach_service = OutreachAgentService()


@api_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Health endpoint for readiness checks."""

    return {"status": "ok"}


@api_router.post(
    "/campaigns/{campaign_id}/generate-outreach",
    response_model=OutreachGenerationResponse,
    tags=["campaigns"],
)
def generate_outreach(
    campaign_id: int,
    payload: OutreachGenerationRequest,
    db: Session = Depends(get_db),
) -> OutreachGenerationResponse:
    """Generate outreach copy for a campaign and creator profile."""

    try:
        return outreach_service.generate_outreach(
            db=db,
            campaign_id=campaign_id,
            campaign_brief=payload.campaign_brief,
            creator_profile=payload.creator_profile,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
