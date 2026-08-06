"""User-related operations built on top of the raw STClient.

These compose client calls into reusable building blocks (e.g. paging through
every user) and provide a cached, in-memory UserStore for batch operations such
as matching a list of emails to ST ids.
"""

from __future__ import annotations

import json
import logging
import tempfile
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Final

import solidaritytechtools.client.models as client_models
from solidaritytechtools.client.base_client import STClient
from solidaritytechtools.utils.emails import get_email_address_without_subaddress, normalize_email

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE: Final[int] = 100
DEFAULT_CACHE_PATH: Final[Path] = (
    Path(tempfile.gettempdir()) / "solidaritytechtools_users_cache.json"
)


def get_all_users(
    client: STClient, *, page_size: int = DEFAULT_PAGE_SIZE
) -> list[client_models.User]:
    """
    Fetch every user from Solidarity Tech, paging until exhausted.

    There is no more efficient filtering endpoint for many operations we need to do, so we load
    all users into memory rather than calling client.get_user() in a loop (which would hit rate
    limits). If ST ever provides a GraphQL or bulk query endpoint, we can rely on this less.

    params:
        client: an open STClient to fetch with
        page_size: number of users to request per page

    returns: list of all User objects
    """
    all_users: list[client_models.User] = []
    offset = 0
    while True:
        logger.info(f"Fetching users from api limit={page_size} offset={offset}")
        response = client.get_users(limit=page_size, offset=offset)
        if not response.data:
            break

        all_users.extend(response.data)

        # Stop once we've collected the total the API reports.
        if response.meta and response.meta.total_count is not None:
            if len(all_users) >= response.meta.total_count:
                break

        # A short page means we've reached the end.
        if len(response.data) < page_size:
            break

        offset += page_size

    return all_users


class UserStore:
    """
    In-memory store of ST users with email indices for fast batch matching.

    Loading every user once and matching locally avoids per-email API calls (and the
    rate limits that come with them). Use UserStore.from_api(api_key) to load with a
    simple on-disk cache so repeated REPL sessions don't re-fetch everything.
    """

    def __init__(self, users: list[client_models.User]):
        self.users = users
        # Exact normalized email -> users, and subaddress-stripped email -> users.
        self._by_email: dict[str, list[client_models.User]] = {}
        self._by_stripped: dict[str, list[client_models.User]] = {}
        self._build_indices()

    def _build_indices(self) -> None:
        self._by_email.clear()
        self._by_stripped.clear()
        for user in self.users:
            email = normalize_email(user.email)
            if not email:
                continue
            self._by_email.setdefault(email, []).append(user)
            stripped = get_email_address_without_subaddress(email)
            if stripped:
                self._by_stripped.setdefault(stripped, []).append(user)

    @classmethod
    def from_client(cls, client: STClient, *, page_size: int = DEFAULT_PAGE_SIZE) -> UserStore:
        """Build a store by fetching all users with an open client (no caching)."""
        return cls(get_all_users(client, page_size=page_size))

    @classmethod
    def from_api(
        cls,
        api_key: str,
        *,
        cache_path: Path | str | None = DEFAULT_CACHE_PATH,
        refresh: bool = False,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> UserStore:
        """
        Build a store from the API, using an on-disk JSON cache when available.

        params:
            api_key: api key to auth with ST
            cache_path: where to read/write the cached users; None disables caching
            refresh: if True, ignore any existing cache and re-fetch from the API
            page_size: number of users to request per page when fetching
        """
        path = Path(cache_path) if cache_path else None
        if path and not refresh and path.exists():
            logger.info(f"Loading users from cache {path}")
            return cls.load(path)

        with STClient(api_key=api_key) as client:
            store = cls.from_client(client, page_size=page_size)
        if path:
            store.save(path)
        return store

    def save(self, path: Path | str) -> None:
        """Persist the users to a JSON cache file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [user.model_dump(mode="json") for user in self.users]
        path.write_text(json.dumps(data))
        logger.info(f"Saved {len(self.users)} users to cache {path}")

    @classmethod
    def load(cls, path: Path | str) -> UserStore:
        """Load users from a JSON cache file written by save()."""
        data = json.loads(Path(path).read_text())
        users = [client_models.User.model_validate(item) for item in data]
        return cls(users)

    def match_email(
        self, email: str, *, strip_subaddress: bool = True
    ) -> client_models.User | None:
        """
        Find the ST user matching a single email, or None.

        Tries an exact (case-insensitive) match first. If strip_subaddress is True and there is
        no exact match, falls back to comparing subaddress-stripped addresses, so subaddressing
        on either side (input or ST account) still matches. When several users match, the newest
        by created_at is returned.
        """
        normalized = normalize_email(email)
        if not normalized:
            return None

        candidates = self._by_email.get(normalized)
        if not candidates and strip_subaddress:
            stripped = get_email_address_without_subaddress(normalized)
            if stripped:
                candidates = self._by_stripped.get(stripped)

        if not candidates:
            return None
        if len(candidates) > 1:
            logger.info(f"More than one ST match for {normalized}, selecting newest")
            candidates = sorted(
                candidates, key=lambda u: u.created_at or datetime.min, reverse=True
            )
        return candidates[0]

    def match_emails(
        self, emails: Iterable[str], *, strip_subaddress: bool = True
    ) -> dict[str, int]:
        """
        Match a list of emails to ST ids.

        returns: mapping of the original input email -> ST user id, only for emails that matched.
        """
        matched: dict[str, int] = {}
        for email in emails:
            user = self.match_email(email, strip_subaddress=strip_subaddress)
            if user is None:
                logger.debug(f"No ST match for {email}")
                continue
            matched[email] = user.id
        return matched


def set_email_permission(
    client: STClient, user_ids: Iterable[int], *, permission: bool
) -> dict[int, bool]:
    """
    Set email_permission for each user id.

    params:
        client: an open STClient to update with
        user_ids: ST user ids to update
        permission: the email_permission value to set

    returns: mapping of user id -> True if the update succeeded, False otherwise
    """
    results: dict[int, bool] = {}
    for user_id in user_ids:
        try:
            client.update_user(user_id, client_models.UserUpdate(email_permission=permission))
            results[user_id] = True
        except Exception:
            logger.exception(f"Failed to update email_permission for user {user_id}")
            results[user_id] = False
    return results
