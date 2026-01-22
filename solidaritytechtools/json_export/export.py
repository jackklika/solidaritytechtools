from __future__ import annotations

import json
from pathlib import Path

from pydantic import RootModel, ValidationError

from solidaritytechtools.json_export.models import Person


class STJsonExportError(Exception):
    """Base exception for ST JSON export errors."""


class STJsonExportValidationError(STJsonExportError):
    """Raised when the ST JSON export file does not have the expected format."""


class STJsonExportModel(RootModel[list[Person]]):
    """Represents a root-level list of Person objects from an ST export."""

    root: list[Person]


class STJsonExport:
    def __init__(self, people: list[Person]):
        self.people = people

    @classmethod
    def from_path(cls, path: Path | str) -> STJsonExport:
        """
        Loads and validates an ST JSON export from a file path.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Export file not found: {path}")

        try:
            model = STJsonExportModel.model_validate_json(path.read_text())
            return cls(people=model.root)
        except ValidationError as e:
            raise STJsonExportValidationError(
                f"ST json export file does not have expected format: {e}"
            ) from e
        except json.JSONDecodeError as e:
            raise STJsonExportValidationError(f"Invalid JSON in export file: {e}") from e


def get_persons_from_json_export(path: Path | str) -> list[Person]:
    """
    Helper function to get a list of Person objects from a ST JSON export file.

    Example:
    ```python
    from solidaritytechtools.json_export import get_persons_from_json_export

    persons = get_persons_from_json_export("/path/to/export.json")
    for person in persons:
        print(person.email)
    ```
    """
    return STJsonExport.from_path(path).people
