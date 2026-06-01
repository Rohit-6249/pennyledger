from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from pennyledger import schemas
from pennyledger.db import get_session
from pennyledger.services import categories as svc

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=schemas.CategoryOut, status_code=201)
async def create_category(
    payload: schemas.CategoryCreate, session: AsyncSession = Depends(get_session)
):
    category = await svc.create_category(session, payload)
    if category is None:
        raise HTTPException(
            status_code=409, detail="Category with this name and kind already exists"
        )
    return category


@router.get("", response_model=list[schemas.CategoryOut])
async def list_categories(
    kind: schemas.CategoryKind | None = None, session: AsyncSession = Depends(get_session)
):
    return await svc.list_categories(session, kind)
