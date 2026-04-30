"""Sorting utilities for DiffResult keys."""

from enum import Enum
from typing import List

from envdiff.comparator import DiffResult


class SortOrder(str, Enum):
    ALPHA = "alpha"
    STATUS = "status"
    REVERSE_ALPHA = "reverse-alpha"


# Priority for status-based sorting: missing entries first, then mismatches, then matching
_STATUS_PRIORITY = {
    "missing_in_right": 0,
    "missing_in_left": 1,
    "mismatch": 2,
    "match": 3,
}


def _key_status(key: str, result: DiffResult) -> int:
    """Return a numeric priority for a key based on its diff status."""
    if key in result.missing_in_right:
        return _STATUS_PRIORITY["missing_in_right"]
    if key in result.missing_in_left:
        return _STATUS_PRIORITY["missing_in_left"]
    if key in result.mismatches:
        return _STATUS_PRIORITY["mismatch"]
    return _STATUS_PRIORITY["match"]


def sorted_keys(result: DiffResult, order: SortOrder = SortOrder.ALPHA) -> List[str]:
    """Return all keys from a DiffResult sorted according to *order*.

    Args:
        result: The diff result whose keys should be sorted.
        order: One of the SortOrder enum values.

    Returns:
        A list of keys in the requested order.
    """
    all_keys = (
        set(result.missing_in_right)
        | set(result.missing_in_left)
        | set(result.mismatches)
        | set(result.matches)
    )

    if order == SortOrder.ALPHA:
        return sorted(all_keys)
    if order == SortOrder.REVERSE_ALPHA:
        return sorted(all_keys, reverse=True)
    if order == SortOrder.STATUS:
        return sorted(all_keys, key=lambda k: (_key_status(k, result), k))

    # Fallback – should never reach here given enum validation
    return sorted(all_keys)
