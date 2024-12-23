from fastapi import Depends
from db.storages.postgres import get_db
from config.settings import settings
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.api.v1.routes.router import item_router

router = APIRouter(prefix=settings.API_V1)


@router.get("/test-db")
async def test_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"result": result.scalar()}

router.include_router(item_router, prefix="/items", tags=["items"])
