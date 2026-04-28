import pytest

from direm.i18n import language_name, normalize_language_code, supported_language_codes, t
from direm.i18n.catalog import CATALOG


def test_supported_language_codes_are_locked() -> None:
    assert supported_language_codes() == ("ru", "kk", "en")


@pytest.mark.parametrize(
    ("input_code", "expected"),
    [
        ("ru", "ru"),
        ("kk", "kk"),
        ("en", "en"),
        ("en-US", "en"),
        ("de", "ru"),
        (None, "ru"),
    ],
)
def test_normalize_language_code(input_code, expected) -> None:
    assert normalize_language_code(input_code) == expected


def test_language_names_match_buttons() -> None:
    assert language_name("ru") == "🇷🇺 Русский"
    assert language_name("kk") == "🇰🇿 Қазақша"
    assert language_name("en") == "🇬🇧 English"


def test_catalog_has_same_keys_for_supported_languages() -> None:
    keys = set(CATALOG["ru"])
    assert keys
    assert set(CATALOG["kk"]) == keys
    assert set(CATALOG["en"]) == keys


def test_translation_uses_language_and_fallback() -> None:
    assert t("kk", "delivery.wrapper") == "Еске салу:"
    assert t("unknown", "delivery.wrapper") == "Напоминание:"


@pytest.mark.parametrize("language_code", ["ru", "kk", "en"])
def test_help_text_is_user_facing(language_code) -> None:
    help_text = t(language_code, "help.text")

    assert "/new" in help_text
    assert "/delete" in help_text
    assert "Worker" not in help_text
    assert "webhook" not in help_text.lower()
    assert "dashboard" not in help_text.lower()
