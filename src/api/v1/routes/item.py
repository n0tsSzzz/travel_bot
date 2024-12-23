from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from src.api.v1.routes.router import item_router

from schema.item import ItemCreate, Item
from db.storages.postgres import get_db
from src.crud.item import create_item, get_items


@item_router.post(
    "/create",
    response_model=Item,
)
async def new_item(
    payload: ItemCreate,
    session: AsyncSession = Depends(get_db),
) -> ORJSONResponse:
    print(payload, 0)
    try:
        item = await create_item(payload, session=session)
        print(item, 6)
        return item
        #     content=item,
        #     status_code=status.HTTP_201_CREATED,
        # )
    except Exception as er:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    

@item_router.get("/get")
async def get_item(session: AsyncSession = Depends(get_db)):
    items = await get_items(session)
    return items