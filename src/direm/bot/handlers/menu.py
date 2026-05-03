from dataclasses import dataclass
from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.handlers import credits, delete, language, new, pause_resume, timezone, version
from direm.bot.menu import (
    MENU_ADD,
    MENU_CREDITS,
    MENU_DELETE,
    MENU_HELP,
    MENU_HOME,
    MENU_LANGUAGE,
    MENU_LIST,
    MENU_PAUSE,
    MENU_RESUME,
    MENU_SETTINGS,
    MENU_TIMEZONE,
    MENU_VERSION,
    help_hub_keyboard,
    list_hub_keyboard,
    main_menu_keyboard,
    render_main_menu_text,
    settings_hub_keyboard,
)
from direm.i18n import t
from direm.repositories.users import UserRepository
from direm.services.user_service import TelegramUserProfile, UserService

router = Router(name="menu")


@router.callback_query(F.data.in_({MENU_HOME, MENU_LIST, MENU_SETTINGS, MENU_HELP}))
async def handle_menu_navigation(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await _ensure_user_from_callback(callback, session)
    if user is None:
        await callback.answer(t("ru", "common.no_profile"), show_alert=True)
        return

    if callback.data == MENU_HOME:
        await callback.message.answer(
            render_main_menu_text(user.language_code, user.timezone),
            reply_markup=main_menu_keyboard(user.language_code),
        )
    elif callback.data == MENU_LIST:
        await callback.message.answer(t(user.language_code, "menu.list_hub"), reply_markup=list_hub_keyboard(user.language_code))
    elif callback.data == MENU_SETTINGS:
        await callback.message.answer(t(user.language_code, "menu.settings_hub"), reply_markup=settings_hub_keyboard(user.language_code))
    elif callback.data == MENU_HELP:
        await callback.message.answer(
            t(user.language_code, "menu.help_hub", help_text=t(user.language_code, "help.text")),
            reply_markup=help_hub_keyboard(user.language_code),
        )

    await callback.answer()


@router.callback_query(
    F.data.in_({MENU_ADD, MENU_PAUSE, MENU_RESUME, MENU_DELETE, MENU_LANGUAGE, MENU_TIMEZONE, MENU_VERSION, MENU_CREDITS})
)
async def handle_menu_action(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    if callback.from_user is None or callback.message is None:
        await callback.answer(t("ru", "common.no_profile"), show_alert=True)
        return

    message = CallbackMessageProxy(callback)

    if callback.data == MENU_ADD:
        await new.handle_new_command(message, state, session)
    elif callback.data == MENU_PAUSE:
        await pause_resume.handle_pause_command(message, state, session)
    elif callback.data == MENU_RESUME:
        await pause_resume.handle_resume_command(message, state, session)
    elif callback.data == MENU_DELETE:
        await delete.handle_delete_command(message, state, session)
    elif callback.data == MENU_LANGUAGE:
        await language.handle_language_command(message, session)
    elif callback.data == MENU_TIMEZONE:
        await timezone.handle_timezone_command(message, state, session)
    elif callback.data == MENU_VERSION:
        await version.handle_version(message, session)
    elif callback.data == MENU_CREDITS:
        await credits.handle_credits(message, session)
    else:
        await callback.answer(t("ru", "menu.invalid"), show_alert=True)
        return

    await callback.answer()


@router.callback_query(F.data.startswith("menu:"))
async def handle_stale_menu_callback(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await _ensure_user_from_callback(callback, session)
    language_code = user.language_code if user else "ru"
    await callback.answer(t(language_code, "menu.invalid"), show_alert=True)


@dataclass
class CallbackMessageProxy:
    callback: CallbackQuery

    @property
    def from_user(self):
        return self.callback.from_user

    @property
    def chat(self):
        return self.callback.message.chat

    @property
    def text(self) -> str:
        return ""

    async def answer(self, text: str, **kwargs: Any) -> Any:
        return await self.callback.message.answer(text, **kwargs)


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
