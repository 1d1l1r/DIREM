from types import SimpleNamespace

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from direm.bot.handlers.menu import handle_menu_action, handle_menu_navigation, handle_stale_menu_callback
from direm.bot.menu import help_hub_keyboard, list_hub_keyboard, main_menu_keyboard, render_main_menu_text, settings_hub_keyboard
from direm.db.base import Base
from direm.repositories.users import UserRepository
from direm.services.user_service import TelegramUserProfile, UserService


class FakeState:
    def __init__(self) -> None:
        self.state = None
        self.cleared = False
        self.data = {}

    async def set_state(self, state) -> None:
        self.state = state

    async def clear(self) -> None:
        self.state = None
        self.cleared = True

    async def update_data(self, **kwargs) -> None:
        self.data.update(kwargs)

    async def get_data(self):
        return self.data


class FakeMessage:
    def __init__(self) -> None:
        self.chat = SimpleNamespace(id=2001)
        self.answers: list[tuple[str, object | None]] = []

    async def answer(self, text: str, **kwargs) -> None:
        self.answers.append((text, kwargs.get("reply_markup")))


class FakeCallback:
    def __init__(self, data: str, *, language_code: str = "en") -> None:
        self.data = data
        self.from_user = SimpleNamespace(id=1001, username="ilya", first_name="Ilya", language_code=language_code)
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


async def seed_user(session, *, language_code: str = "en"):
    service = UserService(UserRepository(session))
    user = await service.register_or_update_from_telegram(
        TelegramUserProfile(
            telegram_user_id=1001,
            chat_id=2001,
            username="ilya",
            first_name="Ilya",
            language_code=language_code,
        )
    )
    return user


def test_main_menu_keyboard_is_localized() -> None:
    keyboard = main_menu_keyboard("en")

    assert [button.text for button in keyboard.inline_keyboard[0]] == ["List", "Settings", "Help"]
    assert [button.callback_data for button in keyboard.inline_keyboard[0]] == ["menu:list", "menu:settings", "menu:help"]
    assert keyboard.inline_keyboard[1][0].text == "Bunker off"
    assert keyboard.inline_keyboard[1][0].callback_data == "menu:bunker"


def test_hub_keyboards_have_expected_actions() -> None:
    assert [button.callback_data for row in list_hub_keyboard("en").inline_keyboard for button in row] == [
        "menu:action:new",
        "menu:action:pause",
        "menu:action:resume",
        "menu:action:delete",
        "menu:home",
    ]
    assert [button.callback_data for row in settings_hub_keyboard("en").inline_keyboard for button in row] == [
        "menu:action:language",
        "menu:action:timezone",
        "menu:home",
    ]
    assert [button.callback_data for row in help_hub_keyboard("en").inline_keyboard for button in row] == [
        "menu:action:version",
        "menu:action:credits",
        "menu:home",
    ]


@pytest.mark.parametrize("language_code", ["ru", "kk", "en"])
def test_main_menu_text_contains_timezone_and_language(language_code: str) -> None:
    text = render_main_menu_text(language_code, "Asia/Almaty")

    assert "Asia/Almaty" in text
    assert "DIREM" in text


async def test_navigation_callbacks_render_hubs(session_factory) -> None:
    async with session_factory() as session:
        await seed_user(session, language_code="en")
        await session.commit()

        list_callback = FakeCallback("menu:list", language_code="en")
        settings_callback = FakeCallback("menu:settings", language_code="en")
        help_callback = FakeCallback("menu:help", language_code="en")

        await handle_menu_navigation(list_callback, session)
        await handle_menu_navigation(settings_callback, session)
        await handle_menu_navigation(help_callback, session)

    assert "Reminders and actions." in list_callback.message.answers[0][0]
    assert list_callback.message.answers[0][1].inline_keyboard[0][0].callback_data == "menu:action:new"
    assert "DIREM settings." in settings_callback.message.answers[0][0]
    assert settings_callback.message.answers[0][1].inline_keyboard[0][0].callback_data == "menu:action:language"
    assert "/version" in help_callback.message.answers[0][0]
    assert help_callback.message.answers[0][1].inline_keyboard[0][0].callback_data == "menu:action:version"


async def test_home_callback_returns_main_menu(session_factory) -> None:
    async with session_factory() as session:
        user = await seed_user(session, language_code="en")
        await UserService(UserRepository(session)).update_timezone(user, "Asia/Almaty")
        await session.commit()

        callback = FakeCallback("menu:home", language_code="en")
        await handle_menu_navigation(callback, session)

    assert "DIREM is active." in callback.message.answers[0][0]
    assert "Asia/Almaty" in callback.message.answers[0][0]
    assert callback.message.answers[0][1].inline_keyboard[0][0].callback_data == "menu:list"


async def test_action_callback_routes_to_new_flow(session_factory) -> None:
    async with session_factory() as session:
        await seed_user(session, language_code="en")
        await session.commit()
        callback = FakeCallback("menu:action:new", language_code="en")
        state = FakeState()

        await handle_menu_action(callback, state, session)

    assert "Create reminder." in callback.message.answers[0][0]
    assert state.state is not None
    assert state.data["language_code"] == "en"


async def test_action_callback_routes_to_version(session_factory) -> None:
    async with session_factory() as session:
        await seed_user(session, language_code="en")
        await session.commit()
        callback = FakeCallback("menu:action:version", language_code="en")

        await handle_menu_action(callback, FakeState(), session)

    assert "DIREM v0.1.0" in callback.message.answers[0][0]


async def test_navigation_callback_routes_to_bunker_screen(session_factory) -> None:
    async with session_factory() as session:
        user = await seed_user(session, language_code="en")
        user.bunker_active = True
        await session.commit()
        callback = FakeCallback("menu:bunker", language_code="en")

        await handle_menu_navigation(callback, session)

    assert "Bunker is active." in callback.message.answers[0][0]
    assert callback.message.answers[0][1].inline_keyboard[0][0].callback_data == "bunker:deactivate"


async def test_stale_menu_callback_does_not_crash(session_factory) -> None:
    async with session_factory() as session:
        await seed_user(session, language_code="en")
        await session.commit()
        callback = FakeCallback("menu:unknown", language_code="en")

        await handle_stale_menu_callback(callback, session)

    assert callback.answers == [("This menu is stale. Open /start again.", True)]
