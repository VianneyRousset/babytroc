import enum

from _typeshed import Incomplete

from . import assets as assets

class NoWordsToChoseFrom(Exception): ...

class Defaults(enum.Enum):
    NOUNS = "nounlist.txt"
    VERBS = "verblist.txt"
    ADJECTIVES = "adjectivelist.txt"
    PROFANITIES = "profanitylist.txt"

class RandomWord:
    parts_of_speech: Incomplete

    def __init__(self, **kwargs) -> None: ...
    def filter(
        self,
        starts_with: str = "",
        ends_with: str = "",
        include_categories: list[str] | None = None,
        include_parts_of_speech: list[str] | None = None,
        word_min_length: int | None = None,
        word_max_length: int | None = None,
        regex: str | None = None,
    ): ...
    def random_words(
        self,
        amount: int = 1,
        starts_with: str = "",
        ends_with: str = "",
        include_categories: list[str] | None = None,
        include_parts_of_speech: list[str] | None = None,
        word_min_length: int | None = None,
        word_max_length: int | None = None,
        regex: str | None = None,
        return_less_if_necessary: bool = False,
    ): ...
    def word(
        self,
        starts_with: str = "",
        ends_with: str = "",
        include_categories: list[str] | None = None,
        include_parts_of_speech: list[str] | None = None,
        word_min_length: int | None = None,
        word_max_length: int | None = None,
        regex: str | None = None,
    ): ...
    @staticmethod
    def read_words(word_file): ...
