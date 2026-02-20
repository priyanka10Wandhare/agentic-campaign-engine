from sqlalchemy import DateTime, Float, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OutreachGenerationLog(Base):
    """Stores outreach generation prompt/response metadata for observability."""

    __tablename__ = "outreach_generation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
