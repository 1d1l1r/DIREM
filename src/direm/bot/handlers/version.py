from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.app.config import get_settings
from direm.bot.reply_keyboard import idle_reply_keyboard
from direm.repositories.users import UserRepository
from direm.services.user_service import TelegramUserProfile, UserService
from direm.services.version_service import build_version_metadata, render_version

router = Router(name="version")


@router.message(Command("version"))
async def handle_version(message: Message, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    language_code = user.language_code if user else "ru"
    metadata = build_version_metadata(get_settings())
    await message.answer(render_version(metadata, language_code), reply_markup=idle_reply_keyboard(language_code))


async def _ensure_user(message: Message, session: AsyncSession):
    if message.from_user is None:
        return None

    service = UserService(UserRepository(session))
    return await service.register_or_update_from_telegram(
        TelegramUserProfile(
            telegram_user_id=message.from_user.id,
            chat_id=message.chat.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            language_code=message.from_user.language_code,
        )
    )
