from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.reply_keyboard import action_result_reply_keyboard, flow_reply_keyboard, idle_reply_keyboard
from direm.bot.states import CreateReminderFlow
from direm.domain.constants import ScheduleType
from direm.domain.errors import InvalidActiveWindowError, InvalidScheduleConfigError
from direm.domain.parsing import normalize_message_text, normalize_title, parse_active_window, parse_hh_mm_time, parse_interval_minutes
from direm.i18n import t
from direm.repositories.reminders import ReminderRepository
from direm.repositories.users import UserRepository
from direm.services.reminder_service import CreateReminderRequest, ReminderService
from direm.services.user_service import TelegramUserProfile, UserService

router = Router(name="new")


@router.message(Command("new"))
async def handle_new_command(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    if user is None:
        await message.answer("DIREM needs a Telegram user profile to create reminders.")
        return

    await state.clear()
    await state.update_data(user_id=user.id, timezone=user.timezone, language_code=user.language_code)
    await state.set_state(CreateReminderFlow.waiting_title)
    await message.answer(t(user.language_code, "new.title_prompt"), reply_markup=flow_reply_keyboard(user.language_code))


@router.message(CreateReminderFlow.waiting_title)
async def handle_title(message: Message, state: FSMContext) -> None:
    language_code = await _state_language(state)
    try:
        title = normalize_title(message.text)
    except InvalidScheduleConfigError:
        await message.answer(t(language_code, "new.title_invalid"))
        return

    await state.update_data(title=title)
    await state.set_state(CreateReminderFlow.waiting_message_text)
    await message.answer(t(language_code, "new.message_prompt"))


@router.message(CreateReminderFlow.waiting_message_text)
async def handle_message_text(message: Message, state: FSMContext) -> None:
    language_code = await _state_language(state)
    try:
        message_text = normalize_message_text(message.text)
    except InvalidScheduleConfigError:
        await message.answer(t(language_code, "new.message_invalid"))
        return

    await state.update_data(message_text=message_text)
    await state.set_state(CreateReminderFlow.waiting_schedule_type)
    await message.answer(t(language_code, "new.schedule_prompt"), reply_markup=_schedule_type_keyboard(language_code))


@router.callback_query(CreateReminderFlow.waiting_schedule_type, F.data == "new:schedule:interval")
async def choose_interval(callback: CallbackQuery, state: FSMContext) -> None:
    language_code = await _state_language(state)
    await state.update_data(schedule_type=ScheduleType.INTERVAL.value, daily_time=None)
    await state.set_state(CreateReminderFlow.waiting_interval_minutes)
    await callback.message.answer(t(language_code, "new.interval_prompt"), reply_markup=flow_reply_keyboard(language_code))
    await callback.answer()


@router.callback_query(CreateReminderFlow.waiting_schedule_type, F.data == "new:schedule:daily")
async def choose_daily(callback: CallbackQuery, state: FSMContext) -> None:
    language_code = await _state_language(state)
    await state.update_data(schedule_type=ScheduleType.DAILY.value, interval_minutes=None)
    await state.set_state(CreateReminderFlow.waiting_daily_time)
    await callback.message.answer(t(language_code, "new.daily_prompt"), reply_markup=flow_reply_keyboard(language_code))
    await callback.answer()


@router.message(CreateReminderFlow.waiting_schedule_type)
async def handle_schedule_type_text(message: Message, state: FSMContext) -> None:
    await message.answer(t(await _state_language(state), "new.use_schedule_buttons"))


@router.message(CreateReminderFlow.waiting_interval_minutes)
async def handle_interval_minutes(message: Message, state: FSMContext) -> None:
    language_code = await _state_language(state)
    try:
        interval_minutes = parse_interval_minutes(message.text)
    except InvalidScheduleConfigError:
        await message.answer(t(language_code, "new.interval_invalid"))
        return

    await state.update_data(interval_minutes=interval_minutes)
    await _ask_active_window(message, state)


@router.message(CreateReminderFlow.waiting_daily_time)
async def handle_daily_time(message: Message, state: FSMContext) -> None:
    language_code = await _state_language(state)
    try:
        daily_time = parse_hh_mm_time(message.text)
    except InvalidScheduleConfigError:
        await message.answer(t(language_code, "new.daily_invalid"))
        return

    await state.update_data(daily_time=_format_time(daily_time))
    await _ask_active_window(message, state)


@router.callback_query(CreateReminderFlow.waiting_active_window_choice, F.data == "new:window:none")
async def choose_no_active_window(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(active_from=None, active_to=None)
    await _show_confirmation(callback.message, state)
    await callback.answer()


@router.callback_query(CreateReminderFlow.waiting_active_window_choice, F.data == "new:window:set")
async def choose_set_active_window(callback: CallbackQuery, state: FSMContext) -> None:
    language_code = await _state_language(state)
    await state.set_state(CreateReminderFlow.waiting_active_window_value)
    await callback.message.answer(t(language_code, "new.window_value_prompt"), reply_markup=flow_reply_keyboard(language_code))
    await callback.answer()


@router.message(CreateReminderFlow.waiting_active_window_choice)
async def handle_active_window_choice_text(message: Message, state: FSMContext) -> None:
    await message.answer(t(await _state_language(state), "new.use_window_buttons"))


@router.message(CreateReminderFlow.waiting_active_window_value)
async def handle_active_window_value(message: Message, state: FSMContext) -> None:
    language_code = await _state_language(state)
    try:
        active_from, active_to = parse_active_window(message.text)
    except (InvalidActiveWindowError, InvalidScheduleConfigError):
        await message.answer(t(language_code, "new.window_invalid"))
        return

    await state.update_data(active_from=_format_time(active_from), active_to=_format_time(active_to))
    await _show_confirmation(message, state)


@router.callback_query(CreateReminderFlow.waiting_confirmation, F.data == "new:confirm:create")
async def confirm_create(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user_from_callback(callback, session)
    if user is None:
        await callback.message.answer(t("ru", "common.no_profile"))
        await callback.answer()
        return

    data = await state.get_data()
    request = _build_create_request(data)
    service = ReminderService(ReminderRepository(session))

    try:
        created = await service.create_reminder(user, request)
    except InvalidScheduleConfigError:
        await state.clear()
        await callback.message.answer(t(user.language_code, "new.invalid_config"), reply_markup=idle_reply_keyboard(user.language_code, bunker_active=user.bunker_active))
        await callback.answer()
        return

    await state.clear()
    await callback.message.answer(
        t(user.language_code, "new.created", first_run=_format_local_datetime(created.first_run_at_utc, user.timezone)),
        reply_markup=action_result_reply_keyboard(user.language_code, bunker_active=user.bunker_active),
    )
    await callback.answer()


@router.callback_query(CreateReminderFlow.waiting_confirmation, F.data == "new:confirm:cancel")
async def cancel_create(callback: CallbackQuery, state: FSMContext) -> None:
    language_code = await _state_language(state)
    await state.clear()
    await callback.message.answer(t(language_code, "new.cancelled"), reply_markup=idle_reply_keyboard(language_code))
    await callback.answer()


@router.message(CreateReminderFlow.waiting_confirmation)
async def handle_confirmation_text(message: Message, state: FSMContext) -> None:
    await message.answer(t(await _state_language(state), "new.use_confirmation_buttons"))


async def _ask_active_window(message: Message, state: FSMContext) -> None:
    language_code = await _state_language(state)
    await state.set_state(CreateReminderFlow.waiting_active_window_choice)
    await message.answer(t(language_code, "new.window_prompt"), reply_markup=_active_window_keyboard(language_code))


async def _show_confirmation(message: Message, state: FSMContext) -> None:
    await state.set_state(CreateReminderFlow.waiting_confirmation)
    data = await state.get_data()
    try:
        text = _render_confirmation(data)
    except InvalidScheduleConfigError:
        await state.set_state(CreateReminderFlow.waiting_active_window_value)
        await message.answer(t(data.get("language_code"), "new.window_daily_invalid"))
        return

    await message.answer(text, reply_markup=_confirmation_keyboard(data.get("language_code")))


def _build_create_request(data: dict) -> CreateReminderRequest:
    daily_time = parse_hh_mm_time(data["daily_time"]) if data.get("daily_time") else None
    active_from = parse_hh_mm_time(data["active_from"]) if data.get("active_from") else None
    active_to = parse_hh_mm_time(data["active_to"]) if data.get("active_to") else None
    return CreateReminderRequest(
        title=data["title"],
        message_text=data["message_text"],
        schedule_type=data["schedule_type"],
        interval_minutes=data.get("interval_minutes"),
        daily_time=daily_time,
        active_from=active_from,
        active_to=active_to,
    )


def _render_confirmation(data: dict) -> str:
    schedule = _format_schedule(data)
    active_window = _format_active_window(data)
    first_run = _preview_first_run(data)
    return (
        t(
            data.get("language_code"),
            "new.confirm",
            title=data["title"],
            message_text=data["message_text"],
            schedule=schedule,
            timezone=data["timezone"],
            active_window=active_window,
            first_run=first_run,
        )
    )


def _preview_first_run(data: dict) -> str:
    request = _build_create_request(data)
    user = type("UserPreview", (), {"timezone": data["timezone"]})()
    next_run = ReminderService.__new__(ReminderService).compute_next_run_at(user, request, datetime.now(UTC))
    return _format_local_datetime(next_run, data["timezone"])


def _format_schedule(data: dict) -> str:
    if data["schedule_type"] == ScheduleType.INTERVAL.value:
        return f"every {data['interval_minutes']} minutes"
    return f"daily at {data['daily_time']}"


def _format_active_window(data: dict) -> str:
    if not data.get("active_from"):
        return t(data.get("language_code"), "common.all_day")
    return f"{data['active_from']}-{data['active_to']}"


def _format_local_datetime(value_utc: datetime, timezone: str) -> str:
    return value_utc.astimezone(ZoneInfo(timezone)).strftime("%Y-%m-%d %H:%M %Z")


def _format_time(value) -> str:
    return value.strftime("%H:%M")


def _schedule_type_keyboard(language_code: str | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(language_code, "new.button_interval"), callback_data="new:schedule:interval"),
                InlineKeyboardButton(text=t(language_code, "new.button_daily"), callback_data="new:schedule:daily"),
            ]
        ]
    )


def _active_window_keyboard(language_code: str | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(language_code, "new.button_no_window"), callback_data="new:window:none"),
                InlineKeyboardButton(text=t(language_code, "new.button_set_window"), callback_data="new:window:set"),
            ]
        ]
    )


def _confirmation_keyboard(language_code: str | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(language_code, "new.button_create"), callback_data="new:confirm:create"),
                InlineKeyboardButton(text=t(language_code, "new.button_cancel"), callback_data="new:confirm:cancel"),
            ]
        ]
    )


async def _state_language(state: FSMContext) -> str:
    data = await state.get_data()
    return data.get("language_code", "ru")


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
