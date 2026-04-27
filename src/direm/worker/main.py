import asyncio

from aiogram import Bot

from direm.app.config import get_settings
from direm.app.logging import configure_logging
from direm.worker.loop import run_worker


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    bot = Bot(token=settings.require_bot_token())
    try:
        await run_worker(
            bot,
            poll_seconds=settings.worker_poll_seconds,
            batch_size=settings.worker_batch_size,
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
