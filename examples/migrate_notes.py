"""Migrate notes from ST json export to ST instance"""

import logging

from solidaritytechtools import STClient
from solidaritytechtools.client.models import UserNoteCreate
from solidaritytechtools.json_export.export import STJsonExport
from solidaritytechtools.match_persons.match_persons import ClientUserMatch, find_best_match

# Setup logger
logger = logging.getLogger(__name__)

API_KEY = "..."
EXPORT_FILE_PATH = "..."


def migrate_notes(*, dry_run: bool = False):
    logger.info("Fetching users and matching data...")
    best_matches: dict[int, ClientUserMatch | None] = find_best_match(EXPORT_FILE_PATH, API_KEY)

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

            logger.info(
                f"Migrating {len(person.notes)} notes for "
                f"json:{person.id} > client:{match.user_id}..."
            )
            logger.debug(f"Source notes: {person.notes}")

            for note_item in person.notes:
                try:
                    # We use the matched live user_id
                    # and preserve the original creation date from the export
                    note_create = UserNoteCreate(
                        user_id=match.user_id,
                        content=note_item.content,
                        created_at=int(note_item.created_at.timestamp()),
                    )
                    if dry_run:
                        logger.info(f"[DRY RUN] Would have created note: {note_create}")
                    else:
                        client.create_user_note(note_create)
                except Exception as e:
                    logger.error(f"  Failed to copy note for user {match.user_id}: {e}")


if __name__ == "__main__":
    # Configure logging to show info messages by default
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    migrate_notes(dry_run=True)
