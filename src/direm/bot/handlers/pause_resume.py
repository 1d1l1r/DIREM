from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.reply_keyboard import flow_reply_keyboard, idle_reply_keyboard
from direm.bot.states import ReminderControlFlow
from direm.domain.constants import ReminderStatus
from direm.domain.errors import InvalidScheduleConfigError
from direm.i18n import t
from direm.repositories.reminders import ReminderRepository
from direm.repositories.users import UserRepository
from direm.services.reminder_control_service import ReminderControlService, ReminderSelectionError
from direm.services.user_service import TelegramUserProfile, UserService

router = Router(name="pause_resume")


@router.message(Command("pause"))
async def handle_pause_command(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    if user is None:
        await message.answer(t("ru", "pause.no_profile"))
        return

    service = ReminderControlService(ReminderRepository(session))
    selectable = await service.list_selectable_for_user(user, status=ReminderStatus.ACTIVE.value)
    await message.answer(
        service.render_selection_prompt(t(user.language_code, "control.pause_action"), selectable, user.timezone, user.language_code),
        reply_markup=_reminder_keyboard("pause", selectable) if selectable else idle_reply_keyboard(user.language_code),
    )
    if selectable:
        await state.set_state(ReminderControlFlow.waiting_pause_selection)
        await message.answer(t(user.language_code, "keyboard.cancel_hint"), reply_markup=flow_reply_keyboard(user.language_code))


@router.message(Command("resume"))
async def handle_resume_command(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    if user is None:
        await message.answer(t("ru", "resume.no_profile"))
        return

    service = ReminderControlService(ReminderRepository(session))
    selectable = await service.list_selectable_for_user(user, status=ReminderStatus.PAUSED.value)
    await message.answer(
        service.render_selection_prompt(t(user.language_code, "control.resume_action"), selectable, user.timezone, user.language_code),
        reply_markup=_reminder_keyboard("resume", selectable) if selectable else idle_reply_keyboard(user.language_code),
    )
    if selectable:
        await state.set_state(ReminderControlFlow.waiting_resume_selection)
        await message.answer(t(user.language_code, "keyboard.cancel_hint"), reply_markup=flow_reply_keyboard(user.language_code))


@router.message(ReminderControlFlow.waiting_pause_selection)
async def handle_pause_selection(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    if user is None:
        await message.answer(t("ru", "pause.no_profile"))
        return

    service = ReminderControlService(ReminderRepository(session))
    try:
        reminder = await service.pause_for_user(user, message.text or "")
    except ReminderSelectionError:
        await message.answer(t(user.language_code, "common.invalid_selection"))
        return

    await state.clear()
    await message.answer(t(user.language_code, "pause.done", title=reminder.title), reply_markup=idle_reply_keyboard(user.language_code, bunker_active=user.bunker_active))


@router.message(ReminderControlFlow.waiting_resume_selection)
async def handle_resume_selection(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    if user is None:
        await message.answer(t("ru", "resume.no_profile"))
        return

    service = ReminderControlService(ReminderRepository(session))
    try:
        reminder = await service.resume_for_user(user, message.text or "")
    except ReminderSelectionError:
        await message.answer(t(user.language_code, "common.invalid_selection"))
        return
    except InvalidScheduleConfigError:
        await state.clear()
        await message.answer(t(user.language_code, "resume.invalid_schedule"), reply_markup=idle_reply_keyboard(user.language_code, bunker_active=user.bunker_active))
        return

    await state.clear()
    await message.answer(t(user.language_code, "resume.done", title=reminder.title), reply_markup=idle_reply_keyboard(user.language_code, bunker_active=user.bunker_active))


@router.callback_query(F.data.startswith("control:pause:"))
async def handle_pause_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user_from_callback(callback, session)
    if user is None:
        await callback.answer(t("ru", "common.no_profile"), show_alert=True)
        return

    reminder_id = _parse_callback_id(callback.data)
    if reminder_id is None:
        await callback.answer(t(user.language_code, "common.invalid_selection"), show_alert=True)
        return

    service = ReminderControlService(ReminderRepository(session))
    try:
        reminder = await service.pause_for_user(user, str(reminder_id))
    except ReminderSelectionError:
        await callback.answer(t(user.language_code, "common.not_found"), show_alert=True)
        return

    await state.clear()
    await callback.message.answer(t(user.language_code, "pause.done", title=reminder.title), reply_markup=idle_reply_keyboard(user.language_code, bunker_active=user.bunker_active))
    await callback.answer()


@router.callback_query(F.data.startswith("control:resume:"))
async def handle_resume_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user_from_callback(callback, session)
    if user is None:
        await callback.answer(t("ru", "common.no_profile"), show_alert=True)
        return

    reminder_id = _parse_callback_id(callback.data)
    if reminder_id is None:
        await callback.answer(t(user.language_code, "common.invalid_selection"), show_alert=True)
        return

    service = ReminderControlService(ReminderRepository(session))
    try:
        reminder = await service.resume_for_user(user, str(reminder_id))
    except ReminderSelectionError:
        await callback.answer(t(user.language_code, "common.not_found"), show_alert=True)
        return
    except InvalidScheduleConfigError:
        await state.clear()
        await callback.message.answer(t(user.language_code, "resume.invalid_schedule"), reply_markup=idle_reply_keyboard(user.language_code, bunker_active=user.bunker_active))
        await callback.answer()
        return

    await state.clear()
    await callback.message.answer(t(user.language_code, "resume.done", title=reminder.title), reply_markup=idle_reply_keyboard(user.language_code, bunker_active=user.bunker_active))
    await callback.answer()


def _reminder_keyboard(action: str, selectable) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{item.public_number}. {item.reminder.title}", callback_data=f"control:{action}:{item.reminder.id}")]
            for item in selectable
        ]
    )


def _parse_callback_id(data: str | None) -> int | None:
    if not data:
        return None
    raw_id = data.rsplit(":", maxsplit=1)[-1]
    if not raw_id.isdigit():
        return None
    return int(raw_id)


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
