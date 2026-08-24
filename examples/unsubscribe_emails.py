"""
Unsubscribe a list of emails from ST email by setting email_permission=False.

Reads emails from a CSV (the email column is auto-detected), matches each to a Solidarity Tech
user (optionally ignoring "+subaddressing", e.g. jack+123@example.com -> jack@example.com), and
sets email_permission=False on every match.

Matching loads all users once into a cached UserStore rather than making one API call per email.
Before a real (non-dry) run we refresh the user cache so the update doesn't act on a stale
snapshot; dry runs reuse the cache for fast previews. The update loop has an API delay to avoid
hitting rate limits; a more intelligent solution would back off upon hitting rate limits.

Run with dry_run=True first to preview what would change.
"""

import logging
import os
from pathlib import Path
from time import sleep

from solidaritytechtools import STClient, match_emails_to_user_ids
from solidaritytechtools.client.models import UserUpdate

logger = logging.getLogger(__name__)

# Constants - Update these for your environment
API_KEY = os.environ.get("ST_API_KEY", "...")
API_DELAY_SECONDS = 5.1
STRIP_SUBADDRESS = True

# CSV containing the emails to unsubscribe; the email column is auto-detected.
EMAILS_CSV_PATH = Path.home() / "Downloads" / "an_report_email-opt-outs_2026-06-20.csv"


def unsubscribe_emails(emails: list[str], *, dry_run: bool = False) -> None:
    logger.info(f"Matching {len(emails)} emails to ST users...")
    # Refresh users for a real run so we don't act on a stale cache; dry runs reuse it.
    matches: dict[str, int] = match_emails_to_user_ids(
        emails, api_key=API_KEY, strip_subaddress=STRIP_SUBADDRESS, refresh=not dry_run
    )

    unmatched = [email for email in emails if email not in matches]
    logger.info(f"Matched {len(matches)} of {len(emails)} emails ({len(unmatched)} unmatched).")
    for email in unmatched:
        logger.debug(f"No ST match for {email}")

    if dry_run:
        logger.info(f"[DRY RUN] Would set email_permission=False on {len(matches)} contacts.")
        for email, user_id in matches.items():
            logger.debug(f"[DRY RUN] Would unsubscribe {email} > {user_id}")
        return

    # For a no-frills bulk update without rate-limiting, the library also provides
    # solidaritytechtools.set_email_permission(client, matches.values(), permission=False).
    updated = 0
    with STClient(api_key=API_KEY) as client:
        for email, user_id in matches.items():
            try:
                sleep(API_DELAY_SECONDS)
                client.update_user(user_id, UserUpdate(email_permission=False))
                updated += 1
                logger.info(f"Unsubscribed {email} > {user_id}")
            except Exception as e:
                logger.error(f"Failed to unsubscribe {email} > {user_id}: {e}")
    logger.info(f"Unsubscribed {updated} of {len(matches)} matched contacts.")


if __name__ == "__main__":
    from solidaritytechtools.utils.csv_tools import get_emails_from_csv

    # Configure logging to show info messages by default
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    emails = get_emails_from_csv(EMAILS_CSV_PATH)

    # Set to dry_run=False when you are ready to apply the changes
    unsubscribe_emails(emails, dry_run=True)
