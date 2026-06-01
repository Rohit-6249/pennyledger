from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from pennyledger import schemas
from pennyledger.db import get_session
from pennyledger.services import accounts as svc

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("", response_model=schemas.AccountOut, status_code=201)
async def create_account(
    payload: schemas.AccountCreate, session: AsyncSession = Depends(get_session)
) -> schemas.AccountOut:
    return await svc.create_account(session, payload)  # type: ignore[return-value]


@router.get("", response_model=list[schemas.AccountOut])
async def list_accounts(session: AsyncSession = Depends(get_session)):
    return await svc.list_accounts(session)


@router.get("/{account_id}", response_model=schemas.AccountOut)
async def get_account(account_id: int, session: AsyncSession = Depends(get_session)):
    account = await svc.get_account(session, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
