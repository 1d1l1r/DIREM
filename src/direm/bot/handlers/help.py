from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.reply_keyboard import HELP_BUTTON_LABELS, idle_reply_keyboard
from direm.i18n import t
from direm.repositories.users import UserRepository
from direm.services.user_service import TelegramUserProfile, UserService

router = Router(name="help")


@router.message(Command("help"))
async def handle_help(message: Message, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    await _answer_help(message, user.language_code if user else "ru", user.bunker_active if user else False)


@router.message(F.text.in_(HELP_BUTTON_LABELS))
async def handle_help_button(message: Message, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    await _answer_help(message, user.language_code if user else "ru", user.bunker_active if user else False)


async def _answer_help(message: Message, language_code: str | None, bunker_active: bool = False) -> None:
    await message.answer(t(language_code, "help.text"), reply_markup=idle_reply_keyboard(language_code, bunker_active=bunker_active))


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
