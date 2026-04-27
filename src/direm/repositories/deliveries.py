from datetime import datetime

from direm.db.models import ReminderDelivery
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
