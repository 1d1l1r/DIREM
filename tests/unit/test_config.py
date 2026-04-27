import pytest

from direm.app.config import Settings


def test_default_settings_are_safe_placeholders() -> None:
    settings = Settings(_env_file=None)

    assert settings.direm_env == "local"
    assert settings.direm_version == "0.1.0"
    assert settings.direm_commit_sha == "unknown"
    assert settings.direm_build_date == "unknown"


def test_bot_token_placeholder_fails_clearly() -> None:
    settings = Settings(TELEGRAM_BOT_TOKEN="replace_me")

    with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN"):
        settings.require_bot_token()
