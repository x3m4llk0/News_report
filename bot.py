import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger

from tgbot.config import load_config
from tgbot.handlers.echo import echo_router
from tgbot.handlers.user import user_router
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.misc.logging import configure_logger
from tgbot.models import db_gino
from tgbot.services import broadcaster


async def on_startup(bot: Bot, admin_ids: list[int]):
    await set_commands(bot)
    await broadcaster.broadcast(bot, admin_ids, "Бот запущен")


def register_global_middlewares(dp: Dispatcher, config):
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.callback_query.outer_middleware(ConfigMiddleware(config))


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="start",
            description="Запустить бота",
        ),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


async def main():
    configure_logger(True)
    logger.info("Starting bot")
    config = load_config(".env")

    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(storage=storage)

    for router in [
        user_router
    ]:
        dp.include_router(router)

    register_global_middlewares(dp, config)
    await db_gino.on_startup(dp)
    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Ошибка в боте")