from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.states import ReminderControlFlow
from direm.repositories.reminders import ReminderRepository
from direm.repositories.users import UserRepository
from direm.services.reminder_control_service import ReminderControlService, ReminderSelectionError
from direm.services.user_service import TelegramUserProfile, UserService

router = Router(name="delete")


@router.message(Command("delete"))
async def handle_delete_command(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    if user is None:
        await message.answer("DIREM needs a Telegram user profile to delete reminders.")
        return

    service = ReminderControlService(ReminderRepository(session))
    selectable = await service.list_selectable_for_user(user)
    await message.answer(
        service.render_selection_prompt("delete", selectable, user.timezone),
        reply_markup=_delete_keyboard(selectable) if selectable else None,
    )
    if selectable:
        await state.set_state(ReminderControlFlow.waiting_delete_selection)


@router.message(ReminderControlFlow.waiting_delete_selection)
async def handle_delete_selection(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    if user is None:
        await message.answer("DIREM needs a Telegram user profile to delete reminders.")
        return

    service = ReminderControlService(ReminderRepository(session))
    try:
        reminder = await service.select_for_user(user, message.text or "")
    except ReminderSelectionError:
        await message.answer("Invalid reminder selection. Send a reminder number or id from the list.")
        return

    await state.update_data(delete_reminder_id=reminder.id)
    await state.set_state(ReminderControlFlow.waiting_delete_confirmation)
    await message.answer(
        f"Delete reminder?\n"
        f"Title: {reminder.title}\n"
        f"Id: {reminder.id}\n\n"
        "Send yes to confirm or no to cancel."
    )


@router.message(ReminderControlFlow.waiting_delete_confirmation)
async def handle_delete_confirmation(message: Message, state: FSMContext, session: AsyncSession) -> None:
    answer = (message.text or "").strip().lower()
    if answer in {"no", "n", "cancel"}:
        await state.clear()
        await message.answer("Delete cancelled.")
        return

    if answer not in {"yes", "y", "delete", "confirm"}:
        await message.answer("Send yes to confirm deletion or no to cancel.")
        return

    user = await _ensure_user(message, session)
    if user is None:
        await message.answer("DIREM needs a Telegram user profile to delete reminders.")
        return

    data = await state.get_data()
    reminder_id = data.get("delete_reminder_id")
    if reminder_id is None:
        await state.clear()
        await message.answer("Delete selection expired. Send /delete to choose again.")
        return

    service = ReminderControlService(ReminderRepository(session))
    try:
        reminder = await service.delete_for_user(user, str(reminder_id))
    except ReminderSelectionError:
        await state.clear()
        await message.answer("Reminder not found for current user. Send /delete to choose again.")
        return

    await state.clear()
    await message.answer(f"Reminder deleted: {reminder.title}")


@router.callback_query(F.data.startswith("control:delete:"))
async def handle_delete_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user_from_callback(callback, session)
    if user is None:
        await callback.answer("DIREM needs a Telegram user profile.", show_alert=True)
        return

    reminder_id = _parse_callback_id(callback.data)
    if reminder_id is None:
        await callback.answer("Invalid reminder selection.", show_alert=True)
        return

    service = ReminderControlService(ReminderRepository(session))
    try:
        reminder = await service.select_for_user(user, str(reminder_id))
    except ReminderSelectionError:
        await callback.answer("Reminder not found.", show_alert=True)
        return

    await state.update_data(delete_reminder_id=reminder.id)
    await state.set_state(ReminderControlFlow.waiting_delete_confirmation)
    await callback.message.answer(
        f"Delete reminder?\n"
        f"Title: {reminder.title}\n"
        f"Id: {reminder.id}",
        reply_markup=_delete_confirmation_keyboard(reminder.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("control:delete_confirm:"))
async def handle_delete_confirm_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    user = await _ensure_user_from_callback(callback, session)
    if user is None:
        await callback.answer("DIREM needs a Telegram user profile.", show_alert=True)
        return

    reminder_id = _parse_callback_id(callback.data)
    if reminder_id is None:
        await state.clear()
        await callback.answer("Invalid reminder selection.", show_alert=True)
        return

    service = ReminderControlService(ReminderRepository(session))
    try:
        reminder = await service.delete_for_user(user, str(reminder_id))
    except ReminderSelectionError:
        await state.clear()
        await callback.answer("Reminder not found.", show_alert=True)
        return

    await state.clear()
    await callback.message.answer(f"Reminder deleted: {reminder.title}")
    await callback.answer()


@router.callback_query(F.data == "control:delete_cancel")
async def handle_delete_cancel_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("Delete cancelled.")
    await callback.answer()


def _delete_keyboard(selectable) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{item.public_number}. {item.reminder.title}", callback_data=f"control:delete:{item.reminder.id}")]
            for item in selectable
        ]
    )


def _delete_confirmation_keyboard(reminder_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Confirm delete", callback_data=f"control:delete_confirm:{reminder_id}"),
                InlineKeyboardButton(text="Cancel", callback_data="control:delete_cancel"),
            ]
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
