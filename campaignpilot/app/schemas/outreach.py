from pydantic import BaseModel, Field, field_validator


class OutreachGenerationRequest(BaseModel):
    campaign_brief: str = Field(min_length=1)
    creator_profile: str = Field(min_length=1)


class OutreachGenerationResponse(BaseModel):
    subject: str
    body: str
    confidence_score: float = Field(ge=0.0, le=1.0)

    @field_validator("body")
    @classmethod
    def max_word_count(cls, value: str) -> str:
        if len(value.split()) > 300:
            raise ValueError("Outreach body exceeds 300 words")
        return value
