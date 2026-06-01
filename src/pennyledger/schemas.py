import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
AccountType = Literal["cash", "bank", "card", "wallet"]
CategoryKind = Literal["expense", "income"]
TxnType = Literal["expense", "income"]


# --- Accounts ---
class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    type: AccountType = "cash"
    currency: str = Field(default="INR", min_length=3, max_length=3)


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    currency: str
    created_at: datetime


# --- Categories ---
class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    kind: CategoryKind = "expense"


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    kind: str


# --- Transactions ---
class TransactionCreate(BaseModel):
    account_id: int
    category_id: int | None = None
    type: TxnType = "expense"
    amount_minor: int = Field(gt=0, description="Amount in minor units (paise/cents); must be > 0")
    note: str = ""
    occurred_on: date


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    category_id: int | None
    type: str
    amount_minor: int
    note: str
    occurred_on: date
    created_at: datetime


# --- Budgets ---
class BudgetCreate(BaseModel):
    category_id: int
    month: str = Field(description="YYYY-MM")
    limit_minor: int = Field(gt=0)

    @field_validator("month")
    @classmethod
    def _check_month(cls, v: str) -> str:
        if not MONTH_RE.match(v):
            raise ValueError("month must be in YYYY-MM format")
        return v


class BudgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    month: str
    limit_minor: int


# --- Reports ---
class CategoryTotal(BaseModel):
    category_id: int | None
    category_name: str
    total_minor: int


class BudgetStatus(BaseModel):
    category_id: int
    category_name: str
    limit_minor: int
    spent_minor: int
    remaining_minor: int
    over_budget: bool


class MonthlyReport(BaseModel):
    month: str
    income_minor: int
    expense_minor: int
    net_minor: int
    by_category: list[CategoryTotal]
    budgets: list[BudgetStatus]
