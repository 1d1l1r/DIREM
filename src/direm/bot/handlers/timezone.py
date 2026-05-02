from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.reply_keyboard import flow_reply_keyboard, idle_reply_keyboard
from direm.bot.states import TimezoneFlow
from direm.domain.errors import InvalidTimezoneError
from direm.i18n import t
from direm.repositories.users import UserRepository
from direm.services.user_service import TelegramUserProfile, UserService

router = Router(name="timezone")

COMMON_TIMEZONES = (
    "Asia/Almaty",
    "Asia/Aqtau",
    "Asia/Aqtobe",
    "Asia/Oral",
    "Asia/Qyzylorda",
    "UTC",
)


@router.message(Command("timezone"))
async def handle_timezone_command(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    if user is None:
        await message.answer(t("ru", "common.no_profile"))
        return

    await state.set_state(TimezoneFlow.waiting_for_timezone)
    await message.answer(
        t(user.language_code, "timezone.prompt", timezone=user.timezone),
        reply_markup=flow_reply_keyboard(user.language_code),
    )
    await message.answer(
        t(user.language_code, "timezone.picker_prompt"),
        reply_markup=_timezone_keyboard(user.language_code),
    )


@router.callback_query(F.data.startswith("timezone:"))
async def handle_timezone_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user_from_callback(callback, session)
    if user is None:
        await callback.answer(t("ru", "common.no_profile"), show_alert=True)
        return

    data = callback.data or ""
    if data == "timezone:manual":
        await state.set_state(TimezoneFlow.waiting_for_timezone)
        await callback.message.answer(
            t(user.language_code, "timezone.manual_prompt", timezone=user.timezone),
            reply_markup=flow_reply_keyboard(user.language_code),
        )
        await callback.answer()
        return

    if not data.startswith("timezone:set:"):
        await callback.answer(t(user.language_code, "timezone.callback_invalid"), show_alert=True)
        return

    timezone = data.removeprefix("timezone:set:")
    if timezone not in COMMON_TIMEZONES:
        await callback.answer(t(user.language_code, "timezone.callback_invalid"), show_alert=True)
        return

    service = UserService(UserRepository(session))
    try:
        user = await service.update_timezone(user, timezone)
    except InvalidTimezoneError:
        await callback.answer(t(user.language_code, "timezone.callback_invalid"), show_alert=True)
        return

    await state.clear()
    await callback.message.answer(
        t(user.language_code, "timezone.updated", timezone=user.timezone),
        reply_markup=idle_reply_keyboard(user.language_code),
    )
    await callback.answer()


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
        await message.answer(
            t(user.language_code, "timezone.invalid"),
            reply_markup=flow_reply_keyboard(user.language_code),
        )
        return

    await state.clear()
    await message.answer(t(user.language_code, "timezone.updated", timezone=user.timezone), reply_markup=idle_reply_keyboard(user.language_code))


def _timezone_keyboard(language_code: str | None = None) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=timezone, callback_data=f"timezone:set:{timezone}")]
        for timezone in COMMON_TIMEZONES
    ]
    rows.append([InlineKeyboardButton(text=t(language_code, "timezone.manual_button"), callback_data="timezone:manual")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


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
