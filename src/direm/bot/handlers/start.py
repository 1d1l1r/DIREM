from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.i18n import language_name, t
from direm.repositories.users import UserRepository
from direm.services.user_service import TelegramUserProfile, UserService

router = Router(name="start")


@router.message(CommandStart())
async def handle_start(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        await message.answer("DIREM needs a Telegram user profile to start.")
        return

    service = UserService(UserRepository(session))
    user = await service.register_or_update_from_telegram(
        TelegramUserProfile(
            telegram_user_id=message.from_user.id,
            chat_id=message.chat.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            language_code=message.from_user.language_code,
        )
    )

    await message.answer(
        t(user.language_code, "start.text", timezone=user.timezone, language=language_name(user.language_code))
    )
