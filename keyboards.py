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
        [InlineKeyboardButton(text='🔙Назад', callback_data='main_menu'),]
    ])
    return keyboard
