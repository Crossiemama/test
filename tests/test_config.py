import pytest

from bot.config import _normalize_bot_token


def test_normalize_bot_token_strips_quotes_and_spaces() -> None:
    token = "  \"123456:ABCdefGhIJKlmNOpQrstUVwxyZ\"  "
    assert _normalize_bot_token(token) == "123456:ABCdefGhIJKlmNOpQrstUVwxyZ"


def test_normalize_bot_token_raises_for_invalid_token() -> None:
    with pytest.raises(ValueError, match="неверный формат"):
        _normalize_bot_token("not-a-telegram-token")
