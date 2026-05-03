from datetime import UTC, datetime, time

from sqlalchemy import case, select
from sqlalchemy.orm import selectinload

from direm.db.models import Reminder, User
from direm.domain.constants import ReminderStatus
from direm.repositories.base import Repository


class ReminderRepository(Repository[Reminder]):
    model = Reminder

    async def create(
        self,
        *,
        user_id: int,
        title: str,
        message_text: str,
        schedule_type: str,
        interval_minutes: int | None,
        daily_time: time | None,
        active_from: time | None,
        active_to: time | None,
        timezone: str,
        status: str,
        next_run_at: datetime,
    ) -> Reminder:
        reminder = Reminder(
            user_id=user_id,
            title=title,
            message_text=message_text,
            schedule_type=schedule_type,
            interval_minutes=interval_minutes,
            daily_time=daily_time,
            active_from=active_from,
            active_to=active_to,
            timezone=timezone,
            status=status,
            next_run_at=next_run_at,
        )
        self.session.add(reminder)
        await self.session.flush()
        return reminder

    async def list_by_user_id(self, user_id: int) -> list[Reminder]:
        result = await self.session.execute(
            select(Reminder)
            .where(Reminder.user_id == user_id, Reminder.deleted_at.is_(None))
            .order_by(
                case((Reminder.status == ReminderStatus.ACTIVE.value, 0), else_=1),
                Reminder.next_run_at.asc().nulls_last(),
                Reminder.title.asc(),
            )
        )
        return list(result.scalars().all())

    async def list_due(self, *, now_utc: datetime, limit: int) -> list[Reminder]:
        result = await self.session.execute(
            select(Reminder)
            .options(selectinload(Reminder.user))
            .where(
                Reminder.status == ReminderStatus.ACTIVE.value,
                Reminder.deleted_at.is_(None),
                Reminder.next_run_at.is_not(None),
                Reminder.next_run_at <= now_utc,
                Reminder.user.has(User.bunker_active.is_(False)),
            )
            .order_by(Reminder.next_run_at.asc(), Reminder.id.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id_for_user(self, reminder_id: int, user_id: int) -> Reminder | None:
        result = await self.session.execute(
            select(Reminder).where(
                Reminder.id == reminder_id,
                Reminder.user_id == user_id,
                Reminder.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        reminder: Reminder,
        *,
        status: str,
        next_run_at: datetime | None = None,
    ) -> Reminder:
        reminder.status = status
        if next_run_at is not None:
            reminder.next_run_at = next_run_at
        await self.session.flush()
        return reminder

    async def soft_delete(self, reminder: Reminder, *, deleted_at: datetime | None = None) -> Reminder:
        reminder.deleted_at = deleted_at or datetime.now(UTC)
        await self.session.flush()
        return reminder

    async def update_next_run_at(self, reminder: Reminder, *, next_run_at: datetime) -> Reminder:
        reminder.next_run_at = next_run_at
        await self.session.flush()
        return reminder
