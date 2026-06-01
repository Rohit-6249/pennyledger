from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from pennyledger.models import Category
from pennyledger.schemas import CategoryCreate


async def create_category(session: AsyncSession, data: CategoryCreate) -> Category | None:
    """Return the new Category, or None if (name, kind) already exists."""
    category = Category(name=data.name, kind=data.kind)
    session.add(category)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return None
    await session.refresh(category)
    return category


async def list_categories(session: AsyncSession, kind: str | None = None) -> list[Category]:
    stmt = select(Category)
    if kind is not None:
        stmt = stmt.where(Category.kind == kind)
    result = await session.execute(stmt.order_by(Category.id))
    return list(result.scalars().all())


async def get_category(session: AsyncSession, category_id: int) -> Category | None:
    return await session.get(Category, category_id)
