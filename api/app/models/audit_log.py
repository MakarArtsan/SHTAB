"""Неизменяемый журнал действий штабных ролей (ТЗ 5.4, инвариант 7 в CLAUDE.md).

Записи только добавляются. Правка и удаление строк не предусмотрены.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("app_user.id"))
    action: Mapped[str] = mapped_column(String(100))
    object_type: Mapped[str] = mapped_column(String(50))
    object_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)

    # Что именно изменилось. Персональных данных здесь быть не должно.
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_audit_log_created_at", text("created_at DESC")),
        Index("ix_audit_log_actor_id", "actor_id"),
    )
