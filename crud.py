import asyncio
from database import engine, Base, async_session
from models import Users, ProductBuy, ProductSell
from sqlalchemy.future import select
import logging
from sqlalchemy import update, union
from sqlalchemy.sql import func
from sqlalchemy import distinct

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


async def add_product_buy(user_id: int, name: str, location: str, date_at: str, price: int) -> int:
    async with async_session() as session:
        new_product = ProductBuy(
            name=name,
            location=location,
            date_at=date_at,
            price=price,
            status='pending',
            user_id=user_id
        )
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)
        return new_product.id


async def add_product_sell(user_id: int, name: str, location: str, date_at: str, price: int) -> int:
    async with async_session() as session:
        new_product = ProductSell(
            name=name,
            location=location,
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


async def get_regions_for_culture(culture: str):
    async with async_session() as session:
        # Запрос на получение регионов для выбранной культуры из таблиц ProductBuy и ProductSell с фильтром по статусу "approved"

        # Для ProductBuy
        buy_query = select(ProductBuy.location).where(
            ProductBuy.name == culture,  # Название культуры
            ProductBuy.status == 'approved'  # Статус должен быть "approved"
        )

        # Для ProductSell
        sell_query = select(ProductSell.location).where(
            ProductSell.name == culture,  # Название культуры
            ProductSell.status == 'approved'  # Статус должен быть "approved"
        )

        # Выполним оба запроса и объединяем их
        result = await session.execute(
            buy_query.union(sell_query)
        )

        # Извлекаем и возвращаем список регионов
        regions = result.scalars().all()
    return regions

async def get_available_cultures():
    """Получает уникальные культуры из таблиц ProductBuy и ProductSell"""
    async with async_session() as session:
        # Получаем уникальные культуры из обеих таблиц
        result = await session.execute(
            select(distinct(ProductBuy.name)).where(ProductBuy.status == "approved")
        )
        cultures_buy = result.scalars().all()

        result = await session.execute(
            select(distinct(ProductSell.name)).where(ProductSell.status == "approved")
        )
        cultures_sell = result.scalars().all()

        # Объединяем списки и убираем дубликаты
        unique_cultures = list(set(cultures_buy + cultures_sell))

    return unique_cultures