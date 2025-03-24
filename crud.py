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


async def add_product_buy(user_id: int, name: str, region: str, district: str, city: str,
                          date_at: str, price: int, vat_required: str, other_quality: str) -> int:
    async with async_session() as session:
        new_product = ProductBuy(
            name=name,
            region=region,
            district=district,
            city=city,
            date_at=date_at,
            price=price,
            status='pending',
            vat_required=vat_required,
            other_quality=other_quality,
            user_id=user_id
        )
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)
        return new_product.id


async def add_product_sell(user_id: int, name: str, region: str, district: str, city: str,
                           date_at: str, price: int, vat_included: str, other_quality: str) -> int:
    async with async_session() as session:
        new_product = ProductSell(
            name=name,
            region=region,
            district=district,
            city=city,
            date_at=date_at,
            price=price,
            status='pending',
            vat_included=vat_included,
            other_quality=other_quality,
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


async def update_status_product(id: int, status: str, table):
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
            .where(ProductBuy.region == region)
            .where(ProductBuy.status == "approved")
        )
        return result.scalars().all()


async def get_prices_by_culture_and_region_sell(culture: str, region: str):
    async with async_session() as session:
        # Фильтруем записи с нужной культурой, регионом и статусом 'approved'
        result = await session.execute(
            select(ProductSell)
            .where(ProductSell.name == culture)
            .where(ProductSell.region == region)
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
        query = select(func.count(Users.id))
        # Выполняем запрос
        result = await session.execute(query)
        # Извлекаем результат (количество строк)
        total_users = result.scalar()

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


async def get_regions_for_culture(culture: str, table: str = None):
    """Получает регионы для выбранной культуры из указанной таблицы или обеих таблиц"""
    async with async_session() as session:
        if table == 'ProductBuy':
            result = await session.execute(
                select(distinct(ProductBuy.region)).where(
                    ProductBuy.name == culture,
                    ProductBuy.status == 'approved'
                )
            )
            return result.scalars().all()
        elif table == 'ProductSell':
            result = await session.execute(
                select(distinct(ProductSell.region)).where(
                    ProductSell.name == culture,
                    ProductSell.status == 'approved'
                )
            )
            return result.scalars().all()
        else:
            # Если таблица не указана, получаем из обеих таблиц
            buy_query = select(ProductBuy.region).where(
                ProductBuy.name == culture,
                ProductBuy.status == 'approved'
            )

            sell_query = select(ProductSell.region).where(
                ProductSell.name == culture,
                ProductSell.status == 'approved'
            )

            result = await session.execute(
                buy_query.union(sell_query)
            )

            return result.scalars().all()


async def get_available_cultures(table: str = None):
    """Получает уникальные культуры из указанной таблицы или обеих таблиц"""
    async with async_session() as session:
        if table == 'ProductBuy':
            result = await session.execute(
                select(distinct(ProductBuy.name)).where(ProductBuy.status == "approved")
            )
            return result.scalars().all()
        elif table == 'ProductSell':
            result = await session.execute(
                select(distinct(ProductSell.name)).where(ProductSell.status == "approved")
            )
            return result.scalars().all()
        else:
            # Если таблица не указана, получаем из обеих таблиц
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


async def get_cities_by_district(district: str):
    """Получает список населенных пунктов в указанном районе"""
    async with async_session() as session:
        # Поиск в таблице покупок
        buy_query = select(distinct(ProductBuy.city)).where(
            ProductBuy.district == district,
            ProductBuy.status == 'approved'
        )

        # Поиск в таблице продаж
        sell_query = select(distinct(ProductSell.city)).where(
            ProductSell.district == district,
            ProductSell.status == 'approved'
        )

        # Объединяем результаты
        result = await session.execute(
            buy_query.union(sell_query)
        )

        return result.scalars().all()


async def get_districts_by_region(region: str):
    """Получает список районов в указанной области"""
    async with async_session() as session:
        # Поиск в таблице покупок
        buy_query = select(distinct(ProductBuy.district)).where(
            ProductBuy.region == region,
            ProductBuy.status == 'approved'
        )

        # Поиск в таблице продаж
        sell_query = select(distinct(ProductSell.district)).where(
            ProductSell.region == region,
            ProductSell.status == 'approved'
        )

        # Объединяем результаты
        result = await session.execute(
            buy_query.union(sell_query)
        )

        return result.scalars().all()


async def get_unique_regions():
    """Получает уникальные регионы из таблиц ProductBuy и ProductSell."""
    async with async_session() as session:
        # Подсчет количества записей для каждого региона в таблице ProductBuy
        buy_query = (
            select(ProductBuy.region, func.count(ProductBuy.id).label('count'))
            .where(ProductBuy.status == 'approved')  # Фильтр по статусу "approved"
            .group_by(ProductBuy.region)
        )

        # Подсчет количества записей для каждого региона в таблице ProductSell
        sell_query = (
            select(ProductSell.region, func.count(ProductSell.id).label('count'))
            .where(ProductSell.status == 'approved')  # Фильтр по статусу "approved"
            .group_by(ProductSell.region)
        )

        # Объединяем результаты двух запросов
        union_query = buy_query.union_all(sell_query).subquery()

        # Группируем по регионам и суммируем количество записей
        final_query = (
            select(union_query.c.region, func.sum(union_query.c.count).label('total_count'))
            .group_by(union_query.c.region)
            .order_by(func.sum(union_query.c.count).desc())  # Сортировка по убыванию популярности
            .limit(10)  # Ограничиваем результат 10 регионами
        )

        # Выполняем запрос
        result = await session.execute(final_query)

        # Извлекаем и возвращаем список регионов
        regions = result.scalars().all()
        return regions


async def get_approved_products():
    async with async_session() as session:
        # Получаем записи из таблицы ProductBuy со статусом "approved"
        product_buy_results = await session.execute(
            select(ProductBuy).where(ProductBuy.status == 'approved')
        )
        product_buy_results = product_buy_results.scalars().all()  # Получаем объекты, а не их ID

        # Получаем записи из таблицы ProductSell со статусом "approved"
        product_sell_results = await session.execute(
            select(ProductSell).where(ProductSell.status == 'approved')
        )
        product_sell_results = product_sell_results.scalars().all()  # Получаем объекты, а не их ID

        # Возвращаем результаты
        return product_buy_results, product_sell_results


async def update_post_status(post_type, post_id, new_status="access"):
    async with async_session() as session:
        if post_type == 'buy':
            # Получаем объект ProductBuy, а не его ID
            product = await session.execute(
                select(ProductBuy).where(ProductBuy.id == post_id)
            )
            product = product.scalars().first()  # Получаем первый объект (или None, если не найдено)
            if product:
                product.status = new_status  # Изменяем статус

        elif post_type == 'sell':
            # Получаем объект ProductSell, а не его ID
            product = await session.execute(
                select(ProductSell).where(ProductSell.id == post_id)
            )
            product = product.scalars().first()  # Получаем первый объект (или None, если не найдено)
            if product:
                product.status = new_status  # Изменяем статус

        # Сохраняем изменения в базе данных
        if product:
            await session.commit()  # Сохраняем изменения, если объект найден и статус обновлен

