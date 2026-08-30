"""Справочные перечисления. Значения совпадают с кодами из ТЗ."""

from enum import StrEnum


class NodeType(StrEnum):
    """Тип узла дерева мест (ТЗ 4.1)."""

    federation = "federation"
    region = "region"
    hq = "hq"
    tik = "tik"
    uik = "uik"


class UserRole(StrEnum):
    """Роли (ТЗ 4.2). Порядок перечисления — снизу вверх по объёму прав."""

    observer = "observer"
    uik_senior = "uik_senior"
    mobile = "mobile"
    coordinator = "coordinator"
    lawyer = "lawyer"
    press = "press"
    dispatcher = "dispatcher"
    region_head = "region_head"
    federal = "federal"
    admin = "admin"


class UserStatus(StrEnum):
    """Жизненный цикл учётной записи (ТЗ 5.4)."""

    created = "created"
    invited = "invited"
    active = "active"
    suspended = "suspended"
    archived = "archived"
