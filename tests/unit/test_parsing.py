from datetime import time

import pytest

from direm.domain.errors import InvalidActiveWindowError, InvalidScheduleConfigError
from direm.domain.parsing import (
    normalize_message_text,
    normalize_title,
    parse_active_window,
    parse_hh_mm_time,
    parse_interval_minutes,
)


def test_parse_valid_hh_mm_time() -> None:
    assert parse_hh_mm_time("09:30") == time(9, 30)


def test_parse_hh_mm_rejects_invalid_time() -> None:
    with pytest.raises(InvalidScheduleConfigError):
        parse_hh_mm_time("25:00")


def test_parse_valid_active_window() -> None:
    assert parse_active_window("10:00-18:00") == (time(10, 0), time(18, 0))


def test_parse_active_window_rejects_overnight_window() -> None:
    with pytest.raises(InvalidActiveWindowError):
        parse_active_window("18:00-10:00")


def test_parse_interval_minutes_accepts_range() -> None:
    assert parse_interval_minutes("45") == 45


def test_parse_interval_minutes_rejects_out_of_range() -> None:
    with pytest.raises(InvalidScheduleConfigError):
        parse_interval_minutes("0")

    with pytest.raises(InvalidScheduleConfigError):
        parse_interval_minutes("1441")


def test_title_and_message_are_trimmed() -> None:
    assert normalize_title("  Focus  ") == "Focus"
    assert normalize_message_text("  Return  ") == "Return"


def test_title_and_message_reject_empty_values() -> None:
    with pytest.raises(InvalidScheduleConfigError):
        normalize_title("  ")

    with pytest.raises(InvalidScheduleConfigError):
        normalize_message_text("")
