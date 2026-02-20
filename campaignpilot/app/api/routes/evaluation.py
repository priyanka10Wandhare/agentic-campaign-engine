from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import Base, engine, get_db
from app.evaluation.runner import run_evaluation
from app.schemas.evaluation import EvaluationResponse

router = APIRouter(tags=["evaluation"])


@router.post("/evaluate/{campaign_id}", response_model=EvaluationResponse)
def evaluate_campaign(campaign_id: str, db: Session = Depends(get_db)) -> EvaluationResponse:
    Base.metadata.create_all(bind=engine)
    try:
        metric = run_evaluation(campaign_id=campaign_id, db=db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to persist evaluation metrics") from exc

    return EvaluationResponse(
        campaign_id=metric.campaign_id,
        llm_latency=metric.llm_latency,
        token_count=metric.token_count,
        confidence_score=metric.confidence_score,
        length_score=metric.length_score,
        cta_score=metric.cta_score,
        structure_score=metric.structure_score,
        total_score=metric.total_score,
    )
