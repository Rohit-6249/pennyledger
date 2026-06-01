from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from pennyledger.models import Budget
from pennyledger.schemas import BudgetCreate


async def create_budget(session: AsyncSession, data: BudgetCreate) -> Budget | None:
    """Return the new Budget, or None if one already exists for (category, month)."""
    budget = Budget(category_id=data.category_id, month=data.month, limit_minor=data.limit_minor)
    session.add(budget)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return None
    await session.refresh(budget)
    return budget


async def list_budgets(session: AsyncSession, month: str | None = None) -> list[Budget]:
    stmt = select(Budget)
    if month is not None:
        stmt = stmt.where(Budget.month == month)
    result = await session.execute(stmt.order_by(Budget.id))
    return list(result.scalars().all())
