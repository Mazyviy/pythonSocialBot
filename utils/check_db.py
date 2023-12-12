from database import db
import time, datetime
import asyncio

# Функция, которая будет запускаться периодически и отправлять сообщения о задачах с близким к концу временем выполнения
async def check_tasks_for_deadline(bot):
    list_tasks = await db.get_list_tasks_check('work')
    if list_tasks:
        for item in list_tasks:
            db_datetime = datetime.datetime.strptime(item[6], "%Y-%m-%d %H:%M:%S")
            minutes_to_add = {'Срочно (в течении 30 мин)': 30,
                              'Средняя важность (от 30 мин до 3 часов)': 60 * 3,
                              'Низшая важность (от 3 часов до 8 часов)': 60 * 8}.get(item[5], 0)
            new_datetime = db_datetime + datetime.timedelta(minutes=minutes_to_add)
            current_datetime = datetime.datetime.now()

            if (new_datetime > current_datetime
                  and (new_datetime - current_datetime).total_seconds()/60<=minutes_to_add
                  and (int((new_datetime - current_datetime).total_seconds()/60)%10==0 and (new_datetime - current_datetime).total_seconds()/60>=10)):
                out=''
                hours, minutes, seconds = map(int, (str(new_datetime - current_datetime).split('.')[0]).split(':'))
                if hours > 0:
                    out= f"{hours} часов"
                else:
                    out=f"{minutes} минут"

                text=(f"Для выполнения задачи № {item[0]} - '{item[1]}' осталось {out}\n"
                      f"Если не успеваете выполнить, откажитесь от нее!"
                      f"Перейти в <a>Принятые заявки</a>")
                await bot.send_message(chat_id=item[4], text=text)

    list_tasks = await db.get_list_tasks_check('work')

# Запускаем цикл проверки задач
async def task_checker(bot):
    while True:
        await check_tasks_for_deadline(bot)
        # Пауза между проверками задач (1 минута)
        await asyncio.sleep(60)

