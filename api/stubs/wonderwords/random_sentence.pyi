from _typeshed import Incomplete

from .random_word import Defaults as Defaults
from .random_word import RandomWord as RandomWord

VOWELS: Incomplete

class RandomSentence:
    gen: Incomplete

    def __init__(
        self,
        nouns: list[str] | None = None,
        verbs: list[str] | None = None,
        adjectives: list[str] | None = None,
    ) -> None: ...
    def bare_bone_sentence(self): ...
    def simple_sentence(self): ...
    def bare_bone_with_adjective(self): ...
    def sentence(self): ...
