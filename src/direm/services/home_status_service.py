from dataclasses import dataclass

from direm.db.models import User
from direm.domain.constants import ReminderStatus
from direm.i18n import language_name, t
from direm.repositories.reminders import ReminderRepository


@dataclass(frozen=True)
class ReminderStats:
    total: int
    active: int
    paused: int


class HomeStatusService:
    def __init__(self, reminder_repository: ReminderRepository) -> None:
        self.reminder_repository = reminder_repository

    async def get_reminder_stats(self, user: User) -> ReminderStats:
        counts = await self.reminder_repository.count_by_status_for_user(user.id)
        active = counts.get(ReminderStatus.ACTIVE.value, 0)
        paused = counts.get(ReminderStatus.PAUSED.value, 0)
        return ReminderStats(total=sum(counts.values()), active=active, paused=paused)

    async def render_for_user(self, user: User) -> str:
        stats = await self.get_reminder_stats(user)
        return t(
            user.language_code,
            "menu.main",
            timezone=user.timezone,
            language=language_name(user.language_code),
            bunker_status=t(user.language_code, "bunker.status_active" if user.bunker_active else "bunker.status_inactive"),
            total_reminders=stats.total,
            active_reminders=stats.active,
            paused_reminders=stats.paused,
        )
