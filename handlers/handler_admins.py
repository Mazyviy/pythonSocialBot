from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters.callback_data import CallbackData
from database import db
from keyboards import keyboards as kb
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.states_admin import ClassStateStatistics, ClassStateTaskClose
from config import values_bot
from datetime import datetime

router_admin = Router()

class CbDataRegestration(CallbackData, prefix="id1158"):
    action: str
    user_id: str
    user_role: str

# Эта функция предназначена для обработки команды "Заявки на регистрацию" от администратора.
# бот извлекает заявки из базы данных и формирует ответ с информацией о каждой заявке
# и кнопками "Принять" и "Отклонить" для дальнейшей обработки.
@router_admin.message(F.text == "Заявки на регистрацию")
async def a_task_registration(message:types.Message):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist is not None and exist[5] == "admin" and exist[6] == 1:
        results = await db.get_applications_for_registration()
        if results:
            for item in results:
                kb_item = [
                    types.InlineKeyboardButton(text="✅ Принять",callback_data=CbDataRegestration(action='add',
                                                                                                 user_id=str(item[3]),
                                                                                                 user_role=item[1]).pack()),
                    types.InlineKeyboardButton(text="❌ Отклонить",callback_data=CbDataRegestration(action='del',
                                                                                                   user_id=str(item[3]),
                                                                                                   user_role=item[1]).pack())
                ]
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[kb_item])
                await message.answer(text=f"↘️ №: {item[0]}. Роль: {values_bot.USER_ROLE_ICON[item[1]]} {values_bot.USER_ROLE[item[1]]}\n"
                                          f"🎫ФИО: {item[2]} ({item[3]})\n"
                                          f"📞Номер: {item[4]}\n"
                                          f"🌎Адрес: {item[5]}",
                                     reply_markup=keyboard)
        else:
            await message.answer("Заявок на рассмотрение нет")

# Эта функция обрабатывает колбек-запросы, связанные с регистрацией пользователей.
# Если действие - "add" (добавить), то пользователь одобряется, и ему отправляется уведомление.
# Если действие - "del" (удалить), то заявка пользователя отклоняется, и ему также отправляется уведомление.
@router_admin.callback_query(CbDataRegestration.filter())
async def button_press_registration(call: types.CallbackQuery, callback_data: dict):
    action = callback_data.action
    user_id = callback_data.user_id
    user_role = callback_data.user_role

    if action == "add":
        await db.upd_user_status(status=1, user_id=user_id)
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(user_id, text="""Ваша заявка на регистрацию одобрена\nНажмите чтобы открыть меню <a>/menu</a>""")
    elif action == "del":
        await db.del_user(user_id)
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(user_id, text="Ваша заявка не регистрацию отклонена")

# Эта функция обрабатывает сообщения с текстом "Список волонтеров" от администратора,
# проверяет его права доступа и, если они соответствуют,
# формирует список зарегистрированных волонтеров для отправки в ответ.
@router_admin.message(F.text == "Список волонтеров")
async def a_list_v(message:types.Message):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist is not None and exist[5] == "admin" and exist[6] == 1:
        list_users = await db.get_list_users("volunteer",1) #user_id, user_role,user_name, user_number, id
        if list_users:
            array_text = ''
            for item in list_users:
                array_text_item = f"🏃🏻 № {item[4]} - {item[2]} (т. {item[3]})\n"
                if len(array_text) + len(array_text_item) < 4096:
                    array_text += array_text_item
                else:
                    await message.answer(array_text)
                    array_text = ""
            if array_text:
                await message.answer(array_text)
        else:
            await message.answer("Нет зарегестрированных волонтеров")

# Эта функция обрабатывает сообщения с текстом "Список администраторов" от администратора,
# проверяет его права доступа и, если они соответствуют,
# формирует список зарегистрированных администраторов для отправки в ответ.
@router_admin.message(F.text == "Список администраторов")
async def a_list_a(message:types.Message):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist is not None and exist[5] == "admin" and exist[6] == 1:
        list_users = await db.get_list_users(user_role="admin", user_status=1)
        if list_users:
            array_text = ''
            for item in list_users:
                array_text_item = f"👑 № {item[4]} - {item[2]} (т. {item[3]})\n"
                if len(array_text) + len(array_text_item) < 4096:
                    array_text += array_text_item
                else:
                    await message.answer(array_text)
                    array_text = ""
            if array_text:
                await message.answer(array_text)
        else:
            await message.answer("Нет зарегестрированных администраторов")

