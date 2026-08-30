"""Сторожевые тесты инвариантов из CLAUDE.md.

Базы данных не требуют: это проверки самого кода, и падать они должны
даже там, где PostgreSQL не поднята.
"""

from pathlib import Path

APP = Path("app")


def test_проверка_доступа_существует_в_одном_месте() -> None:
    """Инвариант 2: оператор `<@` встречается только в core/access.py."""
    нарушители = [
        str(path)
        for path in APP.rglob("*.py")
        if "<@" in path.read_text(encoding="utf-8") and path.name != "access.py"
    ]

    assert нарушители == [], f"проверка доступа продублирована в {нарушители}"
