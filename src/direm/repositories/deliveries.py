from datetime import datetime

from direm.db.models import ReminderDelivery
from direm.domain.constants import DeliveryStatus
from direm.repositories.base import Repository


class ReminderDeliveryRepository(Repository[ReminderDelivery]):
    model = ReminderDelivery

    async def create(
        self,
        *,
        reminder_id: int,
        user_id: int,
        scheduled_for: datetime,
        status: str,
        sent_at: datetime | None = None,
        error_message: str | None = None,
    ) -> ReminderDelivery:
        delivery = ReminderDelivery(
            reminder_id=reminder_id,
            user_id=user_id,
            scheduled_for=scheduled_for,
            status=status,
            sent_at=sent_at,
            error_message=error_message,
        )
        self.session.add(delivery)
        await self.session.flush()
        return delivery

    async def create_pending(
        self,
        *,
        reminder_id: int,
        user_id: int,
        scheduled_for: datetime,
    ) -> ReminderDelivery:
        return await self.create(
            reminder_id=reminder_id,
            user_id=user_id,
            scheduled_for=scheduled_for,
            status=DeliveryStatus.PENDING.value,
        )

    async def mark_sent(self, delivery: ReminderDelivery, *, sent_at: datetime) -> ReminderDelivery:
        delivery.status = DeliveryStatus.SENT.value
        delivery.sent_at = sent_at
        delivery.error_message = None
        await self.session.flush()
        return delivery

    async def mark_failed(self, delivery: ReminderDelivery, *, error_message: str) -> ReminderDelivery:
        delivery.status = DeliveryStatus.FAILED.value
        delivery.sent_at = None
        delivery.error_message = error_message
        await self.session.flush()
        return delivery
