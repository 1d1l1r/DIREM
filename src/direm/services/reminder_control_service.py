from dataclasses import dataclass
from datetime import UTC, datetime

from direm.db.models import Reminder, User
from direm.domain.constants import ReminderStatus, ScheduleType
from direm.domain.errors import InvalidScheduleConfigError
from direm.domain.schedules import compute_next_daily_run, compute_next_interval_run
from direm.i18n import t
from direm.repositories.reminders import ReminderRepository
from direm.services.reminder_list_service import ReminderListItem


class ReminderSelectionError(ValueError):
    pass


@dataclass(frozen=True)
class SelectableReminder:
    public_number: int
    reminder: Reminder


class ReminderControlService:
    def __init__(self, reminder_repository: ReminderRepository) -> None:
        self.reminder_repository = reminder_repository

    async def list_selectable_for_user(self, user: User, *, status: str | None = None) -> list[SelectableReminder]:
        reminders = await self.reminder_repository.list_by_user_id(user.id)
        if status is not None:
            reminders = [reminder for reminder in reminders if reminder.status == status]
        return [SelectableReminder(public_number=index, reminder=reminder) for index, reminder in enumerate(reminders, start=1)]

    def render_selection_prompt(self, action: str, selectable: list[SelectableReminder], timezone: str, language_code: str = "en") -> str:
        if not selectable:
            return t(language_code, "list.empty")

        lines = [t(language_code, "control.choose", action=action), t(language_code, "control.send_number"), ""]
        for item in selectable:
            reminder = item.reminder
            list_item = ReminderListItem(
                title=reminder.title,
                schedule=_format_schedule(reminder),
                active_window=_format_active_window(reminder.active_from, reminder.active_to, language_code),
                next_run_at=_format_next_run_at(reminder.next_run_at, timezone, language_code),
                status=reminder.status,
            )
            lines.extend(
                [
                    f"{item.public_number}. {list_item.title} (id: {reminder.id})",
                    f"{t(language_code, 'common.status')}: {list_item.status}",
                    f"{t(language_code, 'common.schedule')}: {list_item.schedule}",
                    f"{t(language_code, 'common.active_window')}: {list_item.active_window}",
                    f"{t(language_code, 'common.next_run')}: {list_item.next_run_at}",
                    "",
                ]
            )
        return "\n".join(lines).strip()

    async def pause_for_user(self, user: User, selection: str) -> Reminder:
        reminder = await self._resolve_selection(user, selection)
        return await self.reminder_repository.update_status(reminder, status=ReminderStatus.PAUSED.value)

    async def resume_for_user(self, user: User, selection: str) -> Reminder:
        reminder = await self._resolve_selection(user, selection)
        next_run_at = self._compute_next_run_at(user, reminder, datetime.now(UTC))
        return await self.reminder_repository.update_status(
            reminder,
            status=ReminderStatus.ACTIVE.value,
            next_run_at=next_run_at,
        )

    async def select_for_user(self, user: User, selection: str) -> Reminder:
        return await self._resolve_selection(user, selection)

    async def delete_for_user(self, user: User, selection: str) -> Reminder:
        reminder = await self._resolve_selection(user, selection)
        return await self.reminder_repository.soft_delete(reminder)

    async def _resolve_selection(self, user: User, selection: str) -> Reminder:
        raw_selection = (selection or "").strip()
        if not raw_selection.isdigit():
            raise ReminderSelectionError("Selection must be a number.")

        selected_number = int(raw_selection)
        selectable = await self.list_selectable_for_user(user)
        for item in selectable:
            if item.public_number == selected_number or item.reminder.id == selected_number:
                return item.reminder

        raise ReminderSelectionError("Reminder not found for current user.")

    def _compute_next_run_at(self, user: User, reminder: Reminder, now_utc: datetime) -> datetime:
        if reminder.schedule_type == ScheduleType.INTERVAL.value:
            if reminder.interval_minutes is None:
                raise InvalidScheduleConfigError("Interval reminder requires interval minutes.")
            return compute_next_interval_run(
                now_utc=now_utc,
                interval_minutes=reminder.interval_minutes,
                timezone=user.timezone,
                active_from=reminder.active_from,
                active_to=reminder.active_to,
            )

        if reminder.schedule_type == ScheduleType.DAILY.value:
            if reminder.daily_time is None:
                raise InvalidScheduleConfigError("Daily reminder requires daily time.")
            return compute_next_daily_run(
                now_utc=now_utc,
                daily_time=reminder.daily_time,
                timezone=user.timezone,
                active_from=reminder.active_from,
                active_to=reminder.active_to,
            )

        raise InvalidScheduleConfigError("Unsupported schedule type.")


from direm.services.reminder_list_service import _format_active_window, _format_next_run_at, _format_schedule
