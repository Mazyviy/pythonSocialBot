from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from config import values_bot

def keyboard_menu_c()->types.ReplyKeyboardMarkup:
    kb_item_menu_c = [
        [
            types.KeyboardButton(text=values_bot.TASK['products']),
            types.KeyboardButton(text=values_bot.TASK['medicines'])
        ],
        [
            types.KeyboardButton(text=values_bot.TASK['taxi']),
            types.KeyboardButton(text=values_bot.TASK['doctor'])
        ],
        [
            types.KeyboardButton(text="Мои заявки")
        ]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb_item_menu_c, resize_keyboard=True)

def keyboard_menu_v()->types.ReplyKeyboardMarkup:
    kb_item_menu_v = [
        [types.KeyboardButton(text="Принятые заявки")],
        [types.KeyboardButton(text="Свободные заявки")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb_item_menu_v, resize_keyboard=True)

def keyboard_menu_a()->types.ReplyKeyboardMarkup:
    kb_item_menu_a = [
        [
            types.KeyboardButton(text="Общая статистика"),
            types.KeyboardButton(text="Заявки на регистрацию"),
        ],
        [
            types.KeyboardButton(text="Список волонтеров"),
            types.KeyboardButton(text="Список заказчиков"),
        ],
        [
            types.KeyboardButton(text="Список администраторов"),
            types.KeyboardButton(text="Список свободных задач"),
        ],
        [
            types.KeyboardButton(text="Список задач в работе"),
            types.KeyboardButton(text="Список выполненных задач")
        ]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb_item_menu_a, resize_keyboard=True)

def keyboard_submenu_statistics_a()->types.ReplyKeyboardMarkup:
    kb_item_menu = [
        [
            types.KeyboardButton(text="за все время"),
        ],
        [
            types.KeyboardButton(text="за год"),
            types.KeyboardButton(text="за месяц"),
            types.KeyboardButton(text="за день")
        ],
        [
            types.KeyboardButton(text="главное меню"),
        ]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb_item_menu, resize_keyboard=True)

def keyboard_start_registration()->types.ReplyKeyboardMarkup:
    kb_item_start_registration = [
        [types.KeyboardButton(text=values_bot.USER_ROLE['client'])],
        [types.KeyboardButton(text=values_bot.USER_ROLE['volunteer'])],
        [types.KeyboardButton(text=values_bot.USER_ROLE['admin'])]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb_item_start_registration, resize_keyboard=True, one_time_keyboard=True)

def keyboard_request_contact()->types.ReplyKeyboardMarkup:
    kb_item_request_contact = [
        [types.KeyboardButton(text="Предоставить контакт", request_contact=True)]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb_item_request_contact, resize_keyboard=True, one_time_keyboard=True)

def keyboard_request_location()->types.ReplyKeyboardMarkup:
    kb_item_request_location = [
        [types.KeyboardButton(text="Предоставить адрес", request_location=True)],
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb_item_request_location, resize_keyboard=True, one_time_keyboard=True)

def keyboard_urgency_task()->types.ReplyKeyboardMarkup:
    kb_item_urgency_task = [
        [types.KeyboardButton(text=values_bot.URGENCY_TASK['fast'])],
        [types.KeyboardButton(text=values_bot.URGENCY_TASK['medium'])],
        [types.KeyboardButton(text=values_bot.URGENCY_TASK['long'])]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb_item_urgency_task, resize_keyboard=True, one_time_keyboard=True)

def keyboard_cancel()->types.ReplyKeyboardMarkup:
    kb_item = [
        [types.KeyboardButton(text="Отмена")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb_item, resize_keyboard=True, one_time_keyboard=True)

def del_keyboard()->types.ReplyKeyboardRemove:
    return types.ReplyKeyboardRemove()