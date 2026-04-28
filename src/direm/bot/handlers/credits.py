from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.repositories.users import UserRepository
from direm.services.credits_service import render_credits
from direm.services.user_service import TelegramUserProfile, UserService

router = Router(name="credits")


@router.message(Command("credits"))
async def handle_credits(message: Message, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    await message.answer(render_credits(user.language_code if user else "ru"))


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
