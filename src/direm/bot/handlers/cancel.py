from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.home import answer_home_status
from direm.bot.reply_keyboard import CANCEL_BUTTON_LABELS
from direm.i18n import t
from direm.repositories.users import UserRepository
from direm.services.user_service import TelegramUserProfile, UserService

router = Router(name="cancel")


@router.message(Command("cancel"))
async def handle_cancel(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await _cancel(message, state, session)


@router.message(F.text.in_(CANCEL_BUTTON_LABELS))
async def handle_cancel_button(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await _cancel(message, state, session)


async def _cancel(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    language_code = user.language_code if user else "ru"
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(t(language_code, "cancel.none"))
        if user is not None:
            await answer_home_status(message, user, session)
        return

    await state.clear()
    await message.answer(t(language_code, "cancel.done"))
    if user is not None:
        await answer_home_status(message, user, session)


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
