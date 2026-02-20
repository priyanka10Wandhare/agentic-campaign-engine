from __future__ import annotations

from app.models import CampaignState

ALLOWED_TRANSITIONS: dict[CampaignState, set[CampaignState]] = {
    CampaignState.DRAFT: {CampaignState.MATCHED},
    CampaignState.MATCHED: {CampaignState.OUTREACH_GENERATED},
    CampaignState.OUTREACH_GENERATED: {CampaignState.PENDING_APPROVAL},
    CampaignState.PENDING_APPROVAL: {CampaignState.SENT},
    CampaignState.SENT: {CampaignState.COMPLETED, CampaignState.FAILED},
    CampaignState.COMPLETED: set(),
    CampaignState.FAILED: set(),
}


def validate_transition(from_state: CampaignState, to_state: CampaignState) -> bool:
    """Return True when moving from from_state to to_state is allowed."""

    return to_state in ALLOWED_TRANSITIONS[from_state]
