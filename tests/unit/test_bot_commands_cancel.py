from direm.bot.commands import build_bot_commands
from direm.bot.handlers.cancel import handle_cancel


class FakeMessage:
    def __init__(self) -> None:
        self.answers: list[str] = []

    async def answer(self, text: str) -> None:
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