# Эта функция обрабатывает сообщения от администратора,
# проверяет его права доступа и, если они соответствуют,
# формирует список зарегистрированных заказчиков для отправки в ответ.
@router_admin.message(F.text == "Список клиентов")
async def a_list_c(message:types.Message):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist is not None and exist[5] == "admin" and exist[6] == 1:
        list_users = await db.get_list_users(user_role="client",user_status=1)
        if list_users:
            array_text = ''
            for item in list_users:
                array_text_item = f"🛏️ № {item[4]} - {item[2]} (т. {item[3]})\n"
                if len(array_text) + len(array_text_item) < 4096:
                    array_text += array_text_item
                else:
                    await message.answer(array_text)
                    array_text = ""
            if array_text:
                await message.answer(array_text)
        else:
            await message.answer("Нет зарегестрированных заказчиков")

# Эта функция обрабатывает сообщения с текстом "Список свободных задач" от администратора,
# проверяет его права доступа и, если они соответствуют,
# формирует список свободных задач для отправки в ответ.
@router_admin.message(F.text == "Список свободных задач")
async def a_list_free_task(message:types.Message):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist is not None and exist[5] == "admin" and exist[6] == 1:
        list_tasks = await db.get_list_tasks("create")
        if list_tasks:
            array_text=""
            for item in list_tasks:
                user_adr = await db.get_user_adr(item[3])
                user_name = await db.get_user_name(item[3])
                array_text_item = (f"↘️ №: {str(item[0])}. Задача: {item[1]}\n"
                                   f"📋Подробности: {item[2]}\n"
                                   f"🌍Адрес: {user_adr[0]}\n"
                                   f"⏳Срочность: {values_bot.URGENCY_TASK[item[5]]}\n"
                                   f"🛏️Клиент: {user_name[0]} ({item[3]})\n"
                                   f"Дата создания: {item[6]}\n\n")
                if len(array_text) + len(array_text_item) < 4096:
                    array_text += array_text_item
                else:
                    await message.answer(array_text)
                    array_text = ""
            if array_text:
                await message.answer(array_text)
        else:
            await message.answer("Задач нет")

# Эта функция обрабатывает сообщения с текстом "Список задач в работе" от администратора,
# проверяет его права доступа и, если они соответствуют,
# формирует список задач в работе для отправки в ответ.
@router_admin.message(F.text == "Список задач в работе")
async def a_worked_task(message:types.Message):
   exist = await db.get_user_existence_in_db(message.from_user.id)
   if exist is not None and exist[5] == "admin" and exist[6] == 1:
        list_tasks = await db.get_list_tasks("work")
        if list_tasks:
            array_text = ""
            for item in list_tasks:
                user_adr = await db.get_user_adr(item[3])
                user_name_c = await db.get_user_name(item[3])
                user_name_v = await db.get_user_name(item[4])
                array_text_item =(f"↘️ №: {str(item[0])}. Задача: {item[1]}\n"
                                  f"📋Подробности: {item[2]}\n"
                                  f"🌍Адрес: {user_adr[0]}\n"
                                  f"⏳Срочность: {values_bot.URGENCY_TASK[item[5]]}\n"
                                  f"🛏️Клиент: {user_name_c[0]} ({item[3]})\n"
                                  f"🏃Выполняет: {user_name_v[0]} ({item[4]})\n"
                                  f"Дата создания: {item[6]}\n"
                                  f"Взята в работу: {item[7]}\n\n")
                if len(array_text) + len(array_text_item) < 4096:
                    array_text += array_text_item
                else:
                    await message.answer(array_text)
                    array_text = ""
            if array_text:
                await message.answer(array_text)
        else:
            await message.answer("Задач нет")

# Эта функция обрабатывает сообщения с текстом "Список выполненных задач" от администратора,
# проверяет его права доступа и, если они соответствуют,
# формирует список выполненных задач для отправки в ответ.
@router_admin.message(F.text == "Список выполненных задач")
async def a_completed_task(message:types.Message, state: FSMContext):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist is not None and exist[5] == "admin" and exist[6] == 1:
        await state.set_state(state=ClassStateTaskClose.submenu)
        await message.answer(text='выберите диапазон', reply_markup=kb.keyboard_submenu_statistics_a())

@router_admin.message(F.text.in_({'за все время', 'за год', 'за месяц', 'за день'}), ClassStateTaskClose.submenu)
async def a_completed_task_date(message:types.Message, state: FSMContext):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist is not None and exist[5] == "admin" and exist[6] == 1:
        list_tasks = await db.get_list_tasks(state_task="close", date_value= message.text)
        if list_tasks:
            array_text = ""
            for item in list_tasks:
                user_adr = await db.get_user_adr(item[3])
                user_name_c = await db.get_user_name(item[3])
                user_name_v = await db.get_user_name(item[4])
                array_text_item = (f"↘️ №: {str(item[0])}. Задача: {item[1]}\n"
                                   f"📋Подробности: {item[2]}\n"
                                   f"🌍Адрес: {user_adr[0]}\n"
                                   f"⏳Срочность: {values_bot.URGENCY_TASK[item[5]]}\n"
                                   f"🛏️Клиент: {user_name_c[0]} ({item[3]})\n"
                                   f"🏃Выполнил: {user_name_v[0]} ({item[4]})\n"
                                   f"Дата создания: {item[6]}\n"
                                   f"Взята в работу: {item[7]}\n"
                                   f"Закрыта: {item[8]}\n\n")
                if len(array_text) + len(array_text_item) < 4096:
                    array_text += array_text_item
                else:
                    await message.answer(array_text)
                    array_text = ""
            if array_text:
                await message.answer(array_text)
        else:
            await message.answer("Задач нет")

# Эта функция обрабатывает сообщения с текстом "Общая статистика" от администратора,
# проверяет его права доступа и, если они соответствуют,
# отправляет ему подменю.
@router_admin.message(F.text == "Общая статистика")
async def a_total_statistics(message:types.Message, state: FSMContext):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist is not None and exist[5] == "admin" and exist[6] == 1:
        await state.set_state(state=ClassStateStatistics.submenu)
        await message.answer(text='выберите диапазон', reply_markup=kb.keyboard_submenu_statistics_a())

# Эта функция обрабатывает сообщения от администратора,
# проверяет его права доступа и, если они соответствуют,
# формирует общую статистику для отправки в ответ.
@router_admin.message(F.text.in_({'за все время', 'за год', 'за месяц', 'за день'}), ClassStateStatistics.submenu)
async def a_statistics(message:types.Message, state: FSMContext):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist is not None and exist[5] == "admin" and exist[6] == 1:
        count_v = []
        count_b = []
        count_a = []
        count_close_task = []
        cur=''

        if message.text == 'за все время':
            count_v = await db.get_count_data(db_name="users",
                                              column_name="user_role",
                                              column_value="волонтер")
            count_b = await db.get_count_data(db_name="users",
                                              column_name="user_role",
                                              column_value="заказчик")
            count_a = await db.get_count_data(db_name="users",
                                              column_name="user_role",
                                              column_value="администратор")
            count_close_task = await db.get_count_data(db_name="tasks",
                                                       column_name="state_task",
                                                       column_value="close")
            cur = message.text
            return await message.answer(f"<b>за {cur}</b>\n"
                                 f"Кол-во волонтеров: {count_v[0]}\n"
                                 f"Кол-во заказчиков: {count_b[0]}\n"
                                 f"Кол-во администраторов: {count_a[0]}\n"
                                 f"Кол-во закрытых задач: {count_close_task[0]}\n")

        elif message.text == 'за год':
            count_v = await db.get_count_data(db_name="users",
                                              column_name="user_role",
                                              column_value="волонтер",
                                              column_date='date_addition',
                                              date_value='year')
            count_b = await db.get_count_data(db_name="users",
                                              column_name="user_role",
                                              column_value="заказчик",
                                              column_date='date_addition',
                                              date_value='year')
            count_a = await db.get_count_data(db_name="users",
                                              column_name="user_role",
                                              column_value="администратор",
                                              column_date='date_addition',
                                              date_value='year')
            count_close_task = await db.get_count_data(db_name="tasks",
                                                       column_name="state_task",
                                                       column_value="close",
                                                       column_date='date_task_create',
                                                       date_value='year')
            cur = datetime.now().year
            return await message.answer(f"<b>за {cur}</b>\n"
                                 f"Кол-во волонтеров: {count_v[0]} (+{count_v[0] - count_v[1]})\n"
                                 f"Кол-во заказчиков: {count_b[0]} ({'{:+d}'.format(count_v[0] - count_v[1])})\n"
                                 f"Кол-во администраторов: {count_a[0]} ({'{:+d}'.format(count_a[0] - count_a[1])})\n"
                                 f"Кол-во закрытых задач: {count_close_task[0]} ({'{:+d}'.format(count_close_task[0] - count_close_task[1])})\n")

        elif message.text == 'за месяц':
            count_v = await db.get_count_data(db_name="users",
                                              column_name="user_role",
                                              column_value="волонтер",
                                              column_date='date_addition',
                                              date_value='month')
            count_b = await db.get_count_data(db_name="users",
                                              column_name="user_role",
                                              column_value="заказчик",
                                              column_date='date_addition',
                                              date_value='month')
            count_a = await db.get_count_data(db_name="users",
                                              column_name="user_role",
                                              column_value="администратор",
                                              column_date='date_addition',
                                              date_value='month')
            count_close_task = await db.get_count_data(db_name="tasks",
                                                       column_name="state_task",
                                                       column_value="close",
                                                       column_date='date_task_create',
                                                       date_value='month')
            current_date = datetime.now()
            cur = current_date.strftime('%B')

            return await message.answer(f"<b>за {cur}</b>\n"
                                 f"Кол-во волонтеров: {count_v[0]} (+{count_v[0] - count_v[1]})\n"
                                 f"Кол-во заказчиков: {count_b[0]} ({'{:+d}'.format(count_v[0] - count_v[1])})\n"
                                 f"Кол-во администраторов: {count_a[0]} ({'{:+d}'.format(count_a[0] - count_a[1])})\n"
                                 f"Кол-во закрытых задач: {count_close_task[0]} ({'{:+d}'.format(count_close_task[0] - count_close_task[1])})\n")

        elif message.text == 'за день':
            count_v = await db.get_count_data(db_name="users",
                                              column_name="user_role",
                                              column_value="волонтер",
                                              column_date='date_addition',
                                              date_value='day')
            count_b = await db.get_count_data(db_name="users",
                                              column_name="user_role",
                                              column_value="заказчик",
                                              column_date='date_addition',
                                              date_value='day')
            count_a = await db.get_count_data(db_name="users",
                                              column_name="user_role",
                                              column_value="администратор",
                                              column_date='date_addition',
                                              date_value='day')
            count_close_task = await db.get_count_data(db_name="tasks",
                                                       column_name="state_task",
                                                       column_value="close",
                                                       column_date='date_task_create',
                                                       date_value='day')
            cur = "сегодня"
            return await message.answer(f"<b>за {cur}</b>\n"
                                 f"Кол-во волонтеров: {count_v[0]} (+{count_v[0] - count_v[1]})\n"
                                 f"Кол-во заказчиков: {count_b[0]} ({'{:+d}'.format(count_v[0] - count_v[1])})\n"
                                 f"Кол-во администраторов: {count_a[0]} ({'{:+d}'.format(count_a[0] - count_a[1])})\n"
                                 f"Кол-во закрытых задач: {count_close_task[0]} ({'{:+d}'.format(count_close_task[0] - count_close_task[1])})\n")

@router_admin.message(F.text == 'главное меню')
async def a_main_menu(message:types.Message, state: FSMContext):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist is not None and exist[5] == "admin" and exist[6] == 1:
        await message.answer("Выберите пункт меню", reply_markup=kb.keyboard_menu_a())
        await state.clear()