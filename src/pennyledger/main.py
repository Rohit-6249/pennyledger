from contextlib import asynccontextmanager

from fastapi import FastAPI

from pennyledger.db import init_db
from pennyledger.routes import accounts, budgets, categories, reports, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="PennyLedger",
    version="0.1.0",
    description="A small async expense-tracker API: accounts, categories, transactions, "
    "budgets, and monthly reports.",
    lifespan=lifespan,
)

app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(reports.router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {"service": "PennyLedger", "version": "0.1.0", "docs": "/docs"}
