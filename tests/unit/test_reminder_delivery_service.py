from datetime import UTC, datetime, time

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.db.base import Base
from direm.db.models import ReminderDelivery
from direm.domain.constants import DeliveryStatus, ReminderStatus, ScheduleType
from direm.repositories.deliveries import ReminderDeliveryRepository
from direm.repositories.reminders import ReminderRepository
from direm.repositories.users import UserRepository
from direm.services.bunker_service import BunkerService
from direm.services.reminder_delivery_service import ReminderDeliveryService
from direm.services.user_service import TelegramUserProfile, UserService


class FakeSender:
    def __init__(self, *, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.sent_messages: list[tuple[int, str]] = []

    async def send_message(self, chat_id: int, text: str) -> object:
        if self.should_fail:
            raise RuntimeError("telegram unavailable")
        self.sent_messages.append((chat_id, text))
        return object()


@pytest.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(engine, expire_on_commit=False)

    await engine.dispose()


async def create_user(session, telegram_user_id: int, timezone: str = "UTC"):
    service = UserService(UserRepository(session))
    user = await service.register_or_update_from_telegram(
        TelegramUserProfile(
            telegram_user_id=telegram_user_id,
            chat_id=telegram_user_id + 1000,
            username=f"user{telegram_user_id}",
            first_name="User",
        )
    )
    await service.update_timezone(user, timezone)
    return user


async def create_reminder(session, user, *, title: str, status: str, next_run_at: datetime):
    return await ReminderRepository(session).create(
        user_id=user.id,
        title=title,
        message_text="Return to intention.",
        schedule_type=ScheduleType.INTERVAL.value,
        interval_minutes=30,
        daily_time=None,
        active_from=None,
        active_to=None,
        timezone=user.timezone,
        status=status,
        next_run_at=next_run_at,
    )


async def list_deliveries(session) -> list[ReminderDelivery]:
    result = await session.execute(select(ReminderDelivery).order_by(ReminderDelivery.id.asc()))
    return list(result.scalars().all())


async def test_delivers_due_active_reminder_and_advances_next_run(session_factory) -> None:
    async with session_factory() as session:
        now = datetime(2026, 4, 27, 12, 0, tzinfo=UTC)
        user = await create_user(session, 1001, "Asia/Almaty")
        reminder = await create_reminder(
            session,
            user,
            title="Focus",
            status=ReminderStatus.ACTIVE.value,
            next_run_at=datetime(2026, 4, 27, 11, 0, tzinfo=UTC),
        )
        sender = FakeSender()

        delivered = await ReminderDeliveryService(
            ReminderRepository(session),
            ReminderDeliveryRepository(session),
            sender,
        ).deliver_due_once(now_utc=now)

        deliveries = await list_deliveries(session)
        assert delivered == 1
        assert sender.sent_messages == [(user.chat_id, "Напоминание:\nFocus\n\nReturn to intention.")]
        assert deliveries[0].reminder_id == reminder.id
        assert deliveries[0].status == DeliveryStatus.SENT.value
        assert deliveries[0].sent_at == now.replace(tzinfo=None)
        assert reminder.next_run_at == datetime(2026, 4, 27, 12, 30, tzinfo=UTC)


async def test_skips_paused_and_deleted_reminders(session_factory) -> None:
    async with session_factory() as session:
        now = datetime(2026, 4, 27, 12, 0, tzinfo=UTC)
        user = await create_user(session, 1001)
        await create_reminder(
            session,
            user,
            title="Paused",
            status=ReminderStatus.PAUSED.value,
            next_run_at=datetime(2026, 4, 27, 11, 0, tzinfo=UTC),
        )
        deleted = await create_reminder(
            session,
            user,
            title="Deleted",
            status=ReminderStatus.ACTIVE.value,
            next_run_at=datetime(2026, 4, 27, 11, 0, tzinfo=UTC),
        )
        await ReminderRepository(session).soft_delete(deleted)
        sender = FakeSender()

        delivered = await ReminderDeliveryService(
            ReminderRepository(session),
            ReminderDeliveryRepository(session),
            sender,
        ).deliver_due_once(now_utc=now)

        assert delivered == 0
        assert sender.sent_messages == []
        assert await list_deliveries(session) == []


async def test_failed_send_creates_failed_delivery_without_advancing_next_run(session_factory) -> None:
    async with session_factory() as session:
        now = datetime(2026, 4, 27, 12, 0, tzinfo=UTC)
        due_at = datetime(2026, 4, 27, 11, 0, tzinfo=UTC)
        user = await create_user(session, 1001)
        reminder = await create_reminder(
            session,
            user,
            title="Focus",
            status=ReminderStatus.ACTIVE.value,
            next_run_at=due_at,
        )

        delivered = await ReminderDeliveryService(
            ReminderRepository(session),
            ReminderDeliveryRepository(session),
            FakeSender(should_fail=True),
        ).deliver_due_once(now_utc=now)

        deliveries = await list_deliveries(session)
        assert delivered == 0
        assert deliveries[0].status == DeliveryStatus.FAILED.value
        assert deliveries[0].sent_at is None
        assert deliveries[0].error_message == "telegram unavailable"
        assert reminder.next_run_at == due_at


async def test_daily_delivery_uses_user_timezone_for_next_run(session_factory) -> None:
    async with session_factory() as session:
        now = datetime(2026, 4, 27, 4, 30, tzinfo=UTC)
        user = await create_user(session, 1001, "Asia/Almaty")
        reminder = await ReminderRepository(session).create(
            user_id=user.id,
            title="Daily",
            message_text="Daily return.",
            schedule_type=ScheduleType.DAILY.value,
            interval_minutes=None,
            daily_time=time(10, 0),
            active_from=None,
            active_to=None,
            timezone=user.timezone,
            status=ReminderStatus.ACTIVE.value,
            next_run_at=datetime(2026, 4, 27, 4, 0, tzinfo=UTC),
        )

        delivered = await ReminderDeliveryService(
            ReminderRepository(session),
            ReminderDeliveryRepository(session),
            FakeSender(),
        ).deliver_due_once(now_utc=now)

        assert delivered == 1
        assert reminder.next_run_at == datetime(2026, 4, 27, 5, 0, tzinfo=UTC)


async def test_delivery_wrapper_uses_user_language(session_factory) -> None:
    async with session_factory() as session:
        now = datetime(2026, 4, 27, 12, 0, tzinfo=UTC)
        user = await create_user(session, 1001)
        user.language_code = "kk"
        await create_reminder(
            session,
            user,
            title="Ниет",
            status=ReminderStatus.ACTIVE.value,
            next_run_at=datetime(2026, 4, 27, 11, 0, tzinfo=UTC),
        )
        sender = FakeSender()

        await ReminderDeliveryService(
            ReminderRepository(session),
            ReminderDeliveryRepository(session),
            sender,
        ).deliver_due_once(now_utc=now)

        assert sender.sent_messages == [(user.chat_id, "Еске салу:\nНиет\n\nReturn to intention.")]


async def test_suppresses_due_reminder_for_bunker_active_user(session_factory) -> None:
    async with session_factory() as session:
        now = datetime(2026, 4, 27, 12, 0, tzinfo=UTC)
        due_at = datetime(2026, 4, 27, 11, 0, tzinfo=UTC)
        user = await create_user(session, 1001)
        reminder = await create_reminder(
            session,
            user,
            title="Focus",
            status=ReminderStatus.ACTIVE.value,
            next_run_at=due_at,
        )
        await BunkerService(UserRepository(session), clock=lambda: now).activate(user)
        sender = FakeSender()

        delivered = await ReminderDeliveryService(
            ReminderRepository(session),
            ReminderDeliveryRepository(session),
            sender,
        ).deliver_due_once(now_utc=now)

        assert delivered == 0
        assert sender.sent_messages == []
        assert await list_deliveries(session) == []
        assert reminder.next_run_at == due_at
        assert reminder.status == ReminderStatus.ACTIVE.value


async def test_due_query_handles_mixed_bunker_and_non_bunker_users(session_factory) -> None:
    async with session_factory() as session:
        now = datetime(2026, 4, 27, 12, 0, tzinfo=UTC)
        due_at = datetime(2026, 4, 27, 11, 0, tzinfo=UTC)
        active_user = await create_user(session, 1001)
        bunker_user = await create_user(session, 1002)
        active_reminder = await create_reminder(
            session,
            active_user,
            title="Deliver",
            status=ReminderStatus.ACTIVE.value,
            next_run_at=due_at,
        )
        bunker_reminder = await create_reminder(
            session,
            bunker_user,
            title="Suppress",
            status=ReminderStatus.ACTIVE.value,
            next_run_at=due_at,
        )
        await BunkerService(UserRepository(session), clock=lambda: now).activate(bunker_user)
        sender = FakeSender()

        delivered = await ReminderDeliveryService(
            ReminderRepository(session),
            ReminderDeliveryRepository(session),
            sender,
        ).deliver_due_once(now_utc=now)

        deliveries = await list_deliveries(session)
        assert delivered == 1
        assert len(sender.sent_messages) == 1
        assert sender.sent_messages[0][0] == active_user.chat_id
        assert "Deliver" in sender.sent_messages[0][1]
        assert "Return to intention." in sender.sent_messages[0][1]
        assert [delivery.reminder_id for delivery in deliveries] == [active_reminder.id]
        assert active_reminder.next_run_at == datetime(2026, 4, 27, 12, 30, tzinfo=UTC)
        assert bunker_reminder.next_run_at == due_at
        assert bunker_reminder.status == ReminderStatus.ACTIVE.value


async def test_delivery_service_guard_suppresses_bunker_reminder_without_record(session_factory) -> None:
    async with session_factory() as session:
        now = datetime(2026, 4, 27, 12, 0, tzinfo=UTC)
        due_at = datetime(2026, 4, 27, 11, 0, tzinfo=UTC)
        user = await create_user(session, 1001)
        reminder = await create_reminder(
            session,
            user,
            title="Guarded",
            status=ReminderStatus.ACTIVE.value,
            next_run_at=due_at,
        )
        await BunkerService(UserRepository(session), clock=lambda: now).activate(user)
        sender = FakeSender()
        service = ReminderDeliveryService(
            ReminderRepository(session),
            ReminderDeliveryRepository(session),
            sender,
        )

        delivered = await service._deliver_one(reminder, now)

        assert delivered is False
        assert sender.sent_messages == []
        assert await list_deliveries(session) == []
        assert reminder.next_run_at == due_at
        assert reminder.status == ReminderStatus.ACTIVE.value
