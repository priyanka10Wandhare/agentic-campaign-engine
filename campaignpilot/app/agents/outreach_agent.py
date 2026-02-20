import importlib
import json
import time
from dataclasses import dataclass

import structlog
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.outreach_log import OutreachGenerationLog
from app.schemas.outreach import OutreachGenerationResponse

logger = structlog.get_logger(__name__)


@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class OutreachAgentService:
    """Generates structured outreach content using OpenAI with deterministic fallback."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_outreach(
        self,
        db: Session,
        campaign_id: int,
        campaign_brief: str,
        creator_profile: str,
    ) -> OutreachGenerationResponse:
        prompt = self._build_prompt(campaign_brief=campaign_brief, creator_profile=creator_profile)

        start = time.perf_counter()
        if self.settings.openai_api_key and importlib.util.find_spec("openai") is not None:
            response_payload, token_usage = self._generate_with_openai(prompt)
        else:
            response_payload, token_usage = self._generate_mock_response(campaign_brief, creator_profile)

        latency_ms = (time.perf_counter() - start) * 1000
        validated = self._validate_guardrails(response_payload)

        db.add(
            OutreachGenerationLog(
                campaign_id=campaign_id,
                prompt=prompt,
                response=validated.model_dump_json(),
                latency_ms=latency_ms,
                prompt_tokens=token_usage.prompt_tokens,
                completion_tokens=token_usage.completion_tokens,
                total_tokens=token_usage.total_tokens,
            )
        )
        db.commit()

        logger.info(
            "outreach.generated",
            campaign_id=campaign_id,
            latency_ms=round(latency_ms, 2),
            total_tokens=token_usage.total_tokens,
            used_openai=bool(self.settings.openai_api_key),
        )
        return validated

    def _build_prompt(self, campaign_brief: str, creator_profile: str) -> str:
        return (
            "Generate outreach JSON with this exact schema: "
            '{"subject": "string", "body": "string", "confidence_score": 0.0}. '
            "Constraints: body <=300 words and must contain CTA phrase "
            f'\"{self.settings.required_cta_phrase}\". '
            f"Campaign brief: {campaign_brief}\n"
            f"Creator profile: {creator_profile}"
        )

    def _generate_with_openai(self, prompt: str) -> tuple[dict, TokenUsage]:
        openai_module = importlib.import_module("openai")
        client = openai_module.OpenAI(api_key=self.settings.openai_api_key)

        response = client.responses.create(
            model=self.settings.openai_model,
            input=prompt,
            temperature=0.3,
        )
        content = response.output_text
        payload = json.loads(content)
        usage = getattr(response, "usage", None)
        token_usage = TokenUsage(
            prompt_tokens=getattr(usage, "input_tokens", 0) or 0,
            completion_tokens=getattr(usage, "output_tokens", 0) or 0,
            total_tokens=getattr(usage, "total_tokens", 0) or 0,
        )
        return payload, token_usage

    def _generate_mock_response(self, campaign_brief: str, creator_profile: str) -> tuple[dict, TokenUsage]:
        body = (
            f"Hi there, I loved your content and think it aligns with our campaign: {campaign_brief}. "
            f"Given your profile ({creator_profile}), you are a strong fit for this collaboration. "
            f"{self.settings.required_cta_phrase}"
        )
        payload = {
            "subject": "Partnership idea tailored for your audience",
            "body": body,
            "confidence_score": 0.72,
        }
        prompt_tokens = max(1, len(campaign_brief.split()) + len(creator_profile.split()))
        completion_tokens = max(1, len(body.split()))
        return payload, TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )

    def _validate_guardrails(self, payload: dict) -> OutreachGenerationResponse:
        try:
            parsed = OutreachGenerationResponse.model_validate(payload)
        except ValidationError as exc:
            raise ValueError(f"Invalid outreach payload: {exc}") from exc

        if self.settings.required_cta_phrase.lower() not in parsed.body.lower():
            raise ValueError(
                f"Outreach body must include CTA phrase: {self.settings.required_cta_phrase}"
            )
        return parsed
