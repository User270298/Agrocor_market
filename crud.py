import asyncio
from database import engine, Base, async_session
from models import Users, ProductBuy, ProductSell
from sqlalchemy.future import select
import logging
from sqlalchemy import update


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


async def get_user_id_by_telegram_id(telegram_id: int) -> int:
    async with async_session() as session:
        result = await session.execute(
            select(Users.id).where(Users.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        return user  # Вернет ID пользователя или None, если пользователь не найден


async def get_user_telegram_id_by_product_id(product_id: int, table: str) -> int:
    async with async_session() as session:
        model = ProductBuy if table == 'ProductBuy' else ProductSell
        result = await session.execute(
            select(model.user_id).where(model.id == product_id)
        )
        user_id = result.scalar_one_or_none()
        if user_id:
            # Получаем telegram_id из таблицы Users
            result = await session.execute(
                select(Users.telegram_id).where(Users.id == user_id)
            )
            return result.scalar_one_or_none()
        return None


async def add_product_buy(user_id: int, name: str, location: str, date_at: str, price_up: int, price_down: int) -> int:
    async with async_session() as session:
        new_product = ProductBuy(
            name=name,
            location=location,
            date_at=date_at,
            price_up=price_up,
            price_down=price_down,
            price_middle=(price_up + price_down) // 2,
            status='pending',
            user_id=user_id
        )
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)
        return new_product.id


async def add_product_sell(user_id: int, name: str, location: str, date_at: str, price_up: int, price_down: int) -> int:
    async with async_session() as session:
        new_product = ProductSell(
            name=name,
            location=location,
            date_at=date_at,
            price_up=price_up,
            price_down=price_down,
            price_middle=(price_up + price_down) // 2,
            status='pending',
            user_id=user_id
        )
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)
        return new_product.id


async def update_status_product(id: int, status: str, table: Base):
    async with async_session() as session:
        model = ProductBuy if table == 'ProductBuy' else ProductSell
        update_status = update(model).where(model.id == id).values(status=status)
        await session.execute(update_status)
        await session.commit()


async def get_prices_by_culture_and_region_buy(culture: str, region: str):
    async with async_session() as session:
        # Фильтруем записи с нужной культурой, регионом и статусом 'approved'
        result = await session.execute(
            select(ProductBuy)
            .where(ProductBuy.name == culture)
            .where(ProductBuy.location == region)
            .where(ProductBuy.status == "approved")
        )
        return result.scalars().all()



async def get_prices_by_culture_and_region_sell(culture: str, region: str):
    async with async_session() as session:
        # Фильтруем записи с нужной культурой, регионом и статусом 'approved'
        result = await session.execute(
            select(ProductSell)
            .where(ProductSell.name == culture)
            .where(ProductSell.location == region)
            .where(ProductSell.status == "approved")
        )
        return result.scalars().all()
