"""Tests for the user-interface translation layer."""

from chronobright.i18n import Translator, normalize_language


def test_translator_renders_turkish_interpolated_text() -> None:
    translator = Translator("tr")

    assert translator.translate("brightness", level=65) == "Parlaklık: %65"


def test_translator_falls_back_to_english_for_unknown_language() -> None:
    translator = Translator("de")

    assert translator.language == "en"
    assert translator.translate("save_apply") == "Save & Apply Schedule"


def test_normalize_language_accepts_supported_codes_only() -> None:
    assert normalize_language("tr") == "tr"
    assert normalize_language(None) == "en"


def test_translator_returns_unknown_key_unchanged() -> None:
    assert Translator().translate("missing_key") == "missing_key"
