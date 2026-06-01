from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from pennyledger.models import Budget, Category, Transaction
from pennyledger.schemas import BudgetStatus, CategoryTotal, MonthlyReport
from pennyledger.util import month_bounds


async def monthly_report(session: AsyncSession, month: str) -> MonthlyReport:
    start, end = month_bounds(month)

    txns = list(
        (
            await session.execute(
                select(Transaction).where(
                    Transaction.occurred_on >= start, Transaction.occurred_on < end
                )
            )
        )
        .scalars()
        .all()
    )
    cats = {
        c.id: c.name for c in (await session.execute(select(Category))).scalars().all()
    }

    income = sum(t.amount_minor for t in txns if t.type == "income")
    expense = sum(t.amount_minor for t in txns if t.type == "expense")

    totals: dict[int | None, int] = {}
    spent_by_cat: dict[int, int] = {}
    for t in txns:
        totals[t.category_id] = totals.get(t.category_id, 0) + t.amount_minor
        if t.type == "expense" and t.category_id is not None:
            spent_by_cat[t.category_id] = spent_by_cat.get(t.category_id, 0) + t.amount_minor

    by_category = [
        CategoryTotal(
            category_id=cid,
            category_name=cats.get(cid, "Uncategorized") if cid is not None else "Uncategorized",
            total_minor=total,
        )
        for cid, total in sorted(totals.items(), key=lambda kv: (kv[0] is None, kv[0] or 0))
    ]

    budgets = list(
        (await session.execute(select(Budget).where(Budget.month == month))).scalars().all()
    )
    budget_status = []
    for b in budgets:
        spent = spent_by_cat.get(b.category_id, 0)
        budget_status.append(
            BudgetStatus(
                category_id=b.category_id,
                category_name=cats.get(b.category_id, "Unknown"),
                limit_minor=b.limit_minor,
                spent_minor=spent,
                remaining_minor=b.limit_minor - spent,
                over_budget=spent > b.limit_minor,
            )
        )

    return MonthlyReport(
        month=month,
        income_minor=income,
        expense_minor=expense,
        net_minor=income - expense,
        by_category=by_category,
        budgets=budget_status,
    )
