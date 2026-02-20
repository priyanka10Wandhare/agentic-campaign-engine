from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.models import AuditLog, Campaign, CampaignState
from app.services.campaign_workflow import InvalidTransitionError, transition_campaign_state
from app.workflow import validate_transition


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_validate_transition_allows_configured_edge() -> None:
    assert validate_transition(CampaignState.DRAFT, CampaignState.MATCHED)


def test_validate_transition_blocks_invalid_edge() -> None:
    assert not validate_transition(CampaignState.DRAFT, CampaignState.SENT)


def test_transition_persists_state_and_audit_log(db_session: Session) -> None:
    campaign = Campaign(state=CampaignState.DRAFT.value)
    db_session.add(campaign)
    db_session.commit()
    db_session.refresh(campaign)

    result = transition_campaign_state(db=db_session, campaign_id=campaign.id, to_state=CampaignState.MATCHED)

    assert result.changed is True
    assert result.campaign.state == CampaignState.MATCHED.value

    logs = db_session.query(AuditLog).filter(AuditLog.campaign_id == campaign.id).all()
    assert len(logs) == 1
    assert logs[0].from_state == CampaignState.DRAFT.value
    assert logs[0].to_state == CampaignState.MATCHED.value


def test_transition_is_idempotent_when_target_state_matches(db_session: Session) -> None:
    campaign = Campaign(state=CampaignState.MATCHED.value)
    db_session.add(campaign)
    db_session.commit()
    db_session.refresh(campaign)

    result = transition_campaign_state(db=db_session, campaign_id=campaign.id, to_state=CampaignState.MATCHED)

    assert result.changed is False
    assert db_session.query(AuditLog).filter(AuditLog.campaign_id == campaign.id).count() == 0


def test_transition_rejects_invalid_state_change(db_session: Session) -> None:
    campaign = Campaign(state=CampaignState.DRAFT.value)
    db_session.add(campaign)
    db_session.commit()
    db_session.refresh(campaign)

    with pytest.raises(InvalidTransitionError):
        transition_campaign_state(db=db_session, campaign_id=campaign.id, to_state=CampaignState.SENT)

    db_session.refresh(campaign)
    assert campaign.state == CampaignState.DRAFT.value
    assert db_session.query(AuditLog).filter(AuditLog.campaign_id == campaign.id).count() == 0
