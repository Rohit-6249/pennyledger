from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from pennyledger import schemas
from pennyledger.db import get_session
from pennyledger.schemas import MONTH_RE
from pennyledger.services import reports as svc

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly", response_model=schemas.MonthlyReport)
async def monthly(
    month: str = Query(description="Month to report on, YYYY-MM"),
    session: AsyncSession = Depends(get_session),
):
    if not MONTH_RE.match(month):
        raise HTTPException(status_code=422, detail="month must be in YYYY-MM format")
    return await svc.monthly_report(session, month)
