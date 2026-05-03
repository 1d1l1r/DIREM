from types import SimpleNamespace

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.bot.commands import build_bot_commands
from direm.bot.handlers.cancel import handle_cancel
from direm.db.base import Base
from direm.repositories.users import UserRepository
from direm.services.user_service import TelegramUserProfile, UserService


class FakeMessage:
    def __init__(self) -> None:
        self.answers: list[str] = []

    async def answer(self, text: str, **kwargs) -> None:
        self.answers.append(text)


class FakeState:
    def __init__(self, current_state: str | None) -> None:
        self.current_state = current_state
        self.cleared = False

    async def get_state(self) -> str | None:
        return self.current_state

    async def clear(self) -> None:
        self.cleared = True
        self.current_state = None


class FullFakeMessage:
    def __init__(self) -> None:
        self.from_user = SimpleNamespace(id=1001, username="ilya", first_name="Ilya", language_code="en")
        self.chat = SimpleNamespace(id=2001)
        self.answers: list[tuple[str, object | None]] = []

    async def answer(self, text: str, **kwargs) -> None:
        self.answers.append((text, kwargs.get("reply_markup")))


@pytest.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(engine, expire_on_commit=False)

    await engine.dispose()


def test_bot_command_menu_contains_current_commands() -> None:
    commands = build_bot_commands()

    assert [command.command for command in commands] == [
        "start",
        "help",
        "language",
        "timezone",
        "new",
        "list",
        "pause",
        "resume",
        "delete",
        "bunker",
        "version",
        "credits",
        "cancel",
    ]


async def test_cancel_clears_active_state(session_factory=None) -> None:
    message = FakeMessage()
    state = FakeState("CreateReminderFlow:waiting_title")

    class Session:
        pass

    message.from_user = None
    await handle_cancel(message, state, Session())

    assert state.cleared is True
    assert message.answers == ["Текущее действие отменено."]


async def test_cancel_without_active_state_is_friendly() -> None:
    message = FakeMessage()
    state = FakeState(None)

    class Session:
        pass

    message.from_user = None
    await handle_cancel(message, state, Session())

    assert state.cleared is False
    assert message.answers == ["Нечего отменять. Команды можно посмотреть через /help."]


async def test_cancel_active_flow_returns_home_status(session_factory) -> None:
    async with session_factory() as session:
        await UserService(UserRepository(session)).register_or_update_from_telegram(
            TelegramUserProfile(
                telegram_user_id=1001,
                chat_id=2001,
                username="ilya",
                first_name="Ilya",
                language_code="en",
            )
        )
        message = FullFakeMessage()
        state = FakeState("CreateReminderFlow:waiting_title")

        await handle_cancel(message, state, session)

    assert state.cleared is True
    assert message.answers[0][0] == "Current action cancelled."
    assert "DIREM is active." in message.answers[1][0]
    assert message.answers[1][1].keyboard[0][0].text == "Bunker OFF"
    assert message.answers[2][1].inline_keyboard[0][0].callback_data == "menu:list"
