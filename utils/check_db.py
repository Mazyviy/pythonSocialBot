from database import db
import time, datetime
import asyncio
from config import values_bot

# Функция, которая будет запускаться периодически и отправлять сообщения о задачах
# с близким к концу временем выполнения у волонтеров
async def check_tasks_for_deadline_work(bot):
    list_tasks = await db.get_list_tasks_check('work')
    if list_tasks:
        for item in list_tasks:
            db_datetime = datetime.datetime.strptime(item[6], "%Y-%m-%d %H:%M:%S")
            minutes_to_add = {'fast': 30, 'medium': 60 * 3, 'long': 60 * 8}.get(item[5], 0)
            new_datetime = db_datetime + datetime.timedelta(minutes=minutes_to_add)
            current_datetime = datetime.datetime.now()
            # 1) проверка что срок задачи не вышел,
            # 2) отправка через каждые % int(minutes_to_add/3) и если осталось не меньше 10 мин,
            # или осталось времени == minutes_to_add/5
            if (new_datetime > current_datetime
                    and (new_datetime - current_datetime).total_seconds() / 60 <= minutes_to_add
                    and ((int((new_datetime - current_datetime).total_seconds() / 60) % int(minutes_to_add/3) == 0
                         and int((new_datetime - current_datetime).total_seconds() / 60) >= 10)
                    or int((new_datetime - current_datetime).total_seconds() / 60) % 20 == minutes_to_add/5)):
                out=''
                hours, minutes, seconds = map(int, (str(new_datetime - current_datetime).split('.')[0]).split(':'))
                if hours > 0:
                    out= f"{hours} часов"
                else:
                    out=f"{minutes} минут"

                text=(f"Для выполнения задачи № {item[0]} - {item[1]} осталось {out}\n"
                      f"Если не успеваете выполнить, откажитесь от нее!")
                await bot.send_message(chat_id=item[4], text=text)

# Функция, которая будет запускаться периодически и отправлять сообщения о задачах
# с близким к концу временем закрытия у клиентов, по истечению времени - удаляет ее.
async def check_tasks_for_deadline_create(bot):
    list_tasks = await db.get_list_tasks_check('create')
    if list_tasks:
        for item in list_tasks:
            db_datetime = datetime.datetime.strptime(item[6], "%Y-%m-%d %H:%M:%S")
            minutes_to_add = {'fast': 30, 'medium': 60 * 3, 'long': 60 * 8}.get(item[5], 0)
            new_datetime = db_datetime + datetime.timedelta(minutes=minutes_to_add)
            current_datetime = datetime.datetime.now()

            if int((new_datetime - current_datetime).total_seconds()/60)%5==0 and int((new_datetime - current_datetime).total_seconds()/60)==10:
                hours, minutes, seconds = map(int, (str(new_datetime - current_datetime).split('.')[0]).split(':'))
                text =f"К сожалению, время для выполнения вашей задачи № {item[0]} - {item[1]} заканчивается, осталось {minutes} минут. По истечению времени задача будет автоматически закрыта!"
                await bot.send_message(chat_id=item[3], text=text)

            elif int((new_datetime - current_datetime).total_seconds()/60)==0:
                await bot.send_message(chat_id=item[3], text=f"Ваша задача № {item[0]} - {item[1]} закрыта по истечению времени.")
                await db.del_task(task_id=item[0])

# Отправляет всем волонтерам что появилась новая срочная задача - Вызвать доктора
async def send_message_all_volunteer_doctor(bot):
    list_tasks = await db.get_list_tasks_check('create')  #id, task, task_detail, user_id, user_perform, task_urgency, date_task_create, date_task_work
    if list_tasks:
        for item in list_tasks:
            db_datetime = datetime.datetime.strptime(item[6], "%Y-%m-%d %H:%M:%S")
            minutes_to_add = {'fast': 30, 'medium': 60 * 3, 'long': 60 * 8}.get(item[5], 0)
            new_datetime = db_datetime + datetime.timedelta(minutes=minutes_to_add)
            current_datetime = datetime.datetime.now()

            if (item[1] == values_bot.TASK['doctor'] and
                    item[5] == 'fast' and
                    (int((new_datetime - current_datetime).total_seconds() / 60) % 5 == 0) and
                    ((new_datetime - current_datetime).total_seconds() / 60 >= 15)):
                list_volunteer = await db.get_list_users(user_role='volunteer', user_status=1)

                hours, minutes, seconds = map(int, (str(new_datetime - current_datetime).split('.')[0]).split(':'))
                if hours > 0:
                    out = f"{hours} часов"
                else:
                    out = f"{minutes} минут"

                for item_volunteer in list_volunteer:
                    await bot.send_message(chat_id=item_volunteer[0], text=f"❗ Появилась срочная задача № {item[0]} - {item[1]}."
                                                                           f"\nОсталось {out}")

# Запускаем цикл проверки задач
async def task_checker(bot):
    while True:
        await check_tasks_for_deadline_work(bot)
        await check_tasks_for_deadline_create(bot)
        await send_message_all_volunteer_doctor(bot)
        # Пауза между проверками задач (1 минута)
        await asyncio.sleep(60)