from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.states import TimezoneFlow
from direm.domain.errors import InvalidTimezoneError
from direm.i18n import t
from direm.repositories.users import UserRepository
from direm.services.user_service import TelegramUserProfile, UserService

router = Router(name="timezone")


@router.message(Command("timezone"))
async def handle_timezone_command(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    if user is None:
        await message.answer(t("ru", "common.no_profile"))
        return

    await state.set_state(TimezoneFlow.waiting_for_timezone)
    await message.answer(
        t(user.language_code, "timezone.prompt", timezone=user.timezone)
    )


@router.message(TimezoneFlow.waiting_for_timezone)
async def handle_timezone_input(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    if user is None:
        await message.answer(t("ru", "common.no_profile"))
        return

    timezone = (message.text or "").strip()
    service = UserService(UserRepository(session))

    try:
        user = await service.update_timezone(user, timezone)
    except InvalidTimezoneError:
        await message.answer(t(user.language_code, "timezone.invalid"))
        return

    await state.clear()
    await message.answer(t(user.language_code, "timezone.updated", timezone=user.timezone))


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
