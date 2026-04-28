import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.db.base import Base
from direm.db.models import User
from direm.domain.errors import InvalidTimezoneError
from direm.repositories.users import UserRepository
from direm.services.user_service import TelegramUserProfile, UserService


@pytest.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(engine, expire_on_commit=False)

    await engine.dispose()


async def test_register_creates_user_with_default_utc_timezone(session_factory) -> None:
    async with session_factory() as session:
        service = UserService(UserRepository(session))

        user = await service.register_or_update_from_telegram(
            TelegramUserProfile(
                telegram_user_id=1001,
                chat_id=2001,
                username="first",
                first_name="First",
            )
        )
        await session.commit()

        assert user.telegram_user_id == 1001
        assert user.chat_id == 2001
        assert user.username == "first"
        assert user.first_name == "First"
        assert user.timezone == "UTC"
        assert user.language_code == "ru"


async def test_register_uses_supported_telegram_language(session_factory) -> None:
    async with session_factory() as session:
        service = UserService(UserRepository(session))

        user = await service.register_or_update_from_telegram(
            TelegramUserProfile(
                telegram_user_id=1001,
                chat_id=2001,
                username="first",
                first_name="First",
                language_code="kk",
            )
        )

        assert user.language_code == "kk"


async def test_register_falls_back_to_ru_for_unsupported_language(session_factory) -> None:
    async with session_factory() as session:
        service = UserService(UserRepository(session))

        user = await service.register_or_update_from_telegram(
            TelegramUserProfile(
                telegram_user_id=1001,
                chat_id=2001,
                username="first",
                first_name="First",
                language_code="de",
            )
        )

        assert user.language_code == "ru"


async def test_repeated_start_preserves_timezone_and_does_not_duplicate(session_factory) -> None:
    async with session_factory() as session:
        service = UserService(UserRepository(session))

        user = await service.register_or_update_from_telegram(
            TelegramUserProfile(
                telegram_user_id=1001,
                chat_id=2001,
                username="first",
                first_name="First",
            )
        )
        await service.update_timezone(user, "Asia/Almaty")
        await service.update_language(user, "en")

        updated = await service.register_or_update_from_telegram(
            TelegramUserProfile(
                telegram_user_id=1001,
                chat_id=3001,
                username="second",
                first_name="Second",
            )
        )
        await session.commit()

        result = await session.execute(select(User).where(User.telegram_user_id == 1001))
        users = result.scalars().all()

        assert len(users) == 1
        assert updated.id == user.id
        assert updated.chat_id == 3001
        assert updated.username == "second"
        assert updated.first_name == "Second"
        assert updated.timezone == "Asia/Almaty"
        assert updated.language_code == "en"


async def test_update_timezone_accepts_valid_iana_timezone(session_factory) -> None:
    async with session_factory() as session:
        service = UserService(UserRepository(session))
        user = await service.register_or_update_from_telegram(
            TelegramUserProfile(
                telegram_user_id=1001,
                chat_id=2001,
                username=None,
                first_name=None,
            )
        )

        updated = await service.update_timezone(user, "Asia/Almaty")

        assert updated.timezone == "Asia/Almaty"


async def test_update_timezone_rejects_invalid_timezone(session_factory) -> None:
    async with session_factory() as session:
        service = UserService(UserRepository(session))
        user = await service.register_or_update_from_telegram(
            TelegramUserProfile(
                telegram_user_id=1001,
                chat_id=2001,
                username=None,
                first_name=None,
            )
        )

        with pytest.raises(InvalidTimezoneError):
            await service.update_timezone(user, "Almaty")

        assert user.timezone == "UTC"
