from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from direm.domain.constants import ScheduleType
from direm.domain.errors import InvalidActiveWindowError, InvalidScheduleConfigError, InvalidTimezoneError


def validate_timezone(timezone: str) -> str:
    if not timezone:
        raise InvalidTimezoneError("Timezone is required.")

    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise InvalidTimezoneError("Timezone must be a valid IANA timezone.") from exc

    return timezone


def validate_active_window(active_from: time | None, active_to: time | None) -> None:
    if active_from is None and active_to is None:
        return

    if active_from is None or active_to is None:
        raise InvalidActiveWindowError("Active window requires both start and end.")

    if active_from >= active_to:
        raise InvalidActiveWindowError("Overnight active windows are not supported in MVP.")


def is_inside_active_window(
    dt_utc: datetime,
    timezone: str,
    active_from: time | None,
    active_to: time | None,
) -> bool:
    validate_utc_datetime(dt_utc, "dt_utc")
    tz = _load_timezone(timezone)
    validate_active_window(active_from, active_to)

    if active_from is None and active_to is None:
        return True

    local_time = dt_utc.astimezone(tz).time()
    return active_from <= local_time < active_to


def compute_next_interval_run(
    now_utc: datetime,
    interval_minutes: int,
    timezone: str,
    active_from: time | None = None,
    active_to: time | None = None,
) -> datetime:
    validate_utc_datetime(now_utc, "now_utc")
    if interval_minutes <= 0:
        raise InvalidScheduleConfigError("Interval minutes must be positive.")

    tz = _load_timezone(timezone)
    validate_active_window(active_from, active_to)

    base_next_utc = now_utc + timedelta(minutes=interval_minutes)
    if active_from is None and active_to is None:
        return base_next_utc

    return _adjust_to_active_window(base_next_utc, tz, active_from, active_to)


def compute_next_daily_run(
    now_utc: datetime,
    daily_time: time,
    timezone: str,
    active_from: time | None = None,
    active_to: time | None = None,
) -> datetime:
    validate_utc_datetime(now_utc, "now_utc")
    tz = _load_timezone(timezone)
    validate_active_window(active_from, active_to)

    if active_from is not None and not (active_from <= daily_time < active_to):
        raise InvalidScheduleConfigError("Daily time must be inside active window.")

    now_local = now_utc.astimezone(tz)
    candidate_local = datetime.combine(now_local.date(), daily_time, tzinfo=tz)
    if candidate_local <= now_local:
        candidate_local += timedelta(days=1)

    return candidate_local.astimezone(UTC)


def compute_next_after_due(
    now_utc: datetime,
    schedule_type: str,
    interval_minutes: int | None,
    daily_time: time | None,
    timezone: str,
    active_from: time | None = None,
    active_to: time | None = None,
) -> datetime:
    if schedule_type == ScheduleType.INTERVAL.value:
        if interval_minutes is None:
            raise InvalidScheduleConfigError("Interval schedule requires interval_minutes.")
        return compute_next_interval_run(now_utc, interval_minutes, timezone, active_from, active_to)

    if schedule_type == ScheduleType.DAILY.value:
        if daily_time is None:
            raise InvalidScheduleConfigError("Daily schedule requires daily_time.")
        return compute_next_daily_run(now_utc, daily_time, timezone, active_from, active_to)

    raise InvalidScheduleConfigError("Unsupported schedule type.")


def validate_utc_datetime(value: datetime, name: str = "datetime") -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise InvalidScheduleConfigError(f"{name} must be timezone-aware UTC.")

    if value.utcoffset() != timedelta(0):
        raise InvalidScheduleConfigError(f"{name} must be UTC.")


def _load_timezone(timezone: str) -> ZoneInfo:
    validate_timezone(timezone)
    return ZoneInfo(timezone)


def _adjust_to_active_window(
    candidate_utc: datetime,
    timezone: ZoneInfo,
    active_from: time,
    active_to: time,
) -> datetime:
    candidate_local = candidate_utc.astimezone(timezone)
    local_time = candidate_local.time()

    if active_from <= local_time < active_to:
        return candidate_utc

    if local_time < active_from:
        next_local = datetime.combine(candidate_local.date(), active_from, tzinfo=timezone)
    else:
        next_local = datetime.combine(candidate_local.date() + timedelta(days=1), active_from, tzinfo=timezone)

    return next_local.astimezone(UTC)
