from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.vector import Vector


class Creator(Base):
    __tablename__ = "creators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    niche: Mapped[str] = mapped_column(String(255), nullable=False)
    followers: Mapped[int] = mapped_column(Integer, nullable=False)
    engagement_rate: Mapped[float] = mapped_column(Float, nullable=False)
    embedding: Mapped[str] = mapped_column(Vector(1536), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
