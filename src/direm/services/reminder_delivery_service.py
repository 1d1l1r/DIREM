import logging
from datetime import UTC, datetime
from collections.abc import Callable
from typing import Protocol

from direm.db.models import Reminder
from direm.domain.errors import InvalidScheduleConfigError
from direm.domain.schedules import compute_next_after_due
from direm.i18n import t
from direm.repositories.deliveries import ReminderDeliveryRepository
from direm.repositories.reminders import ReminderRepository

logger = logging.getLogger(__name__)


class TelegramSender(Protocol):
    async def send_message(self, chat_id: int, text: str, reply_markup: object | None = None) -> object:
        pass


class ReminderDeliveryService:
    def __init__(
        self,
        reminder_repository: ReminderRepository,
        delivery_repository: ReminderDeliveryRepository,
        sender: TelegramSender,
        checkin_markup_factory: Callable[[str | None, int], object] | None = None,
    ) -> None:
        self.reminder_repository = reminder_repository
        self.delivery_repository = delivery_repository
        self.sender = sender
        self.checkin_markup_factory = checkin_markup_factory

    async def deliver_due_once(self, *, now_utc: datetime | None = None, limit: int = 20) -> int:
        now = now_utc or datetime.now(UTC)
        reminders = await self.reminder_repository.list_due(now_utc=now, limit=limit)

        delivered_count = 0
        for reminder in reminders:
            if await self._deliver_one(reminder, now):
                delivered_count += 1

        return delivered_count

    async def _deliver_one(self, reminder: Reminder, now_utc: datetime) -> bool:
        if reminder.user.bunker_active:
            logger.info("Suppressing reminder id=%s for Bunker-active user id=%s", reminder.id, reminder.user_id)
            return False

        scheduled_for = reminder.next_run_at or now_utc
        delivery = await self.delivery_repository.create_pending(
            reminder_id=reminder.id,
            user_id=reminder.user_id,
            scheduled_for=scheduled_for,
        )
        reply_markup = self._build_checkin_markup(reminder, delivery.id)
        try:
            await self.sender.send_message(
                chat_id=reminder.user.chat_id,
                text=self._render_message(reminder),
                reply_markup=reply_markup,
            )
        except Exception as exc:
            logger.exception("Failed to send reminder id=%s to user id=%s", reminder.id, reminder.user_id)
            await self.delivery_repository.mark_failed(delivery, error_message=str(exc))
            return False

        await self.delivery_repository.mark_sent(delivery, sent_at=now_utc)
        await self.reminder_repository.update_next_run_at(
            reminder,
            next_run_at=self._compute_next_run_at(reminder, now_utc),
        )
        return True

    def _compute_next_run_at(self, reminder: Reminder, now_utc: datetime) -> datetime:
        try:
            return compute_next_after_due(
                now_utc=now_utc,
                schedule_type=reminder.schedule_type,
                interval_minutes=reminder.interval_minutes,
                daily_time=reminder.daily_time,
                timezone=reminder.user.timezone,
                active_from=reminder.active_from,
                active_to=reminder.active_to,
            )
        except InvalidScheduleConfigError:
            logger.exception("Reminder id=%s has invalid schedule after delivery.", reminder.id)
            raise

    def _render_message(self, reminder: Reminder) -> str:
        return f"{t(reminder.user.language_code, 'delivery.wrapper')}\n{reminder.title}\n\n{reminder.message_text}"

    def _build_checkin_markup(self, reminder: Reminder, delivery_id: int) -> object | None:
        if self.checkin_markup_factory is None:
            return None
        return self.checkin_markup_factory(reminder.user.language_code, delivery_id)
