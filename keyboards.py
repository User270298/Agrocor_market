from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from crud import get_regions_for_culture


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
         InlineKeyboardButton(text='💵Спрос и предложения', callback_data='prices')],
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
    # Разбиваем список культур на ряды по 2 кнопки
    keyboard_buttons = [
        [InlineKeyboardButton(text=cultures[i], callback_data=f"culture_{i}"),
         InlineKeyboardButton(text=cultures[i + 1], callback_data=f"culture_{i + 1}")]
        if i + 1 < len(cultures) else [InlineKeyboardButton(text=cultures[i], callback_data=f"culture_{i}")]
        for i in range(0, len(cultures), 2)
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard


def create_regions_keyboard(regions):
    # Создаем массив кнопок по 3 в ряд
    keyboard_buttons = [
        [InlineKeyboardButton(text=regions[i], callback_data=f"region_{i}"),
         InlineKeyboardButton(text=regions[i + 1], callback_data=f"region_{i + 1}"),
         InlineKeyboardButton(text=regions[i + 2], callback_data=f"region_{i + 2}")]
        if i + 2 < len(regions) else
        [InlineKeyboardButton(text=regions[i], callback_data=f"region_{i}"),
         InlineKeyboardButton(text=regions[i + 1], callback_data=f"region_{i + 1}")]
        if i + 1 < len(regions) else
        [InlineKeyboardButton(text=regions[i], callback_data=f"region_{i}")]
        for i in range(0, len(regions), 3)
    ]

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
        ],
        [
            InlineKeyboardButton(
                text='Закрыть (Продано)', callback_data=f'close_{product_id}_{table_name}'
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
    """Создает клавиатуру с кнопками культур по 2 в ряд, используя только доступные культуры."""
    keyboard_buttons = [
        [InlineKeyboardButton(text=cultures[i], callback_data=f"cult_{cultures[i]}"),
         InlineKeyboardButton(text=cultures[i + 1], callback_data=f"cult_{cultures[i + 1]}")]
        if i + 1 < len(cultures) else [InlineKeyboardButton(text=cultures[i], callback_data=f"cult_{cultures[i]}")]
        for i in range(0, len(cultures), 2)
    ]
    keyboard_buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


async def get_region_keyboard(culture: str, table: str = None):
    # Получаем регионы для культуры из базы данных с учетом таблицы
    regions = await get_regions_for_culture(culture, table)

    if not regions:
        # Если регионов нет, возвращаем клавиатуру только с кнопкой возврата
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="keyboard_price")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ])

    # Разбиваем список регионов на строки по 3 элемента
    rows = [regions[i:i + 3] for i in range(0, len(regions), 3)]

    # Создаем массив кнопок с текстом региона
    keyboard_buttons = [
        [InlineKeyboardButton(text=region, callback_data=f"reg_{region}") for region in row]
        for row in rows
    ]

    # Добавляем кнопки навигации
    keyboard_buttons.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="keyboard_price"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def contact_trader():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Связаться с трейдером", url="https://wa.me/+79094213334")],
        [InlineKeyboardButton(text='Перейти в главное меню', callback_data='main_menu')]
    ])
    return keyboard


def subscription_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📋Подписаться', callback_data='approve_subscription')],
        [InlineKeyboardButton(text='Отписаться', callback_data='cancel_subscription')],
        [InlineKeyboardButton(text='Перейти в главное меню', callback_data='main_menu')]
    ])
    return keyboard


def create_vat_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="vat_Yes"),
                InlineKeyboardButton(text="❌ Нет", callback_data="vat_No")
            ]
        ]
    )
    return keyboard


def change_region_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Наиболее актуальные регионы', callback_data='actual')],
            [InlineKeyboardButton(text='Все регионы', callback_data='all_region')],
        ]
    )
    return keyboard


# Кнопка для завершения
def create_finish_button(post_type, post_id):
    """
    Создает кнопку 'Завершить' для каждого поста (покупки или продажи)
    :param post_id: ID записи
    :param post_type: Тип записи ('buy' или 'sell')
    :return: InlineKeyboardMarkup с кнопкой
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Завершить",
            callback_data=f"finish_{post_type}_{post_id}"
        )]]
    )
