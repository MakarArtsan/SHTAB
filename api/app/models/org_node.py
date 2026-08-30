"""Дерево мест: федерация → регион → ТИК → УИК, плюс штабные узлы (ТЗ 4.1)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import NodeType
from app.models.types import Ltree


class OrgNode(Base):
    __tablename__ = "org_node"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    type: Mapped[NodeType] = mapped_column(Enum(NodeType, name="node_type"))
    name: Mapped[str] = mapped_column(String(200))

    # Материализованный путь. По нему и только по нему проверяется доступ.
    path: Mapped[str] = mapped_column(Ltree, unique=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("org_node.id"))

    region_code: Mapped[str | None] = mapped_column(String(3))
    tik_number: Mapped[int | None] = mapped_column(Integer)
    uik_number: Mapped[int | None] = mapped_column(Integer)

    # Часовой пояс узла: в БД всё в UTC, пользователю показываем местное время.
    tz: Mapped[str] = mapped_column(String(64), default="Europe/Moscow")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_org_node_path_gist", "path", postgresql_using="gist"),
        Index("ix_org_node_parent_id", "parent_id"),
    )
