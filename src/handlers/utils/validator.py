import re

from src.lexicon.lexicon_ru import ERROR_LEXICON_RU

FORBIDDEN_CHARS: tuple[str, ...] = ("_", "@", "/", "\\", "-", "+", "[", "]", "|")

no_numbers_regex = re.compile(r"^[^0-9]*$")
only_digits_regex = re.compile(r"^\d+$")


def check_valid_msg(text: str) -> tuple[str | None, ...]:
    if any(ch in text for ch in FORBIDDEN_CHARS):
        return None, ERROR_LEXICON_RU["incorrect_format"] + ERROR_LEXICON_RU["prohibited_symbol"] + repr(FORBIDDEN_CHARS)
    return text, None


def check_valid_title(text: str) -> tuple[str | None, None | str]:
    _, exc_msg = check_valid_msg(text)
    if exc_msg:
        return None, exc_msg

    if not bool(no_numbers_regex.match(text)):
        return None, ERROR_LEXICON_RU["incorrect_format"] + ERROR_LEXICON_RU["is_digits"]

    if not 2 <= len(text) <= 40:
        return None, ERROR_LEXICON_RU["incorrect_format"] + ERROR_LEXICON_RU["length_val"]
    return text, None


def check_valid_days(text: str) -> tuple[None | str, str | None]:
    _, exc_msg = check_valid_msg(text)
    if exc_msg:
        return None, exc_msg

    if not bool(only_digits_regex.match(text)):
        return None, ERROR_LEXICON_RU["incorrect_format"] + ERROR_LEXICON_RU["not_digit"]

    return text, None
