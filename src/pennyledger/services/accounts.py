from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from pennyledger.models import Account
from pennyledger.schemas import AccountCreate


async def create_account(session: AsyncSession, data: AccountCreate) -> Account:
    account = Account(name=data.name, type=data.type, currency=data.currency)
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return account


async def list_accounts(session: AsyncSession) -> list[Account]:
    result = await session.execute(select(Account).order_by(Account.id))
    return list(result.scalars().all())


async def get_account(session: AsyncSession, account_id: int) -> Account | None:
    return await session.get(Account, account_id)
