from pydantic import BaseModel


class EvaluationResponse(BaseModel):
    campaign_id: str
    llm_latency: float
    token_count: int
    confidence_score: float
    length_score: float
    cta_score: float
    structure_score: float
    total_score: float
