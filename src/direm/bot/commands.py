from aiogram.types import BotCommand


COMMANDS: tuple[tuple[str, str], ...] = (
    ("start", "Open DIREM"),
    ("help", "Show help"),
    ("language", "Choose language"),
    ("timezone", "View or set timezone"),
    ("new", "Create reminder"),
    ("list", "Show reminders"),
    ("pause", "Pause reminder"),
    ("resume", "Resume reminder"),
    ("delete", "Delete reminder"),
    ("bunker", "Toggle Bunker mode"),
    ("version", "Show version"),
    ("credits", "Show credits"),
    ("cancel", "Cancel current action"),
)


def build_bot_commands() -> list[BotCommand]:
    return [BotCommand(command=command, description=description) for command, description in COMMANDS]
