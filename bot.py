# -*- coding: utf-8 -*-
import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
import utils.check_db
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from config.config_reader import config
from database import db
from handlers.handler_base import router_base
from handlers.handler_registration import router_registration
from handlers.handler_volunteers import router_volunteer
from handlers.handler_clients import router_client
from handlers.handler_admins import router_admin
from utils.commands import set_commands
from handlers.handler_tests import router_test

async def send_notification(bot, message):
    list_admins = await db.get_admins()
    try:
        for item in list_admins:
            await bot.send_message(item[0], message)
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления: {e}")

async def main():
    # Запуск базы данных
    await db.db_start()
    # Создание объекта бота с использованием токена из конфигурации
    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
    # Запуск цикла проверки задач в отдельном потоке
    utils.check_db.start_check(bot)
    # Создание хранилища данных
    storage = MemoryStorage()
    # Создание диспетчера для обработки команд и сообщений бота
    dp = Dispatcher(storage=storage)
    await send_notification(bot, message="Бот был успешно запущен.")
    # Подключение роутеров для обработки различных типов сообщений
    await set_commands(bot)
    dp.include_routers(router_registration, router_volunteer, router_client, router_admin, router_test, router_base)

    try:
        # Удаление вебхука перед запуском обновлений
        await bot.delete_webhook(drop_pending_updates=True)
        # Запуск получения обновлений от бота через лонг-поллинг
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally :
        await send_notification(bot, message="Бот был остановлен.")
        utils.check_db.stop_check()
        # Закрытие сессии бота
        await bot.session.close()
        # Закрытие соединения с базой данных
        await db.db_close()

if __name__ == "__main__":
    # Настройка обработчика для записи в файл с ротацией по времени (каждый день)
    file_handler = TimedRotatingFileHandler("logs/log.txt", when="midnight", interval=1, backupCount=7)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")
    file_handler.setFormatter(file_formatter)

    # Настройка обработчика для вывода на экран
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")
    console_handler.setFormatter(console_formatter)

    # Настройка корневого логгера
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Запуск основной функции асинхронно
    asyncio.run(main())