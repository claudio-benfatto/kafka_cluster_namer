"""Core name generation logic."""

import random
import re

from kafka_namer.words import ADJECTIVES, NOUNS

MAX_NAME_LENGTH = 249  # Kafka's limit for topic names; a safe upper bound for cluster names too
VALID_PREFIX = re.compile(r"[a-z0-9-]*")


def validate_prefix(prefix: str) -> bool:
    """Return True if the prefix only contains lowercase letters, digits and dashes."""
    return VALID_PREFIX.match(prefix) is not None


def generate_name(
    rng: random.Random | None = None,
    separator: str = "-",
    prefix: str | None = None,
) -> str:
    """Return a single "adjective-noun" name, e.g. "swift-otter".

    Pass a seeded ``random.Random`` for reproducible output.
    If ``prefix`` is given, it is prepended, e.g. "prod-swift-otter".
    """
    rng = rng or random.Random()
    parts = [rng.choice(ADJECTIVES), rng.choice(NOUNS)]
    if prefix:
        parts.insert(0, prefix)

    name = separator.join(parts)
    if len(name) >= MAX_NAME_LENGTH:
        raise ValueError(f"Generated name exceeds {MAX_NAME_LENGTH} characters")
    return name


def generate_names(
    count: int,
    rng: random.Random | None = None,
    separator: str = "-",
    prefix: str | None = None,
    exclude: list[str] = [],
) -> list[str]:
    """Return ``count`` unique names that are not in ``exclude``.

    Newly generated names are added to ``exclude`` so that later calls
    never hand out the same name twice.

    Raises ValueError if more names are requested than there are possible
    adjective/noun combinations.
    """
    max_unique = len(ADJECTIVES) * len(NOUNS)
    if count > max_unique:
        raise ValueError(f"Cannot generate {count} unique names; only {max_unique} combinations exist")

    rng = rng or random.Random()
    names: set[str] = set()
    while len(names) < count:
        name = generate_name(rng, separator, prefix)
        if name not in exclude:
            names.add(name)

    exclude.extend(names)
    return sorted(names)
