from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from pennyledger import schemas
from pennyledger.db import get_session
from pennyledger.schemas import MONTH_RE
from pennyledger.services import accounts as accounts_svc
from pennyledger.services import categories as categories_svc
from pennyledger.services import transactions as svc

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=schemas.TransactionOut, status_code=201)
async def create_transaction(
    payload: schemas.TransactionCreate, session: AsyncSession = Depends(get_session)
):
    if await accounts_svc.get_account(session, payload.account_id) is None:
        raise HTTPException(status_code=404, detail="Account not found")
    if payload.category_id is not None:
        category = await categories_svc.get_category(session, payload.category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        if category.kind != payload.type:
            raise HTTPException(
                status_code=409,
                detail=f"Category kind '{category.kind}' does not match transaction type "
                f"'{payload.type}'",
            )
    return await svc.create_transaction(session, payload)


@router.get("", response_model=list[schemas.TransactionOut])
async def list_transactions(
    account_id: int | None = None,
    category_id: int | None = None,
    type: schemas.TxnType | None = None,
    month: str | None = Query(default=None, description="Filter by month, YYYY-MM"),
    session: AsyncSession = Depends(get_session),
):
    if month is not None and not MONTH_RE.match(month):
        raise HTTPException(status_code=422, detail="month must be in YYYY-MM format")
    return await svc.list_transactions(session, account_id, category_id, type, month)


@router.get("/{txn_id}", response_model=schemas.TransactionOut)
async def get_transaction(txn_id: int, session: AsyncSession = Depends(get_session)):
    txn = await svc.get_transaction(session, txn_id)
    if txn is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn


@router.delete("/{txn_id}", status_code=204)
async def delete_transaction(txn_id: int, session: AsyncSession = Depends(get_session)) -> None:
    txn = await svc.get_transaction(session, txn_id)
    if txn is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    await svc.delete_transaction(session, txn)
