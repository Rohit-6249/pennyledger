from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from pennyledger import schemas
from pennyledger.db import get_session
from pennyledger.schemas import MONTH_RE
from pennyledger.services import budgets as svc
from pennyledger.services import categories as categories_svc

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("", response_model=schemas.BudgetOut, status_code=201)
async def create_budget(
    payload: schemas.BudgetCreate, session: AsyncSession = Depends(get_session)
):
    if await categories_svc.get_category(session, payload.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    budget = await svc.create_budget(session, payload)
    if budget is None:
        raise HTTPException(
            status_code=409, detail="A budget already exists for this category and month"
        )
    return budget


@router.get("", response_model=list[schemas.BudgetOut])
async def list_budgets(
    month: str | None = Query(default=None, description="Filter by month, YYYY-MM"),
    session: AsyncSession = Depends(get_session),
):
    if month is not None and not MONTH_RE.match(month):
        raise HTTPException(status_code=422, detail="month must be in YYYY-MM format")
    return await svc.list_budgets(session, month)
