from types import SimpleNamespace

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.bot.handlers.language import _language_keyboard, handle_language_callback
from direm.db.base import Base
from direm.repositories.users import UserRepository


class FakeMessage:
    def __init__(self) -> None:
        self.chat = SimpleNamespace(id=2001)
        self.answers: list[str] = []

    async def answer(self, text: str, **kwargs) -> None:
        self.answers.append(text)


class FakeCallback:
    def __init__(self, data: str) -> None:
        self.data = data
        self.from_user = SimpleNamespace(id=1001, username="ilya", first_name="Ilya", language_code="ru")
        self.message = FakeMessage()
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


def test_language_keyboard_contains_supported_languages() -> None:
    keyboard = _language_keyboard()

    assert [row[0].callback_data for row in keyboard.inline_keyboard] == [
        "language:set:ru",
        "language:set:kk",
        "language:set:en",
    ]


async def test_language_callback_persists_selected_language(session_factory) -> None:
    async with session_factory() as session:
        callback = FakeCallback("language:set:kk")

        await handle_language_callback(callback, session)
        await session.commit()

        user = await UserRepository(session).get_by_telegram_user_id(1001)

    assert user is not None
    assert user.language_code == "kk"
    assert callback.message.answers == ["Тіл жаңартылды: 🇰🇿 Қазақша"]
