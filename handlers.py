import asyncio
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from keyboards import keyboard_start, keyboard_main_menu, back_keyboard, buy_keyboard, create_culture_keyboard, \
    create_regions_keyboard, admin_keyboard, get_price, get_culture_keyboard, get_region_keyboard, contact_trader, \
    subscription_keyboard, create_vat_keyboard, change_region_keyboard
from crud import add_user, get_users_telegram_ids, add_product_buy, add_product_sell, update_status_product, \
    get_user_id_by_telegram_id, get_user_telegram_id_by_product_id, get_prices_by_culture_and_region_buy, \
    get_prices_by_culture_and_region_sell, subscribe_decision, get_subscribed_users, get_product, get_statistics, \
    get_regions_for_culture, get_available_cultures, get_unique_regions
from config import CULTURES, REGIONS, ADMIN_ID
from datetime import datetime, date
from aiocache import cached

router = Router()


class AddUser(StatesGroup):
    phone = State()
    name = State()


@cached(ttl=5)  # Кэшируем данные на 10 секунд
async def get_cached_statistics():
    return await get_statistics()


async def main_menu():
    total_buy_requests, total_sell_requests, total_users, active_users, subscribed_users = await get_cached_statistics()
    text = f'''Главное меню *AGROCOR Market* 🌾
📊*Заявок в боте на сегодня:*
✅ на покупку: {total_buy_requests}
✅ на продажу: {total_sell_requests}

*Количество пользователей:*
➡️ Зарегистрировано: {total_users + 1}
➡️ Выставляют заявки: {active_users}
➡️ Наблюдают за ценами: {subscribed_users}'''
    return text


