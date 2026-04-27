from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.states import TimezoneFlow
from direm.domain.errors import InvalidTimezoneError
from direm.repositories.users import UserRepository
from direm.services.user_service import TelegramUserProfile, UserService

router = Router(name="timezone")


@router.message(Command("timezone"))
async def handle_timezone_command(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    if user is None:
        await message.answer("DIREM needs a Telegram user profile to set timezone.")
        return

    await state.set_state(TimezoneFlow.waiting_for_timezone)
    await message.answer(
        f"Current timezone: {user.timezone}\n\n"
        "Send your timezone as an IANA name, for example:\n"
        "Asia/Almaty\n"
        "Europe/Moscow\n"
        "UTC"
    )


@router.message(TimezoneFlow.waiting_for_timezone)
async def handle_timezone_input(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    if user is None:
        await message.answer("DIREM needs a Telegram user profile to set timezone.")
        return

    timezone = (message.text or "").strip()
    service = UserService(UserRepository(session))

    try:
        user = await service.update_timezone(user, timezone)
    except InvalidTimezoneError:
        await message.answer(
            "Invalid timezone.\n"
            "Use an IANA name, for example: Asia/Almaty or UTC."
        )
        return

    await state.clear()
    await message.answer(f"Timezone updated: {user.timezone}")


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
        )
    )
