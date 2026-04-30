"""Key filtering utilities for envdiff comparisons."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class FilterConfig:
    """Configuration for key filtering."""

    include_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)
    prefix: str | None = None


def _matches_any(key: str, patterns: Iterable[str]) -> bool:
    """Return True if *key* matches at least one glob pattern."""
    return any(fnmatch.fnmatch(key, p) for p in patterns)


def apply_filter(keys: Iterable[str], config: FilterConfig) -> list[str]:
    """Return a filtered, sorted list of keys according to *config*.

    Filtering order:
    1. Keep only keys that start with *prefix* (if set).
    2. If *include_patterns* are given, keep only matching keys.
    3. Remove keys that match any *exclude_patterns*.
    """
    result: list[str] = []
    for key in keys:
        if config.prefix and not key.startswith(config.prefix):
            continue
        if config.include_patterns and not _matches_any(key, config.include_patterns):
            continue
        if config.exclude_patterns and _matches_any(key, config.exclude_patterns):
            continue
        result.append(key)
    return sorted(result)


def build_filter_config(
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    prefix: str | None = None,
) -> FilterConfig:
    """Convenience constructor for :class:`FilterConfig`."""
    return FilterConfig(
        include_patterns=include or [],
        exclude_patterns=exclude or [],
        prefix=prefix,
    )
