from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.repositories.reminders import ReminderRepository
from direm.repositories.users import UserRepository
from direm.services.reminder_list_service import ReminderListService
from direm.services.user_service import TelegramUserProfile, UserService

router = Router(name="list")


@router.message(Command("list"))
async def handle_list(message: Message, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    if user is None:
        await message.answer("DIREM needs a Telegram user profile to list reminders.")
        return

    service = ReminderListService(ReminderRepository(session))
    items = await service.list_for_user(user)
    await message.answer(service.render_for_user(items))


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
