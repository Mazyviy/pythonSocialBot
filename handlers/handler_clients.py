from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from datetime import datetime
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from geopy.geocoders import Nominatim
from database import db
from keyboards import keyboards as kb
from states.states_client import ClassStateTaskProducts, ClassStateTaskMedicines, ClassStateTaxi, ClassStateDoctor
from handlers.handler_volunteers import CbDataCompletedTask
from config import values_bot

router_client = Router()

class CbDataDelTask(CallbackData, prefix="id2"):
    task_id: Optional[int] = None
    task: str
    action: str

# Эта функция обрабатывает сообщения с текстом "Мои заявки" от клиента/заказчика,
# проверяет его права доступа и, если они соответствуют,
# формирует список его открытых заявок.
@router_client.message(F.text == "Мои заявки")
async def c_my_request(message: types.Message):
   exist=await db.get_user_existence_in_db(message.from_user.id)
   if exist[5] == "client" and exist[6] == 1:
        list_tasks = await db.get_list_tasks_client(message.from_user.id)
        if list_tasks:
            for item in list_tasks:
                kb_iteam = [
                    InlineKeyboardButton(text="Отменить", callback_data=CbDataDelTask(action='delete', task_id=item[0], task=item[1]).pack())
                ]
                keyboard=types.InlineKeyboardMarkup(inline_keyboard=[kb_iteam])

                if item[5]:
                    user_name = await db.get_user_name(item[5])
                    await message.answer(
                        f"↘️ Номер: {item[0]} Задача: {item[1]}\nПодробности: {item[2]}\n⏳Срочность: {values_bot.URGENCY_TASK[f'{item[3]}']}\nДата создания: {item[4]}\nВолонтер: {user_name[0]}",
                        reply_markup=keyboard)
                else:
                    await message.answer(
                        f"↘️ Номер: {item[0]} Задача: {item[1]}\nПодробности: {item[2]}\n⏳Срочность: {values_bot.URGENCY_TASK[f'{item[3]}']}",
                        reply_markup=keyboard)

        else:
            await message.answer("Созданных просьб нет")

# Эта функция удаляет выбранную заявку клиента.
# Если заявка в работе, то волонтер уведомляется об удалении задачи
@router_client.callback_query(CbDataDelTask.filter())
async def button_del_task(call: types.CallbackQuery, callback_data: dict):
    action = callback_data.action
    task_id = callback_data.task_id
    task = callback_data.task

    if action == "delete":
        result_db = await db.get_task_is_work(task_id=task_id)
        state_task =result_db[0]
        user_perform = result_db[1]
        if state_task == "work":
            await call.bot.send_message(chat_id=user_perform, text=f"Задача №: {task_id} - {task}, удалена клиентом!")
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await db.del_task(task_id)
        await call.answer(text=f"Вы удалили задачу {task} ", show_alert=True)

# Эта функция обрабатывает сообщения с текстом "Вызвать врача" от клиента/заказчика
@router_client.message(F.text == values_bot.TASK['doctor'])
async def c_doctor(message: types.Message, state: FSMContext):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist[5] == "client" and exist[6] == 1:
        await message.answer("Напишите, что с вами случилось или на что жалуетесь", reply_markup=kb.keyboard_cancel())
        await state.set_state(ClassStateDoctor.health_complaint)

@router_client.message(F.text == "Отмена")
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Выберите меню",reply_markup=kb.keyboard_menu_c())

# просит клиента выберать важность задачи
@router_client.message(ClassStateDoctor.health_complaint)
async def c_urgency_doctor(message: types.Message, state:FSMContext):
    answer = message.text
    await state.update_data(health_complaint=answer)
    await message.answer("Выберите важность задачи", reply_markup=kb.keyboard_urgency_task())
    await state.set_state(ClassStateDoctor.task_urgency_doctor)

# добавляет задачу в базу
@router_client.message(ClassStateDoctor.task_urgency_doctor)
async def c_set_doctro(message: types.Message, state:FSMContext):
    await state.update_data(task_urgency_doctor=values_bot.URGENCY_TASK_R[f'{message.text}'])
    data = await state.get_data()
    health_complaint = data.get('health_complaint')
    task_urgency_doctor = data.get('task_urgency_doctor')
    await db.add_task("Вызвать врача", health_complaint,"create", task_urgency_doctor, message.from_user.id)
    await state.clear()
    await message.answer("Ваше заявка зарегистрирована", reply_markup=kb.keyboard_menu_c())

# Эта функция обрабатывает сообщения с текстом "Купить продукты" от клиента/заказчика,
# проверяет его права доступа и, если они соответствуют,
# просит клиента ввести список продуктов
@router_client.message(F.text == values_bot.TASK['products'])
async def c_buy_products(message: types.Message, state: FSMContext):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist[5] == "client" and exist[6] == 1:
        await message.answer("Напишите список продуктов", reply_markup=kb.keyboard_cancel())
        await state.set_state(ClassStateTaskProducts.list_products)

# просит клиента выберать важность задачи
@router_client.message(ClassStateTaskProducts.list_products)
async def c_urgency_products(message: types.Message, state:FSMContext):
    answer = message.text
    await state.update_data(list_products=answer)
    await message.answer("Выберите важность задачи", reply_markup=kb.keyboard_urgency_task())
    await state.set_state(ClassStateTaskProducts.task_urgency_products)

# добавляет задачу в базу
@router_client.message(ClassStateTaskProducts.task_urgency_products)
async def b_set_list_products(message: types.Message, state:FSMContext):
    await state.update_data(task_urgency_products=values_bot.URGENCY_TASK_R[f'{message.text}'])
    data = await state.get_data()
    list_products = data.get('list_products')
    task_urgency_products = data.get('task_urgency_products')
    await db.add_task("Купить продукты", list_products,"create", task_urgency_products, message.from_user.id)
    await state.clear()
    await message.answer("Ваше заявка зарегистрирована", reply_markup=kb.keyboard_menu_c())

