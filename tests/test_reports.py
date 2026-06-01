from httpx import AsyncClient


async def _seed(client: AsyncClient) -> dict[str, int]:
    account = (await client.post("/accounts", json={"name": "Wallet"})).json()["id"]
    food = (await client.post("/categories", json={"name": "Food"})).json()["id"]
    salary = (
        await client.post("/categories", json={"name": "Salary", "kind": "income"})
    ).json()["id"]

    # June expenses on Food: 300 + 250 = 550; income (Salary): 5000
    txns = [
        {"account_id": account, "category_id": food, "type": "expense",
         "amount_minor": 30000, "occurred_on": "2026-06-03"},
        {"account_id": account, "category_id": food, "type": "expense",
         "amount_minor": 25000, "occurred_on": "2026-06-10"},
        {"account_id": account, "category_id": salary, "type": "income",
         "amount_minor": 500000, "occurred_on": "2026-06-01"},
        # A May expense that must NOT appear in the June report
        {"account_id": account, "category_id": food, "type": "expense",
         "amount_minor": 99999, "occurred_on": "2026-05-30"},
    ]
    for t in txns:
        assert (await client.post("/transactions", json=t)).status_code == 201
    return {"account": account, "food": food, "salary": salary}


async def test_monthly_totals(client: AsyncClient) -> None:
    await _seed(client)
    report = (await client.get("/reports/monthly", params={"month": "2026-06"})).json()
    assert report["income_minor"] == 500000
    assert report["expense_minor"] == 55000
    assert report["net_minor"] == 445000


async def test_budget_status_over_and_under(client: AsyncClient) -> None:
    ids = await _seed(client)
    # Budget of 500 (50000 minor) for Food; spent 55000 -> over by 5000
    await client.post(
        "/budgets", json={"category_id": ids["food"], "month": "2026-06", "limit_minor": 50000}
    )
    report = (await client.get("/reports/monthly", params={"month": "2026-06"})).json()
    assert len(report["budgets"]) == 1
    food_budget = report["budgets"][0]
    assert food_budget["spent_minor"] == 55000
    assert food_budget["remaining_minor"] == -5000
    assert food_budget["over_budget"] is True


async def test_empty_month_is_zeroed(client: AsyncClient) -> None:
    await _seed(client)
    report = (await client.get("/reports/monthly", params={"month": "2026-01"})).json()
    assert report["income_minor"] == 0
    assert report["expense_minor"] == 0
    assert report["by_category"] == []
    assert report["budgets"] == []
