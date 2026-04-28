from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from direm.bot.reply_keyboard import idle_reply_keyboard
from direm.i18n import language_name, supported_language_codes, t
from direm.repositories.users import UserRepository
from direm.services.user_service import TelegramUserProfile, UserService

router = Router(name="language")


@router.message(Command("language"))
async def handle_language_command(message: Message, session: AsyncSession) -> None:
    user = await _ensure_user(message, session)
    if user is None:
        await message.answer(t("ru", "common.no_profile"))
        return

    await message.answer(
        t(user.language_code, "language.prompt", language=language_name(user.language_code)),
        reply_markup=_language_keyboard(),
    )


@router.callback_query(F.data.startswith("language:set:"))
async def handle_language_callback(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await _ensure_user_from_callback(callback, session)
    if user is None:
        await callback.answer(t("ru", "common.no_profile"), show_alert=True)
        return

    language_code = (callback.data or "").rsplit(":", maxsplit=1)[-1]
    if language_code not in supported_language_codes():
        await callback.answer(t(user.language_code, "language.invalid"), show_alert=True)
        return

    service = UserService(UserRepository(session))
    user = await service.update_language(user, language_code)
    await callback.message.answer(
        t(user.language_code, "language.updated", language=language_name(user.language_code)),
        reply_markup=idle_reply_keyboard(user.language_code),
    )
    await callback.answer()


def _language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=language_name(language_code), callback_data=f"language:set:{language_code}")]
            for language_code in supported_language_codes()
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
