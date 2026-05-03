from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.menu import main_menu_keyboard, render_main_menu_text
from direm.bot.reply_keyboard import idle_reply_keyboard
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
    existing_user = await service.get_by_telegram_user_id(message.from_user.id)
    user = await service.register_or_update_from_telegram(
        TelegramUserProfile(
            telegram_user_id=message.from_user.id,
            chat_id=message.chat.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            language_code=message.from_user.language_code,
        )
    )

    if existing_user is None:
        await message.answer(
            t(user.language_code, "start.onboarding", timezone=user.timezone, language=language_name(user.language_code)),
            reply_markup=idle_reply_keyboard(user.language_code),
        )
        return

    await message.answer(
        render_main_menu_text(user.language_code, user.timezone, bunker_active=user.bunker_active),
        reply_markup=main_menu_keyboard(user.language_code, bunker_active=user.bunker_active),
    )
