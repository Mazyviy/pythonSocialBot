from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='/start',
            description='Start/Начать использование бота'
        ),
        BotCommand(
            command='/support',
            description='Канал/Поддержка'
        )
    ]
    await bot.set_my_commands(commands,BotCommandScopeDefault())