"""Tests for envdiff.reporter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.comparator import DiffResult
from envdiff.reporter import ReportError, report_exit_code, write_report


@pytest.fixture()
def no_diffs() -> DiffResult:
    return DiffResult(missing_in_right=[], missing_in_left=[], mismatches={})


@pytest.fixture()
def some_diffs() -> DiffResult:
    return DiffResult(
        missing_in_right=["SECRET"],
        missing_in_left=["NEW_KEY"],
        mismatches={"PORT": ("8080", "9090")},
    )


# ---------------------------------------------------------------------------
# exit code
# ---------------------------------------------------------------------------

def test_exit_code_no_diffs(no_diffs):
    assert report_exit_code(no_diffs) == 0


def test_exit_code_with_diffs(some_diffs):
    assert report_exit_code(some_diffs) == 1


# ---------------------------------------------------------------------------
# write to stdout
# ---------------------------------------------------------------------------

def test_write_report_text_stdout(capsys, some_diffs):
    write_report(some_diffs, fmt="text", color=False)
    captured = capsys.readouterr()
    assert "SECRET" in captured.out
    assert "PORT" in captured.out


def test_write_report_json_stdout(capsys, some_diffs):
    write_report(some_diffs, fmt="json", color=False)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "missing_in_right" in data
    assert "SECRET" in data["missing_in_right"]


def test_write_report_markdown_stdout(capsys, some_diffs):
    write_report(some_diffs, fmt="markdown", color=False)
    captured = capsys.readouterr()
    assert "#" in captured.out  # markdown heading


# ---------------------------------------------------------------------------
# write to file
# ---------------------------------------------------------------------------

def test_write_report_to_file(tmp_path, some_diffs):
    out_file = tmp_path / "report.md"
    write_report(some_diffs, fmt="markdown", output_path=str(out_file))
    assert out_file.exists()
    content = out_file.read_text()
    assert "PORT" in content


def test_write_report_creates_parent_dirs(tmp_path, some_diffs):
    out_file = tmp_path / "nested" / "deep" / "report.txt"
    write_report(some_diffs, fmt="text", output_path=str(out_file), color=False)
    assert out_file.exists()


def test_write_report_raises_on_bad_path(some_diffs):
    with pytest.raises(ReportError):
        # Root-level path that cannot be created on most systems
        write_report(some_diffs, output_path="/proc/envdiff_test_no_permission/x.txt")
