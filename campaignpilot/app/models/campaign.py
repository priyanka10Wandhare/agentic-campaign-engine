import enum

from sqlalchemy import Enum, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CampaignState(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    state: Mapped[CampaignState] = mapped_column(
        Enum(CampaignState, name="campaign_state"),
        default=CampaignState.DRAFT,
        server_default=text("'draft'"),
        nullable=False,
    )

    tenant = relationship("Tenant", back_populates="campaigns")
