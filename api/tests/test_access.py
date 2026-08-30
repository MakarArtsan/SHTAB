"""Проверка доступа. Главный тест проекта: ошибка здесь — это посторонний в штабе."""

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.access import accessible_node_ids, assert_can_access
from app.core.errors import AccessDenied
from app.models import AppUser, OrgNode, UserRole

pytestmark = pytest.mark.usefixtures("tree")


async def _user(session: AsyncSession, role: UserRole, node_path: str) -> AppUser:
    user = await session.scalar(
        select(AppUser)
        .join(OrgNode, OrgNode.id == AppUser.node_id)
        .where(AppUser.role == role, OrgNode.path == node_path)
    )
    assert user is not None, f"в seed нет роли {role} на узле {node_path}"
    return user


async def _node_id(session: AsyncSession, path: str) -> uuid.UUID:
    node_id = await session.scalar(select(OrgNode.id).where(OrgNode.path == path))
    assert node_id is not None, f"в seed нет узла {path}"
    return node_id


async def test_наблюдатель_видит_только_свой_уик(session: AsyncSession) -> None:
    observer = await _user(session, UserRole.observer, "ru.r77.t001.u0001")

    nodes = await accessible_node_ids(session, observer.id)

    assert nodes == [await _node_id(session, "ru.r77.t001.u0001")]


async def test_наблюдатель_не_попадёт_на_соседний_уик(session: AsyncSession) -> None:
    observer = await _user(session, UserRole.observer, "ru.r77.t001.u0001")
    чужой_уик = await _node_id(session, "ru.r77.t001.u0002")

    with pytest.raises(AccessDenied):
        await assert_can_access(session, observer.id, чужой_уик)


async def test_наблюдатель_не_видит_свой_тик(session: AsyncSession) -> None:
    """Видимость идёт только вниз: вверх по ветке — нельзя."""
    observer = await _user(session, UserRole.observer, "ru.r77.t001.u0001")

    with pytest.raises(AccessDenied):
        await assert_can_access(session, observer.id, await _node_id(session, "ru.r77.t001"))


async def test_координатор_видит_весь_свой_куст(session: AsyncSession) -> None:
    coordinator = await _user(session, UserRole.coordinator, "ru.r77.t001")

    nodes = await accessible_node_ids(session, coordinator.id)

    # сам ТИК, штаб ТИК и десять УИК
    assert len(nodes) == 12
    await assert_can_access(session, coordinator.id, await _node_id(session, "ru.r77.t001.u0010"))


async def test_координатор_не_видит_чужой_куст(session: AsyncSession) -> None:
    coordinator = await _user(session, UserRole.coordinator, "ru.r77.t001")
    чужой_уик = await _node_id(session, "ru.r77.t002.u0011")

    with pytest.raises(AccessDenied):
        await assert_can_access(session, coordinator.id, чужой_уик)


async def test_диспетчер_видит_весь_регион(session: AsyncSession) -> None:
    """Диспетчер сидит в штабном узле, а видеть должен регион целиком."""
    dispatcher = await _user(session, UserRole.dispatcher, "ru.r77.hq")

    nodes = await accessible_node_ids(session, dispatcher.id)

    # регион, его штаб, два ТИК со штабами и двадцать УИК
    assert len(nodes) == 26
    for path in ("ru.r77.t001.u0001", "ru.r77.t002.u0020", "ru.r77.t002"):
        await assert_can_access(session, dispatcher.id, await _node_id(session, path))


async def test_диспетчер_не_видит_федерацию(session: AsyncSession) -> None:
    dispatcher = await _user(session, UserRole.dispatcher, "ru.r77.hq")

    with pytest.raises(AccessDenied):
        await assert_can_access(session, dispatcher.id, await _node_id(session, "ru"))


async def test_юрист_и_пресс_служба_видят_регион_как_диспетчер(session: AsyncSession) -> None:
    """Все штабные роли живут в одном узле, поэтому область видимости у них общая."""
    dispatcher = await _user(session, UserRole.dispatcher, "ru.r77.hq")
    ожидаемое = set(await accessible_node_ids(session, dispatcher.id))

    assert len(ожидаемое) == 26
    for role in (UserRole.lawyer, UserRole.press, UserRole.region_head):
        user = await _user(session, role, "ru.r77.hq")
        assert set(await accessible_node_ids(session, user.id)) == ожидаемое


async def test_мобильная_группа_видит_поддерево_своего_тик(session: AsyncSession) -> None:
    """Осознанное расширение: по ТЗ это назначенные УИК, сужение — на этапе инцидентов."""
    mobile = await _user(session, UserRole.mobile, "ru.r77.t001")

    nodes = await accessible_node_ids(session, mobile.id)

    assert len(nodes) == 12


async def test_администратор_видит_всё_дерево(session: AsyncSession) -> None:
    admin = await _user(session, UserRole.admin, "ru")

    nodes = await accessible_node_ids(session, admin.id)
    всего = await session.scalar(select(OrgNode.id).where(OrgNode.path == "ru"))

    assert всего is not None
    assert len(nodes) == 27


async def test_неизвестный_пользователь_не_получает_доступа(session: AsyncSession) -> None:
    with pytest.raises(AccessDenied):
        await assert_can_access(session, uuid.uuid4(), await _node_id(session, "ru"))
