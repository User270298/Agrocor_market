import asyncio
from database import engine, Base, async_session
from models import Users, Product
from sqlalchemy.future import select
import logging


async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")


async def add_user(telephon: str, name: str, telegram_id: int):
    async with async_session() as session:
        async with session.begin():
            new_user = Users(telephon=telephon, name=name, telegram_id=telegram_id)
            session.add(new_user)
        print(f'User {new_user.name} added successfully')


async def get_users_telegram_ids():
    async with async_session() as session:
        async with session.begin():
            # Выбираем только поле telegram_id
            result = await session.execute(select(Users.telegram_id))
            telegram_ids = [row[0] for row in result.all()]  # Извлекаем значения из результата
            return telegram_ids


async def search_product(name: str):
    async with async_session() as session:
        result = await session.execute(select(Product).where(Product.name == name))
        products = result.scalars().first()
        return products
