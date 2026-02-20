from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CampaignState(StrEnum):
    """Represents the lifecycle state of a campaign."""

    DRAFT = "draft"
    MATCHED = "matched"
    OUTREACH_GENERATED = "outreach_generated"
    PENDING_APPROVAL = "pending_approval"
    SENT = "sent"
    COMPLETED = "completed"
    FAILED = "failed"


class Campaign(Base):
    """Campaign domain model."""

    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    state: Mapped[str] = mapped_column(String(64), nullable=False, default=CampaignState.DRAFT.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    audit_logs: Mapped[list[AuditLog]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan", passive_deletes=True
    )


class AuditLog(Base):
    """State transition audit trail for campaigns."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    from_state: Mapped[str] = mapped_column(String(64), nullable=False)
    to_state: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    campaign: Mapped[Campaign] = relationship(back_populates="audit_logs")
