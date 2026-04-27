from datetime import UTC, datetime, time, timedelta

import pytest

from direm.domain.constants import ScheduleType
from direm.domain.errors import InvalidActiveWindowError, InvalidScheduleConfigError, InvalidTimezoneError
from direm.domain.schedules import (
    compute_next_after_due,
    compute_next_daily_run,
    compute_next_interval_run,
    is_inside_active_window,
    validate_active_window,
    validate_timezone,
)


def dt_utc(year: int, month: int, day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


def test_timezone_validation_accepts_utc() -> None:
    assert validate_timezone("UTC") == "UTC"


def test_timezone_validation_accepts_iana_timezone() -> None:
    assert validate_timezone("Asia/Almaty") == "Asia/Almaty"


def test_timezone_validation_rejects_invalid_timezone() -> None:
    with pytest.raises(InvalidTimezoneError):
        validate_timezone("Moon/Base")


def test_active_window_validation_accepts_no_window() -> None:
    validate_active_window(None, None)


def test_active_window_validation_accepts_same_day_window() -> None:
    validate_active_window(time(10, 0), time(18, 0))


def test_active_window_validation_rejects_missing_end() -> None:
    with pytest.raises(InvalidActiveWindowError):
        validate_active_window(time(10, 0), None)


def test_active_window_validation_rejects_missing_start() -> None:
    with pytest.raises(InvalidActiveWindowError):
        validate_active_window(None, time(18, 0))


def test_active_window_validation_rejects_overnight_window() -> None:
    with pytest.raises(InvalidActiveWindowError):
        validate_active_window(time(18, 0), time(10, 0))


def test_active_window_validation_rejects_equal_bounds() -> None:
    with pytest.raises(InvalidActiveWindowError):
        validate_active_window(time(10, 0), time(10, 0))


def test_active_window_check_all_day_returns_true() -> None:
    assert is_inside_active_window(dt_utc(2026, 4, 25, 9), "UTC", None, None)


def test_active_window_check_inside_window_returns_true() -> None:
    assert is_inside_active_window(dt_utc(2026, 4, 25, 11), "UTC", time(10, 0), time(18, 0))


def test_active_window_check_before_window_returns_false() -> None:
    assert not is_inside_active_window(dt_utc(2026, 4, 25, 9, 59), "UTC", time(10, 0), time(18, 0))


def test_active_window_check_at_end_returns_false() -> None:
    assert not is_inside_active_window(dt_utc(2026, 4, 25, 18), "UTC", time(10, 0), time(18, 0))


def test_interval_without_active_window_returns_now_plus_interval() -> None:
    now = dt_utc(2026, 4, 25, 8)

    assert compute_next_interval_run(now, 45, "UTC") == now + timedelta(minutes=45)


def test_interval_inside_active_window_returns_base_next_run() -> None:
    now = dt_utc(2026, 4, 25, 10)

    assert compute_next_interval_run(now, 30, "UTC", time(10, 0), time(18, 0)) == dt_utc(2026, 4, 25, 10, 30)


def test_interval_before_active_window_returns_today_active_from() -> None:
    now = dt_utc(2026, 4, 25, 8)

    assert compute_next_interval_run(now, 30, "UTC", time(10, 0), time(18, 0)) == dt_utc(2026, 4, 25, 10)


def test_interval_after_active_window_returns_next_day_active_from() -> None:
    now = dt_utc(2026, 4, 25, 17, 45)

    assert compute_next_interval_run(now, 30, "UTC", time(10, 0), time(18, 0)) == dt_utc(2026, 4, 26, 10)


def test_interval_rejects_zero_or_negative_interval() -> None:
    with pytest.raises(InvalidScheduleConfigError):
        compute_next_interval_run(dt_utc(2026, 4, 25, 8), 0, "UTC")

    with pytest.raises(InvalidScheduleConfigError):
        compute_next_interval_run(dt_utc(2026, 4, 25, 8), -1, "UTC")


def test_interval_requires_aware_utc_datetime() -> None:
    with pytest.raises(InvalidScheduleConfigError):
        compute_next_interval_run(datetime(2026, 4, 25, 8), 30, "UTC")


def test_daily_future_time_returns_today() -> None:
    now = dt_utc(2026, 4, 25, 8)

    assert compute_next_daily_run(now, time(10, 0), "UTC") == dt_utc(2026, 4, 25, 10)


def test_daily_past_time_returns_tomorrow() -> None:
    now = dt_utc(2026, 4, 25, 12)

    assert compute_next_daily_run(now, time(10, 0), "UTC") == dt_utc(2026, 4, 26, 10)


def test_daily_almaty_conversion_works() -> None:
    now = dt_utc(2026, 4, 25, 3)

    assert compute_next_daily_run(now, time(10, 0), "Asia/Almaty") == dt_utc(2026, 4, 25, 5)


def test_daily_time_inside_active_window_passes() -> None:
    now = dt_utc(2026, 4, 25, 8)

    assert compute_next_daily_run(now, time(11, 0), "UTC", time(10, 0), time(18, 0)) == dt_utc(2026, 4, 25, 11)


def test_daily_time_outside_active_window_rejects() -> None:
    with pytest.raises(InvalidScheduleConfigError):
        compute_next_daily_run(dt_utc(2026, 4, 25, 8), time(19, 0), "UTC", time(10, 0), time(18, 0))


def test_no_catch_up_storm_interval_after_downtime_returns_now_plus_interval() -> None:
    now = dt_utc(2026, 4, 25, 12)

    result = compute_next_after_due(now, ScheduleType.INTERVAL.value, 45, None, "UTC")

    assert result == now + timedelta(minutes=45)
    assert result > now


def test_no_catch_up_storm_daily_returns_future_time() -> None:
    now = dt_utc(2026, 4, 25, 12)

    result = compute_next_after_due(now, ScheduleType.DAILY.value, None, time(10, 0), "UTC")

    assert result == dt_utc(2026, 4, 26, 10)
    assert result > now


def test_next_after_due_rejects_missing_interval_config() -> None:
    with pytest.raises(InvalidScheduleConfigError):
        compute_next_after_due(dt_utc(2026, 4, 25, 12), ScheduleType.INTERVAL.value, None, None, "UTC")


def test_next_after_due_rejects_missing_daily_config() -> None:
    with pytest.raises(InvalidScheduleConfigError):
        compute_next_after_due(dt_utc(2026, 4, 25, 12), ScheduleType.DAILY.value, None, None, "UTC")


def test_next_after_due_rejects_unknown_schedule_type() -> None:
    with pytest.raises(InvalidScheduleConfigError):
        compute_next_after_due(dt_utc(2026, 4, 25, 12), "weekly", None, None, "UTC")
