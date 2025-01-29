import asyncio
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from keyboards import keyboard_start, keyboard_main_menu, back_keyboard, buy_keyboard, create_culture_keyboard, \
    create_regions_keyboard, admin_keyboard, get_price, get_culture_keyboard, get_region_keyboard, contact_trader, \
    subscription_keyboard
from crud import add_user, get_users_telegram_ids, add_product_buy, add_product_sell, update_status_product, \
    get_user_id_by_telegram_id, get_user_telegram_id_by_product_id, get_prices_by_culture_and_region_buy, \
    get_prices_by_culture_and_region_sell, subscribe_decision, get_subscribed_users, get_product, get_statistics
from config import CULTURES, REGIONS, ADMIN_ID
from datetime import datetime, date
from aiocache import cached

router = Router()


class AddUser(StatesGroup):
    phone = State()
    name = State()


@cached(ttl=600)  # Кэшируем данные на 10 секунд
async def get_cached_statistics():
    return await get_statistics()


async def main_menu():
    total_buy_requests, total_sell_requests, total_users, active_users, subscribed_users = await get_cached_statistics()
    text = f'''Главное меню *AGROCOR Market* 🌾
📊*Заявок в боте на сегодня:*
✅ на покупку: {total_buy_requests}
✅ на продажу: {total_sell_requests}

*Количество пользователей:*
➡️ Зарегистрировано: {total_users}
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


class AddBuy(StatesGroup):
    name = State()
    location = State()
    date_at = State()
    price_up = State()
    price_down = State()


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
    await state.set_state(AddBuy.name)


@router.callback_query(F.data.startswith('culture_'))
async def culture(callback_query: CallbackQuery, state: FSMContext):
    culture_index = int(callback_query.data.split('_')[1])  # Берем индекс
    culture = CULTURES[culture_index]
    await state.update_data(name=culture)
    await callback_query.message.answer(f"Вы выбрали: *{culture}*.\nУкажите ваш регион:", parse_mode='Markdown',
                                        reply_markup=create_regions_keyboard(REGIONS))
    await state.set_state(AddBuy.location)


@router.callback_query(F.data.startswith('region_'))
async def input_location(callback_query: CallbackQuery, state: FSMContext):
    location_index = int(callback_query.data.split('_')[1])  # Берем индекс
    location = REGIONS[location_index]
    await state.update_data(location=location)  # Сохраняем регион
    await callback_query.message.answer("Введите дату (в формате ЧЧ.ММ.ГГГГ)")
    await state.set_state(AddBuy.date_at)


@router.message(AddBuy.date_at)
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
            await message.answer("Введите максимальную цену (в формате Руб/МТ):")
            await state.set_state(AddBuy.price_up)

    except ValueError:
        await message.answer("Неверный формат даты. Введите в формате ЧЧ.ММ.ГГГГ.")


@router.message(AddBuy.price_up)
async def input_price_up(message: Message, state: FSMContext):
    price_up = int(message.text)
    await state.update_data(price_up=price_up)  # Сохраняем максимальную цену
    await message.answer("Введите минимальную цену(в формате Руб/МТ):")
    await state.set_state(AddBuy.price_down)


@router.message(AddBuy.price_down)
async def input_price_down(message: Message, state: FSMContext, bot):
    price_down = int(message.text)
    user_data = await state.get_data()
    await state.update_data(price_down=price_down)
    user_id = await get_user_id_by_telegram_id(message.from_user.id)
    if user_data['action'] == 'buyers':
        product_id = await add_product_buy(name=user_data['name'], location=user_data['location'],
                                           date_at=user_data['date_at'],
                                           price_up=user_data['price_up'],
                                           price_down=price_down,
                                           user_id=user_id, )
    else:
        product_id = await add_product_sell(name=user_data['name'], location=user_data['location'],
                                            date_at=user_data['date_at'],
                                            price_up=user_data['price_up'],
                                            price_down=price_down,
                                            user_id=user_id, )
    await message.answer("Данные успешно отправлены администратору на проверку! 🎉")
    text = await main_menu()
    await message.answer(text, parse_mode='Markdown', reply_markup=keyboard_main_menu())
    for admin in ADMIN_ID:
        publish = '*КУПИТЬ*' if user_data['action'] == 'buyers' else '*ПРОДАТЬ*'
        await message.bot.send_message(chat_id=admin,
                                       text='Новая публикация!🎉\n\n'
                                            f'{publish}\n'
                                            f'🌾Культура: {user_data['name']}\n'
                                            f'🌐Регион: {user_data['location']}\n'
                                            f'--------------\n'
                                            f'На дату {user_data["date_at"].strftime("%d.%m.%Y")}:\n'
                                            f'Минимальная цена {price_down}\n'
                                            f'Максимальная цена {user_data["price_up"]}\n'
                                            f'Средняя цена {round((user_data["price_up"] + price_down) / 2)}',
                                       parse_mode='Markdown',
                                       reply_markup=admin_keyboard(product_id, 'ProductBuy' if user_data[
                                                                                                   'action'] == 'buyers' else 'ProductSell')
                                       )
    await state.clear()


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
            f"📍 *Регион:* {product.location}\n"
            f"📅 *Дата:* {product.date_at.strftime('%d.%m.%Y')}\n"
            f"💰 *Цена:* {product.price_down} Руб/МТ - {product.price_up} Руб/МТ\n "
            f"Средняя {product.price_middle} Руб/МТ"

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
    await callback_query.message.answer('Выберите название культуры:', reply_markup=get_culture_keyboard(CULTURES))
    await state.set_state(GetProduct.name)


@router.callback_query(GetProduct.name)
async def get_region(callback_query: CallbackQuery, state: FSMContext):
    # Сохраняем выбранную культуру
    culture_index = int(callback_query.data.split('_')[1])  # Берем индекс
    culture = CULTURES[culture_index]

    await state.update_data(culture=culture)
    # Спрашиваем у пользователя регион
    await callback_query.message.answer("Выберите регион:", reply_markup=get_region_keyboard(REGIONS))
    await state.set_state(GetProduct.location)


@router.callback_query(F.data.startswith("reg_"))
async def show_prices(callback_query: CallbackQuery, state: FSMContext):
    # Получаем данные из состояния
    location_index = int(callback_query.data.split('_')[1])  # Берем индекс
    region = REGIONS[location_index]

    user_data = await state.get_data()
    culture = user_data["culture"]

    # Получаем записи из базы данных с фильтром по культуре и региону
    prices_buy = await get_prices_by_culture_and_region_buy(culture, region)
    message_buy = f"📊 *КУПЛЯ*\n🌾Культура '{culture}'\n📍Регионе '{region}'\n"
    if prices_buy:
        # Формируем сообщение с ценами
        for price_buy in prices_buy:
            message_buy += (
                f"----------------\n"
                f"*На дату {price_buy.date_at.strftime('%d.%m.%Y')}:*\n"
                f"Цена мин: {price_buy.price_down} Руб/МТ\n"
                f"Цена макс: {price_buy.price_up} Руб/МТ\n"
                f"Цена сер: {price_buy.price_middle} Руб/МТ\n"
                f"----------------\n\n"
            )
    await callback_query.message.answer(message_buy, parse_mode="Markdown", reply_markup=contact_trader())

    prices_sell = await get_prices_by_culture_and_region_sell(culture, region)
    # print(prices_sell)
    message_sell = f"📊 *ПРОДАЖА*\nКультура '{culture}'\nРегионе '{region}'\n"
    if prices_sell:
        # Формируем сообщение с ценами
        for price_sell in prices_sell:
            message_sell += (

                f"*На дату {price_sell.date_at.strftime('%d.%m.%Y')}:*\n"
                f"Цена мин: {price_sell.price_down} Руб/МТ\n"
                f"Цена макс: {price_sell.price_up} Руб/МТ\n"
                f"Цена сер: {price_sell.price_middle} Руб/МТ\n"
                f"----------------\n\n"
            )
    await callback_query.message.answer(message_sell, parse_mode="Markdown", reply_markup=contact_trader())
