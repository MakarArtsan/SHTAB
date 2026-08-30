"""Проверка доступа. Единственная на всю систему.

Правило одно: пользователь видит свой узел и всё, что под ним, —
`org_node.path <@ scope`. Второго способа проверки в проекте быть не должно,
оператор `<@` встречается только здесь (это закреплено тестом).

Штабной узел (`hq`) — рабочая группа при регионе или ТИК, а не место в
иерархии мест: он лежит рядом с ТИК, а не над ними. Поэтому для штабного узла
областью видимости служит путь родителя — иначе диспетчер и юрист не увидели бы
ничего, кроме собственного штаба. Обоснование — в ADR 0001.
"""

import uuid

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AccessDenied
from app.models.app_user import AppUser
from app.models.enums import NodeType
from app.models.org_node import OrgNode


def scope_path(node: OrgNode) -> str:
    """Путь, ограничивающий видимость пользователя, привязанного к этому узлу."""
    if node.type != NodeType.hq:
        return node.path

    parent_path, _, _ = node.path.rpartition(".")
    if not parent_path:
        raise ValueError(f"штабной узел {node.path} без родителя: область видимости не определена")
    return parent_path


def nodes_in_scope(scope: str) -> Select[tuple[uuid.UUID]]:
    """Подзапрос с идентификаторами доступных узлов.

    Возвращаем именно запрос, а не список: узлов десятки тысяч, и подставлять
    их в IN (...) нельзя.
    """
    return select(OrgNode.id).where(OrgNode.path.op("<@")(scope))


async def user_scope_path(session: AsyncSession, user_id: uuid.UUID) -> str:
    """Область видимости пользователя. Узел берём из базы, а не из запроса клиента."""
    node = await session.scalar(
        select(OrgNode).join(AppUser, AppUser.node_id == OrgNode.id).where(AppUser.id == user_id)
    )
    if node is None:
        raise AccessDenied
    return scope_path(node)


async def accessible_node_ids(session: AsyncSession, user_id: uuid.UUID) -> list[uuid.UUID]:
    """Все узлы, доступные пользователю."""
    scope = await user_scope_path(session, user_id)
    result = await session.scalars(nodes_in_scope(scope))
    return list(result)


async def assert_can_access(
    session: AsyncSession, user_id: uuid.UUID, node_id: uuid.UUID
) -> None:
    """Бросает AccessDenied, если узел вне поддерева пользователя."""
    scope = await user_scope_path(session, user_id)
    allowed = await session.scalar(nodes_in_scope(scope).where(OrgNode.id == node_id))
    if allowed is None:
        raise AccessDenied
