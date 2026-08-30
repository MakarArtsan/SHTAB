import httpx
import pytest

from app.main import app


@pytest.mark.asyncio
async def test_health_отвечает_ok() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_неизвестный_путь_отдаёт_единый_формат_ошибки() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/такого-пути-нет")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
