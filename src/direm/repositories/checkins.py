from sqlalchemy import select

from direm.db.models import ReminderCheckIn, ReminderDelivery
from direm.repositories.base import Repository


class ReminderCheckInRepository(Repository[ReminderCheckIn]):
    model = ReminderCheckIn

    async def get_by_delivery_id_for_user(self, *, delivery_id: int, user_id: int) -> ReminderCheckIn | None:
        result = await self.session.execute(
            select(ReminderCheckIn).where(
                ReminderCheckIn.reminder_delivery_id == delivery_id,
                ReminderCheckIn.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_delivery_for_user(self, *, delivery_id: int, user_id: int) -> ReminderDelivery | None:
        result = await self.session.execute(
            select(ReminderDelivery).where(
                ReminderDelivery.id == delivery_id,
                ReminderDelivery.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_for_delivery(
        self,
        *,
        delivery: ReminderDelivery,
        response_type: str,
        response_text: str | None = None,
    ) -> ReminderCheckIn:
        checkin = await self.get_by_delivery_id_for_user(
            delivery_id=delivery.id,
            user_id=delivery.user_id,
        )
        if checkin is None:
            checkin = ReminderCheckIn(
                user_id=delivery.user_id,
                reminder_id=delivery.reminder_id,
                reminder_delivery_id=delivery.id,
                response_type=response_type,
                response_text=response_text,
            )
            self.session.add(checkin)
        else:
            checkin.response_type = response_type
            checkin.response_text = response_text

        await self.session.flush()
        return checkin
