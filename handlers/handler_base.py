from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from database import db
from keyboards import keyboards as kb
from handlers.handler_registration import get_menu_registration

router_base = Router()

# Обработка команды 'start'
# Если пользователь не зарегистрирован, то начинается регистрация
# иначе выдается соответствующее роли меню
@router_base.message(Command('start'))
async def process_start_command(message: types.Message, state: FSMContext):
    bot_info = await message.bot.get_me()
    bot_name = bot_info.first_name
    await message.answer(f"Добро пожаловать {message.from_user.full_name} в <b>{bot_name}</b>! 🤝\n"
                         f"Мы здесь, чтобы помогать вам и вашему сообществу. Начнем! 💪\n"
                         f"ВНИМАНИЕ!!! Этот проект в разработке!!!")
    result = await db.get_user_existence_in_db(message.from_user.id)
    if result is None:
        await get_menu_registration(message, state)
    elif result[6]==0:
        await message.answer(f"Вы уже прошли регистрацию как {result[5]} {result[1]}\n"
                             "Но ваша заявка еще неодобрена!")
    else:
        await get_menu(message)

# Обработка комманды 'menu'
# выдает пользователю соответствующее ему меню
@router_base.message(Command('menu'))
async def get_menu(message: types.Message):
    results=await db.get_user_existence_in_db(user_id=message.from_user.id)
    if results[5] == "client" and results[6]==1:
        await message.answer(text="Выберите пункт меню", reply_markup=kb.keyboard_menu_c())
    elif results[5] == "volunteer" and results[6] == 1:
        await message.answer(text="Выберите пункт меню", reply_markup=kb.keyboard_menu_v())
    elif results[5] == "admin" and results[6] == 1:
        await message.answer(text="Выберите пункт меню", reply_markup=kb.keyboard_menu_a())

# Обработка всех сообщений пользователя, для которых не определен обработчик
# Если пользователь авторизован, ему выдается меню,
# если нет то выводится сообщение и переводит пользователя на регистрацию
@router_base.message()
async def any_message(message:types.Message, state: FSMContext):
    result = await db.get_user_existence_in_db(message.from_user.id)
    if result is None or None in result:
        await message.answer("Вы не зарегистрированы!")
        await get_menu_registration(message, state)
    else:
        if result[6] == 0:
            await message.answer("Ваша заявка еще не одобрена!")
        elif result[6] == 1:
            await get_menu(message)