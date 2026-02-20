from pydantic import BaseModel


class MatchedCreator(BaseModel):
    id: int
    tenant_id: str
    niche: str
    followers: int
    engagement_rate: float
    similarity: float


class MatchCreatorsResponse(BaseModel):
    campaign_id: int
    status: str
    matched_creators: list[MatchedCreator]
