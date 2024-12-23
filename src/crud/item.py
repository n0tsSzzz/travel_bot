from sqlalchemy.ext.asyncio import AsyncSession
from schema.item import ItemCreate
from db.models.item import Item
from sqlalchemy import select


async def create_item(
    item: ItemCreate,
    session: AsyncSession,
) -> Item:
    new_item = Item(**item.model_dump())
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)
    return new_item


async def get_items(session: AsyncSession) -> list[Item]:
    result = await session.execute(select(Item))
    items = result.scalars().all() 
    return items