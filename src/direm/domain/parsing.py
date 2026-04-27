from datetime import time

from direm.domain.errors import InvalidActiveWindowError, InvalidScheduleConfigError
from direm.domain.schedules import validate_active_window


MAX_TITLE_LENGTH = 80
MAX_MESSAGE_TEXT_LENGTH = 1000
MIN_INTERVAL_MINUTES = 1
MAX_INTERVAL_MINUTES = 1440


def normalize_title(value: str | None) -> str:
    title = (value or "").strip()
    if not title:
        raise InvalidScheduleConfigError("Title is required.")
    if len(title) > MAX_TITLE_LENGTH:
        raise InvalidScheduleConfigError("Title is too long.")
    return title


def normalize_message_text(value: str | None) -> str:
    message_text = (value or "").strip()
    if not message_text:
        raise InvalidScheduleConfigError("Message text is required.")
    if len(message_text) > MAX_MESSAGE_TEXT_LENGTH:
        raise InvalidScheduleConfigError("Message text is too long.")
    return message_text


def parse_interval_minutes(value: str | None) -> int:
    raw_value = (value or "").strip()
    try:
        interval_minutes = int(raw_value)
    except ValueError as exc:
        raise InvalidScheduleConfigError("Interval must be an integer.") from exc

    if interval_minutes < MIN_INTERVAL_MINUTES or interval_minutes > MAX_INTERVAL_MINUTES:
        raise InvalidScheduleConfigError("Interval is out of allowed range.")

    return interval_minutes


def parse_hh_mm_time(value: str | None) -> time:
    raw_value = (value or "").strip()
    parts = raw_value.split(":")
    if len(parts) != 2:
        raise InvalidScheduleConfigError("Time must use HH:MM format.")

    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError as exc:
        raise InvalidScheduleConfigError("Time must use HH:MM format.") from exc

    try:
        return time(hour=hour, minute=minute)
    except ValueError as exc:
        raise InvalidScheduleConfigError("Time is outside 24-hour range.") from exc


def parse_active_window(value: str | None) -> tuple[time, time]:
    raw_value = (value or "").strip()
    parts = raw_value.split("-")
    if len(parts) != 2:
        raise InvalidActiveWindowError("Active window must use HH:MM-HH:MM format.")

    active_from = parse_hh_mm_time(parts[0])
    active_to = parse_hh_mm_time(parts[1])
    validate_active_window(active_from, active_to)
    return active_from, active_to
