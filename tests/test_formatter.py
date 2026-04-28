"""Tests for envdiff.formatter."""

import json

import pytest

from envdiff.comparator import DiffResult
from envdiff.formatter import format_json, format_markdown, format_result, format_text


@pytest.fixture()
def no_diffs() -> DiffResult:
    return DiffResult(diffs=[])


@pytest.fixture()
def mixed_diffs() -> DiffResult:
    return DiffResult(
        diffs=[
            ("DB_HOST", "mismatch", "localhost", "db.prod"),
            ("SECRET", "missing_right", "abc123", None),
            ("API_KEY", "missing_left", None, "xyz789"),
        ]
    )


# --- format_text ---

def test_text_no_diffs(no_diffs: DiffResult) -> None:
    out = format_text(no_diffs)
    assert "No differences" in out


def test_text_shows_all_keys(mixed_diffs: DiffResult) -> None:
    out = format_text(mixed_diffs, left_label="dev", right_label="prod")
    assert "DB_HOST" in out
    assert "SECRET" in out
    assert "API_KEY" in out


def test_text_mismatch_shows_both_values(mixed_diffs: DiffResult) -> None:
    out = format_text(mixed_diffs, left_label="dev", right_label="prod")
    assert "localhost" in out
    assert "db.prod" in out


def test_text_missing_right_label(mixed_diffs: DiffResult) -> None:
    out = format_text(mixed_diffs, left_label="dev", right_label="prod")
    assert "only in dev" in out


def test_text_missing_left_label(mixed_diffs: DiffResult) -> None:
    out = format_text(mixed_diffs, left_label="dev", right_label="prod")
    assert "only in prod" in out


def test_text_diff_count(mixed_diffs: DiffResult) -> None:
    out = format_text(mixed_diffs)
    assert "3 difference(s)" in out


# --- format_json ---

def test_json_is_valid_json(mixed_diffs: DiffResult) -> None:
    out = format_json(mixed_diffs, left_label="dev", right_label="prod")
    data = json.loads(out)
    assert data["count"] == 3


def test_json_no_diffs_empty_list(no_diffs: DiffResult) -> None:
    data = json.loads(format_json(no_diffs))
    assert data["differences"] == []
    assert data["count"] == 0


def test_json_entry_has_expected_keys(mixed_diffs: DiffResult) -> None:
    data = json.loads(format_json(mixed_diffs, left_label="dev", right_label="prod"))
    entry = data["differences"][0]
    assert {"key", "status", "dev", "prod"} <= entry.keys()


# --- format_markdown ---

def test_markdown_no_diffs(no_diffs: DiffResult) -> None:
    out = format_markdown(no_diffs)
    assert "No differences" in out


def test_markdown_contains_table_header(mixed_diffs: DiffResult) -> None:
    out = format_markdown(mixed_diffs)
    assert "| Key |" in out


def test_markdown_missing_shown_as_missing(mixed_diffs: DiffResult) -> None:
    out = format_markdown(mixed_diffs)
    assert "_missing_" in out


# --- format_result dispatch ---

def test_format_result_defaults_to_text(mixed_diffs: DiffResult) -> None:
    out = format_result(mixed_diffs)
    assert "difference(s)" in out


def test_format_result_json(mixed_diffs: DiffResult) -> None:
    out = format_result(mixed_diffs, fmt="json")
    json.loads(out)  # must not raise


def test_format_result_markdown(mixed_diffs: DiffResult) -> None:
    out = format_result(mixed_diffs, fmt="markdown")
    assert "|" in out
