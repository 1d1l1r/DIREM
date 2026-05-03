from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.reply_keyboard import action_result_reply_keyboard, flow_reply_keyboard
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

REGION_TIMEZONES = {
    "kazakhstan": (
        ("Asia/Almaty", "Asia/Almaty"),
        ("Asia/Aqtau", "Asia/Aqtau"),
        ("Asia/Aqtobe", "Asia/Aqtobe"),
        ("Asia/Oral", "Asia/Oral"),
        ("Asia/Qyzylorda", "Asia/Qyzylorda"),
    ),
    "russia": (
        ("Moscow", "Europe/Moscow"),
        ("Yekaterinburg", "Asia/Yekaterinburg"),
        ("Novosibirsk", "Asia/Novosibirsk"),
        ("Krasnoyarsk", "Asia/Krasnoyarsk"),
        ("Irkutsk", "Asia/Irkutsk"),
        ("Yakutsk", "Asia/Yakutsk"),
        ("Vladivostok", "Asia/Vladivostok"),
        ("Kamchatka", "Asia/Kamchatka"),
    ),
    "europe": (
        ("London", "Europe/London"),
        ("Berlin / Paris / Rome", "Europe/Berlin"),
        ("Warsaw", "Europe/Warsaw"),
        ("Helsinki", "Europe/Helsinki"),
        ("Istanbul", "Europe/Istanbul"),
    ),
    "asia": (
        ("Tashkent", "Asia/Tashkent"),
        ("Dubai", "Asia/Dubai"),
        ("Tbilisi", "Asia/Tbilisi"),
        ("Tokyo", "Asia/Tokyo"),
        ("Seoul", "Asia/Seoul"),
        ("Shanghai", "Asia/Shanghai"),
        ("Singapore", "Asia/Singapore"),
        ("Bangkok", "Asia/Bangkok"),
    ),
    "america": (
        ("New York", "America/New_York"),
        ("Chicago", "America/Chicago"),
        ("Denver", "America/Denver"),
        ("Los Angeles", "America/Los_Angeles"),
        ("Toronto", "America/Toronto"),
        ("Mexico City", "America/Mexico_City"),
        ("Sao Paulo", "America/Sao_Paulo"),
    ),
}

REGION_KEYS = (*REGION_TIMEZONES.keys(), "utc")
CURATED_TIMEZONES = frozenset(
    timezone
    for options in REGION_TIMEZONES.values()
    for _, timezone in options
) | frozenset(COMMON_TIMEZONES)


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

    if data == "timezone:other":
        await callback.message.answer(
            t(user.language_code, "timezone.region_prompt"),
            reply_markup=_region_keyboard(user.language_code),
        )
        await callback.answer()
        return

    if data == "timezone:back":
        await callback.message.answer(
            t(user.language_code, "timezone.picker_prompt"),
            reply_markup=_timezone_keyboard(user.language_code),
        )
        await callback.answer()
        return

    if data.startswith("timezone:region:"):
        region = data.removeprefix("timezone:region:")
        if region not in REGION_KEYS:
            await callback.answer(t(user.language_code, "timezone.callback_invalid"), show_alert=True)
            return
        if region == "utc":
            await callback.message.answer(
                t(user.language_code, "timezone.utc_explain"),
                reply_markup=_utc_keyboard(user.language_code),
            )
        else:
            await callback.message.answer(
                t(user.language_code, "timezone.region_list_prompt", region=t(user.language_code, f"timezone.region.{region}")),
                reply_markup=_region_timezone_keyboard(region, user.language_code),
            )
        await callback.answer()
        return

    if not data.startswith("timezone:set:"):
        await callback.answer(t(user.language_code, "timezone.callback_invalid"), show_alert=True)
        return

    timezone = data.removeprefix("timezone:set:")
    if timezone not in CURATED_TIMEZONES:
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
        t(user.language_code, "timezone.updated", timezone=_timezone_display_name(user.timezone, user.language_code)),
        reply_markup=action_result_reply_keyboard(user.language_code, bunker_active=user.bunker_active),
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
        await message.answer(
            t(user.language_code, "timezone.picker_prompt"),
            reply_markup=_timezone_keyboard(user.language_code),
        )
        return

    await state.clear()
    await message.answer(
        t(user.language_code, "timezone.updated", timezone=_timezone_display_name(user.timezone, user.language_code)),
        reply_markup=action_result_reply_keyboard(user.language_code, bunker_active=user.bunker_active),
    )


def _timezone_keyboard(language_code: str | None = None) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=_timezone_button_text(timezone, language_code), callback_data=f"timezone:set:{timezone}")]
        for timezone in COMMON_TIMEZONES
    ]
    rows.append([InlineKeyboardButton(text=t(language_code, "timezone.other_button"), callback_data="timezone:other")])
    rows.append([InlineKeyboardButton(text=t(language_code, "timezone.manual_button"), callback_data="timezone:manual")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _timezone_button_text(timezone: str, language_code: str | None = None) -> str:
    if timezone == "UTC":
        return t(language_code, "timezone.utc_label")
    return timezone


def _region_keyboard(language_code: str | None = None) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=t(language_code, f"timezone.region.{region}"), callback_data=f"timezone:region:{region}")]
        for region in REGION_KEYS
    ]
    rows.append([InlineKeyboardButton(text=t(language_code, "timezone.back_button"), callback_data="timezone:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _region_timezone_keyboard(region: str, language_code: str | None = None) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=_format_region_timezone_button(label, timezone), callback_data=f"timezone:set:{timezone}")]
        for label, timezone in REGION_TIMEZONES[region]
    ]
    rows.append([InlineKeyboardButton(text=t(language_code, "timezone.back_button"), callback_data="timezone:other")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _utc_keyboard(language_code: str | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(language_code, "timezone.utc_label"), callback_data="timezone:set:UTC")],
            [InlineKeyboardButton(text=t(language_code, "timezone.back_button"), callback_data="timezone:other")],
        ]
    )


def _format_region_timezone_button(label: str, timezone: str) -> str:
    if label == timezone:
        return timezone
    return f"{label} - {timezone}"


def _timezone_display_name(timezone: str, language_code: str | None = None) -> str:
    if timezone == "UTC":
        return t(language_code, "timezone.utc_label")
    return timezone


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
