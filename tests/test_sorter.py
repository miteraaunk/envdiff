"""Tests for envdiff.sorter."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.sorter import SortOrder, sorted_keys


@pytest.fixture()
def mixed_result() -> DiffResult:
    return DiffResult(
        missing_in_right={"ZEBRA"},
        missing_in_left={"APPLE"},
        mismatches={"MANGO": ("v1", "v2")},
        matches={"BANANA": "same"},
    )


def test_alpha_order_is_default(mixed_result: DiffResult) -> None:
    keys = sorted_keys(mixed_result)
    assert keys == sorted(keys)


def test_alpha_order_explicit(mixed_result: DiffResult) -> None:
    keys = sorted_keys(mixed_result, SortOrder.ALPHA)
    assert keys == ["APPLE", "BANANA", "MANGO", "ZEBRA"]


def test_reverse_alpha_order(mixed_result: DiffResult) -> None:
    keys = sorted_keys(mixed_result, SortOrder.REVERSE_ALPHA)
    assert keys == ["ZEBRA", "MANGO", "BANANA", "APPLE"]


def test_status_order_groups_correctly(mixed_result: DiffResult) -> None:
    keys = sorted_keys(mixed_result, SortOrder.STATUS)
    # missing_in_right (0) < missing_in_left (1) < mismatch (2) < match (3)
    assert keys.index("ZEBRA") < keys.index("APPLE")
    assert keys.index("APPLE") < keys.index("MANGO")
    assert keys.index("MANGO") < keys.index("BANANA")


def test_status_order_ties_broken_alphabetically() -> None:
    result = DiffResult(
        missing_in_right={"Z_KEY", "A_KEY"},
        missing_in_left=set(),
        mismatches={},
        matches={},
    )
    keys = sorted_keys(result, SortOrder.STATUS)
    assert keys == ["A_KEY", "Z_KEY"]


def test_empty_result_returns_empty_list() -> None:
    result = DiffResult(
        missing_in_right=set(),
        missing_in_left=set(),
        mismatches={},
        matches={},
    )
    assert sorted_keys(result) == []
    assert sorted_keys(result, SortOrder.STATUS) == []


def test_only_matches(mixed_result: DiffResult) -> None:
    result = DiffResult(
        missing_in_right=set(),
        missing_in_left=set(),
        mismatches={},
        matches={"FOO": "bar", "BAZ": "qux"},
    )
    keys = sorted_keys(result, SortOrder.ALPHA)
    assert keys == ["BAZ", "FOO"]
