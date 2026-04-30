"""Tests for envdiff.filter."""

import pytest

from envdiff.filter import (
    FilterConfig,
    apply_filter,
    build_filter_config,
)

ALL_KEYS = ["APP_HOST", "APP_PORT", "DB_URL", "DB_PASS", "SECRET_KEY", "DEBUG"]


def test_no_filters_returns_all_sorted():
    cfg = FilterConfig()
    assert apply_filter(ALL_KEYS, cfg) == sorted(ALL_KEYS)


def test_prefix_filter():
    cfg = build_filter_config(prefix="DB_")
    assert apply_filter(ALL_KEYS, cfg) == ["DB_PASS", "DB_URL"]


def test_include_glob_pattern():
    cfg = build_filter_config(include=["APP_*"])
    assert apply_filter(ALL_KEYS, cfg) == ["APP_HOST", "APP_PORT"]


def test_exclude_glob_pattern():
    cfg = build_filter_config(exclude=["*PASS", "SECRET_*"])
    result = apply_filter(ALL_KEYS, cfg)
    assert "DB_PASS" not in result
    assert "SECRET_KEY" not in result
    assert "APP_HOST" in result


def test_include_and_exclude_combined():
    cfg = build_filter_config(include=["DB_*"], exclude=["DB_PASS"])
    assert apply_filter(ALL_KEYS, cfg) == ["DB_URL"]


def test_prefix_and_exclude_combined():
    cfg = build_filter_config(prefix="APP_", exclude=["APP_PORT"])
    assert apply_filter(ALL_KEYS, cfg) == ["APP_HOST"]


def test_include_no_match_returns_empty():
    cfg = build_filter_config(include=["NONEXISTENT_*"])
    assert apply_filter(ALL_KEYS, cfg) == []


def test_empty_key_list():
    cfg = build_filter_config(prefix="APP_")
    assert apply_filter([], cfg) == []


def test_build_filter_config_defaults():
    cfg = build_filter_config()
    assert cfg.include_patterns == []
    assert cfg.exclude_patterns == []
    assert cfg.prefix is None


def test_multiple_include_patterns():
    cfg = build_filter_config(include=["APP_*", "DEBUG"])
    result = apply_filter(ALL_KEYS, cfg)
    assert result == ["APP_HOST", "APP_PORT", "DEBUG"]
