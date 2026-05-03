from dataclasses import dataclass

from direm.db.models import ReminderCheckIn
from direm.domain.constants import CheckInResponseType
from direm.repositories.checkins import ReminderCheckInRepository


class CheckInValidationError(ValueError):
    pass


class CheckInDeliveryNotFoundError(CheckInValidationError):
    pass


@dataclass(frozen=True)
class ReminderCheckInResult:
    checkin: ReminderCheckIn
    created: bool


class ReminderCheckInService:
    def __init__(self, checkin_repository: ReminderCheckInRepository) -> None:
        self.checkin_repository = checkin_repository

    async def record_response(
        self,
        *,
        user_id: int,
        delivery_id: int,
        response_type: str,
        response_text: str | None = None,
    ) -> ReminderCheckInResult:
        normalized_response_type = self._validate_response_type(response_type)
        delivery = await self.checkin_repository.get_delivery_for_user(
            delivery_id=delivery_id,
            user_id=user_id,
        )
        if delivery is None:
            raise CheckInDeliveryNotFoundError("Reminder delivery was not found for this user.")

        existing = await self.checkin_repository.get_by_delivery_id_for_user(
            delivery_id=delivery_id,
            user_id=user_id,
        )
        checkin = await self.checkin_repository.upsert_for_delivery(
            delivery=delivery,
            response_type=normalized_response_type,
            response_text=response_text,
        )
        return ReminderCheckInResult(checkin=checkin, created=existing is None)

    def _validate_response_type(self, response_type: str) -> str:
        try:
            return CheckInResponseType(response_type).value
        except ValueError as exc:
            raise CheckInValidationError(f"Unsupported check-in response type: {response_type}") from exc
