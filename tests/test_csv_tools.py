from __future__ import annotations

from pathlib import Path

import pytest

from solidaritytechtools.utils.csv_tools import AmbiguousEmailColumnError, get_emails_from_csv


def _write_csv(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "data.csv"
    path.write_text(content)
    return path


def test_single_email_column_by_header(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, "name,email\nAlice,alice@example.com\nBob,bob@example.com\n")
    assert get_emails_from_csv(path) == ["alice@example.com", "bob@example.com"]


def test_header_detection_normalizes_name(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, "Name,E-Mail Address\nA,a@x.com\n")
    assert get_emails_from_csv(path) == ["a@x.com"]


def test_skips_empty_cells(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, "email\na@x.com\n\nb@x.com\n")
    assert get_emails_from_csv(path) == ["a@x.com", "b@x.com"]


def test_ambiguous_email_columns_raises(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, "personal_email,work_email\na@x.com,a@work.com\n")
    with pytest.raises(AmbiguousEmailColumnError):
        get_emails_from_csv(path)


def test_disambiguates_email_headers_by_content(tmp_path: Path) -> None:
    # Both headers contain "email" but only one holds actual addresses.
    path = _write_csv(tmp_path, "email,email_opt_in\na@x.com,true\nb@x.com,false\n")
    assert get_emails_from_csv(path) == ["a@x.com", "b@x.com"]


def test_content_fallback_when_no_email_header(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, "name,contact\nAlice,alice@example.com\nBob,bob@example.com\n")
    assert get_emails_from_csv(path) == ["alice@example.com", "bob@example.com"]


def test_no_email_column_raises_value_error(tmp_path: Path) -> None:
    path = _write_csv(tmp_path, "name,age\nAlice,30\nBob,40\n")
    with pytest.raises(ValueError):
        get_emails_from_csv(path)