# Эта функция обрабатывает сообщения с текстом "Купить лекарства" от клиента/заказчика,
# проверяет его права доступа и, если они соответствуют,
# просит клиента ввести список лекарств
@router_client.message(F.text == values_bot.TASK['medicines'])
async def c_buy_medicines(message: types.Message, state:FSMContext):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist[5] == "client" and exist[6] == 1:
        await message.answer("Напишите список лекарств", reply_markup=kb.keyboard_cancel())
        await state.set_state(ClassStateTaskMedicines.list_medicines)

# просит клиента выберать важность задачи
@router_client.message(ClassStateTaskMedicines.list_medicines)
async def c_set_list_products(message: types.Message, state:FSMContext):
    await state.update_data(list_medicines=message.text)
    await message.answer("Выберите важность задачи", reply_markup=kb.keyboard_urgency_task())
    await state.set_state(ClassStateTaskMedicines.task_urgency_medicines)

# добавляет задачу в базу
@router_client.message(ClassStateTaskMedicines.task_urgency_medicines)
async def c_set_list_products(message: types.Message, state:FSMContext):
    await state.update_data(task_urgency_medicines=values_bot.URGENCY_TASK_R[f'{message.text}'])
    data = await state.get_data()
    list_medicines = data.get('list_medicines')
    task_urgency_medicines = data.get('task_urgency_medicines')
    await db.add_task("Купить лекарства",list_medicines,"create",task_urgency_medicines, message.from_user.id)
    await state.clear()
    await message.answer("Ваше заявка зарегистрирована",reply_markup=kb.keyboard_menu_c())

# Эта функция обрабатывает сообщения с текстом "Социальное такси" от клиента/заказчика,
# проверяет его права доступа и, если они соответствуют,
# просит клиента написать адрес отправления
@router_client.message(F.text == values_bot.TASK['taxi'])
async def c_taxi(message: types.Message, state: FSMContext):
    exist = await db.get_user_existence_in_db(message.from_user.id)
    if exist[5] == "client" and exist[6] == 1:
        await message.answer("Напишите адрес отправления (город улица дом)",reply_markup=kb.keyboard_cancel())
        await state.set_state(ClassStateTaxi.first_adress_taxi)

# проверяет введеный адрес отправления на существование, если все good просит
# ввести конечный адрес, иначе просит ввести адресс отправления еще раз
@router_client.message(lambda message: message.content_type == types.ContentType.TEXT, ClassStateTaxi.first_adress_taxi)
async def c_taxi_first_adress(message: types.Message, state=FSMContext):
    geolocator = Nominatim(user_agent="coordinateconverter")
    location = geolocator.geocode(message.text, addressdetails=True, language="ru")

    if location:
        address_parts = location.address.split(', ')
        reversed_address = ', '.join(reversed(address_parts))
        await state.update_data(first_adress_taxi=reversed_address)
    else:
        print("Местоположение не найдено. Введите еще раз")
        await ClassStateTaxi.first_adress_taxi()

    await message.answer("Напишите конечный адрес (город улица дом)")
    await state.set_state(ClassStateTaxi.second_adress_taxi)

# проверяет введеный конечный адрес на существование, если все good
# просит клиента выберать важность задачи, иначе просит ввести конечный адресс еще раз
@router_client.message(lambda message: message.content_type == types.ContentType.TEXT, ClassStateTaxi.second_adress_taxi)
async def c_taxi_second_adress(message: types.Message, state=FSMContext):
    geolocator = Nominatim(user_agent="coordinateconverter")
    location = geolocator.geocode(message.text, addressdetails=True, language="ru")

    if location:
        address_parts = location.address.split(', ')
        reversed_address = ', '.join(reversed(address_parts))
        await state.update_data(second_adress_taxi=reversed_address)
    else:
        print("Местоположение не найдено. Введите еще раз")
        await ClassStateTaxi.second_adress_taxi()

    await message.answer("Выберите важность задачи", reply_markup=kb.keyboard_urgency_task())
    await state.set_state(ClassStateTaxi.task_urgency_taxi)

# добавляет задачу в базу
@router_client.message(ClassStateTaxi.task_urgency_taxi)
async def b_taxi_finish(message: types.Message, state=FSMContext):
    await state.update_data(task_urgency_taxi=values_bot.URGENCY_TASK_R[f'{message.text}'])
    data = await state.get_data()
    first_adress = data.get('first_adress_taxi')
    second_adress = data.get('second_adress_taxi')
    task_urgency_taxi = data.get('task_urgency_taxi')
    adress = f"Такси от \n• {first_adress} \nдо \n• {second_adress}"
    await db.add_task("Социальное такси",adress,"create",task_urgency_taxi, message.from_user.id)
    await state.clear()
    await message.answer("Ваше заявка зарегистрирована", reply_markup=kb.keyboard_menu_c())

# просит подтвердить клиента, что волонтер выполнил заявку
@router_client.callback_query(CbDataCompletedTask.filter())
async def c_task_assurance(call: types.CallbackQuery, callback_data: dict):
    answer = callback_data.answer
    id = callback_data.id
    user_perform = callback_data.user_perform
    task = await db.get_task_id(id)

    if answer == "yes":
        await db.upd_state_task(id,column_name="date_task_close", state_task="close")
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(user_perform, text=f"Вы молодец. Задача id: {id} - {task[0]} выполнена")
    elif answer == "no":
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(user_perform, text=f"Вы не выполнили задачу. Задача id: {id} - {task[0]}")