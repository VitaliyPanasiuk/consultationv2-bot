import asyncio
import logging
import os  # <<< Добавлен импорт

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties

# --- Начало блока для веб-сервера ---
from aiohttp import web  # <<< Добавлен импорт
# --- Конец блока для веб-сервера ---

from tgbot.config import load_config
from tgbot.handlers.admin import admin_router
from tgbot.handlers.user import user_router
from tgbot.handlers.price import price_router
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.services import broadcaster
from db.db import init_db_pool, db_pool
from logs.logs import initlogging


# --- Начало блока для веб-сервера ---

async def web_server_handler(request):
    
    return web.Response(text="Bot is running")

async def on_bot_startup(dispatcher: Dispatcher):
    
    app = web.Application()
    app.router.add_get("/", web_server_handler)
    
    port = int(os.environ.get('PORT', 8080))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host='0.0.0.0', port=port)
    await site.start()
    
    dispatcher.workflow_data["webapp_runner"] = runner 
    print(f"Веб-сервер запущен на порту {port}...")

async def on_bot_shutdown(dispatcher: Dispatcher):
    runner = dispatcher.workflow_data.get("webapp_runner")
    if runner:
        await runner.cleanup()
        print("Веб-сервер остановлен.")



async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Бот був запущений")


def register_global_middlewares(dp: Dispatcher, config):
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.callback_query.outer_middleware(ConfigMiddleware(config))


async def main():
    db_logger, bot_logger = initlogging()
    bot_logger.info("Starting bot")
    
    await init_db_pool()
    db_logger.info("Starting DB") 
    
    config = load_config(".env")

    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher(storage=storage)
    
    dp.startup.register(on_bot_startup)
    dp.shutdown.register(on_bot_shutdown)

    for router in [
        admin_router,
        user_router,
        price_router,
    ]:
        dp.include_router(router)

    register_global_middlewares(dp, config)

    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass