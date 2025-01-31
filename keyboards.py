from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext


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
        ]
    ])
    return keyboard


def get_culture_keyboard(cultures):
    """Создает клавиатуру с кнопками культур по 2 в ряд."""
    keyboard_buttons = [
        [InlineKeyboardButton(text=cultures[i], callback_data=f"cult_{i}"),
         InlineKeyboardButton(text=cultures[i + 1], callback_data=f"cult_{i + 1}")]
        if i + 1 < len(cultures) else [InlineKeyboardButton(text=cultures[i], callback_data=f"cult_{i}")]
        for i in range(0, len(cultures), 2)
    ]

    # Добавляем кнопку "Назад"
    # keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_buy_keyboard")])

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


def search_price():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🚛 Доставка', callback_data='search_delivery'),
         InlineKeyboardButton(text='🏭 Самовывоз', callback_data='search_pickup')],
    ])
    return keyboard


def keyboard_basis():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🚛 Доставка', callback_data='delivery'),
         InlineKeyboardButton(text='🏭 Самовывоз', callback_data='pickup')],
        [InlineKeyboardButton(text='Перейти в главное меню', callback_data='main_menu')]
    ])
    return keyboard


async def keyboard_delivery(state: FSMContext, basis):
    """Создает клавиатуру с возможностью выбора нескольких пунктов доставки."""
    data = await state.get_data()  # Загружаем данные из состояния
    selected_basis = data.get("selected_basis", [])  # Загружаем ранее выбранные пункты

    keyboard_buttons = [
        [
            InlineKeyboardButton(
                text=f"✅ {basis[i]}" if basis[i] in selected_basis else basis[i],
                callback_data=f"basis_{i}"
            ),
            InlineKeyboardButton(
                text=f"✅ {basis[i + 1]}" if i + 1 < len(basis) and basis[i + 1] in selected_basis else basis[i + 1],
                callback_data=f"basis_{i + 1}"
            ) if i + 1 < len(basis) else None,
            InlineKeyboardButton(
                text=f"✅ {basis[i + 2]}" if i + 2 < len(basis) and basis[i + 2] in selected_basis else basis[i + 2],
                callback_data=f"basis_{i + 2}"
            ) if i + 2 < len(basis) else None
        ]
        for i in range(0, len(basis), 3)
    ]

    # Фильтруем None (чтобы ряды были ровными)
    keyboard_buttons = [list(filter(None, row)) for row in keyboard_buttons]

    # Добавляем кнопки "Далее" и "Назад"
    keyboard_buttons.append([
        InlineKeyboardButton(text="Далее", callback_data="confirm_basis"),
        # InlineKeyboardButton(text="🔙 Назад", callback_data="back_delivery_keyboard")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def get_price():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Просмотр цен', callback_data='keyboard_price')],
        [InlineKeyboardButton(text='🔙Назад', callback_data='main_menu')]
    ])
    return keyboard


# ----------------------------------------------------------------------------
def get_cult_keyboard(cultures):
    """Создает inline-клавиатуру с культурами"""
    keyboard_buttons = [
        [
            InlineKeyboardButton(text=cultures[i], callback_data=f"cu_{i}"),
            InlineKeyboardButton(text=cultures[i + 1], callback_data=f"cu_{i + 1}")
        ] if i + 1 < len(cultures) else [InlineKeyboardButton(text=cultures[i], callback_data=f"cu_{i}")]
        for i in range(0, len(cultures), 2)
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def get_keyboard_basis():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🚛 Доставка', callback_data='type_delivery'),
         InlineKeyboardButton(text='🏭 Самовывоз', callback_data='type_pickup')],
        # [InlineKeyboardButton(text='Перейти в главное меню', callback_data='main_menu')]
    ])
    return keyboard


async def get_keyboard_basis_region(state: FSMContext, basis):
    """Создает клавиатуру с возможностью выбора нескольких пунктов доставки."""
    data = await state.get_data()

    # Ensure 'selected_basis' key exists, otherwise default to an empty list
    selected_basis = data.get("selected_basis", [])

    keyboard_buttons = [
        [
            InlineKeyboardButton(
                text=f"✅ {basis[i]}" if basis[i] in selected_basis else basis[i],
                callback_data=f"sis_{i}"
            ),
            InlineKeyboardButton(
                text=f"✅ {basis[i + 1]}" if i + 1 < len(basis) and basis[i + 1] in selected_basis else basis[i + 1],
                callback_data=f"sis_{i + 1}"
            ) if i + 1 < len(basis) else None,
            InlineKeyboardButton(
                text=f"✅ {basis[i + 2]}" if i + 2 < len(basis) and basis[i + 2] in selected_basis else basis[i + 2],
                callback_data=f"sis_{i + 2}"
            ) if i + 2 < len(basis) else None
        ]
        for i in range(0, len(basis), 3)
    ]

    # Remove None values to maintain structure
    keyboard_buttons = [list(filter(None, row)) for row in keyboard_buttons]

    # Add confirmation button
    keyboard_buttons.append([
        InlineKeyboardButton(text="Подтвердить", callback_data="conf_basis")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

def get_regions_keyboard(regions):
    # Создаем массив кнопок по 3 в ряд
    keyboard_buttons = [
        [InlineKeyboardButton(text=regions[i], callback_data=f"gion_{i}"),
         InlineKeyboardButton(text=regions[i + 1], callback_data=f"gion_{i + 1}"),
         InlineKeyboardButton(text=regions[i + 2], callback_data=f"gion_{i + 2}")]
        if i + 2 < len(regions) else
        [InlineKeyboardButton(text=regions[i], callback_data=f"gion_{i}"),
         InlineKeyboardButton(text=regions[i + 1], callback_data=f"gion_{i + 1}")]
        if i + 1 < len(regions) else
        [InlineKeyboardButton(text=regions[i], callback_data=f"gion_{i}")]
        for i in range(0, len(regions), 3)
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard