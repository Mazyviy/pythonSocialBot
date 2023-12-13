from aiogram import Router, F, types
from aiogram.types import Message
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from keyboards import keyboards as kb
from config import values_bot

router_volunteer = Router()

class CbDataCompletedTask(CallbackData, prefix="id1"):
    answer: str
    id: Optional[int] = None
    user_perform: str

class CbDataWorkTask(CallbackData, prefix="id2"):
    action: str
    task_id: Optional[int] = None
    user_id: str
    task: str

class CbDataFreeTask(CallbackData, prefix="id3"):
    action: str
    task_id: Optional[int] = None
    user_id: str
    user_perform: str
    task: str

# Эта функция обрабатывает сообщения с текстом "Принятые заявки" от волонтера,
# проверяет его права доступа и, если они соответствуют,
# выводит принятые волонтером заявки, в которых он может закрыть заявку или вовсе отказаться от нее
@router_volunteer.message(F.text == "Принятые заявки")
async def v_accepted_tasks(message: types.Message):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist is not None and exist[5] == "volunteer" and exist[6] == 1:
        list_tasks = await db.get_list_accepted_tasks_volunteer(message.from_user.id)
        if list_tasks:
            for item in list_tasks:
                user_adr = await db.get_user_adr(item[3])
                user_name = await db.get_user_name(item[3])
                user_number = await db.get_user_nunmber(item[3])
                kb_item = [
                    types.InlineKeyboardButton(text="Выполнил", callback_data=CbDataWorkTask(action='perform',
                                                                                             task=item[1],
                                                                                             user_id=str(item[3]),
                                                                                             task_id=int(item[0])).pack()),
                    types.InlineKeyboardButton(text="Отказаться", callback_data=CbDataWorkTask(action='refuse',
                                                                                               task=item[1],
                                                                                               user_id=str(item[3]),
                                                                                               task_id=int(item[0])).pack())
                ]
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[kb_item])
                await message.answer(text=f"↘️ № {item[0]}. Задача: {item[1]}\n"
                                     f"📋Подробности: {item[2]}\n"
                                     f"⏳Срочность: {values_bot.URGENCY_TASK[f'{item[4]}']}\n"
                                     f"🌍Адрес: {user_adr[0]}\n"
                                     f"🛏️Заказчик: {user_name[0]} (т. {user_number[0]})\n"
                                     f"Дата создания: {item[5]}\n"
                                     f"Взята в работу: {item[6]}\n",
                                     reply_markup=keyboard)
        else:
            await message.answer("Принятых заявок нет")

# Если волонтер нажимает "Выполнил", то создается инлайн-клавиатура с двумя кнопками "Да" и "Нет",
# и бот отправляет сообщение клиенту с этой клавиатурой, где он должен подтвердить выполнение задачи.
# Если волонтер нажимает "Отказаться", то обновляется состояние задачи в базе данных и клиенту
# отправляется уведомление об отказе от задачи.
@router_volunteer.callback_query(CbDataWorkTask.filter())
async def button_press_work_task(call: types.CallbackQuery, callback_data: dict):
    action = callback_data.action
    task_id = callback_data.task_id
    user_id = callback_data.user_id
    task=await db.get_task_id(task_id)
    if action == "perform":
        state = await db.get_task_state(task_id=task_id)
        if state is not None and state[0]:
            kb_iteam = [
                InlineKeyboardButton(text="Да", callback_data=CbDataCompletedTask(answer='yes',
                                                                                  id=int(task_id),
                                                                                  user_perform=str(call.from_user.id)).pack()),
                InlineKeyboardButton(text="Нет", callback_data=CbDataCompletedTask(answer='no',
                                                                                   id=int(task_id),
                                                                                   user_perform=str(call.from_user.id)).pack())
            ]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[kb_iteam])
            await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await call.bot.send_message(user_id=user_id,
                                        text=f"↘️ № {task_id}. Задача: {task[0]}\n"
                                             f"🏃🏻Волонтер: {call.from_user.id}\n"
                                             f"Волонтер сделал просьбу?",
                                        reply_markup=keyboard
                                        )
            await call.message.answer("Как только клиент подтвердит выполнение задачи, вам придет уведомление")
        else:
            await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await call.answer(text=f"Данной заявки уже не существует", show_alert=True)

    elif action == "refuse":
        state = await db.get_task_state(task_id=task_id)
        if state is not None and state[0]:
            await db.upd_state_task_v(task_id, column_name="date_task_work",state_task="create")
            await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await call.answer(text=f"Вы отказались от задачи № {task_id} - {task[0]}", show_alert=True)
        else:
            await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await call.answer(text=f"Данной заявки уже не существует", show_alert=True)

# Эта функция обрабатывает сообщения с текстом "Свободные заявки" от волонтера,
# проверяет его права доступа и, если они соответствуют,
# выводит свободные заявки, которые он может взять
@router_volunteer.message(F.text == "Свободные заявки")
async def free_tasks(message: types.Message):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist is not None and exist[5] == "volunteer" and exist[6] == 1:
        list_tasks = await db.get_list_tasks("create")

        if list_tasks:
            for item in list_tasks:
                user_adr = await db.get_user_adr(item[3])
                user_name = await db.get_user_name(item[3])
                kb_item = [
                    types.InlineKeyboardButton(text="Взять",
                                               callback_data=CbDataFreeTask(action='add',
                                                                            task_id=item[0],
                                                                            user_id=str(item[3]),
                                                                            user_perform=str(message.from_user.id),
                                                                            task=str(item[1])).pack()
                                               ),
                ]
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[kb_item])
                await message.answer(text=f"↘️ № {item[0]}. Задача: {item[1]}\n"
                                     f"📋Подробности: {item[2]}\n"
                                     f"⏳Срочность: {values_bot.URGENCY_TASK[f'{item[5]}']}\n"
                                     f"🌍Адрес: {user_adr[0]}\n"
                                     f"🛏️Заказчик: {user_name[0]}\n"
                                     f"Дата создания: {item[6]}\n",
                                     reply_markup=keyboard
                                     )
        else:
            await message.answer("Задач нет")

# Обработка добавления задачи волонтером , и отправку уведомления клиету, что его задача выбрана.
@router_volunteer.callback_query(CbDataFreeTask.filter())
async def button_press_free_task(call: types.CallbackQuery, callback_data: dict):
    action = callback_data.action
    task_id = callback_data.task_id
    task = callback_data.task
    user_id = callback_data.user_id
    user_perform = callback_data.user_perform
    if action == "add":
        state = await db.get_task_state(task_id=task_id)
        if state is not None and state[0]:
            await db.upd_add_task_volunteer(task_id, user_perform)
            await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await call.answer(text=f"Задача № {task_id} - {task} добавлена", show_alert=True)
            await call.bot.send_message(user_id, text=f"Ваша заявка № {task_id} - {task} была выбрана волонтером!")
        else:
            await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await call.answer(text=f"Данной заявки уже не существует", show_alert=True)