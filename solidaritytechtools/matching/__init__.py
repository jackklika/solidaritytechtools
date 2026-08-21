"""Canonical contact matching across data sources.

Reduce both sides to normalized ContactKeys, index one side, then look the other side up. Keys
are tried strongest first (email/phone, then name+zip, then name alone) so a weak key can never
override a strong one.

```python
from solidaritytechtools.matching import ContactIndex, contact_keys, keys_from_user

index = ContactIndex(st_users, keys_from_user)
match = index.match(contact_keys(emails="a@example.com", phones="(414) 555-1234"))
if match:
    print(match.record.id, match.strategy, match.confidence)
```

For a whole dataset at once, use match_contacts(). For csv rows or dataframe records, use
keys_from_mapping as the extractor. For a new source, write a few lines returning contact_keys().
"""

from solidaritytechtools.matching.adapters import (
    KeyExtractor,
    keys_from_mapping,
    keys_from_person,
    keys_from_user,
    prefer_member_then_newest,
    prefer_newest,
)
from solidaritytechtools.matching.index import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_STRATEGIES,
    EMAIL_STRATEGY,
    NAME_STRATEGY,
    NAME_ZIP_STRATEGY,
    PHONE_STRATEGY,
    ContactIndex,
    ContactMatch,
    MatchStrategy,
    first_record,
    match_contacts,
)
from solidaritytechtools.matching.keys import ContactKeys, contact_keys, split_name

__all__ = [
    "ContactKeys",
    "contact_keys",
    "split_name",
    "ContactIndex",
    "ContactMatch",
    "MatchStrategy",
    "match_contacts",
    "first_record",
    "DEFAULT_STRATEGIES",
    "DEFAULT_CONFIDENCE_THRESHOLD",
    "EMAIL_STRATEGY",
    "PHONE_STRATEGY",
    "NAME_ZIP_STRATEGY",
    "NAME_STRATEGY",
    "KeyExtractor",
    "keys_from_user",
    "keys_from_person",
    "keys_from_mapping",
    "prefer_newest",
    "prefer_member_then_newest",
]
