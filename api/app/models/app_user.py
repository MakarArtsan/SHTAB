"""Учётные записи. Роль и узел назначает тот, кто выше, — сам себе никто (ТЗ 5.1)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import UserRole, UserStatus


class AppUser(Base):
    __tablename__ = "app_user"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Логин. Нормализованный вид +7XXXXXXXXXX — ровно 12 символов.
    phone_norm: Mapped[str] = mapped_column(String(12), unique=True)
    display_name: Mapped[str] = mapped_column(String(200))

    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"))
    node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("org_node.id"))
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status"), default=UserStatus.created
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("app_user.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_app_user_node_id", "node_id"),
        Index("ix_app_user_role", "role"),
    )