@router.message(Command(commands=['start']))
async def start(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    telegram_ids = await get_users_telegram_ids()
    text = await main_menu()
    if telegram_id in telegram_ids:
        await message.answer(text, parse_mode='Markdown',
                             reply_markup=keyboard_main_menu())
    else:
        await message.answer(f'''
{text}

Для работы с ботом, *в частности*: 
Размещение заявок на покупку или продажу, получение информации о ценах и использование других ресурсов просьба поделиться номером своего телефона и пройти короткую регистрацию, нажав соответствующую кнопку меню ниже ️ ️ 

По любым вопросам обращайтесь к администратору бота:
☎️ +79056440180
Рабочее время: с 10:00 до 18:00

Для продолжения предоставьте номер телефона. Нажмите 
"Отправить телефон"👇''', parse_mode="Markdown", reply_markup=keyboard_start())
        await state.set_state(AddUser.phone)


@router.message(AddUser.phone)
async def handle_phone(message: Message, state: FSMContext):
    if message.contact:
        phone_number = message.contact.phone_number  # Номер телефона из объекта Contact
    else:
        phone_number = message.text

    await state.update_data(phone=phone_number)
    await message.answer('Спасибо! Теперь введите свою фамилию, имя и отчество(ФИО):',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddUser.name)


@router.message(AddUser.name)
async def handle_name(message: Message, state: FSMContext):
    user_name = message.text
    await state.update_data(name=user_name)

    telegram_id = message.from_user.id
    user_data = await state.get_data()
    text = await main_menu()
    await add_user(user_data['phone'], user_data['name'], telegram_id)
    await message.answer(f"Спасибо, {user_name}! Вы успешно зарегистрированы.")
    await message.answer(text, parse_mode='Markdown', reply_markup=keyboard_main_menu())
    await state.clear()


# analytics, prices, buy, subscription, instruction, urls

@router.callback_query(F.data == 'instruction')
async def handle_instruction(callback_query: CallbackQuery):
    await callback_query.message.answer('''
По любым вопросам обращайтесь к администратору бота:

☎️ +79056440180

*Рабочее время:* с 10:00 до 18:00''', parse_mode='Markdown', reply_markup=back_keyboard())


@router.callback_query(F.data == 'urls')
async def handle_urls(callback_query: CallbackQuery):
    await callback_query.message.answer('''
🔗 **Ссылки на другие источники**:

📰 **Новости**  
[Перейти в Agrocor News](https://t.me/agrocornews_channel)

🤖 **Бот-ассистент**  
[Перейти Agrocor Assistant Bot](https://t.me/agrocorassistant_bot)

🚢 **Vessel Catcher**  
[Перейти в Vessel Catcher](https://t.me/+AqsaM2xqhS44NDQy)

📬 **Предложения**  
[Открыть предложения Agrocor](https://t.me/+Qo-k-cCWpb9hMGIy)

📝 **Запросы**  
[Перейти к запросам Agrocor](https://t.me/+xFOPd8ApOjVmNmFi)
    ''', parse_mode="Markdown", disable_web_page_preview=True, reply_markup=back_keyboard())


@router.callback_query(F.data == 'main_menu')
async def main_menu_panel(callback_query: CallbackQuery):
    text = await main_menu()
    await callback_query.message.answer(text, parse_mode="Markdown",
                                        reply_markup=keyboard_main_menu())


@router.callback_query(F.data == 'analytics')
async def analytics(callback_query: CallbackQuery):
    await callback_query.message.answer('''
📊Раздел "Аналитика"

Всегда актуальная аналитика рынка с выводами экспертов и профессиональных аналитиков:

👉[ПЕРЕЙТИ К АНАЛИТИКЕ...](https://t.me/agrocornews_channel)
Аналитический обзор: рынок зерновых и масличных культур в России и мире🌏
''', parse_mode="Markdown", reply_markup=back_keyboard(), disable_web_page_preview=True)


@router.callback_query(F.data == 'buy')
async def buy(callback_query: CallbackQuery, state: FSMContext):
    # telegram_id = callback_query.from_user.id
    await callback_query.message.answer('''
🛒 *Раздел "Купить/Продать"*
Создание и управление заявками на покупку или продажу агрокультур.
---
*Создать заявку*  
Создайте новую заявку на покупку или продажу агрокультуры в выбранном регионе.
---
*Мои заявки*  
Просматривайте, редактируйте или удаляйте свои заявки.  
Также вы можете увидеть встречные предложения, которые соответствуют вашим заявкам.
---
️ ️Выберите пункт меню ниже 👇
''', parse_mode="Markdown", disable_web_page_preview=True, reply_markup=buy_keyboard())


@router.callback_query(F.data == 'subscription')
async def subscription(callback_query: CallbackQuery):
    await callback_query.message.answer(
        "🌾 *Хотите быть в курсе поступления новых агрокультур?*\n\n"
        "Подпишитесь на наши уведомления, и вы всегда будете знать о *свежих предложениях* на рынке *купли и продажи* агрокультур!",
        parse_mode="Markdown", reply_markup=subscription_keyboard()
    )


@router.callback_query(F.data == 'approve_subscription')
async def approve_subscription(callback_query: CallbackQuery):
    telegram_id = callback_query.from_user.id
    await subscribe_decision(telegram_id, 'Yes')
    await callback_query.message.answer('Вы оформили подписку!')
    text = await main_menu()
    await callback_query.message.answer(text, parse_mode="Markdown",
                                        reply_markup=keyboard_main_menu())


@router.callback_query(F.data == 'cancel_subscription')
async def approve_subscription(callback_query: CallbackQuery):
    telegram_id = callback_query.from_user.id
    await subscribe_decision(telegram_id, 'No')
    await callback_query.message.answer('Вы отключили подписку!')
    text = await main_menu()
    await callback_query.message.answer(text, parse_mode="Markdown",
                                        reply_markup=keyboard_main_menu())


class AddBuySell(StatesGroup):
    name = State()
    region = State()
    district = State()
    city = State()
    vat_required = State()
    other_quality = State()
    date_at = State()
    price = State()


@router.callback_query(F.data.startswith('key_'))
async def key_buy(callback_query: CallbackQuery, state: FSMContext):
    key = callback_query.data.split('_')[1]
    await state.update_data(action=key)
    if key == 'buyers':
        await callback_query.message.answer('Вы выбрали раздел *Купить*', parse_mode="Markdown", )
        await callback_query.message.answer('Выберите культуру, которую хотите купить:',
                                            reply_markup=create_culture_keyboard(CULTURES))
    elif key == 'sellers':
        await callback_query.message.answer('Вы выбрали раздел *Продать*', parse_mode="Markdown")

        await callback_query.message.answer('Выберите культуру, которую хотите продать:',
                                            reply_markup=create_culture_keyboard(CULTURES))
    await state.set_state(AddBuySell.name)


@router.callback_query(F.data.startswith('culture_'))
async def culture(callback_query: CallbackQuery, state: FSMContext):
    culture_index = int(callback_query.data.split('_')[1])
    culture = CULTURES[culture_index]
    await state.update_data(name=culture)
    data = await state.get_data()
    if data['action'] == 'sellers':
        await callback_query.message.answer(f"Вы выбрали: *{culture}*.\nУкажите область:", parse_mode='Markdown',
                                            reply_markup=create_regions_keyboard(REGIONS))
    else:
        await callback_query.message.answer(f"Вы выбрали: *{culture}*.\nВыберите формат отображения регионов:", parse_mode='Markdown',
                                            reply_markup=change_region_keyboard())

@router.callback_query(F.data.startswith('actual'))
async def actual_region(callback_query: CallbackQuery, state: FSMContext):
    regions = await get_unique_regions()
    await callback_query.message.answer(f"Укажите область:", parse_mode='Markdown',
                                        reply_markup=create_regions_keyboard(regions))

@router.callback_query(F.data.startswith('all_region'))
async def actual_region(callback_query: CallbackQuery, state: FSMContext):
    regions = await get_unique_regions()
    await callback_query.message.answer(f"Укажите область:", parse_mode='Markdown',
                                        reply_markup=create_regions_keyboard(REGIONS))


@router.callback_query(F.data.startswith('region_'))
async def input_region(callback_query: CallbackQuery, state: FSMContext):
    region_index = int(callback_query.data.split('_')[1])
    region = REGIONS[region_index]
    await state.update_data(region=region)
    await callback_query.message.answer("Введите район:")
    await state.set_state(AddBuySell.district)


@router.message(AddBuySell.district)
async def input_district(message: Message, state: FSMContext):
    await state.update_data(district=message.text)
    await message.answer("Введите населенный пункт:")
    await state.set_state(AddBuySell.city)


@router.message(AddBuySell.city)
async def input_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Работаете ли вы с НДС?",
                         reply_markup=create_vat_keyboard())
    await state.set_state(AddBuySell.vat_required)


