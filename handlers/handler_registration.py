from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.types import Message
from geopy.geocoders import Nominatim
from datetime import datetime
from database import db
from keyboards import keyboards as kb
from states.states_registration import ClassStateRegestration
from config import values_bot

router_registration = Router()

# Функция для начала процесса регистрации
async def get_menu_registration(message: types.Message, state: FSMContext):
    await message.answer("Выберите свою роль", reply_markup=kb.keyboard_start_registration())
    await state.set_state(state=ClassStateRegestration.role_regestration)

# Функция для продолжения процесса регистрации
# на данном этапе ролучаем роль от пользователя и просим ввести ФИО
@router_registration.message(ClassStateRegestration.role_regestration)
async def set_role_registration(message: types.Message, state:FSMContext):
    await db.set_user_in_db(message.from_user.id, values_bot.USER_ROLE_R[f'{message.text}'])
    await message.answer("Введите свое ФИО",reply_markup=kb.del_keyboard())
    await state.set_state(ClassStateRegestration.name_regestration)

# Функция для продолжения процесса регистрации
# на данном этапе ролучаем ФИО от пользователя и просим ввести дату рождения
@router_registration.message(ClassStateRegestration.name_regestration)
async def set_name_registration(message: types.Message, state:FSMContext):
    await db.upd_data_in_db("user_name",message.text, message.from_user.id)
    await message.answer("Уточните вашу дату рождения (дд.мм.гггг)")
    await state.set_state(ClassStateRegestration.date_regestration)

# Функция для проверки корректности введеной даты рождения от пользователя
def validate_date(date_string):
    try:
        date_obj = datetime.strptime(date_string, '%d.%m.%Y')
        current_date = datetime.now()

        if date_obj < current_date:
            return True, date_obj
        else:
            return False, None
    except ValueError:
        return False, None

# Функция для продолжения процесса регистрации
# на данном этапе ролучаем дату рождения от пользователя и запрашиваем номер телефона
@router_registration.message(ClassStateRegestration.date_regestration)
async def set_date_registration(message: types.Message, state:FSMContext):
    is_valid, date_obj = validate_date(message.text)
    if is_valid:
        await db.upd_data_in_db("user_date",message.text, message.from_user.id)
    else:
        await message.answer("Некорректный формат даты. Введите еще раз")
        await ClassStateRegestration.name_regestration()

    await message.answer("Отлично. Укажите ваш номер телефона (нажмите на кнопку ниже)", reply_markup=kb.keyboard_request_contact())
    await state.set_state(ClassStateRegestration.number_regestration)

# Функция для продолжения процесса регистрации
# на данном этапе ролучаем номер от пользователя и просим указать адрес проживания
@router_registration.message(ClassStateRegestration.number_regestration)
async def set_number_registration(message: types.Message, state:FSMContext):
    await db.upd_data_in_db("user_number",message.contact.phone_number, message.from_user.id)
    await message.answer("Теперь укажите ваш адрес проживания. Введите адрес в формате (город, улица, дом, кв)!")
    await state.set_state(ClassStateRegestration.adr_regestration)

# Функция для завершения процесса регистрации
# на данном этапе ролучаем адрес от пользователя и проверяем адрес на существование
# Далее отпрает уведомление администраторам для подтверждения пользователя
@router_registration.message(ClassStateRegestration.adr_regestration)
async def set_adr_registration(message: types.Message, state:FSMContext):
    await db.upd_data_in_db("user_address",message.text, message.from_user.id)
    await db.upd_data_in_db("user_status", 0, message.from_user.id)
    await message.answer("Ваша заявка проверяется, ожидайте подтверждение администратора", reply_markup=kb.del_keyboard())
    await state.clear()

    list_admins = await db.get_admins()
    for item in list_admins:
        await message.bot.send_message(item[0], text=f"Новая заявка на регистрацию!")