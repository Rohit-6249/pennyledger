from httpx import AsyncClient


async def _make_account(client: AsyncClient, name: str = "Wallet") -> int:
    resp = await client.post("/accounts", json={"name": name})
    assert resp.status_code == 201
    return resp.json()["id"]


async def _make_category(client: AsyncClient, name: str, kind: str = "expense") -> int:
    resp = await client.post("/categories", json={"name": name, "kind": kind})
    assert resp.status_code == 201
    return resp.json()["id"]


async def test_health_and_root(client: AsyncClient) -> None:
    assert (await client.get("/health")).json() == {"status": "ok"}
    assert (await client.get("/")).json()["service"] == "PennyLedger"


async def test_create_and_list_transaction(client: AsyncClient) -> None:
    account_id = await _make_account(client)
    category_id = await _make_category(client, "Food")

    resp = await client.post(
        "/transactions",
        json={
            "account_id": account_id,
            "category_id": category_id,
            "type": "expense",
            "amount_minor": 25000,
            "note": "Lunch",
            "occurred_on": "2026-06-01",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["amount_minor"] == 25000
    assert body["type"] == "expense"

    listed = await client.get("/transactions", params={"account_id": account_id})
    assert listed.status_code == 200
    assert len(listed.json()) == 1


async def test_amount_must_be_positive(client: AsyncClient) -> None:
    account_id = await _make_account(client)
    resp = await client.post(
        "/transactions",
        json={"account_id": account_id, "amount_minor": 0, "occurred_on": "2026-06-01"},
    )
    assert resp.status_code == 422


async def test_missing_account_is_404(client: AsyncClient) -> None:
    resp = await client.post(
        "/transactions",
        json={"account_id": 999, "amount_minor": 100, "occurred_on": "2026-06-01"},
    )
    assert resp.status_code == 404


async def test_category_kind_must_match_type(client: AsyncClient) -> None:
    account_id = await _make_account(client)
    income_cat = await _make_category(client, "Salary", kind="income")
    resp = await client.post(
        "/transactions",
        json={
            "account_id": account_id,
            "category_id": income_cat,
            "type": "expense",
            "amount_minor": 100,
            "occurred_on": "2026-06-01",
        },
    )
    assert resp.status_code == 409


async def test_month_filter_and_delete(client: AsyncClient) -> None:
    account_id = await _make_account(client)
    for day, month_amt in [("2026-05-31", 100), ("2026-06-02", 200)]:
        await client.post(
            "/transactions",
            json={"account_id": account_id, "amount_minor": month_amt, "occurred_on": day},
        )

    june = await client.get("/transactions", params={"month": "2026-06"})
    assert [t["amount_minor"] for t in june.json()] == [200]

    txn_id = june.json()[0]["id"]
    assert (await client.delete(f"/transactions/{txn_id}")).status_code == 204
    assert (await client.get(f"/transactions/{txn_id}")).status_code == 404


async def test_bad_month_filter_is_422(client: AsyncClient) -> None:
    resp = await client.get("/transactions", params={"month": "2026/06"})
    assert resp.status_code == 422
