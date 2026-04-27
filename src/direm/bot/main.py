import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from direm.app.config import get_settings
from direm.app.logging import configure_logging
from direm.bot.commands import build_bot_commands
from direm.bot.router import build_router


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    logging.getLogger(__name__).info("Starting DIREM bot v%s", settings.direm_version)

    bot = Bot(token=settings.require_bot_token())
    await bot.set_my_commands(build_bot_commands())
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(build_router())
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
