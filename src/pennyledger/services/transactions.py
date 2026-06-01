from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from pennyledger.models import Transaction
from pennyledger.schemas import TransactionCreate
from pennyledger.util import month_bounds


async def create_transaction(session: AsyncSession, data: TransactionCreate) -> Transaction:
    txn = Transaction(
        account_id=data.account_id,
        category_id=data.category_id,
        type=data.type,
        amount_minor=data.amount_minor,
        note=data.note,
        occurred_on=data.occurred_on,
    )
    session.add(txn)
    await session.commit()
    await session.refresh(txn)
    return txn


async def list_transactions(
    session: AsyncSession,
    account_id: int | None = None,
    category_id: int | None = None,
    type: str | None = None,
    month: str | None = None,
) -> list[Transaction]:
    stmt = select(Transaction)
    if account_id is not None:
        stmt = stmt.where(Transaction.account_id == account_id)
    if category_id is not None:
        stmt = stmt.where(Transaction.category_id == category_id)
    if type is not None:
        stmt = stmt.where(Transaction.type == type)
    if month is not None:
        start, end = month_bounds(month)
        stmt = stmt.where(Transaction.occurred_on >= start, Transaction.occurred_on < end)
    stmt = stmt.order_by(Transaction.occurred_on.desc(), Transaction.id.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_transaction(session: AsyncSession, txn_id: int) -> Transaction | None:
    return await session.get(Transaction, txn_id)


async def delete_transaction(session: AsyncSession, txn: Transaction) -> None:
    await session.delete(txn)
    await session.commit()
