from types import SimpleNamespace

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.bot.handlers.new import confirm_create
from direm.bot.middlewares import DatabaseSessionMiddleware
from direm.bot.router import build_router
from direm.db.base import Base
from direm.repositories.reminders import ReminderRepository


class FakeMessage:
    def __init__(self) -> None:
        self.chat = SimpleNamespace(id=2001)
        self.answers: list[str] = []

    async def answer(self, text: str, **kwargs) -> None:
        self.answers.append(text)


class FakeCallback:
    def __init__(self) -> None:
        self.from_user = SimpleNamespace(id=1001, username="ilya", first_name="Ilya", language_code="en")
        self.message = FakeMessage()
        self.answered = False

    async def answer(self) -> None:
        self.answered = True


class FakeState:
    def __init__(self, data: dict) -> None:
        self.data = data
        self.cleared = False

    async def get_data(self) -> dict:
        return self.data

    async def clear(self) -> None:
        self.cleared = True
        self.data = {}


@pytest.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(engine, expire_on_commit=False)

    await engine.dispose()


def test_callback_queries_receive_database_session_middleware() -> None:
    router = build_router()

    assert any(isinstance(middleware, DatabaseSessionMiddleware) for middleware in router.callback_query.middleware._middlewares)


async def test_confirm_create_persists_reminder_and_clears_state(session_factory) -> None:
    state = FakeState(
        {
            "title": "Dorpheus focus",
            "message_text": "Return to the current step.",
            "schedule_type": "interval",
            "interval_minutes": 45,
            "daily_time": None,
            "active_from": None,
            "active_to": None,
            "timezone": "Asia/Almaty",
        }
    )
    callback = FakeCallback()

    async with session_factory() as session:
        await confirm_create(callback, state, session)
        await session.commit()

        reminders = await ReminderRepository(session).list_by_user_id(1)

    assert state.cleared is True
    assert callback.answered is True
    assert callback.message.answers[0].startswith("Reminder created.")
    assert len(reminders) == 1
    assert reminders[0].title == "Dorpheus focus"
