from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import MatchCreatorsResponse
from app.services.creator_matching import match_campaign_creators

api_router = APIRouter()


@api_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Health endpoint for readiness checks."""

    return {"status": "ok"}


@api_router.post("/campaigns/{campaign_id}/match-creators", response_model=MatchCreatorsResponse, tags=["campaigns"])
def match_creators_endpoint(campaign_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    """Match campaign with top creators using embedding similarity search."""

    return match_campaign_creators(campaign_id=campaign_id, db=db)
