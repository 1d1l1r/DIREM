from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from direm.i18n import supported_language_codes, t


HELP_BUTTON_LABELS = tuple(t(language_code, "keyboard.help") for language_code in supported_language_codes())
CANCEL_BUTTON_LABELS = tuple(t(language_code, "keyboard.cancel") for language_code in supported_language_codes())


def idle_reply_keyboard(language_code: str | None = None) -> ReplyKeyboardMarkup:
    return _single_button_keyboard(t(language_code, "keyboard.help"))


def flow_reply_keyboard(language_code: str | None = None) -> ReplyKeyboardMarkup:
    return _single_button_keyboard(t(language_code, "keyboard.cancel"))


def _single_button_keyboard(text: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=text)]], resize_keyboard=True)
