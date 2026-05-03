from types import SimpleNamespace

from direm.bot.handlers.help import handle_help_button
from direm.bot.reply_keyboard import (
    BUNKER_BUTTON_LABELS,
    CANCEL_BUTTON_LABELS,
    HELP_BUTTON_LABELS,
    MAIN_MENU_BUTTON_LABELS,
    action_result_reply_keyboard,
    flow_reply_keyboard,
    idle_reply_keyboard,
)


class FakeMessage:
    def __init__(self, text: str = "Help") -> None:
        self.text = text
        self.from_user = None
        self.chat = SimpleNamespace(id=2001)
        self.answers: list[tuple[str, object | None]] = []

    async def answer(self, text: str, **kwargs) -> None:
        self.answers.append((text, kwargs.get("reply_markup")))


class Session:
    pass


def test_reply_keyboard_labels_are_localized() -> None:
    assert HELP_BUTTON_LABELS == ("Помощь", "Көмек", "Help")
    assert CANCEL_BUTTON_LABELS == ("Отмена", "Болдырмау", "Cancel")
    assert BUNKER_BUTTON_LABELS == ("Бункер OFF", "Бункер ON", "Бункер OFF", "Бункер ON", "Bunker OFF", "Bunker ON")
    assert MAIN_MENU_BUTTON_LABELS == ("Главное меню", "Басты мәзір", "Main menu")


def test_idle_reply_keyboard_shows_bunker_button() -> None:
    keyboard = idle_reply_keyboard("kk")

    assert keyboard.keyboard[0][0].text == "Бункер OFF"
    assert keyboard.resize_keyboard is True


def test_idle_reply_keyboard_reflects_bunker_state() -> None:
    assert idle_reply_keyboard("en", bunker_active=False).keyboard[0][0].text == "Bunker OFF"
    assert idle_reply_keyboard("en", bunker_active=True).keyboard[0][0].text == "Bunker ON"


def test_flow_reply_keyboard_shows_cancel_button() -> None:
    keyboard = flow_reply_keyboard("en")

    assert keyboard.keyboard[0][0].text == "Cancel"
    assert keyboard.resize_keyboard is True


def test_action_result_reply_keyboard_shows_bunker_and_main_menu() -> None:
    keyboard = action_result_reply_keyboard("en", bunker_active=True)

    assert keyboard.keyboard[0][0].text == "Bunker ON"
    assert keyboard.keyboard[1][0].text == "Main menu"
    assert keyboard.resize_keyboard is True


async def test_help_button_renders_same_help_with_idle_keyboard() -> None:
    message = FakeMessage("Help")

    await handle_help_button(message, Session())

    assert "Основное:" in message.answers[0][0]
    assert message.answers[0][1].keyboard[0][0].text == "Бункер OFF"
