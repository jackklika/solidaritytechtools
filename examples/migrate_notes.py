"""
Migrate notes from ST json export to ST instance with deduplication and rate limiting

This code has successfully been used by a DSA chapter to migrate notes between ST accounts.

We have an API delay to prevent hitting rate limits. A more intelligent solution would do a
backoff upon hitting rate limits.
"""

import logging
from time import sleep

from solidaritytechtools import STClient
from solidaritytechtools.client.models import UserNoteCreate
from solidaritytechtools.export_matching import ClientUserMatch, best_match_per_person
from solidaritytechtools.json_export.export import STJsonExport

logger = logging.getLogger(__name__)

# Constants - Update these for your environment
API_KEY = "..."
EXPORT_FILE_PATH = "..."
API_DELAY_SECONDS = 5.1


def migrate_notes(*, dry_run: bool = False):
    logger.info("Fetching users and matching data...")
    best_matches: dict[int, ClientUserMatch | None] = best_match_per_person(
        EXPORT_FILE_PATH, API_KEY
    )

    # Load the full export data (to get the actual content of the notes)
    export = STJsonExport.from_path(EXPORT_FILE_PATH)

    # Connect to the API and migrate notes
    with STClient(api_key=API_KEY) as client:
        for person in export.people:
            match: ClientUserMatch | None = best_matches.get(person.id)

            # Check if we found a confident match for this person
            if not match:
                logger.warning(f"Skipping json:{person.id}: No match found in ST.")
                continue

            if not person.notes:
                continue

            # --- Deduplication Logic ---
            # Fetch existing activities for this user to avoid duplicates
            # We fetch a large batch (100) to ensure we see historical notes
            logger.info(f"Checking for existing notes for user {match.user_id}...")
            sleep(API_DELAY_SECONDS)

            try:
                existing_activities = client.get_activities(user_id=match.user_id, limit=100).data
                # We collect timestamps of existing UserNote actions
                # Actionable type is checked based on ST API conventions
                existing_timestamps = {
                    int(a.created_at.timestamp())
                    for a in existing_activities
                    if a.actionable_type == "UserNote"
                }
            except Exception as e:
                logger.error(f"  Failed to fetch activities for user {match.user_id}: {e}")
                existing_timestamps = set()

            logger.info(f"Migrating notes for json:{person.id} > client:{match.user_id}...")
            logger.debug(f"Source notes: {person.notes}")

            for note_item in person.notes:
                ts = int(note_item.created_at.timestamp())

                # Deduplication check using exact timestamp. Could be improved to use content.
                if ts in existing_timestamps:
                    logger.info(
                        f"  Skipping note from {note_item.created_at}: Already exists in ST."
                    )
                    continue

                try:
                    note_create = UserNoteCreate(
                        user_id=match.user_id,
                        content=note_item.content,
                        created_at=ts,
                    )

                    if dry_run:
                        logger.info(f"[DRY RUN] Would have created note: {note_create}")
                    else:
                        sleep(API_DELAY_SECONDS)
                        client.create_user_note(note_create)
                        logger.info(f"  Successfully migrated note from {note_item.created_at}")

                except Exception as e:
                    logger.error(f"  Failed to copy note for user {match.user_id}: {e}")


if __name__ == "__main__":
    # Configure logging to show info messages by default
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Set to dry_run=False when you are ready to perform the actual migration
    migrate_notes(dry_run=True)
