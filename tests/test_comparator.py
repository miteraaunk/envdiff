"""Tests for envdiff.comparator."""

import pytest

from envdiff.comparator import DiffResult, compare_envs, has_differences, summary
from envdiff.filter import build_filter_config

LEFT = {"APP_HOST": "localhost", "APP_PORT": "8080", "DB_URL": "postgres://left"}
RIGHT = {"APP_HOST": "localhost", "APP_PORT": "9090", "SECRET": "abc"}


def test_missing_in_right():
    result = compare_envs(LEFT, RIGHT)
    assert "DB_URL" in result.missing_in_right


def test_missing_in_left():
    result = compare_envs(LEFT, RIGHT)
    assert "SECRET" in result.missing_in_left


def test_value_mismatch_detected():
    result = compare_envs(LEFT, RIGHT)
    assert "APP_PORT" in result.mismatches
    assert result.mismatches["APP_PORT"] == ("8080", "9090")


def test_no_mismatch_for_equal_value():
    result = compare_envs(LEFT, RIGHT)
    assert "APP_HOST" not in result.mismatches
    assert "APP_HOST" in result.matching


def test_has_differences_true():
    result = compare_envs(LEFT, RIGHT)
    assert has_differences(result) is True


def test_has_differences_false():
    same = {"K": "V"}
    result = compare_envs(same, same)
    assert has_differences(result) is False


def test_summary_no_differences():
    same = {"K": "V"}
    result = compare_envs(same, same)
    assert summary(result) == "No differences found."


def test_summary_with_differences():
    result = compare_envs(LEFT, RIGHT)
    s = summary(result)
    assert "missing in right" in s
    assert "missing in left" in s
    assert "mismatch" in s


def test_filter_limits_comparison():
    cfg = build_filter_config(prefix="APP_")
    result = compare_envs(LEFT, RIGHT, filter_config=cfg)
    # DB_URL and SECRET are outside the prefix — should be ignored
    assert "DB_URL" not in result.missing_in_right
    assert "SECRET" not in result.missing_in_left
    assert "APP_PORT" in result.mismatches


def test_filter_exclude_key():
    cfg = build_filter_config(exclude=["APP_PORT"])
    result = compare_envs(LEFT, RIGHT, filter_config=cfg)
    assert "APP_PORT" not in result.mismatches


def test_empty_envs():
    result = compare_envs({}, {})
    assert not has_differences(result)
