from dataclasses import dataclass
from datetime import UTC, datetime, time
from zoneinfo import ZoneInfo

from direm.db.models import Reminder, User
from direm.domain.constants import ScheduleType
from direm.i18n import t
from direm.repositories.reminders import ReminderRepository


@dataclass(frozen=True)
class ReminderListItem:
    title: str
    schedule: str
    active_window: str
    next_run_at: str
    status: str


class ReminderListService:
    def __init__(self, reminder_repository: ReminderRepository) -> None:
        self.reminder_repository = reminder_repository

    async def list_for_user(self, user: User) -> list[ReminderListItem]:
        reminders = await self.reminder_repository.list_by_user_id(user.id)
        return [self._to_item(reminder, user.timezone, user.language_code) for reminder in reminders]

    def render_for_user(self, items: list[ReminderListItem], language_code: str = "en") -> str:
        if not items:
            return t(language_code, "list.empty")

        blocks = [t(language_code, "list.header")]
        for index, item in enumerate(items, start=1):
            blocks.append(
                "\n".join(
                    [
                        f"{index}. {item.title}",
                        f"{t(language_code, 'common.status')}: {item.status}",
                        f"{t(language_code, 'common.schedule')}: {item.schedule}",
                        f"{t(language_code, 'common.active_window')}: {item.active_window}",
                        f"{t(language_code, 'common.next_run')}: {item.next_run_at}",
                    ]
                )
            )
        return "\n\n".join(blocks)

    def _to_item(self, reminder: Reminder, timezone: str, language_code: str) -> ReminderListItem:
        return ReminderListItem(
            title=reminder.title,
            schedule=_format_schedule(reminder),
            active_window=_format_active_window(reminder.active_from, reminder.active_to, language_code),
            next_run_at=_format_next_run_at(reminder.next_run_at, timezone, language_code),
            status=reminder.status,
        )


def _format_schedule(reminder: Reminder) -> str:
    if reminder.schedule_type == ScheduleType.INTERVAL.value:
        return f"every {reminder.interval_minutes} minutes"

    if reminder.schedule_type == ScheduleType.DAILY.value and reminder.daily_time is not None:
        return f"daily at {_format_time(reminder.daily_time)}"

    return reminder.schedule_type


def _format_active_window(active_from: time | None, active_to: time | None, language_code: str = "en") -> str:
    if active_from is None or active_to is None:
        return t(language_code, "common.all_day")
    return f"{_format_time(active_from)}-{_format_time(active_to)}"


def _format_next_run_at(next_run_at: datetime | None, timezone: str, language_code: str = "en") -> str:
    if next_run_at is None:
        return t(language_code, "common.not_scheduled")
    if next_run_at.tzinfo is None or next_run_at.utcoffset() is None:
        next_run_at = next_run_at.replace(tzinfo=UTC)
    return next_run_at.astimezone(ZoneInfo(timezone)).strftime("%Y-%m-%d %H:%M %Z")


def _format_time(value: time) -> str:
    return value.strftime("%H:%M")
