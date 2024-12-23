from db.storages.postgres import db
import asyncio

async def main():
    f = await db.user_exists(1)
    print(f)
    # await db.add_user(1, 'Marko')

asyncio.run(main())