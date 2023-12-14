from datetime import datetime
import aiosqlite
from config import values_bot

# Подключается к БД (или создает ее)
async def connect_to_database():
    connection = await aiosqlite.connect(values_bot.DATABASE_NAME)
    return connection

# создает таблицы users и tasks.
async def db_start():
    global db
    db = await connect_to_database()

    await db.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id TEXT UNIQUE,
                            user_name TEXT,
                            user_date DATE,
                            user_number TEXT,
                            user_address TEXT,
                            user_role TEXT,
                            user_status INTEGER,
                            date_addition DATE
                        )''')
    await db.execute('''CREATE TABLE IF NOT EXISTS tasks (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            task TEXT,
                            task_detail TEXT,
                            task_urgency TEXT,
                            user_id TEXT,
                            user_perform TEXT,
                            state_task TEXT,
                            date_task_create DATA,
                            date_task_work DATA,
                            date_task_close DATA
                        )''')
    await db.commit()

# Для закрытие соединения с БД
async def db_close():
    await db.close()

# Эта функция предназначена для выполнения запроса к базе данных с использованием переданного user_id.
# Запрос осуществляется на таблицу "users" с целью получения информации о пользователе. В случае наличия записи с указанным user_id,
# функция возвращает кортеж с данными о пользователе. Если запись отсутствует, то возвращается None.
# Запрос формирует результат с использованием функции COALESCE, которая возвращает первое непустое значение из списка аргументов.
# Таким образом, если какое-либо поле пользователя в базе данных имеет значение NULL (пусто), оно будет заменено на None в результирующем кортеже.
# В итоге, функция предназначена для проверки существования пользователя в базе данных и возврата информации о нем, если он найден.
async def get_user_existence_in_db(user_id):
    query = ("SELECT "
             "COALESCE(user_id, NULL) AS user_id,"
             "COALESCE(user_name, NULL) AS user_name,"
             "COALESCE(user_date, NULL) AS user_date,"
             "COALESCE(user_number, NULL) AS user_number, "
             "COALESCE(user_address, NULL) AS user_address,"
             "COALESCE(user_role, NULL) AS user_role, "
             "COALESCE(user_status, NULL) AS user_status "
             "FROM users WHERE user_id=?")
    async with db.execute(query, (user_id,)) as cursor:
        return await cursor.fetchone()

# Эта функция предназначена для выполнения запроса к базе данных с использованием переданного user_id.
# Запрос осуществляется на таблицу "users" с целью получения информации о пользователе,
# у которого значение поля user_status равно 0 (пользователь еще не зарегистрирован).
# Функция возвращает список кортежей, каждый из которых содержит три значения: user_id (идентификатор пользователя),
# user_role (роль пользователя) и user_name (имя пользователя).
# Эти данные предоставляют информацию о пользователях, которые ожидают регистрации.
async def get_applications_for_registration():
    query = ("SELECT id, user_role, user_name, user_id, user_number, user_address "
             "FROM users "
             "WHERE user_status=0 ORDER BY id DESC")
    async with db.execute(query) as cursor:
        return await cursor.fetchall()

# Эта функция изменяет статус пользователя в базе данных на указанное значение.
async def upd_user_status(status, user_id):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = "UPDATE users SET user_status=?, date_addition=? WHERE user_id=?"
    await db.execute(query, (status, current_datetime, user_id,))
    await db.commit()

# функция удаляет пользователя из базы данных по его идентификатору.
async def del_user(user_id):
    query = "DELETE FROM users WHERE user_id=?"
    await db.execute(query, (user_id,))
    await db.commit()

# функция возвращает список пользователей из базы данных, удовлетворяющих указанным ролям и статусам.
async def get_list_users(user_role, user_status):
    query = ("SELECT user_id, user_role, user_name, user_number, id "
             "FROM users "
             "WHERE user_role=? AND user_status=?")
    async with db.execute(query, (user_role, user_status,)) as cursor:
        return await cursor.fetchall()

# После выполнения запроса, функция возвращает список кортежей c столбцами
# ("id", "task", "task_detail", "user_id", "user_perform", "task_urgency"),
# содержащих информацию о задачах, которые соответствуют состоянию задачи - открытая, закрытая, свободная.
async def get_list_tasks(state_task, date_value=''):
    if state_task == "create":
        query = ("SELECT id, task, task_detail, user_id, user_perform, task_urgency, date_task_create "
                 "FROM tasks "
                 "WHERE state_task=? "
                 "ORDER BY date_task_create DESC")
        async with db.execute(query, (state_task,)) as cursor:
            return await cursor.fetchall()
    elif state_task == "close":
        if date_value is not None:
            if date_value == 'за год':
                query = ("SELECT id, task, task_detail, user_id, user_perform, task_urgency, date_task_create, date_task_work, date_task_close "
                         "FROM tasks "
                         "WHERE state_task=? AND strftime('%Y', date_task_create) = strftime('%Y', 'now') "
                         "ORDER BY date_task_close DESC")
                async with db.execute(query, (state_task,)) as cursor:
                    return await cursor.fetchall()
            elif date_value == 'за месяц':
                query = ("SELECT id, task, task_detail, user_id, user_perform, task_urgency, date_task_create, date_task_work, date_task_close "
                         "FROM tasks "
                         "WHERE state_task=? AND strftime('%Y-%m', date_task_create) = strftime('%Y-%m', 'now') "
                         "ORDER BY date_task_close DESC")
                async with db.execute(query,(state_task,)) as cursor:
                    return await cursor.fetchall()
            elif date_value == 'за день':
                query = ("SELECT id, task, task_detail, user_id, user_perform, task_urgency, date_task_create, date_task_work, date_task_close "
                         "FROM tasks "
                         "WHERE state_task=? AND date(date_task_create) = date('now', 'localtime') "
                         "ORDER BY date_task_close DESC")
                async with db.execute(query, (state_task,)) as cursor:
                    return await cursor.fetchall()
            elif date_value=='за все время':
                query = ("SELECT id, task, task_detail, user_id, user_perform, task_urgency, date_task_create, date_task_work, date_task_close "
                         "FROM tasks "
                         "WHERE state_task=? "
                         "ORDER BY date_task_close DESC")
                async with db.execute(query, (state_task,)) as cursor:
                    return await cursor.fetchall()
        else:
            query = ("SELECT id, task, task_detail, user_id, user_perform, task_urgency, date_task_create, date_task_work, date_task_close "
                     "FROM tasks "
                     "WHERE state_task=? "
                     "ORDER BY date_task_close DESC")
            async with db.execute(query, (state_task,)) as cursor:
                return await cursor.fetchall()

    elif state_task == "work":
        query = ("SELECT id, task, task_detail, user_id, user_perform, task_urgency, date_task_create, date_task_work "
                 "FROM tasks "
                 "WHERE state_task=? ORDER BY date_task_work DESC")
        async with db.execute(query, (state_task,)) as cursor:
            return await cursor.fetchall()

# Функция возвращает список принятых задач для волонтёра.
async def get_list_accepted_tasks_volunteer(user_id):
    query = ("SELECT id, task, task_detail, user_id, task_urgency, date_task_create, date_task_work "
             "FROM tasks "
             "WHERE user_perform=? AND state_task='work' "
             "ORDER BY date_task_create DESC")
    async with db.execute(query, (user_id,)) as cursor:
        return await cursor.fetchall()

# функция позволяет получить количество записей в базе данных,
# которые соответствуют определенному условию фильтрации по указанному столбцу.
async def get_count_data(db_name, column_name, column_value, column_date='', date_value=''):
    if column_date:
        if date_value=='year':
            query = (f"SELECT "
                     f"(SELECT count(*) FROM {db_name} WHERE {column_name}=? AND strftime('%Y', {column_date}) = strftime('%Y', 'now')) as current_year, "
                     f"(SELECT count(*) FROM {db_name} WHERE {column_name}=? AND strftime('%Y', {column_date}) = strftime('%Y', 'now', '-1 year')) as last_year")
            async with db.cursor() as cursor:
                await cursor.execute(query, (column_value, column_value))
                current_year, last_year = await cursor.fetchone()
                return [current_year, last_year]

        elif date_value=='month':
            query = (f"SELECT "
                     f"(SELECT count(*) FROM {db_name} WHERE {column_name}=? AND strftime('%Y-%m', {column_date}) = strftime('%Y-%m', 'now')) as current_month, "
                     f"(SELECT count(*) FROM {db_name} WHERE {column_name}=? AND strftime('%Y-%m', {column_date}) = strftime('%Y-%m', 'now', '-1 month')) as last_month")
            async with db.cursor() as cursor:
                await cursor.execute(query, (column_value, column_value))
                current_month, last_month = await cursor.fetchone()
                return [current_month, last_month]

        elif date_value=='day':
            query = (f"SELECT "
                     f"(SELECT count(*) FROM {db_name} WHERE {column_name} = ? AND date({column_date}) = date('now', 'localtime')) as current_day, "
                     f"(SELECT count(*) FROM {db_name} WHERE {column_name} = ? AND date({column_date}) = date('now', '-1 day', 'localtime')) as last_day")
            async with db.cursor() as cursor:
                await cursor.execute(query, (column_value, column_value))
                current_day, last_day = await cursor.fetchone()
                return [current_day, last_day]

    else:
        query = (f"SELECT count(*) FROM {db_name} WHERE {column_name}=?")
        async with db.execute(query, (column_value,)) as cursor:
            return await cursor.fetchone()

# функция используется для получения списка задач из базы данных
# для конкретного пользователя (user_id), которые находятся в состоянии 'created' (созданные).
async def get_list_tasks_client(user_id):
    query = ("SELECT id, task,task_detail, task_urgency, date_task_create, user_perform "
             "FROM tasks "
             "WHERE user_id=? AND (state_task='create' OR state_task='work')")
    async with db.execute(query, (user_id,)) as cursor:
        return await cursor.fetchall()

# функция удаляет задачу с указанным идентификатором из таблицы задач в базе данных.
async def del_task(task_id):
    query = "DELETE FROM tasks WHERE id=?"
    await db.execute(query, (task_id,))
    await db.commit()

# добавление задачи в БД, используется в handler_clients
async def add_task(task, task_detail,state_task,task_urgency,user_id):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = "INSERT INTO tasks (task, task_detail, task_urgency, user_id, state_task, date_task_create) VALUES (?,?,?,?,?,?)"
    await db.execute(query, (task, task_detail, task_urgency, user_id, state_task, current_datetime,))
    await db.commit()

# Функция возвращает адрес пользователя по его идентификатору.
async def get_user_adr(user_id):
    query = ("SELECT user_address FROM users WHERE user_id=?")
    async with db.execute(query, (user_id,)) as cursor:
        return await cursor.fetchone()

# функция возвращает имя пользователя по его идентификатору.
async def get_user_name(user_id):
    query = ("SELECT user_name FROM users WHERE user_id=?")
    async with db.execute(query, (user_id,)) as cursor:
        return await cursor.fetchone()

# функция возвращает номер пользователя по его идентификатору.
async def get_user_nunmber(user_id):
    query = ("SELECT user_number FROM users WHERE user_id=?")
    async with db.execute(query, (user_id,)) as cursor:
        return await cursor.fetchone()

# функция для обновления состояния и даты закрытия задачи.
async def upd_state_task(task_id, column_name,state_task):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = f"UPDATE tasks SET state_task=?, {column_name}=? WHERE id=?"
    await db.execute(query, (state_task,current_datetime, task_id,))
    await db.commit()

async def upd_state_task_v(task_id, column_name,state_task):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = f"UPDATE tasks SET state_task=?, {column_name}=?, user_perform='', date_task_work='' WHERE id=?"
    await db.execute(query, (state_task,current_datetime, task_id,))
    await db.commit()

# получения списка задач, которые еще не были взяты на выполнение
async def get_list_free_tasks_volunteer(user_id):
    query = ("SELECT id, task, task_detail FROM tasks WHERE user_perform=? AND state_task='create'")
    async with db.execute(query, (user_id,)) as cursor:
        return await cursor.fetchall()

# Эта функция для обновления записи о задаче. Более конкретно, она изменяет состояние задачи на 'work',
# устанавливает пользователя, который будет выполнять задачу (user_perform),
# и устанавливает дату начала выполнения задачи (date).
async def upd_add_task_volunteer(task_id,user_perform):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = "UPDATE tasks SET state_task='work', user_perform=?, date_task_work=? WHERE id=?"
    await db.execute(query, (user_perform,current_datetime, task_id,))
    await db.commit()

# Эта функция добавляет или обновляет данные пользователя в базе данных.
# Она принимает идентификатор пользователя (user_id) и роль пользователя (user_role) в качестве аргументов.
# Значение user_status устанавливается на 0.
async def set_user_in_db(user_id,user_role):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = "REPLACE INTO users (user_id, user_role) VALUES (?,?)"
    await db.execute(query, (user_id, user_role,))
    await db.commit()

# Эта функция обновляет данные в базе данных для указанного пользователя.
# Она принимает имя столбца (column_name), новые данные (data) и идентификатор пользователя (user_id) в качестве аргументов.
# Затем она выполняет SQL-запрос для обновления значения в указанном столбце ("users") на новое значение (data)
# для пользователя с указанным идентификатором (user_id).
async def upd_data_in_db(column_name, data, user_id):
    query = f"UPDATE users SET {column_name}=? WHERE user_id=?"
    await db.execute(query, (data,user_id,))
    await db.commit()

# выводит список администраторов со статусом 1 (активные)
async def get_admins():
    query = ("SELECT user_id from users WHERE user_role='admin' AND user_status=1")
    async with db.execute(query) as cursor:
        return await cursor.fetchall()

# Функция `get_task_id` выполняет запрос к базе данных для получения задачи по её идентификатору.
# Она принимает один параметр - `task_id` (идентификатор задачи).
async def get_task_id(task_id):
    query = ("SELECT task from tasks WHERE id=?")
    async with db.execute(query, (task_id,)) as cursor:
        return await cursor.fetchone()

# Функция `get_task_id` выполняет запрос к базе данных для получения state задачи по её идентификатору.
# Она принимает один параметр - `task_id` (идентификатор задачи).
async def get_task_state(task_id):
    query = ("SELECT state_task from tasks WHERE id=?")
    async with db.execute(query, (task_id,)) as cursor:
        return await cursor.fetchone()

async def get_task_is_work(task_id):
    query = ("SELECT state_task, user_perform FROM tasks WHERE id=?")
    async with db.execute(query, (task_id,)) as cursor:
        return await cursor.fetchone()

async def get_list_tasks_check(state_task):
    if state_task == "create":
        query = ("SELECT id, task, task_detail, user_id, user_perform, task_urgency, date_task_create "
                 "FROM tasks "
                 "WHERE state_task=? "
                 "ORDER BY date_task_create DESC")
        async with db.execute(query, (state_task,)) as cursor:
            return await cursor.fetchall()

    elif state_task == "work":
        query = ("SELECT id, task, task_detail, user_id, user_perform, task_urgency, date_task_create, date_task_work "
                 "FROM tasks "
                 "WHERE state_task=? "
                 "ORDER BY date_task_work DESC")
        async with db.execute(query, (state_task,)) as cursor:
            return await cursor.fetchall()

async def get_list_tasks_check_doctor():
    query = ("SELECT id, task, task_detail, user_id, user_perform, task_urgency, date_task_create "
             "FROM tasks "
             "WHERE state_task='create' and task='Вызвать врача' and task_urgency='' "
             "ORDER BY date_task_create DESC")
    async with db.execute(query, (state_task,)) as cursor:
        return await cursor.fetchall()



#####################test################
# функция используется для обновления роли пользователя в базе данных
async def change_role(user_id, user_role):
    query = "UPDATE users SET user_role=? WHERE user_id=?"
    await db.execute(query, (user_role, user_id,))
    await db.commit()
#########################################