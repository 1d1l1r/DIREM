from types import SimpleNamespace

from direm.bot.handlers.delete import _delete_confirmation_keyboard, _delete_keyboard, _parse_callback_id as parse_delete_id
from direm.bot.handlers.pause_resume import _parse_callback_id as parse_pause_resume_id
from direm.bot.handlers.pause_resume import _reminder_keyboard
from direm.services.reminder_control_service import SelectableReminder


def selectable(public_number: int, reminder_id: int, title: str) -> SelectableReminder:
    reminder = SimpleNamespace(id=reminder_id, title=title)
    return SelectableReminder(public_number=public_number, reminder=reminder)


def test_pause_resume_keyboard_uses_action_and_reminder_id() -> None:
    keyboard = _reminder_keyboard("pause", [selectable(1, 42, "Focus")])

    button = keyboard.inline_keyboard[0][0]
    assert button.text == "1. Focus"
    assert button.callback_data == "control:pause:42"


def test_delete_keyboard_and_confirmation_callbacks() -> None:
    keyboard = _delete_keyboard([selectable(2, 77, "Clean")])
    confirm_keyboard = _delete_confirmation_keyboard(77)

    assert keyboard.inline_keyboard[0][0].callback_data == "control:delete:77"
    assert confirm_keyboard.inline_keyboard[0][0].callback_data == "control:delete_confirm:77"
    assert confirm_keyboard.inline_keyboard[0][1].callback_data == "control:delete_cancel"


def test_callback_id_parser_rejects_invalid_data() -> None:
    assert parse_pause_resume_id("control:pause:42") == 42
    assert parse_pause_resume_id("control:pause:abc") is None
    assert parse_pause_resume_id(None) is None
    assert parse_delete_id("control:delete_confirm:77") == 77
    assert parse_delete_id("control:delete:bad") is None