@router.callback_query(F.data.startswith('vat_'))
async def input_vat(callback_query: CallbackQuery, state: FSMContext):
    vat_choice = callback_query.data.split('_')[1]
    await state.update_data(vat_required=vat_choice)
    await callback_query.message.answer('Введите качественные показатели товара:')
    await state.set_state(AddBuySell.other_quality)


@router.message(AddBuySell.other_quality)
async def other_quality(message: Message, state: FSMContext):
    await state.update_data(other_quality=message.text)
    await message.answer("Введите крайнюю возможную дату поставки (в формате ДД.ММ.ГГГГ)")
    await state.set_state(AddBuySell.date_at)


@router.message(AddBuySell.date_at)
async def input_date_at(message: Message, state: FSMContext):
    try:
        # Преобразуем введенную строку в объект date
        date_at = datetime.strptime(message.text, "%d.%m.%Y").date()

        # Получаем текущую дату
        today = date.today()

        # Проверяем, что введенная дата не раньше сегодняшнего дня
        if date_at < today:
            await message.answer(
                "Дата не может быть раньше сегодняшнего дня. Введите дату заново в формате ЧЧ.ММ.ГГГГ.")
        else:
            # Сохраняем дату в состоянии
            await state.update_data(date_at=date_at)
            user_data = await state.get_data()
            text = "Введите цену с учетом НДС (только число, в Руб/МТ):" if user_data[
                                                                                'vat_required'] == 'Yes' else 'Введите цену без учета НДС(только число, в Руб/МТ):'
            await message.answer(text)
            await state.set_state(AddBuySell.price)

    except ValueError:
        await message.answer("Неверный формат даты. Введите в формате ЧЧ.ММ.ГГГГ.")


