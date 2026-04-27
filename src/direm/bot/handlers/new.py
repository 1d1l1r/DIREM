from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.states import CreateReminderFlow
from direm.domain.constants import ScheduleType
from direm.domain.errors import InvalidActiveWindowError, InvalidScheduleConfigError
from direm.domain.parsing import normalize_message_text, normalize_title, parse_active_window, parse_hh_mm_time, parse_interval_minutes
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
    await state.update_data(user_id=user.id, timezone=user.timezone)
    await state.set_state(CreateReminderFlow.waiting_title)
    await message.answer(
        "Create reminder.\n\n"
        "Send a short title.\n"
        "Example: Dorpheus focus"
    )


@router.message(CreateReminderFlow.waiting_title)
async def handle_title(message: Message, state: FSMContext) -> None:
    try:
        title = normalize_title(message.text)
    except InvalidScheduleConfigError:
        await message.answer("Title is required. Keep it short, up to 80 characters.")
        return

    await state.update_data(title=title)
    await state.set_state(CreateReminderFlow.waiting_message_text)
    await message.answer("Send the reminder message text.")


@router.message(CreateReminderFlow.waiting_message_text)
async def handle_message_text(message: Message, state: FSMContext) -> None:
    try:
        message_text = normalize_message_text(message.text)
    except InvalidScheduleConfigError:
        await message.answer("Message text is required. Keep it up to 1000 characters.")
        return

    await state.update_data(message_text=message_text)
    await state.set_state(CreateReminderFlow.waiting_schedule_type)
    await message.answer("Choose schedule type.", reply_markup=_schedule_type_keyboard())


@router.callback_query(CreateReminderFlow.waiting_schedule_type, F.data == "new:schedule:interval")
async def choose_interval(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(schedule_type=ScheduleType.INTERVAL.value, daily_time=None)
    await state.set_state(CreateReminderFlow.waiting_interval_minutes)
    await callback.message.answer("Send interval in minutes.\nExample: 45")
    await callback.answer()


@router.callback_query(CreateReminderFlow.waiting_schedule_type, F.data == "new:schedule:daily")
async def choose_daily(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(schedule_type=ScheduleType.DAILY.value, interval_minutes=None)
    await state.set_state(CreateReminderFlow.waiting_daily_time)
    await callback.message.answer("Send daily local time in HH:MM format.\nExamples: 09:00, 22:30")
    await callback.answer()


@router.message(CreateReminderFlow.waiting_schedule_type)
async def handle_schedule_type_text(message: Message) -> None:
    await message.answer("Use the schedule type buttons, or send /cancel to stop creating this reminder.")


@router.message(CreateReminderFlow.waiting_interval_minutes)
async def handle_interval_minutes(message: Message, state: FSMContext) -> None:
    try:
        interval_minutes = parse_interval_minutes(message.text)
    except InvalidScheduleConfigError:
        await message.answer("Send a positive integer from 1 to 1440.\nExample: 45")
        return

    await state.update_data(interval_minutes=interval_minutes)
    await _ask_active_window(message, state)


@router.message(CreateReminderFlow.waiting_daily_time)
async def handle_daily_time(message: Message, state: FSMContext) -> None:
    try:
        daily_time = parse_hh_mm_time(message.text)
    except InvalidScheduleConfigError:
        await message.answer("Send a valid time in HH:MM format.\nExample: 22:30")
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
    await state.set_state(CreateReminderFlow.waiting_active_window_value)
    await callback.message.answer("Send active window as HH:MM-HH:MM.\nExample: 10:00-18:00")
    await callback.answer()


@router.message(CreateReminderFlow.waiting_active_window_choice)
async def handle_active_window_choice_text(message: Message) -> None:
    await message.answer("Use the active window buttons, or send /cancel to stop creating this reminder.")


@router.message(CreateReminderFlow.waiting_active_window_value)
async def handle_active_window_value(message: Message, state: FSMContext) -> None:
    try:
        active_from, active_to = parse_active_window(message.text)
    except (InvalidActiveWindowError, InvalidScheduleConfigError):
        await message.answer("Invalid active window. Use same-day HH:MM-HH:MM, for example: 10:00-18:00.")
        return

    await state.update_data(active_from=_format_time(active_from), active_to=_format_time(active_to))
    await _show_confirmation(message, state)


@router.callback_query(CreateReminderFlow.waiting_confirmation, F.data == "new:confirm:create")
async def confirm_create(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user_from_callback(callback, session)
    if user is None:
        await callback.message.answer("DIREM needs a Telegram user profile to create reminders.")
        await callback.answer()
        return

    data = await state.get_data()
    request = _build_create_request(data)
    service = ReminderService(ReminderRepository(session))

    try:
        created = await service.create_reminder(user, request)
    except InvalidScheduleConfigError:
        await callback.message.answer("Reminder configuration is invalid. Start again with /new.")
        await state.clear()
        await callback.answer()
        return

    await state.clear()
    await callback.message.answer(
        "Reminder created.\n"
        f"First run: {_format_local_datetime(created.first_run_at_utc, user.timezone)}"
    )
    await callback.answer()


@router.callback_query(CreateReminderFlow.waiting_confirmation, F.data == "new:confirm:cancel")
async def cancel_create(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("Reminder creation cancelled.")
    await callback.answer()


@router.message(CreateReminderFlow.waiting_confirmation)
async def handle_confirmation_text(message: Message) -> None:
    await message.answer("Use the confirmation buttons, or send /cancel to stop creating this reminder.")


async def _ask_active_window(message: Message, state: FSMContext) -> None:
    await state.set_state(CreateReminderFlow.waiting_active_window_choice)
    await message.answer("Add active window?", reply_markup=_active_window_keyboard())


async def _show_confirmation(message: Message, state: FSMContext) -> None:
    await state.set_state(CreateReminderFlow.waiting_confirmation)
    data = await state.get_data()
    try:
        text = _render_confirmation(data)
    except InvalidScheduleConfigError:
        await state.set_state(CreateReminderFlow.waiting_active_window_value)
        await message.answer("Daily time must be inside the active window. Send another window, for example: 10:00-18:00.")
        return

    await message.answer(text, reply_markup=_confirmation_keyboard())


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
        "Create reminder?\n\n"
        f"Title: {data['title']}\n"
        f"Message: {data['message_text']}\n"
        f"Schedule: {schedule}\n"
        f"Timezone: {data['timezone']}\n"
        f"Active window: {active_window}\n"
        f"First run: {first_run}"
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
        return "all day"
    return f"{data['active_from']}-{data['active_to']}"


def _format_local_datetime(value_utc: datetime, timezone: str) -> str:
    return value_utc.astimezone(ZoneInfo(timezone)).strftime("%Y-%m-%d %H:%M %Z")


def _format_time(value) -> str:
    return value.strftime("%H:%M")


def _schedule_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Interval", callback_data="new:schedule:interval"),
                InlineKeyboardButton(text="Daily time", callback_data="new:schedule:daily"),
            ]
        ]
    )


def _active_window_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="No active window", callback_data="new:window:none"),
                InlineKeyboardButton(text="Set active window", callback_data="new:window:set"),
            ]
        ]
    )


def _confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Create", callback_data="new:confirm:create"),
                InlineKeyboardButton(text="Cancel", callback_data="new:confirm:cancel"),
            ]
        ]
    )


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
        )
    )
