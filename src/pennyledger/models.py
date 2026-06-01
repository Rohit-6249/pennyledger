from datetime import UTC, date, datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Account(SQLModel, table=True):
    __tablename__ = "accounts"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=80, index=True)
    type: str = Field(default="cash")  # cash | bank | card | wallet
    currency: str = Field(default="INR", max_length=3)
    created_at: datetime = Field(default_factory=_utcnow)


class Category(SQLModel, table=True):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("name", "kind", name="uq_category_name_kind"),)

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=60, index=True)
    kind: str = Field(default="expense")  # expense | income


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="accounts.id", index=True)
    category_id: int | None = Field(default=None, foreign_key="categories.id", index=True)
    type: str = Field(default="expense")  # expense | income
    amount_minor: int  # amount in minor units (paise/cents); always > 0
    note: str = Field(default="")
    occurred_on: date = Field(index=True)
    created_at: datetime = Field(default_factory=_utcnow)


class Budget(SQLModel, table=True):
    __tablename__ = "budgets"
    __table_args__ = (UniqueConstraint("category_id", "month", name="uq_budget_category_month"),)

    id: int | None = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="categories.id", index=True)
    month: str = Field(max_length=7, index=True)  # YYYY-MM
    limit_minor: int
