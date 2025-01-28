from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def keyboard_start():
    # Создаем кнопку с запросом номера телефона
    button = KeyboardButton(text='Отправить свой номер📞', request_contact=True)

    # Создаем клавиатуру с кнопкой
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button]],  # Кнопки должны быть переданы как список списков
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def keyboard_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📊Аналитика', callback_data='analytics'),
         InlineKeyboardButton(text='💵Цены', callback_data='prices')],
        [InlineKeyboardButton(text='🛒Купить/Продать', callback_data='buy'),
         InlineKeyboardButton(text='📋Подписка', callback_data='subscription')],
        [InlineKeyboardButton(text='⚙️Инструкция', callback_data='instruction'),
         InlineKeyboardButton(text='🔗Ссылки на источники', callback_data='urls')]
    ])
    return keyboard


def back_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔙Назад', callback_data='main_menu'), ]
    ])
    return keyboard


def buy_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Купить', callback_data='key_buyers'),
         InlineKeyboardButton(text='Продать', callback_data='key_sellers')],
        [InlineKeyboardButton(text='🔙Назад', callback_data='main_menu')]
    ])
    return keyboard


def create_culture_keyboard(cultures):
    # Разбиваем список культур на подсписки по 2 элемента
    rows = [cultures[i:i + 2] for i in range(0, len(cultures), 2)]

    # Создаем массив кнопок
    keyboard_buttons = [
        [InlineKeyboardButton(text=culture, callback_data=f"culture_{hash(culture)}") for culture in row]
        for row in rows
    ]
    # keyboard_buttons.append([InlineKeyboardButton(text="🔙Назад", callback_data="back_buy_keyboard")])
    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard


def create_regions_keyboard(regions):
    # Разбиваем список регионов на подсписки по 3 элемента
    rows = [regions[i:i + 3] for i in range(0, len(regions), 3)]

    # Создаем массив кнопок
    keyboard_buttons = [
        [InlineKeyboardButton(text=region, callback_data=f"region_{hash(region)}") for region in row]
        for row in rows
    ]
    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard


def admin_keyboard(product_id: int, table_name: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Подтвердить', callback_data=f'approved_{product_id}_{table_name}'
            ),
            InlineKeyboardButton(
                text='Отклонить', callback_data=f'cancel_{product_id}_{table_name}'
            )
        ]
    ])
    return keyboard


def get_price():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Просмотр цен', callback_data='keyboard_price')],
        [InlineKeyboardButton(text='🔙Назад', callback_data='main_menu')]
    ])
    return keyboard


def get_culture_keyboard(cultures):
    # Разбиваем список культур на подсписки по 2 элемента
    rows = [cultures[i:i + 2] for i in range(0, len(cultures), 2)]

    # Создаем массив кнопок
    keyboard_buttons = [
        [InlineKeyboardButton(text=culture, callback_data=f"cult_{hash(culture)}") for culture in row]
        for row in rows
    ]
    # keyboard_buttons.append([InlineKeyboardButton(text="🔙Назад", callback_data="back_buy_keyboard")])
    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard


def get_region_keyboard(regions):
    # Разбиваем список регионов на строки по 2 элемента
    rows = [regions[i:i + 3] for i in range(0, len(regions), 3)]
    # Создаем массив кнопок
    keyboard_buttons = [
        [InlineKeyboardButton(text=region, callback_data=f"reg_{hash(region)}") for region in row]
        for row in rows
    ]
    # Добавляем кнопку "Назад"
    # keyboard_buttons.append([InlineKeyboardButton(text="🔙Назад", callback_data="back_culture")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard
