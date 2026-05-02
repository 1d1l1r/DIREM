from types import SimpleNamespace

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.bot.handlers.start import handle_start
from direm.db.base import Base
from direm.repositories.users import UserRepository
from direm.services.user_service import TelegramUserProfile, UserService


class FakeMessage:
    def __init__(self, *, language_code: str = "en") -> None:
        self.from_user = SimpleNamespace(id=1001, username="ilya", first_name="Ilya", language_code=language_code)
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


async def test_start_shows_onboarding_for_new_user(session_factory) -> None:
    async with session_factory() as session:
        message = FakeMessage(language_code="en")

        await handle_start(message, session)
        await session.commit()

    answer, keyboard = message.answers[0]
    assert "Quick start:" in answer
    assert "/language" in answer
    assert "/timezone" in answer
    assert "/new" in answer
    assert "/help" in answer
    assert keyboard.keyboard[0][0].text == "Help"


async def test_start_keeps_existing_user_non_intrusive(session_factory) -> None:
    async with session_factory() as session:
        service = UserService(UserRepository(session))
        user = await service.register_or_update_from_telegram(
            TelegramUserProfile(
                telegram_user_id=1001,
                chat_id=2001,
                username="ilya",
                first_name="Ilya",
                language_code="en",
            )
        )
        await service.update_timezone(user, "Asia/Almaty")
        await service.update_language(user, "kk")
        await session.commit()

        message = FakeMessage(language_code="en")
        await handle_start(message, session)
        await session.commit()

        updated = await UserRepository(session).get_by_telegram_user_id(1001)

    answer, keyboard = message.answers[0]
    assert "Жылдам бастау:" not in answer
    assert "DIREM іске қосылды." in answer
    assert "Asia/Almaty" in answer
    assert updated is not None
    assert updated.timezone == "Asia/Almaty"
    assert updated.language_code == "kk"
    assert keyboard.keyboard[0][0].text == "Көмек"


@pytest.mark.parametrize(
    ("language_code", "expected"),
    [
        ("ru", "Быстрый старт:"),
        ("kk", "Жылдам бастау:"),
        ("en", "Quick start:"),
    ],
)
async def test_start_onboarding_is_localized(session_factory, language_code: str, expected: str) -> None:
    async with session_factory() as session:
        message = FakeMessage(language_code=language_code)

        await handle_start(message, session)

    assert expected in message.answers[0][0]
