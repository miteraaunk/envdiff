"""Tests for envdiff.comparator module."""

import pytest
from envdiff.comparator import compare_envs, DiffResult


LEFT = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
RIGHT = {"HOST": "prod.example.com", "PORT": "5432", "SECRET_KEY": "abc123"}


def test_missing_in_right():
    result = compare_envs(LEFT, RIGHT)
    assert "DEBUG" in result.missing_in_right
    assert "SECRET_KEY" not in result.missing_in_right


def test_missing_in_left():
    result = compare_envs(LEFT, RIGHT)
    assert "SECRET_KEY" in result.missing_in_left
    assert "DEBUG" not in result.missing_in_left


def test_value_mismatch_detected():
    result = compare_envs(LEFT, RIGHT)
    assert "HOST" in result.value_mismatches
    assert result.value_mismatches["HOST"] == ("localhost", "prod.example.com")


def test_no_mismatch_for_equal_value():
    result = compare_envs(LEFT, RIGHT)
    assert "PORT" not in result.value_mismatches


def test_has_differences_true():
    result = compare_envs(LEFT, RIGHT)
    assert result.has_differences is True


def test_has_differences_false():
    env = {"KEY": "value"}
    result = compare_envs(env, env.copy())
    assert result.has_differences is False


def test_labels_in_summary():
    result = compare_envs(LEFT, RIGHT, left_label="dev", right_label="prod")
    summary = result.summary()
    assert "[dev]" in summary
    assert "[prod]" in summary


def test_summary_no_differences():
    env = {"A": "1", "B": "2"}
    result = compare_envs(env, env.copy())
    assert result.summary() == "No differences found."


def test_none_values_mismatch():
    left = {"KEY": None}
    right = {"KEY": "value"}
    result = compare_envs(left, right)
    assert "KEY" in result.value_mismatches
    assert result.value_mismatches["KEY"] == (None, "value")


def test_empty_envs():
    result = compare_envs({}, {})
    assert not result.has_differences
