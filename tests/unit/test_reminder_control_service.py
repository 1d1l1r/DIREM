from datetime import UTC, datetime, time

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.db.base import Base
from direm.domain.constants import ReminderStatus, ScheduleType
from direm.repositories.reminders import ReminderRepository
from direm.repositories.users import UserRepository
from direm.services.reminder_control_service import ReminderControlService, ReminderSelectionError
from direm.services.reminder_service import CreateReminderRequest, ReminderService
from direm.services.user_service import TelegramUserProfile, UserService


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


async def create_interval_reminder(session, user, title: str):
    return await ReminderService(ReminderRepository(session)).create_reminder(
        user,
        CreateReminderRequest(
            title=title,
            message_text="Return.",
            schedule_type=ScheduleType.INTERVAL.value,
            interval_minutes=30,
        ),
    )


async def create_windowed_interval_reminder(session, user, title: str):
    return await ReminderService(ReminderRepository(session)).create_reminder(
        user,
        CreateReminderRequest(
            title=title,
            message_text="Return.",
            schedule_type=ScheduleType.INTERVAL.value,
            interval_minutes=30,
            active_from=time(10, 0),
            active_to=time(18, 0),
        ),
    )


async def test_control_empty_state(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        service = ReminderControlService(ReminderRepository(session))

        selectable = await service.list_selectable_for_user(user)

        assert selectable == []
        assert service.render_selection_prompt("pause", selectable, user.timezone) == "No reminders yet.\nCreate one with /new."


async def test_control_selection_prompt_renders_without_active_window(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        await create_interval_reminder(session, user, "Focus")
        service = ReminderControlService(ReminderRepository(session))
        selectable = await service.list_selectable_for_user(user)

        rendered = service.render_selection_prompt("pause", selectable, user.timezone)

        assert "Choose reminder to pause." in rendered
        assert "Focus" in rendered
        assert "Active window: all day" in rendered


async def test_control_selection_prompt_renders_active_window_for_delete(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        await create_windowed_interval_reminder(session, user, "Windowed")
        service = ReminderControlService(ReminderRepository(session))
        selectable = await service.list_selectable_for_user(user)

        rendered = service.render_selection_prompt("delete", selectable, user.timezone)

        assert "Choose reminder to delete." in rendered
        assert "Windowed" in rendered
        assert "Active window: 10:00-18:00" in rendered


async def test_pause_changes_status_for_current_user(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        created = await create_interval_reminder(session, user, "Focus")
        service = ReminderControlService(ReminderRepository(session))

        paused = await service.pause_for_user(user, str(created.reminder.id))

        assert paused.status == ReminderStatus.PAUSED.value


async def test_resume_changes_status_and_refreshes_next_run(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        created = await create_interval_reminder(session, user, "Focus")
        service = ReminderControlService(ReminderRepository(session))
        paused = await service.pause_for_user(user, str(created.reminder.id))
        paused.next_run_at = datetime(2020, 1, 1, tzinfo=UTC)

        resumed = await service.resume_for_user(user, str(created.reminder.id))

        assert resumed.status == ReminderStatus.ACTIVE.value
        assert resumed.next_run_at > datetime.now(UTC)


async def test_control_rejects_other_user_reminder(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        other_user = await create_user(session, 1002)
        other_created = await create_interval_reminder(session, other_user, "Other")
        service = ReminderControlService(ReminderRepository(session))

        with pytest.raises(ReminderSelectionError):
            await service.pause_for_user(user, str(other_created.reminder.id))


async def test_control_accepts_public_number_selection(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        await create_interval_reminder(session, user, "First")
        await create_interval_reminder(session, user, "Second")
        service = ReminderControlService(ReminderRepository(session))

        paused = await service.pause_for_user(user, "1")

        assert paused.status == ReminderStatus.PAUSED.value
        assert paused.title == "First"


async def test_control_selectable_can_filter_by_status(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        first = await create_interval_reminder(session, user, "Active")
        second = await create_interval_reminder(session, user, "Paused")
        service = ReminderControlService(ReminderRepository(session))
        await service.pause_for_user(user, str(second.reminder.id))

        active_selectable = await service.list_selectable_for_user(user, status=ReminderStatus.ACTIVE.value)
        paused_selectable = await service.list_selectable_for_user(user, status=ReminderStatus.PAUSED.value)

        assert [item.reminder.title for item in active_selectable] == ["Active"]
        assert [item.reminder.title for item in paused_selectable] == ["Paused"]


async def test_control_rejects_invalid_selection(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        await create_interval_reminder(session, user, "First")
        service = ReminderControlService(ReminderRepository(session))

        with pytest.raises(ReminderSelectionError):
            await service.pause_for_user(user, "abc")

        with pytest.raises(ReminderSelectionError):
            await service.pause_for_user(user, "999")


async def test_delete_marks_current_user_reminder_deleted(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        created = await create_interval_reminder(session, user, "Focus")
        repository = ReminderRepository(session)
        service = ReminderControlService(repository)

        deleted = await service.delete_for_user(user, str(created.reminder.id))
        reminders = await repository.list_by_user_id(user.id)

        assert deleted.deleted_at is not None
        assert reminders == []


async def test_delete_accepts_public_number_selection(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        await create_interval_reminder(session, user, "First")
        await create_interval_reminder(session, user, "Second")
        service = ReminderControlService(ReminderRepository(session))

        deleted = await service.delete_for_user(user, "1")

        assert deleted.title == "First"
        assert deleted.deleted_at is not None


async def test_delete_rejects_other_user_reminder(session_factory) -> None:
    async with session_factory() as session:
        user = await create_user(session, 1001)
        other_user = await create_user(session, 1002)
        other_created = await create_interval_reminder(session, other_user, "Other")
        service = ReminderControlService(ReminderRepository(session))

        with pytest.raises(ReminderSelectionError):
            await service.delete_for_user(user, str(other_created.reminder.id))
