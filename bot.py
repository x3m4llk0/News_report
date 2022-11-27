import asyncio
from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger
from aiogram import Bot, Dispatcher

from tgbot.handlers.admin import admin_router
from tgbot.handlers.echo import echo_router
from tgbot.handlers.start import user_router
from tgbot.handlers.send_news import send_news_router
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.misc.logging import configure_logger
from tgbot.models import db_gino
from tgbot.services import broadcaster



#Информирование о запуске и установка дефолтных команд
async def on_startup(bot: Bot, admin_ids: list[int]):
    await set_commands(bot)
    await broadcaster.broadcast(bot, admin_ids, "Бот запущен")


#Регистрация мидлварей
def register_global_middlewares(dp: Dispatcher, config):
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.callback_query.outer_middleware(ConfigMiddleware(config))


#Создание меню дефолтных команд
async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="news",
            description="Отправить новость",
        ),
        BotCommand(
            command="help",
            description="Помощь",
        ),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


#Основная функция. Запуск бота, памяти и тд
async def main():
    from loader import config, dp, bot, storage

    #Старт логов
    configure_logger(True)
    logger.info("Starting bot")

    #Инициализация
    for router in [
        admin_router,
        user_router,
        send_news_router,
        echo_router
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
        logger.error("Bot stopped")
