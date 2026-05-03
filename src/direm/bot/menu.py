from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from direm.i18n import language_name, t


MENU_HOME = "menu:home"
MENU_LIST = "menu:list"
MENU_SETTINGS = "menu:settings"
MENU_HELP = "menu:help"
MENU_BUNKER = "menu:bunker"

MENU_ADD = "menu:action:new"
MENU_PAUSE = "menu:action:pause"
MENU_RESUME = "menu:action:resume"
MENU_DELETE = "menu:action:delete"
MENU_LANGUAGE = "menu:action:language"
MENU_TIMEZONE = "menu:action:timezone"
MENU_VERSION = "menu:action:version"
MENU_CREDITS = "menu:action:credits"


def render_main_menu_text(language_code: str | None, timezone: str, *, bunker_active: bool = False) -> str:
    return t(
        language_code,
        "menu.main",
        timezone=timezone,
        language=language_name(language_code),
        bunker_status=t(language_code, "bunker.status_active" if bunker_active else "bunker.status_inactive"),
    )


def main_menu_keyboard(language_code: str | None = None, *, bunker_active: bool = False) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(language_code, "menu.button.list"), callback_data=MENU_LIST),
                InlineKeyboardButton(text=t(language_code, "menu.button.settings"), callback_data=MENU_SETTINGS),
                InlineKeyboardButton(text=t(language_code, "menu.button.help"), callback_data=MENU_HELP),
            ],
            [
                InlineKeyboardButton(
                    text=t(language_code, "menu.button.bunker_active" if bunker_active else "menu.button.bunker_inactive"),
                    callback_data=MENU_BUNKER,
                )
            ],
        ]
    )


def list_hub_keyboard(language_code: str | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(language_code, "menu.button.add"), callback_data=MENU_ADD),
                InlineKeyboardButton(text=t(language_code, "menu.button.pause"), callback_data=MENU_PAUSE),
            ],
            [
                InlineKeyboardButton(text=t(language_code, "menu.button.resume"), callback_data=MENU_RESUME),
                InlineKeyboardButton(text=t(language_code, "menu.button.delete"), callback_data=MENU_DELETE),
            ],
            [InlineKeyboardButton(text=t(language_code, "menu.button.back"), callback_data=MENU_HOME)],
        ]
    )


def settings_hub_keyboard(language_code: str | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(language_code, "menu.button.language"), callback_data=MENU_LANGUAGE),
                InlineKeyboardButton(text=t(language_code, "menu.button.timezone"), callback_data=MENU_TIMEZONE),
            ],
            [InlineKeyboardButton(text=t(language_code, "menu.button.back"), callback_data=MENU_HOME)],
        ]
    )


def help_hub_keyboard(language_code: str | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(language_code, "menu.button.version"), callback_data=MENU_VERSION),
                InlineKeyboardButton(text=t(language_code, "menu.button.credits"), callback_data=MENU_CREDITS),
            ],
            [InlineKeyboardButton(text=t(language_code, "menu.button.back"), callback_data=MENU_HOME)],
        ]
    )
