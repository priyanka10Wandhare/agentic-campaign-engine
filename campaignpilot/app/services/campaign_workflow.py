from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import AuditLog, Campaign, CampaignState
from app.workflow import validate_transition


class CampaignNotFoundError(ValueError):
    """Raised when a campaign cannot be found."""


class InvalidTransitionError(ValueError):
    """Raised when a transition is not allowed by the state machine."""


@dataclass
class TransitionResult:
    campaign: Campaign
    changed: bool


def transition_campaign_state(
    db: Session,
    campaign_id: int,
    to_state: CampaignState,
    message: str | None = None,
) -> TransitionResult:
    """Transition campaign state with state-machine validation and audit logging."""

    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise CampaignNotFoundError(f"Campaign {campaign_id} not found")

    current_state = CampaignState(campaign.state)

    if current_state == to_state:
        return TransitionResult(campaign=campaign, changed=False)

    if not validate_transition(current_state, to_state):
        raise InvalidTransitionError(f"Transition {current_state.value} -> {to_state.value} is not allowed")

    campaign.state = to_state.value
    db.add(
        AuditLog(
            campaign_id=campaign.id,
            from_state=current_state.value,
            to_state=to_state.value,
            message=message,
        )
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    return TransitionResult(campaign=campaign, changed=True)
