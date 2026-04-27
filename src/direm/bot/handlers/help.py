from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="help")


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(
        "Available now:\n"
        "/start - open DIREM\n"
        "/help - show this help\n"
        "/timezone - view or set your timezone\n"
        "/new - create a reminder record\n"
        "/list - show your reminder records\n"
        "/pause - pause a reminder record\n"
        "/resume - resume a reminder record\n"
        "/delete - delete a reminder record\n"
        "/version - show runtime version\n"
        "/credits - show project credits\n"
        "/cancel - cancel the current action\n\n"
        "Worker delivery is implemented as a basic MVP. Retries, delivery history, dashboards and webhook mode are not implemented."
    )
