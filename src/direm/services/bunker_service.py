from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from direm.db.models import Reminder, User
from direm.domain.constants import ScheduleType
from direm.domain.errors import InvalidScheduleConfigError
from direm.domain.schedules import compute_next_daily_run, compute_next_interval_run
from direm.repositories.reminders import ReminderRepository
from direm.repositories.users import UserRepository


@dataclass(frozen=True)
class BunkerState:
    active: bool
    activated_at: datetime | None


@dataclass(frozen=True)
class BunkerDeactivateResult:
    state: BunkerState
    rescheduled_count: int
    was_already_inactive: bool = False


class BunkerService:
    def __init__(
        self,
        user_repository: UserRepository,
        reminder_repository: ReminderRepository | None = None,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.user_repository = user_repository
        self.reminder_repository = reminder_repository
        self.clock = clock or (lambda: datetime.now(UTC))

    async def get_current_state(self, user: User) -> BunkerState:
        active, activated_at = await self.user_repository.get_bunker_state(user)
        return BunkerState(active=active, activated_at=activated_at)

    async def activate(self, user: User) -> BunkerState:
        if user.bunker_active and user.bunker_activated_at is not None:
            return await self.get_current_state(user)

        activated = await self.user_repository.activate_bunker(user, activated_at=self._now_utc())
        return BunkerState(active=activated.bunker_active, activated_at=activated.bunker_activated_at)

    async def deactivate(self, user: User) -> BunkerState:
        if not user.bunker_active and user.bunker_activated_at is None:
            return await self.get_current_state(user)

        deactivated = await self.user_repository.deactivate_bunker(user)
        return BunkerState(active=deactivated.bunker_active, activated_at=deactivated.bunker_activated_at)

    async def deactivate_and_reschedule(self, user: User) -> BunkerDeactivateResult:
        if not user.bunker_active and user.bunker_activated_at is None:
            return BunkerDeactivateResult(
                state=await self.get_current_state(user),
                rescheduled_count=0,
                was_already_inactive=True,
            )

        if self.reminder_repository is None:
            raise ValueError("ReminderRepository is required for Bunker exit rescheduling.")

        now_utc = self._now_utc()
        reminders = await self.reminder_repository.list_active_for_user(user.id)
        next_run_values = [(reminder, self._compute_next_run_at(user, reminder, now_utc)) for reminder in reminders]

        for reminder, next_run_at in next_run_values:
            await self.reminder_repository.update_next_run_at(reminder, next_run_at=next_run_at)

        deactivated = await self.user_repository.deactivate_bunker(user)
        return BunkerDeactivateResult(
            state=BunkerState(active=deactivated.bunker_active, activated_at=deactivated.bunker_activated_at),
            rescheduled_count=len(next_run_values),
            was_already_inactive=False,
        )

    def _now_utc(self) -> datetime:
        now = self.clock()
        if now.tzinfo is None:
            return now.replace(tzinfo=UTC)
        return now.astimezone(UTC)

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
