"""Match contacts between two datasets by indexing one side and cascading lookups.

The index holds records of any type -- ST users, csv rows, dataclasses -- as long as you can
say how to pull identifiers out of them. Lookups try the strongest key first and stop there,
so an email match never gets downgraded by a weaker name match.

Loading one side into memory and matching locally is deliberate: there is no bulk lookup
endpoint on the ST api, so per-person calls would hit rate limits.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable, Sequence
from dataclasses import dataclass
from typing import Final, Generic, TypeVar

from solidaritytechtools.matching.keys import ContactKeys

logger = logging.getLogger(__name__)

T = TypeVar("T")
S = TypeVar("S")

EMAIL_CONFIDENCE: Final[float] = 1.0
PHONE_CONFIDENCE: Final[float] = 1.0
NAME_ZIP_CONFIDENCE: Final[float] = 0.9
NAME_ONLY_CONFIDENCE: Final[float] = 0.7

DEFAULT_CONFIDENCE_THRESHOLD: Final[float] = 0.8


@dataclass(frozen=True)
class MatchStrategy:
    """
    One rung of the match cascade.

    params:
        name: label reported on matches made this way, e.g. "email"
        confidence: how much to trust a match on this key
        keys: the lookup keys a contact contributes for this strategy
        require_unique: only match when exactly one record holds the key. Use for weak keys --
            a name shared by several records identifies nobody.
    """

    name: str
    confidence: float
    keys: Callable[[ContactKeys], tuple[Hashable, ...]]
    require_unique: bool = False


def _email_keys(keys: ContactKeys) -> tuple[Hashable, ...]:
    return tuple(sorted(keys.emails))


def _phone_keys(keys: ContactKeys) -> tuple[Hashable, ...]:
    return tuple(sorted(keys.phones))


def _name_zip_keys(keys: ContactKeys) -> tuple[Hashable, ...]:
    if keys.name and keys.zip5:
        return ((*keys.name, keys.zip5),)
    return ()


def _name_keys(keys: ContactKeys) -> tuple[Hashable, ...]:
    return (keys.name,) if keys.name else ()


EMAIL_STRATEGY: Final[MatchStrategy] = MatchStrategy("email", EMAIL_CONFIDENCE, _email_keys)
PHONE_STRATEGY: Final[MatchStrategy] = MatchStrategy("phone", PHONE_CONFIDENCE, _phone_keys)
NAME_ZIP_STRATEGY: Final[MatchStrategy] = MatchStrategy(
    "name_zip", NAME_ZIP_CONFIDENCE, _name_zip_keys
)
NAME_STRATEGY: Final[MatchStrategy] = MatchStrategy(
    "name", NAME_ONLY_CONFIDENCE, _name_keys, require_unique=True
)

DEFAULT_STRATEGIES: Final[tuple[MatchStrategy, ...]] = (
    EMAIL_STRATEGY,
    PHONE_STRATEGY,
    NAME_ZIP_STRATEGY,
    NAME_STRATEGY,
)


@dataclass
class ContactMatch(Generic[T]):
    """A matched record, plus which strategy found it and how much to trust it."""

    record: T
    strategy: str
    confidence: float


def first_record(records: Sequence[T]) -> T:
    """Default tie-breaker: keep the earliest indexed record."""
    return records[0]


class ContactIndex(Generic[T]):
    """
    Indexes one side of a match so the other side can be looked up cheaply.

    Example:
    ```python
    index = ContactIndex(st_users, keys_from_user)
    match = index.match(contact_keys(emails="a@example.com", phones="(414) 555-1234"))
    if match:
        print(match.record.id, match.strategy, match.confidence)
    ```
    """

    def __init__(
        self,
        records: Iterable[T],
        key_extractor: Callable[[T], ContactKeys],
        *,
        strategies: Sequence[MatchStrategy] = DEFAULT_STRATEGIES,
        tie_breaker: Callable[[Sequence[T]], T] = first_record,
    ):
        self.records: list[T] = list(records)
        self.strategies = tuple(strategies)
        self._tie_breaker = tie_breaker
        # Positions rather than records, so unhashable record types still dedupe cleanly.
        self._indices: dict[str, dict[Hashable, list[int]]] = {
            strategy.name: defaultdict(list) for strategy in self.strategies
        }
        self._build(key_extractor)

    def _build(self, key_extractor: Callable[[T], ContactKeys]) -> None:
        skipped = 0
        for position, record in enumerate(self.records):
            keys = key_extractor(record)
            if keys.is_empty:
                skipped += 1
                continue
            for strategy in self.strategies:
                index = self._indices[strategy.name]
                for key in strategy.keys(keys):
                    index[key].append(position)
        logger.info(
            f"Indexed {len(self.records) - skipped}/{len(self.records)} records "
            f"({skipped} had no usable identifiers)"
        )

    def candidates(self, keys: ContactKeys) -> list[ContactMatch[T]]:
        """
        Every record matching on any strategy, best confidence first, one entry per record.

        Use this when you want to see competing matches; use match() for just the best one.
        """
        best: dict[int, tuple[float, str]] = {}
        for strategy in self.strategies:
            index = self._indices[strategy.name]
            for key in strategy.keys(keys):
                positions = index.get(key)
                if not positions:
                    continue
                if strategy.require_unique and len(set(positions)) > 1:
                    continue
                for position in positions:
                    current = best.get(position)
                    if current is None or strategy.confidence > current[0]:
                        best[position] = (strategy.confidence, strategy.name)

        matches = [
            ContactMatch(self.records[position], name, confidence)
            for position, (confidence, name) in best.items()
        ]
        matches.sort(key=lambda match: match.confidence, reverse=True)
        return matches

    def match(self, keys: ContactKeys, *, threshold: float = 0.0) -> ContactMatch[T] | None:
        """
        Resolve a contact to a single record, strongest key first.

        Strategies are tried in order and the first one that hits wins, so a weaker key can
        never override a stronger one. When several records share the winning key, the
        tie_breaker picks between them.

        params:
            keys: the normalized identifiers to look up
            threshold: ignore strategies weaker than this confidence

        returns: the best match, or None
        """
        if keys.is_empty:
            return None
        for strategy in self.strategies:
            if strategy.confidence < threshold:
                continue
            index = self._indices[strategy.name]
            for key in strategy.keys(keys):
                positions = index.get(key)
                if not positions:
                    continue
                unique = sorted(set(positions))
                if strategy.require_unique and len(unique) > 1:
                    continue
                chosen = (
                    self.records[unique[0]]
                    if len(unique) == 1
                    else self._tie_breaker([self.records[p] for p in unique])
                )
                return ContactMatch(chosen, strategy.name, strategy.confidence)
        return None


def match_contacts(
    left: Iterable[S],
    right: Iterable[T],
    left_keys: Callable[[S], ContactKeys],
    right_keys: Callable[[T], ContactKeys],
    *,
    strategies: Sequence[MatchStrategy] = DEFAULT_STRATEGIES,
    tie_breaker: Callable[[Sequence[T]], T] = first_record,
    threshold: float = 0.0,
) -> dict[int, ContactMatch[T]]:
    """
    Match every record on the left against the right side.

    params:
        left: records to look up
        right: records to index and match against
        left_keys / right_keys: how to pull identifiers out of each side
        strategies: the cascade to use, strongest first
        tie_breaker: picks between right-side records sharing a key
        threshold: ignore strategies weaker than this confidence

    returns: mapping of the left record's position -> its match, for those that matched
    """
    index = ContactIndex(right, right_keys, strategies=strategies, tie_breaker=tie_breaker)
    matches: dict[int, ContactMatch[T]] = {}
    for position, record in enumerate(left):
        if match := index.match(left_keys(record), threshold=threshold):
            matches[position] = match

    counts: dict[str, int] = defaultdict(int)
    for match in matches.values():
        counts[match.strategy] += 1
    logger.info(f"Matched {len(matches)} contacts ({dict(sorted(counts.items()))})")
    return matches
