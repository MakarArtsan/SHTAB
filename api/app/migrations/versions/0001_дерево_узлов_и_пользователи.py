"""Дерево узлов, учётные записи, журнал аудита

Расширения: включаем только ltree и pg_trgm — они нужны уже сейчас.
postgis и vector добавят миграции карты и базы знаний, когда появятся
колонки, которым они нужны.

Revision ID: 0001
Revises:
Create Date: 2026-08-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.models.types import Ltree

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NODE_TYPES = ("federation", "region", "hq", "tik", "uik")
USER_ROLES = (
    "observer",
    "uik_senior",
    "mobile",
    "coordinator",
    "lawyer",
    "press",
    "dispatcher",
    "region_head",
    "federal",
    "admin",
)
USER_STATUSES = ("created", "invited", "active", "suspended", "archived")


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS ltree")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "org_node",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.Enum(*NODE_TYPES, name="node_type"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("path", Ltree(), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("region_code", sa.String(length=3), nullable=True),
        sa.Column("tik_number", sa.Integer(), nullable=True),
        sa.Column("uik_number", sa.Integer(), nullable=True),
        sa.Column("tz", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["parent_id"], ["org_node.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("path"),
    )
    # GIST по пути — на нём держится вся проверка доступа.
    op.create_index("ix_org_node_path_gist", "org_node", ["path"], postgresql_using="gist")
    op.create_index("ix_org_node_parent_id", "org_node", ["parent_id"])

    op.create_table(
        "app_user",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("phone_norm", sa.String(length=12), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column("role", sa.Enum(*USER_ROLES, name="user_role"), nullable=False),
        sa.Column("node_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.Enum(*USER_STATUSES, name="user_status"), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["app_user.id"]),
        sa.ForeignKeyConstraint(["node_id"], ["org_node.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone_norm"),
    )
    op.create_index("ix_app_user_node_id", "app_user", ["node_id"])
    op.create_index("ix_app_user_role", "app_user", ["role"])

    op.create_table(
        "audit_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("object_type", sa.String(length=50), nullable=False),
        sa.Column("object_id", sa.Uuid(), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["actor_id"], ["app_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_log_created_at", "audit_log", [sa.text("created_at DESC")])
    op.create_index("ix_audit_log_actor_id", "audit_log", ["actor_id"])


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("app_user")
    op.drop_table("org_node")
    sa.Enum(name="user_status").drop(op.get_bind())
    sa.Enum(name="user_role").drop(op.get_bind())
    sa.Enum(name="node_type").drop(op.get_bind())
