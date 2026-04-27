from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from direm.services.credits_service import render_credits

router = Router(name="credits")


@router.message(Command("credits"))
async def handle_credits(message: Message) -> None:
    await message.answer(render_credits())
