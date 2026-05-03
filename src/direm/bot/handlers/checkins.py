from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.checkin_buttons import CHECKIN_CALLBACK_PREFIX, parse_checkin_callback_data
from direm.i18n import t
from direm.repositories.checkins import ReminderCheckInRepository
from direm.repositories.users import UserRepository
from direm.services.checkin_service import (
    CheckInDeliveryNotFoundError,
    CheckInValidationError,
    ReminderCheckInService,
)
from direm.services.user_service import TelegramUserProfile, UserService

router = Router(name="checkins")


@router.callback_query(F.data.startswith(f"{CHECKIN_CALLBACK_PREFIX}:"))
async def handle_checkin_callback(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await _ensure_user_from_callback(callback, session)
    language_code = user.language_code if user else "ru"
    parsed = parse_checkin_callback_data(callback.data)
    if user is None or parsed is None:
        await callback.answer(t(language_code, "checkin.invalid"), show_alert=True)
        return

    delivery_id, response_type = parsed
    try:
        await ReminderCheckInService(ReminderCheckInRepository(session)).record_response(
            user_id=user.id,
            delivery_id=delivery_id,
            response_type=response_type,
        )
    except (CheckInDeliveryNotFoundError, CheckInValidationError):
        await callback.answer(t(language_code, "checkin.invalid"), show_alert=True)
        return

    await callback.answer(t(language_code, f"checkin.confirm.{response_type}"))


async def _ensure_user_from_callback(callback: CallbackQuery, session: AsyncSession):
    if callback.from_user is None or callback.message is None:
        return None

    service = UserService(UserRepository(session))
    return await service.register_or_update_from_telegram(
        TelegramUserProfile(
            telegram_user_id=callback.from_user.id,
            chat_id=callback.message.chat.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            language_code=callback.from_user.language_code,
        )
    )
