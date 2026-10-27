import random

import pytest

from kafka_namer.generator import generate_name, generate_names
from kafka_namer.words import ADJECTIVES, NOUNS


def test_name_has_two_words_from_the_word_lists():
    adjective, noun = generate_name().split("-")
    assert adjective in ADJECTIVES
    assert noun in NOUNS


def test_same_seed_gives_same_name():
    assert generate_name(random.Random(42)) == generate_name(random.Random(42))


def test_custom_separator():
    assert "_" in generate_name(separator="_")


def test_prefix_is_prepended():
    assert generate_name(prefix="prod").startswith("prod-")


def test_generate_names_returns_requested_count_of_unique_names():
    names = generate_names(10)
    assert len(names) == 10
    assert len(set(names)) == 10


def test_generate_names_rejects_impossible_count():
    with pytest.raises(ValueError):
        generate_names(len(ADJECTIVES) * len(NOUNS) + 1)
