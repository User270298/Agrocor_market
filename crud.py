import asyncio
from database import engine, Base, async_session
from models import Users, ProductBuy, ProductSell
from sqlalchemy.future import select
import logging
from sqlalchemy import update
from sqlalchemy.sql import func
from typing import List, Optional

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")


async def add_user(telephon: str, name: str, telegram_id: int, subscribe: str = 'No'):
    async with async_session() as session:
        async with session.begin():
            new_user = Users(telephon=telephon, name=name, telegram_id=telegram_id, subscribe=subscribe)
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


async def add_product_buy(user_id: int, name: str, location: str, date_at: str, basis: str, price: int) -> int:
    async with async_session() as session:
        new_product = ProductBuy(
            name=name,
            location=location,
            basis=basis,
            date_at=date_at,
            price=price,
            status='pending',
            user_id=user_id
        )
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)
        return new_product.id


async def add_product_sell(user_id: int, name: str, location: str, date_at: str, basis: str, price: int) -> int:
    async with async_session() as session:
        new_product = ProductSell(
            name=name,
            location=location,
            basis=basis,
            date_at=date_at,
            price=price,
            status='pending',
            user_id=user_id
        )
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)
        return new_product.id


async def get_product(product_id: int, table: str):
    async with async_session() as session:
        model = ProductBuy if table == 'ProductBuy' else ProductSell
        result = await session.execute(select(model).where(model.id == product_id))
        product = result.scalar_one_or_none()
        return product


async def update_status_product(id: int, status: str, table: Base):
    async with async_session() as session:
        model = ProductBuy if table == 'ProductBuy' else ProductSell
        update_status = update(model).where(model.id == id).values(status=status)
        await session.execute(update_status)
        await session.commit()




async def subscribe_decision(telegram_id: int, decision: str):
    async with async_session() as session:
        stmt = update(Users).where(Users.telegram_id == telegram_id).values(subscribe=decision)
        await session.execute(stmt)
        await session.commit()


async def get_subscribed_users():
    async with async_session() as session:
        result = await session.execute(
            select(Users.telegram_id).where(Users.subscribe == 'Yes')
        )
        return [row[0] for row in result.all()]


async def get_statistics():
    async with async_session() as session:
        # Подсчитываем общее количество пользователей
        query = select(func.count()).select_from(Users)
        result = await session.execute(query)
        total_users = result.scalar_one_or_none()

        # Подсчитываем количество заявок на покупку со статусом "approved"
        total_buy_requests_query = select(func.count(ProductBuy.id)).where(ProductBuy.status == "approved")
        total_buy_requests = (await session.execute(total_buy_requests_query)).scalar()

        # Подсчитываем количество заявок на продажу со статусом "approved"
        total_sell_requests_query = select(func.count(ProductSell.id)).where(ProductSell.status == "approved")
        total_sell_requests = (await session.execute(total_sell_requests_query)).scalar()

        # Подсчитываем активных пользователей (тех, кто разместил заявки)
        active_users_query = select(func.count(ProductBuy.user_id.distinct())).where(ProductBuy.status == "approved")
        active_users_buy = (await session.execute(active_users_query)).scalar()

        active_users_sell_query = select(func.count(ProductSell.user_id.distinct())).where(
            ProductSell.status == "approved")
        active_users_sell = (await session.execute(active_users_sell_query)).scalar()

        active_users = active_users_buy + active_users_sell

        # Подсчитываем подписанных пользователей
        subscribed_users_query = select(func.count(Users.id)).where(Users.subscribe == "Yes")
        subscribed_users = (await session.execute(subscribed_users_query)).scalar()

        return total_users, total_buy_requests, total_sell_requests, active_users, subscribed_users


from sqlalchemy import or_, func

async def get_prices_by_culture_and_region_buy(culture: str, location: str, basis_regions: List[str]):
    async with async_session() as session:
        query = select(ProductBuy).where(
            ProductBuy.name == culture,
            ProductBuy.location == location,
            ProductBuy.status == 'approved',  # ✅ Исправлена ошибка
            or_(
                ProductBuy.basis.is_(None),  # ✅ Для самовывоза (если база NULL)
                *[func.lower(ProductBuy.basis).like(f"%{region.lower()}%") for region in basis_regions]  # ✅ Поиск в строке
            )
        )

        result = await session.execute(query)
        return result.scalars().all()


async def get_prices_by_culture_and_region_sell(culture: str, location: str, basis_regions: List[str]):
    async with async_session() as session:
        query = select(ProductSell).where(
            ProductSell.name == culture,
            ProductSell.location == location,
            ProductSell.status == 'approved',  # ✅ Исправлена ошибка
            or_(
                ProductSell.basis.is_(None),  # ✅ Если база NULL (самовывоз)
                *[func.lower(ProductSell.basis).like(f"%{region.lower()}%") for region in basis_regions]  # ✅ Поиск в строке
            )
        )

        result = await session.execute(query)
        return result.scalars().all()