from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from database import db
from keyboards import keyboards as kb
from states.states_registration import ClassStateRegistration
from config import values_bot
from utils.functions import validate_date, check_address_format

router_registration = Router()

# Функция для начала процесса регистрации
async def get_menu_registration(message: types.Message, state: FSMContext):
    await message.answer(text="Выберите свою роль", reply_markup=kb.keyboard_start_registration())
    await state.set_state(ClassStateRegistration.role_registration)

# Функция для продолжения процесса регистрации
# на данном этапе ролучаем роль от пользователя и просим ввести ФИО
@router_registration.message(ClassStateRegistration.role_registration)
async def set_role_registration(message: types.Message, state:FSMContext):
    if message.text.startswith('/'):
        await message.reply("Пожалуйста, введите вашу роль, а не команду.")
        return

    elif message.text not in values_bot.USER_ROLE_R:
        await message.reply("Это не допустимая роль. Пожалуйста, выберите роль из предложенных.")
        return

    await db.set_user_in_db(message.from_user.id, values_bot.USER_ROLE_R[f'{message.text}'])
    await message.answer(text="Введите свое ФИО", reply_markup=kb.del_keyboard())
    await state.set_state(ClassStateRegistration.name_registration)

# Функция для продолжения процесса регистрации
# на данном этапе ролучаем ФИО от пользователя и просим ввести дату рождения
@router_registration.message(ClassStateRegistration.name_registration)
async def set_name_registration(message: types.Message, state:FSMContext):
    if message.text.startswith('/'):
        await message.reply("Пожалуйста, введите ваше имя, а не команду.")
        return

    await db.upd_data_in_db(column_name="user_name",
                            data=message.text,
                            user_id=message.from_user.id)
    await message.answer("Уточните вашу дату рождения (дд.мм.гггг)")
    await state.set_state(ClassStateRegistration.date_registration)

# Функция для продолжения процесса регистрации
# на данном этапе ролучаем дату рождения от пользователя и запрашиваем номер телефона
@router_registration.message(ClassStateRegistration.date_registration)
async def set_date_registration(message: types.Message, state:FSMContext):
    if message.text.startswith('/'):
        await message.reply("Пожалуйста, введите дату, а не команду.")
        return

    is_valid, date_obj = await validate_date(message.text)

    if is_valid:
        await db.upd_data_in_db(column_name="user_date",
                                data=message.text,
                                user_id=message.from_user.id)
    else:
        await message.answer("Некорректный формат даты. Введите еще раз")
        return await state.set_state(ClassStateRegistration.date_registration)

    await message.answer(text="Отлично. Укажите ваш номер телефона (нажмите на кнопку ниже)", reply_markup=kb.keyboard_request_contact())
    await state.set_state(ClassStateRegistration.number_registration)

# Функция для продолжения процесса регистрации
# на данном этапе ролучаем номер от пользователя и просим указать адрес проживания
@router_registration.message(ClassStateRegistration.number_registration)
async def set_number_registration(message: types.Message, state:FSMContext):
    if types.ContentType.CONTACT == message.content_type:
        if message.contact.user_id == message.from_user.id:
            await db.upd_data_in_db(column_name="user_number",
                                    data=message.contact.phone_number,
                                    user_id=message.from_user.id)
            await message.answer("Теперь укажите ваш адрес проживания. "
                                 "Введите адрес в формате (город, улица, дом, кв)!")
            await state.set_state(ClassStateRegistration.adr_registration)
        else:
            await message.reply("Пожалуйста, предоставьте свой собственный номер.")
            return await state.set_state(ClassStateRegistration.date_registration)
    else:
        await message.answer("Предоставьте свой номер. Нажмите на кнопку ниже!")
        return await state.set_state(ClassStateRegistration.date_registration)

# Функция для завершения процесса регистрации
# на данном этапе ролучаем адрес от пользователя и проверяем адрес на существование
# Далее отпрает уведомление администраторам для подтверждения пользователя
@router_registration.message(ClassStateRegistration.adr_registration)
async def set_adr_registration(message: types.Message, state:FSMContext):
    if message.text.startswith('/'):
        await message.reply("Пожалуйста, предоставьте номер, а не команду.")
        return

    address_format = await check_address_format(address=message.text)
    if address_format:
        await db.upd_data_in_db(column_name="user_address",
                                data=message.text,
                                user_id=message.from_user.id)
        await db.upd_data_in_db(column_name="user_status",
                                data=0,
                                user_id=message.from_user.id)
        await message.answer(text="Ваша заявка проверяется, ожидайте подтверждение администратора",
                             reply_markup=kb.del_keyboard())
        await state.clear()

        list_admins = await db.get_admins()
        for item in list_admins:
            await message.bot.send_message(item[0], text=f"Новая заявка на регистрацию!")

    else:
        await message.answer("Вы ввели неккоректный адрес, введите еще раз.")
        return await state.set_state(ClassStateRegistration.adr_registration)
