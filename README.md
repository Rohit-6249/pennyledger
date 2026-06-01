# PennyLedger

A small async FastAPI service for personal expense tracking — accounts, categories, transactions,
budgets, and a monthly report. SQLite by default, no infra required.

Money is stored in **minor units** (integer paise/cents) to avoid floating-point rounding.

## Stack

Python 3.12 · FastAPI · SQLModel (async) · SQLite (aiosqlite)
Tooling: uv · ruff · mypy · pytest

## Run

```bash
uv sync
uv run uvicorn pennyledger.main:app --reload
```

Then open <http://localhost:8000/docs> for the interactive API.

## Test

```bash
uv run pytest
uv run ruff check src tests
```

## Endpoints

- `GET  /health`, `GET /`
- `POST /accounts`, `GET /accounts`, `GET /accounts/{id}`
- `POST /categories`, `GET /categories` (filter: `kind`)
- `POST /transactions`, `GET /transactions` (filters: `account_id`, `category_id`, `type`, `month`)
- `GET  /transactions/{id}`, `DELETE /transactions/{id}`
- `POST /budgets`, `GET /budgets` (filter: `month`)
- `GET  /reports/monthly?month=YYYY-MM`

## Domain

- **Account** — where money sits (`cash | bank | card | wallet`).
- **Category** — `expense` or `income`; unique per `(name, kind)`.
- **Transaction** — a single movement: `amount_minor > 0`, a `type`, an optional category, and an
  `occurred_on` date. A transaction's category `kind` must match its `type`.
- **Budget** — a spending `limit_minor` for one category in one `YYYY-MM` month; unique per
  `(category, month)`.
- **Monthly report** — income, expense, net, per-category totals, and budget-vs-actual status.

## Layout

- `src/pennyledger/models.py` — SQLModel ORM tables
- `src/pennyledger/schemas.py` — Pydantic request/response models
- `src/pennyledger/services/` — business logic, one module per resource
- `src/pennyledger/routes/` — HTTP handlers, one module per resource
- `tests/` — async pytest suite on in-memory SQLite

To add a new resource: add a model, a schema, a service module, a routes module, and a test module —
same pattern.

## License

MIT
