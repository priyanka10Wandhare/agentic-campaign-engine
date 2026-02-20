import json
import time
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.metrics import EvaluationMetric

DATASET_PATH = Path(__file__).with_name("evaluation_dataset.json")
CTA_KEYWORDS = {"buy", "shop", "start", "launch", "claim", "sign up", "learn more", "get started"}
REQUIRED_SECTIONS = ("headline:", "body:", "cta:")


def _length_score(text: str) -> float:
    words = len(text.split())
    if 12 <= words <= 80:
        return 1.0
    if 8 <= words <= 100:
        return 0.5
    return 0.0


def _cta_score(text: str) -> float:
    lowered = text.lower()
    return 1.0 if any(keyword in lowered for keyword in CTA_KEYWORDS) else 0.0


def _structure_score(text: str) -> float:
    lowered = text.lower()
    matched = sum(1 for section in REQUIRED_SECTIONS if section in lowered)
    return matched / len(REQUIRED_SECTIONS)


def _confidence(length_score: float, cta_score: float, structure_score: float) -> float:
    return round((length_score + cta_score + structure_score) / 3, 4)


def _load_campaign_entries(campaign_id: str) -> list[dict[str, str]]:
    payload = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    return [row for row in payload if row["campaign_id"] == campaign_id]


def run_evaluation(campaign_id: str, db: Session) -> EvaluationMetric:
    """Evaluate dataset entries for a campaign, persist aggregated metrics, and return the DB row."""

    entries = _load_campaign_entries(campaign_id)
    if not entries:
        raise ValueError(f"No evaluation samples found for campaign_id={campaign_id}")

    start = time.perf_counter()
    length_scores: list[float] = []
    cta_scores: list[float] = []
    structure_scores: list[float] = []
    token_count = 0

    for entry in entries:
        text = entry["content"]
        length_scores.append(_length_score(text))
        cta_scores.append(_cta_score(text))
        structure_scores.append(_structure_score(text))
        token_count += len(text.split())

    llm_latency = round(time.perf_counter() - start, 6)
    length_score = round(sum(length_scores) / len(length_scores), 4)
    cta_score = round(sum(cta_scores) / len(cta_scores), 4)
    structure_score = round(sum(structure_scores) / len(structure_scores), 4)
    confidence_score = _confidence(length_score, cta_score, structure_score)
    total_score = confidence_score

    metric = EvaluationMetric(
        campaign_id=campaign_id,
        llm_latency=llm_latency,
        token_count=token_count,
        confidence_score=confidence_score,
        length_score=length_score,
        cta_score=cta_score,
        structure_score=structure_score,
        total_score=total_score,
    )

    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric
