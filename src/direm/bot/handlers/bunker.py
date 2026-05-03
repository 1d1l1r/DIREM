import logging
from dataclasses import dataclass
from typing import Any

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.home import answer_home_status
from direm.bot.menu import MENU_HOME
from direm.bot.reply_keyboard import BUNKER_BUTTON_LABELS, idle_reply_keyboard
from direm.domain.errors import InvalidScheduleConfigError
from direm.i18n import t
from direm.repositories.reminders import ReminderRepository
from direm.repositories.users import UserRepository
from direm.services.bunker_service import BunkerService
from direm.services.user_service import TelegramUserProfile, UserService

logger = logging.getLogger(__name__)

router = Router(name="bunker")

BUNKER_ACTIVATE = "bunker:activate"
BUNKER_DEACTIVATE = "bunker:deactivate"


@router.message(Command("bunker"))
async def handle_bunker_command(message: Message, session: AsyncSession) -> None:
    user = await _ensure_user_from_message(message, session)
    if user is None:
        await message.answer(t("ru", "common.no_profile"))
        return

    await answer_bunker_screen(message, user)
    await message.answer(
        t(user.language_code, "bunker.reply_hint"),
        reply_markup=idle_reply_keyboard(user.language_code, bunker_active=user.bunker_active),
    )


@router.message(F.text.in_(BUNKER_BUTTON_LABELS))
async def handle_bunker_reply_toggle(message: Message, session: AsyncSession) -> None:
    user = await _ensure_user_from_message(message, session)
    if user is None:
        await message.answer(t("ru", "common.no_profile"))
        return

    await _toggle_bunker(message, user, session)


@router.callback_query(F.data == BUNKER_ACTIVATE)
async def handle_bunker_activate(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await _ensure_user_from_callback(callback, session)
    if user is None or callback.message is None:
        await callback.answer(t("ru", "common.no_profile"), show_alert=True)
        return

    service = BunkerService(UserRepository(session))
    await service.activate(user)
    await callback.message.answer(
        t(user.language_code, "bunker.activate_done"),
        reply_markup=idle_reply_keyboard(user.language_code, bunker_active=True),
    )
    await answer_home_status(callback.message, user, session)
    await callback.answer()


@router.callback_query(F.data == BUNKER_DEACTIVATE)
async def handle_bunker_deactivate(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await _ensure_user_from_callback(callback, session)
    if user is None or callback.message is None:
        await callback.answer(t("ru", "common.no_profile"), show_alert=True)
        return

    service = BunkerService(UserRepository(session), ReminderRepository(session))
    try:
        result = await service.deactivate_and_reschedule(user)
    except InvalidScheduleConfigError:
        language_code = user.language_code
        user_id = user.id
        await session.rollback()
        logger.exception("Failed to deactivate Bunker for user id=%s because a reminder schedule is invalid.", user_id)
        await callback.message.answer(
            t(language_code, "bunker.deactivate_failed"),
            reply_markup=idle_reply_keyboard(language_code, bunker_active=True),
        )
        await callback.answer(t(language_code, "bunker.deactivate_failed_short"), show_alert=True)
        return

    if result.was_already_inactive:
        await callback.message.answer(
            t(user.language_code, "bunker.already_inactive"),
            reply_markup=idle_reply_keyboard(user.language_code, bunker_active=False),
        )
    else:
        await callback.message.answer(
            t(user.language_code, "bunker.deactivate_done", count=result.rescheduled_count),
            reply_markup=idle_reply_keyboard(user.language_code, bunker_active=False),
        )
    await answer_home_status(callback.message, user, session)
    await callback.answer()


@router.callback_query(F.data.startswith("bunker:"))
async def handle_stale_bunker_callback(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await _ensure_user_from_callback(callback, session)
    language_code = user.language_code if user else "ru"
    await callback.answer(t(language_code, "bunker.invalid"), show_alert=True)


async def answer_bunker_screen(message: Message, user, *, active: bool | None = None) -> None:
    is_active = user.bunker_active if active is None else active
    await message.answer(
        t(user.language_code, "bunker.screen_active" if is_active else "bunker.screen_inactive"),
        reply_markup=bunker_keyboard(user.language_code, is_active),
    )


async def _toggle_bunker(message: Message, user, session: AsyncSession) -> None:
    if user.bunker_active:
        service = BunkerService(UserRepository(session), ReminderRepository(session))
        try:
            result = await service.deactivate_and_reschedule(user)
        except InvalidScheduleConfigError:
            language_code = user.language_code
            user_id = user.id
            await session.rollback()
            logger.exception("Failed to deactivate Bunker for user id=%s because a reminder schedule is invalid.", user_id)
            await message.answer(
                t(language_code, "bunker.deactivate_failed"),
                reply_markup=idle_reply_keyboard(language_code, bunker_active=True),
            )
            return

        if result.was_already_inactive:
            await message.answer(t(user.language_code, "bunker.already_inactive"), reply_markup=idle_reply_keyboard(user.language_code))
        else:
            await message.answer(
                t(user.language_code, "bunker.deactivate_done", count=result.rescheduled_count),
                reply_markup=idle_reply_keyboard(user.language_code, bunker_active=False),
            )
        await answer_home_status(message, user, session)
        return

    await BunkerService(UserRepository(session)).activate(user)
    await message.answer(
        t(user.language_code, "bunker.activate_done"),
        reply_markup=idle_reply_keyboard(user.language_code, bunker_active=True),
    )
    await answer_home_status(message, user, session)


def bunker_keyboard(language_code: str | None, active: bool) -> InlineKeyboardMarkup:
    action_button = InlineKeyboardButton(
        text=t(language_code, "bunker.button_deactivate" if active else "bunker.button_activate"),
        callback_data=BUNKER_DEACTIVATE if active else BUNKER_ACTIVATE,
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [action_button],
            [InlineKeyboardButton(text=t(language_code, "menu.button.back"), callback_data=MENU_HOME)],
        ]
    )


async def _ensure_user_from_message(message: Message, session: AsyncSession):
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

    proxy = CallbackMessageProxy(callback)
    return await _ensure_user_from_message(proxy, session)


@dataclass
class CallbackMessageProxy:
    callback: CallbackQuery

    @property
    def from_user(self):
        return self.callback.from_user

    @property
    def chat(self):
        return self.callback.message.chat

    async def answer(self, text: str, **kwargs: Any) -> Any:
        return await self.callback.message.answer(text, **kwargs)
