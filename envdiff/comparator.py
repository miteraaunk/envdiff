"""Core comparison logic for envdiff."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from envdiff.filter import FilterConfig, apply_filter


@dataclass
class DiffResult:
    """Holds the diff between two .env mappings."""

    missing_in_right: list[str] = field(default_factory=list)
    missing_in_left: list[str] = field(default_factory=list)
    mismatches: dict[str, tuple[str, str]] = field(default_factory=dict)
    # keys present in both with equal values
    matching: list[str] = field(default_factory=list)


def has_differences(result: DiffResult) -> bool:
    """Return True if *result* contains any differences."""
    return bool(
        result.missing_in_right or result.missing_in_left or result.mismatches
    )


def summary(result: DiffResult) -> str:
    """Return a one-line human-readable summary."""
    parts = []
    if result.missing_in_right:
        parts.append(f"{len(result.missing_in_right)} missing in right")
    if result.missing_in_left:
        parts.append(f"{len(result.missing_in_left)} missing in left")
    if result.mismatches:
        parts.append(f"{len(result.mismatches)} mismatch(es)")
    if not parts:
        return "No differences found."
    return "Differences: " + ", ".join(parts) + "."


def compare_envs(
    left: Mapping[str, str],
    right: Mapping[str, str],
    filter_config: FilterConfig | None = None,
) -> DiffResult:
    """Compare *left* and *right* env mappings.

    If *filter_config* is provided, only the filtered subset of keys is
    considered during comparison.
    """
    result = DiffResult()

    all_keys: set[str] = set(left) | set(right)

    if filter_config is not None:
        all_keys = set(apply_filter(all_keys, filter_config))

    for key in sorted(all_keys):
        in_left = key in left
        in_right = key in right
        if in_left and not in_right:
            result.missing_in_right.append(key)
        elif in_right and not in_left:
            result.missing_in_left.append(key)
        elif left[key] != right[key]:
            result.mismatches[key] = (left[key], right[key])
        else:
            result.matching.append(key)

    return result
