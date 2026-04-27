from dataclasses import dataclass
from datetime import UTC, datetime, time

from direm.db.models import Reminder, User
from direm.domain.constants import ReminderStatus, ScheduleType
from direm.domain.errors import InvalidScheduleConfigError
from direm.domain.parsing import normalize_message_text, normalize_title
from direm.domain.schedules import compute_next_daily_run, compute_next_interval_run, validate_active_window
from direm.repositories.reminders import ReminderRepository


@dataclass(frozen=True)
class CreateReminderRequest:
    title: str
    message_text: str
    schedule_type: str
    interval_minutes: int | None = None
    daily_time: time | None = None
    active_from: time | None = None
    active_to: time | None = None


@dataclass(frozen=True)
class CreatedReminder:
    reminder: Reminder
    first_run_at_utc: datetime


class ReminderService:
    def __init__(self, reminder_repository: ReminderRepository) -> None:
        self.reminder_repository = reminder_repository

    async def create_reminder(self, user: User, request: CreateReminderRequest) -> CreatedReminder:
        title = normalize_title(request.title)
        message_text = normalize_message_text(request.message_text)
        validate_active_window(request.active_from, request.active_to)

        now_utc = datetime.now(UTC)
        next_run_at = self.compute_next_run_at(user, request, now_utc)

        reminder = await self.reminder_repository.create(
            user_id=user.id,
            title=title,
            message_text=message_text,
            schedule_type=request.schedule_type,
            interval_minutes=request.interval_minutes,
            daily_time=request.daily_time,
            active_from=request.active_from,
            active_to=request.active_to,
            timezone=user.timezone,
            status=ReminderStatus.ACTIVE.value,
            next_run_at=next_run_at,
        )
        return CreatedReminder(reminder=reminder, first_run_at_utc=next_run_at)

    def compute_next_run_at(self, user: User, request: CreateReminderRequest, now_utc: datetime) -> datetime:
        if request.schedule_type == ScheduleType.INTERVAL.value:
            if request.interval_minutes is None:
                raise InvalidScheduleConfigError("Interval schedule requires interval minutes.")
            return compute_next_interval_run(
                now_utc=now_utc,
                interval_minutes=request.interval_minutes,
                timezone=user.timezone,
                active_from=request.active_from,
                active_to=request.active_to,
            )

        if request.schedule_type == ScheduleType.DAILY.value:
            if request.daily_time is None:
                raise InvalidScheduleConfigError("Daily schedule requires daily time.")
            return compute_next_daily_run(
                now_utc=now_utc,
                daily_time=request.daily_time,
                timezone=user.timezone,
                active_from=request.active_from,
                active_to=request.active_to,
            )

        raise InvalidScheduleConfigError("Unsupported schedule type.")
