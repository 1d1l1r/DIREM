from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.menu import main_menu_keyboard
from direm.bot.reply_keyboard import idle_reply_keyboard
from direm.db.models import User
from direm.i18n import t
from direm.repositories.reminders import ReminderRepository
from direm.services.home_status_service import HomeStatusService


async def answer_home_status(message: Message, user: User, session: AsyncSession) -> None:
    text = await HomeStatusService(ReminderRepository(session)).render_for_user(user)
    await message.answer(
        text,
        reply_markup=idle_reply_keyboard(user.language_code, bunker_active=user.bunker_active),
    )
    await message.answer(t(user.language_code, "menu.navigation"), reply_markup=main_menu_keyboard(user.language_code))
