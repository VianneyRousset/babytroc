from itertools import groupby
import random


ALL_WORDS = [
    "lorem",
    "ipsum",
    "dolor",
    "sit",
    "amet",
    "consectetur",
    "adipiscing",
    "elit",
    "sed",
    "do",
    "eiusmod",
    "tempor",
    "incididunt",
    "ut",
    "labore",
    "et",
    "dolore",
    "magna",
    "aliqua",
    "enim",
    "ad",
    "minim",
    "veniam",
    "quis",
    "nostrud",
    "exercitation",
    "ullamco",
    "laboris",
    "nisi",
    "ut",
    "aliquip",
    "ex",
    "ea",
    "commodo",
    "consequat",
    "duis",
    "aute",
    "irure",
    "dolor",
    "in",
    "reprehenderit",
    "in",
    "voluptate",
    "velit",
    "esse",
    "cillum",
    "dolore",
    "eu",
    "fugiat",
    "nulla",
    "pariatur",
    "excepteur",
    "sint",
    "occaecat",
    "cupidatat",
    "non",
    "proident",
    "sunt",
    "in",
    "culpa",
    "qui",
    "officia",
    "deserunt",
    "mollit",
    "anim",
    "id",
    "est",
    "laborum",
]

ALL_WORDS_BY_LENGTH = {
    wl: set(w)
    for wl, w in groupby(
        iterable=sorted(
            ALL_WORDS,
            key=len,
        ),
        key=len,
    )
}
MIN_WORDS_LENGTH = min(ALL_WORDS_BY_LENGTH.keys())
MAX_WORDS_LENGTH = max(ALL_WORDS_BY_LENGTH.keys())


def lorem_word(
    length=None,
    *,
    min_length=MIN_WORDS_LENGTH,
    max_length=MAX_WORDS_LENGTH,
):
    if length is not None:
        min_length = length
        max_length = length

    available_words = [
        word
        for word_length, words_list in ALL_WORDS_BY_LENGTH.items()
        for word in words_list
        if word_length >= min_length and word_length <= max_length
    ]
    return random.choice(available_words)


def lorem_sentence(
    length=None,
    *,
    min_length=30,
    max_length=60,
    separator=" ",
    end="",
    capitalize=True,
):
    if length is None:
        return lorem_sentence(
            length=random.randint(min_length, max_length),
            separator=separator,
            end=end,
            capitalize=capitalize,
        )

    if end:
        return (
            lorem_sentence(
                length=length - len(end),
                separator=separator,
                end="",
                capitalize=capitalize,
            )
            + end
        )

    words = []
    remaining_length = length

    while remaining_length > 0:
        if remaining_length < MAX_WORDS_LENGTH:
            word = lorem_word(
                length=remaining_length,
            )

        else:
            word = lorem_word(
                max_length=remaining_length - MIN_WORDS_LENGTH - len(separator),
            )

        words.append(word)
        remaining_length = remaining_length - len(word) - len(separator)

    sentence = separator.join(words)

    if capitalize:
        sentence = sentence.capitalize()

    return sentence


def lorem_paragraph(
    length=None,
    *,
    min_length=100,
    max_length=300,
    max_sentence_length=60,
):
    if length is None:
        return lorem_paragraph(random.randint(min_length, max_length))

    separator = " "
    sentences = []
    remaining_length = length

    while remaining_length > 0:
        if remaining_length < max_sentence_length:
            sentence = lorem_sentence(
                length=remaining_length,
                end=".",
            )

        else:
            sentence = lorem_sentence(
                max_length=min(
                    remaining_length - MIN_WORDS_LENGTH - len(separator) - 1,
                    max_sentence_length,
                ),
                end=".",
            )

        sentences.append(sentence)
        remaining_length = remaining_length - len(sentence) - len(separator)

    return separator.join(sentences)
