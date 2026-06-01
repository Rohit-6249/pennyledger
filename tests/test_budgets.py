from httpx import AsyncClient


async def _category(client: AsyncClient, name: str = "Food") -> int:
    return (await client.post("/categories", json={"name": name})).json()["id"]


async def test_create_budget(client: AsyncClient) -> None:
    cat = await _category(client)
    resp = await client.post(
        "/budgets", json={"category_id": cat, "month": "2026-06", "limit_minor": 500000}
    )
    assert resp.status_code == 201
    assert resp.json()["limit_minor"] == 500000


async def test_duplicate_budget_is_conflict(client: AsyncClient) -> None:
    cat = await _category(client)
    payload = {"category_id": cat, "month": "2026-06", "limit_minor": 500000}
    assert (await client.post("/budgets", json=payload)).status_code == 201
    assert (await client.post("/budgets", json=payload)).status_code == 409


async def test_budget_for_missing_category_is_404(client: AsyncClient) -> None:
    resp = await client.post(
        "/budgets", json={"category_id": 999, "month": "2026-06", "limit_minor": 1000}
    )
    assert resp.status_code == 404


async def test_bad_month_is_422(client: AsyncClient) -> None:
    cat = await _category(client)
    resp = await client.post(
        "/budgets", json={"category_id": cat, "month": "June", "limit_minor": 1000}
    )
    assert resp.status_code == 422


async def test_list_budgets_filtered_by_month(client: AsyncClient) -> None:
    cat = await _category(client)
    await client.post("/budgets", json={"category_id": cat, "month": "2026-06", "limit_minor": 1})
    await client.post("/budgets", json={"category_id": cat, "month": "2026-07", "limit_minor": 2})
    june = await client.get("/budgets", params={"month": "2026-06"})
    assert [b["month"] for b in june.json()] == ["2026-06"]
