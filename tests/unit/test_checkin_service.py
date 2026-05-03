from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.db.base import Base
from direm.db.models import Reminder, ReminderCheckIn
from direm.domain.constants import CheckInResponseType, DeliveryStatus, ReminderStatus, ScheduleType
from direm.repositories.checkins import ReminderCheckInRepository
from direm.repositories.deliveries import ReminderDeliveryRepository
from direm.repositories.users import UserRepository
from direm.services.checkin_service import (
    CheckInDeliveryNotFoundError,
    CheckInValidationError,
    ReminderCheckInService,
)
from direm.services.user_service import TelegramUserProfile, UserService


@pytest.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(engine, expire_on_commit=False)

    await engine.dispose()


async def create_user(session, telegram_user_id: int):
    return await UserService(UserRepository(session)).register_or_update_from_telegram(
        TelegramUserProfile(
            telegram_user_id=telegram_user_id,
            chat_id=telegram_user_id + 1000,
            username=f"user{telegram_user_id}",
            first_name="User",
            language_code="en",
        )
    )


async def create_reminder(session, user, *, next_run_at: datetime):
    reminder = Reminder(
        user_id=user.id,
        title="Morning focus",
        message_text="Return to intent.",
        schedule_type=ScheduleType.INTERVAL.value,
        interval_minutes=30,
        timezone=user.timezone,
        status=ReminderStatus.ACTIVE.value,
        next_run_at=next_run_at,
    )
    session.add(reminder)
    await session.flush()
    return reminder


async def create_delivery(session, user, reminder, *, status: str = DeliveryStatus.SENT.value):
    return await ReminderDeliveryRepository(session).create(
        reminder_id=reminder.id,
        user_id=user.id,
        scheduled_for=reminder.next_run_at,
        status=status,
        sent_at=datetime(2026, 5, 3, 9, 0, tzinfo=UTC) if status == DeliveryStatus.SENT.value else None,
    )


async def list_checkins(session) -> list[ReminderCheckIn]:
    result = await session.execute(select(ReminderCheckIn).order_by(ReminderCheckIn.id.asc()))
    return list(result.scalars().all())


async def test_record_response_creates_checkin_for_user_delivery(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        reminder = await create_reminder(session, user, next_run_at=datetime(2026, 5, 3, 8, 30, tzinfo=UTC))
        delivery = await create_delivery(session, user, reminder)

        result = await ReminderCheckInService(ReminderCheckInRepository(session)).record_response(
            user_id=user.id,
            delivery_id=delivery.id,
            response_type=CheckInResponseType.DONE.value,
        )

        assert result.created is True
        assert result.checkin.user_id == user.id
        assert result.checkin.reminder_id == reminder.id
        assert result.checkin.reminder_delivery_id == delivery.id
        assert result.checkin.response_type == CheckInResponseType.DONE.value
        assert result.checkin.response_text is None


async def test_repeated_response_updates_existing_checkin_instead_of_duplicate(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        reminder = await create_reminder(session, user, next_run_at=datetime(2026, 5, 3, 8, 30, tzinfo=UTC))
        delivery = await create_delivery(session, user, reminder)
        service = ReminderCheckInService(ReminderCheckInRepository(session))

        first = await service.record_response(
            user_id=user.id,
            delivery_id=delivery.id,
            response_type=CheckInResponseType.DONE.value,
        )
        second = await service.record_response(
            user_id=user.id,
            delivery_id=delivery.id,
            response_type=CheckInResponseType.SKIPPED.value,
        )

        checkins = await list_checkins(session)
        assert first.created is True
        assert second.created is False
        assert first.checkin.id == second.checkin.id
        assert len(checkins) == 1
        assert checkins[0].response_type == CheckInResponseType.SKIPPED.value


async def test_invalid_response_type_is_rejected(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        reminder = await create_reminder(session, user, next_run_at=datetime(2026, 5, 3, 8, 30, tzinfo=UTC))
        delivery = await create_delivery(session, user, reminder)

        with pytest.raises(CheckInValidationError):
            await ReminderCheckInService(ReminderCheckInRepository(session)).record_response(
                user_id=user.id,
                delivery_id=delivery.id,
                response_type="snooze",
            )

        assert await list_checkins(session) == []


async def test_user_cannot_record_checkin_for_another_users_delivery(session_factory) -> None:
    async with session_factory() as session:
        owner = await create_user(session, 1001)
        other = await create_user(session, 1002)
        reminder = await create_reminder(session, owner, next_run_at=datetime(2026, 5, 3, 8, 30, tzinfo=UTC))
        delivery = await create_delivery(session, owner, reminder)

        with pytest.raises(CheckInDeliveryNotFoundError):
            await ReminderCheckInService(ReminderCheckInRepository(session)).record_response(
                user_id=other.id,
                delivery_id=delivery.id,
                response_type=CheckInResponseType.DONE.value,
            )

        assert await list_checkins(session) == []


@pytest.mark.parametrize("delivery_status", [DeliveryStatus.PENDING.value, DeliveryStatus.FAILED.value])
async def test_checkin_requires_sent_delivery(session_factory, delivery_status: str) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        reminder = await create_reminder(session, user, next_run_at=datetime(2026, 5, 3, 8, 30, tzinfo=UTC))
        delivery = await create_delivery(session, user, reminder, status=delivery_status)

        with pytest.raises(CheckInDeliveryNotFoundError):
            await ReminderCheckInService(ReminderCheckInRepository(session)).record_response(
                user_id=user.id,
                delivery_id=delivery.id,
                response_type=CheckInResponseType.DONE.value,
            )

        assert await list_checkins(session) == []


async def test_response_text_may_be_null_or_updated_by_foundation(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        reminder = await create_reminder(session, user, next_run_at=datetime(2026, 5, 3, 8, 30, tzinfo=UTC))
        delivery = await create_delivery(session, user, reminder)
        service = ReminderCheckInService(ReminderCheckInRepository(session))

        created = await service.record_response(
            user_id=user.id,
            delivery_id=delivery.id,
            response_type=CheckInResponseType.LATER.value,
        )
        assert created.checkin.response_text is None

        updated = await service.record_response(
            user_id=user.id,
            delivery_id=delivery.id,
            response_type=CheckInResponseType.LATER.value,
            response_text="Future text foundation.",
        )

        assert updated.checkin.response_text == "Future text foundation."


async def test_later_does_not_mutate_reminder_schedule_or_next_run(session_factory) -> None:
    async with session_factory() as session:
        next_run_at = datetime(2026, 5, 3, 8, 30, tzinfo=UTC)
        user = await create_user(session, 1001)
        reminder = await create_reminder(session, user, next_run_at=next_run_at)
        delivery = await create_delivery(session, user, reminder)

        await ReminderCheckInService(ReminderCheckInRepository(session)).record_response(
            user_id=user.id,
            delivery_id=delivery.id,
            response_type=CheckInResponseType.LATER.value,
        )

        assert reminder.schedule_type == ScheduleType.INTERVAL.value
        assert reminder.interval_minutes == 30
        assert reminder.next_run_at == next_run_at
        assert delivery.status == DeliveryStatus.SENT.value
