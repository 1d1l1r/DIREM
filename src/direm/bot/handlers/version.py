from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from direm.app.config import get_settings
from direm.services.version_service import build_version_metadata, render_version

router = Router(name="version")


@router.message(Command("version"))
async def handle_version(message: Message) -> None:
    metadata = build_version_metadata(get_settings())
    await message.answer(render_version(metadata))
