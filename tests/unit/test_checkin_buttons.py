from direm.bot.checkin_buttons import build_checkin_callback_data, checkin_keyboard, parse_checkin_callback_data


def test_checkin_keyboard_uses_delivery_id_and_localized_labels() -> None:
    keyboard = checkin_keyboard("en", 42)

    buttons = keyboard.inline_keyboard[0]
    assert [button.text for button in buttons] == ["Done", "Later", "Skipped"]
    assert [button.callback_data for button in buttons] == [
        "checkin:42:done",
        "checkin:42:later",
        "checkin:42:skipped",
    ]


def test_parse_checkin_callback_data_accepts_valid_data() -> None:
    assert parse_checkin_callback_data(build_checkin_callback_data(42, "later")) == (42, "later")


def test_parse_checkin_callback_data_rejects_invalid_data() -> None:
    assert parse_checkin_callback_data(None) is None
    assert parse_checkin_callback_data("checkin:abc:done") is None
    assert parse_checkin_callback_data("checkin:0:done") is None
    assert parse_checkin_callback_data("checkin:42:snooze") is None
    assert parse_checkin_callback_data("other:42:done") is None
