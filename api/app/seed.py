"""Тестовые данные: один регион, два ТИК, двадцать УИК, тридцать человек.

Команда только для разработки: она стирает содержимое таблиц перед заливкой.
На продакшне не запускается.
"""

import asyncio
import sys
import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_engine, get_sessionmaker
from app.models import AppUser, AuditLog, NodeType, OrgNode, UserRole, UserStatus

REGION_CODE = "77"
REGION_NAME = "Город Москва"
TIK_COUNT = 2
UIK_PER_TIK = 10


def _node(
    type_: NodeType,
    name: str,
    path: str,
    parent: OrgNode | None,
    **fields: object,
) -> OrgNode:
    return OrgNode(
        id=uuid.uuid4(),
        type=type_,
        name=name,
        path=path,
        parent_id=parent.id if parent else None,
        tz="Europe/Moscow",
        **fields,
    )


def build_tree() -> list[OrgNode]:
    """Дерево из ТЗ 4.1: федерация → регион → ТИК → УИК, штабы сбоку."""
    federation = _node(NodeType.federation, "Российская Федерация", "ru", None)
    region = _node(
        NodeType.region, REGION_NAME, f"ru.r{REGION_CODE}", federation, region_code=REGION_CODE
    )
    nodes = [
        federation,
        region,
        _node(NodeType.hq, "Штаб региона", f"{region.path}.hq", region, region_code=REGION_CODE),
    ]

    for tik_number in range(1, TIK_COUNT + 1):
        tik = _node(
            NodeType.tik,
            f"ТИК №{tik_number}",
            f"{region.path}.t{tik_number:03d}",
            region,
            region_code=REGION_CODE,
            tik_number=tik_number,
        )
        nodes.append(tik)
        nodes.append(
            _node(
                NodeType.hq,
                f"Штаб ТИК №{tik_number}",
                f"{tik.path}.hq",
                tik,
                region_code=REGION_CODE,
                tik_number=tik_number,
            )
        )
        first_uik = (tik_number - 1) * UIK_PER_TIK + 1
        for uik_number in range(first_uik, first_uik + UIK_PER_TIK):
            nodes.append(
                _node(
                    NodeType.uik,
                    f"УИК №{uik_number}",
                    f"{tik.path}.u{uik_number:04d}",
                    tik,
                    region_code=REGION_CODE,
                    tik_number=tik_number,
                    uik_number=uik_number,
                )
            )
    return nodes


def build_users(nodes: list[OrgNode]) -> list[AppUser]:
    """По человеку на каждую роль плюс наблюдатель на каждый УИК — всего тридцать."""
    by_path = {node.path: node for node in nodes}
    region_path = f"ru.r{REGION_CODE}"

    plan: list[tuple[UserRole, str, str]] = [
        (UserRole.admin, "ru", "Администратор системы"),
        (UserRole.federal, "ru", "Федеральный штаб"),
        (UserRole.region_head, f"{region_path}.hq", "Руководитель штаба региона"),
        (UserRole.dispatcher, f"{region_path}.hq", "Диспетчер ситуационного центра"),
        (UserRole.lawyer, f"{region_path}.hq", "Юрист штаба"),
        (UserRole.press, f"{region_path}.hq", "Пресс-служба"),
        (UserRole.mobile, f"{region_path}.t001", "Мобильная группа ТИК №1"),
        (UserRole.uik_senior, f"{region_path}.t001.u0001", "Старший по участку УИК №1"),
    ]
    for tik_number in range(1, TIK_COUNT + 1):
        plan.append(
            (
                UserRole.coordinator,
                f"{region_path}.t{tik_number:03d}",
                f"Координатор куста ТИК №{tik_number}",
            )
        )
    for node in nodes:
        if node.type is NodeType.uik:
            plan.append((UserRole.observer, node.path, f"Наблюдатель УИК №{node.uik_number}"))

    return [
        AppUser(
            id=uuid.uuid4(),
            # Диапазон +7900… зарезервирован под тестовые номера, живым людям не принадлежит.
            phone_norm=f"+7900{number:07d}",
            display_name=name,
            role=role,
            node_id=by_path[path].id,
            status=UserStatus.active,
        )
        for number, (role, path, name) in enumerate(plan, start=1)
    ]


async def seed(session: AsyncSession) -> tuple[int, int]:
    await session.execute(delete(AuditLog))
    await session.execute(delete(AppUser))
    await session.execute(delete(OrgNode))

    nodes = build_tree()
    session.add_all(nodes)
    await session.flush()

    users = build_users(nodes)
    session.add_all(users)
    await session.commit()
    return len(nodes), len(users)


async def run() -> tuple[int, int]:
    async with get_sessionmaker()() as session:
        result = await seed(session)
    await get_engine().dispose()
    return result


def main() -> None:
    if get_settings().app_env == "production":
        print("На продакшне seed не запускается: команда стирает данные.", file=sys.stderr)
        raise SystemExit(1)

    nodes, users = asyncio.run(run())
    print(f"Готово: узлов {nodes}, пользователей {users}.")
    print("Пароли не заданы — вход появится на следующем этапе.")


if __name__ == "__main__":
    main()