@router.message(AddBuySell.price)
async def input_price_buy(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        user_data = await state.get_data()
        user_id = await get_user_id_by_telegram_id(message.from_user.id)

        product_id = await add_product_buy(
            name=user_data['name'],
            region=user_data['region'],
            district=user_data['district'],
            city=user_data['city'],
            date_at=user_data['date_at'],
            price=price,
            vat_required=user_data['vat_required'],
            other_quality=user_data['other_quality'],
            user_id=user_id
        )

        await message.answer("Данные успешно отправлены администратору на проверку! 🎉")
        text = await main_menu()
        await message.answer(text, parse_mode='Markdown', reply_markup=keyboard_main_menu())
        action = 'КУПИТЬ' if user_data['action'] == 'buyers' else "ПРОДАТЬ"

        for admin in ADMIN_ID:
            await message.bot.send_message(
                chat_id=admin,
                text=f'''Новая публикация!🎉

*{action}*
🌾Культура: {user_data['name']}
🌐Область: {user_data['region']}
📍Район: {user_data['district']}
🏘️Населенный пункт: {user_data['city']}
💰НДС: {'Да' if user_data['vat_required'] == 'Yes' else 'Нет'}
📄Качественные показатели: {user_data['other_quality']}
--------------
На дату: {user_data["date_at"].strftime("%d.%m.%Y")}
{'Цена с учетом НДС' if user_data['vat_required'] == 'Yes' else 'Цена без учета НДС'}: {price} Руб/МТ
''',
                parse_mode='Markdown',
                reply_markup=admin_keyboard(product_id, 'ProductBuy')
            )
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите корректную цену (*только число*, в Руб/МТ).", parse_mode="Markdown")


@router.callback_query(F.data.startswith('approved_'))
async def admin_approved(callback_query: CallbackQuery, state: FSMContext):
    product_id = int(callback_query.data.split('_')[1])
    table = callback_query.data.split('_')[2]
    await update_status_product(product_id, 'approved', table)

    user_telegram_id = await get_user_telegram_id_by_product_id(product_id, table)
    if user_telegram_id:
        # Отправляем сообщение пользователю
        await callback_query.bot.send_message(
            chat_id=user_telegram_id,
            text=f"Ваш пост был подтверждён администратором! ✅"
        )

    subscribed_users = await get_subscribed_users()
    product = await get_product(product_id, table)
    if product:
        post_message = (
            f"📢 *Новый пост!*\n\n"
            f"🔎 *Категория:* {'Купля' if table == 'ProductBuy' else 'Продажа'}"
            f"🌾 *Культура:* {product.name}\n"
            f"📍 *Регион:* {product.region}\n"
            f"📍 *Район:* {product.district}\n"
            f"📍 *Населенный пункт:* {product.city}"
            f"📄 *Качественные показатели:* {product.other_quality}\n"
            f"📅 *Дата:* {product.date_at.strftime('%d.%m.%Y')}\n"
            f"💰 *НДС:* {'Да' if product.vat_required == 'Yes' else 'Нет'}\n"
            f"💰 *{'Цена с учетом НДС' if product.vat_required == 'Yes' else 'Цена без учета НДС'}:* {product.price} Руб/МТ"
        )
        for subscriber in subscribed_users:
            if subscriber != user_telegram_id:  # Исключаем владельца поста из рассылки
                await callback_query.bot.send_message(
                    chat_id=subscriber,
                    text=post_message,
                    parse_mode="Markdown"
                )
    await callback_query.answer("Пост подтверждён.")


@router.callback_query(F.data.startswith('cancel_'))
async def admin_approved(callback_query: CallbackQuery, state: FSMContext):
    product_id = int(callback_query.data.split('_')[1])
    table = callback_query.data.split('_')[2]
    await update_status_product(product_id, 'cancel', table)
    user_telegram_id = await get_user_telegram_id_by_product_id(product_id, table)
    if user_telegram_id:
        # Отправляем сообщение пользователю
        await callback_query.bot.send_message(
            chat_id=user_telegram_id,
            text=f"Ваш пост был отклонён администратором. ❌"
        )
    await callback_query.answer("Пост подтверждён.")


@router.callback_query(F.data == 'prices')
async def prices_start(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer('''
🌾 Раздел *"Цены"* 🌾
Вы можете ознакомиться с *актуальными ценами* на покупку и продажу агрокультур в выбранных регионах.

📍 *Доступная информация:*

Цены в *разрезе местонахождения*
*Активные заявки* по вашему запросу
🔎 Все данные обновляются автоматически и доступны прямо в боте.

💡 Используйте этот раздел, чтобы быть в курсе рынка и принимать *выгодные решения!*''', parse_mode='Markdown',
                                        reply_markup=get_price())


class GetProduct(StatesGroup):
    name = State()
    location = State()


@router.callback_query(F.data == 'keyboard_price')
async def get_culture(callback_query: CallbackQuery, state: FSMContext):
    # Получаем доступные культуры из базы
    available_cultures = await get_available_cultures()

    if not available_cultures:
        await callback_query.message.answer("Нет доступных культур для выбора.")
        return

    # Отправляем клавиатуру с культурами
    await callback_query.message.answer(
        'Выберите название культуры:',
        reply_markup=get_culture_keyboard(available_cultures)
    )
    await state.set_state(GetProduct.name)


@router.callback_query(F.data.startswith("cult_"))
async def get_region(callback_query: CallbackQuery, state: FSMContext):
    # Получаем выбранную культуру из callback_data
    culture = callback_query.data.split('_', 1)[1]  # Берем название культуры из callback_data

    # Сохраняем выбранную культуру в состояние
    await state.update_data(culture=culture)

    # Получаем регионы для выбранной культуры
    regions = await get_regions_for_culture(culture)

    if not regions:  # Если нет доступных регионов
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к выбору культуры", callback_data="keyboard_price")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ])
        await callback_query.message.answer(
            f"🚫 Для культуры *{culture}* нет доступных регионов. Выберите другой вариант:",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return  # Прерываем выполнение функции

    # Если регионы есть, формируем клавиатуру с регионами
    region_keyboard = await get_region_keyboard(culture)

    # Спрашиваем у пользователя регион
    await callback_query.message.answer(f"Вы выбрали культуру *{culture}*.\nВыберите регион:",
                                        parse_mode="Markdown",
                                        reply_markup=region_keyboard)

    await state.set_state(GetProduct.location)


@router.callback_query(F.data.startswith("reg_"))
async def show_prices(callback_query: CallbackQuery, state: FSMContext):
    # Получаем регион из callback_data
    region = callback_query.data.split('_')[1]

    # Получаем данные культуры из состояния
    user_data = await state.get_data()
    culture = user_data["culture"]

    # Получаем записи из базы данных с фильтром по культуре и региону
    prices_buy = await get_prices_by_culture_and_region_buy(culture, region)

    if prices_buy:
        message_buy = f"📊 *КУПЛЯ*\n🌾Культура: '{culture}'\n📍Регион: '{region}'\n"
        for price_buy in prices_buy:
            message_buy += (
                f"----------------\n"
                f"*На дату {price_buy.date_at.strftime('%d.%m.%Y')}:*\n"
                f"Цена {"с учетом НДС" if price_buy.vat_required == 'Yes' else 'без учета НДС'}: {price_buy.price} Руб/МТ\n"
                f"Область: {price_buy.region}\n"
                f"Район: {price_buy.district}\n"
                f"Населенный пункт: {price_buy.city}\n"
                f"Работа с НДС: {'Да' if price_buy.vat_required == 'Yes' else 'Нет'}\n"
                f"Качественные показатели: {price_buy.other_quality}\n"
                f"----------------\n\n"
            )

        await callback_query.message.answer(message_buy, parse_mode="Markdown", reply_markup=contact_trader())

    # Аналогично для ПРОДАЖИ
    prices_sell = await get_prices_by_culture_and_region_sell(culture, region)

    if prices_sell:
        message_sell = f"📊 *ПРОДАЖА*\n🌾Культура: '{culture}'\n📍Регион: '{region}'\n"
        for price_sell in prices_sell:
            message_sell += (
                f"----------------\n"
                f"*На дату {price_sell.date_at.strftime('%d.%m.%Y')}:*\n"
                f"Цена {"с учетом НДС" if price_sell.vat_required == 'Yes' else 'без учета НДС'}: {price_sell.price} Руб/МТ\n"
                f"Область: {price_sell.region}\n"
                f"Район: {price_sell.district}\n"
                f"Населенный пункт: {price_sell.city}\n"
                f"Работа с НДС: {'Да' if price_sell.vat_included == 'Yes' else 'Нет'}\n"
                f"Качественные показатели: {price_sell.other_quality}\n"
                f"----------------\n\n"
            )

        await callback_query.message.answer(message_sell, parse_mode="Markdown", reply_markup=contact_trader())
