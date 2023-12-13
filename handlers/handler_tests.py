from aiogram import Router, F, types
from aiogram.types import Message
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from datetime import datetime
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from keyboards import keyboards as kb
from aiogram.filters import Command
from config import values_bot

# Тестовый handler для смены роли через команду /change
router_test = Router()

class CbDataTest(CallbackData, prefix="id55"):
    user_role: str
    user_id: str

@router_test.message(Command('change'))
async def change_role(message: types.Message):
    kb_iteam = [
        types.InlineKeyboardButton(text=values_bot.USER_ROLE['admin'], callback_data=CbDataTest(user_role="admin",
                                                                                                user_id=str(message.from_user.id)).pack()),
        types.InlineKeyboardButton(text=values_bot.USER_ROLE['volunteer'], callback_data=CbDataTest(user_role="volunteer",
                                                                                                    user_id=str(message.from_user.id)).pack()),
        types.InlineKeyboardButton(text=values_bot.USER_ROLE['client'], callback_data=CbDataTest(user_role="client",
                                                                                                 user_id=str(message.from_user.id)).pack())
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[kb_iteam])
    await message.answer(text="Выбери себе роль", reply_markup=keyboard)

@router_test.callback_query(CbDataTest.filter())
async def change_role_t(call: types.CallbackQuery,  callback_data: dict):
    user_role = callback_data.user_role
    user_id = callback_data.user_id
    await db.change_role(user_id, user_role)
    await call.message.answer(text="Роль изменена, нажмите на <b><a>/menu</a></b>", reply_markup=kb.del_keyboard())