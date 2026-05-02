from types import SimpleNamespace

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.bot.handlers.timezone import (
    COMMON_TIMEZONES,
    _timezone_keyboard,
    handle_timezone_callback,
    handle_timezone_command,
    handle_timezone_input,
)
from direm.db.base import Base
from direm.repositories.users import UserRepository


class FakeState:
    def __init__(self) -> None:
        self.state = None
        self.cleared = False

    async def set_state(self, state) -> None:
        self.state = state

    async def clear(self) -> None:
        self.state = None
        self.cleared = True


class FakeMessage:
    def __init__(self, *, text: str | None = None, language_code: str = "en") -> None:
        self.text = text
        self.from_user = SimpleNamespace(id=1001, username="ilya", first_name="Ilya", language_code=language_code)
        self.chat = SimpleNamespace(id=2001)
        self.answers: list[tuple[str, object | None]] = []

    async def answer(self, text: str, **kwargs) -> None:
        self.answers.append((text, kwargs.get("reply_markup")))


class FakeCallback:
    def __init__(self, data: str, *, language_code: str = "en") -> None:
        self.data = data
        self.from_user = SimpleNamespace(id=1001, username="ilya", first_name="Ilya", language_code=language_code)
        self.message = FakeMessage(language_code=language_code)
        self.answers: list[tuple[str | None, bool | None]] = []

    async def answer(self, text: str | None = None, show_alert: bool | None = None) -> None:
        self.answers.append((text, show_alert))


@pytest.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(engine, expire_on_commit=False)

    await engine.dispose()


def test_timezone_keyboard_contains_common_choices_and_manual() -> None:
    keyboard = _timezone_keyboard("en")

    callback_data = [row[0].callback_data for row in keyboard.inline_keyboard]
    assert callback_data == [*(f"timezone:set:{timezone}" for timezone in COMMON_TIMEZONES), "timezone:manual"]
    assert keyboard.inline_keyboard[-1][0].text == "Enter manually"


async def test_timezone_command_renders_current_timezone_and_picker(session_factory) -> None:
    async with session_factory() as session:
        message = FakeMessage(language_code="en")
        state = FakeState()

        await handle_timezone_command(message, state, session)

    prompt, reply_keyboard = message.answers[0]
    picker_prompt, inline_keyboard = message.answers[1]
    assert "Current timezone: UTC" in prompt
    assert "Choose an option below" in prompt
    assert reply_keyboard.keyboard[0][0].text == "Cancel"
    assert picker_prompt == "Common choices:"
    assert inline_keyboard.inline_keyboard[0][0].callback_data == "timezone:set:Asia/Almaty"


async def test_timezone_callback_persists_almaty(session_factory) -> None:
    async with session_factory() as session:
        callback = FakeCallback("timezone:set:Asia/Almaty", language_code="en")
        state = FakeState()

        await handle_timezone_callback(callback, state, session)
        await session.commit()

        user = await UserRepository(session).get_by_telegram_user_id(1001)

    assert user is not None
    assert user.timezone == "Asia/Almaty"
    assert state.cleared is True
    assert callback.message.answers[0][0] == "Timezone updated: Asia/Almaty"


async def test_timezone_callback_persists_kazakhstan_timezone(session_factory) -> None:
    async with session_factory() as session:
        callback = FakeCallback("timezone:set:Asia/Qyzylorda", language_code="en")
        state = FakeState()

        await handle_timezone_callback(callback, state, session)
        await session.commit()

        user = await UserRepository(session).get_by_telegram_user_id(1001)

    assert user is not None
    assert user.timezone == "Asia/Qyzylorda"


async def test_timezone_manual_callback_keeps_manual_input_path(session_factory) -> None:
    async with session_factory() as session:
        callback = FakeCallback("timezone:manual", language_code="en")
        state = FakeState()

        await handle_timezone_callback(callback, state, session)

    assert state.state is not None
    assert "Europe/London" in callback.message.answers[0][0]
    assert callback.message.answers[0][1].keyboard[0][0].text == "Cancel"


async def test_timezone_manual_input_still_persists_iana_timezone(session_factory) -> None:
    async with session_factory() as session:
        message = FakeMessage(text="Europe/London", language_code="en")
        state = FakeState()

        await handle_timezone_input(message, state, session)
        await session.commit()

        user = await UserRepository(session).get_by_telegram_user_id(1001)

    assert user is not None
    assert user.timezone == "Europe/London"
    assert state.cleared is True
    assert message.answers[0][0] == "Timezone updated: Europe/London"


async def test_timezone_invalid_input_returns_recovery_text(session_factory) -> None:
    async with session_factory() as session:
        message = FakeMessage(text="Not/AZone", language_code="en")
        state = FakeState()

        await handle_timezone_input(message, state, session)

    assert state.cleared is False
    assert "Invalid timezone." in message.answers[0][0]
    assert "start again with /timezone" in message.answers[0][0]
    assert message.answers[0][1].keyboard[0][0].text == "Cancel"


async def test_timezone_invalid_callback_does_not_crash(session_factory) -> None:
    async with session_factory() as session:
        callback = FakeCallback("timezone:set:Bad/Zone", language_code="en")
        state = FakeState()

        await handle_timezone_callback(callback, state, session)

    assert callback.answers == [("Could not use that timezone choice. Open /timezone again.", True)]
    assert state.cleared is False
