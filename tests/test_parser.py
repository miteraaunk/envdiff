"""Tests for envdiff.parser module."""

import textwrap
from pathlib import Path

import pytest

from envdiff.parser import EnvParseError, parse_env_file


@pytest.fixture()
def tmp_env(tmp_path):
    """Helper that writes content to a temp .env file and returns its path."""

    def _write(content: str) -> Path:
        env_file = tmp_path / ".env"
        env_file.write_text(textwrap.dedent(content), encoding="utf-8")
        return env_file

    return _write


def test_parse_simple_pairs(tmp_env):
    path = tmp_env("""
        APP_ENV=production
        DEBUG=false
        PORT=8080
    """)
    result = parse_env_file(path)
    assert result == {"APP_ENV": "production", "DEBUG": "false", "PORT": "8080"}


def test_parse_ignores_comments_and_blanks(tmp_env):
    path = tmp_env("""
        # This is a comment
        KEY=value

        # Another comment
        OTHER=123
    """)
    result = parse_env_file(path)
    assert result == {"KEY": "value", "OTHER": "123"}


def test_parse_double_quoted_value(tmp_env):
    path = tmp_env('SECRET="my secret value"\n')
    result = parse_env_file(path)
    assert result["SECRET"] == "my secret value"


def test_parse_single_quoted_value(tmp_env):
    path = tmp_env("TOKEN='abc123'\n")
    result = parse_env_file(path)
    assert result["TOKEN"] == "abc123"


def test_parse_empty_value(tmp_env):
    path = tmp_env("EMPTY=\n")
    result = parse_env_file(path)
    assert result["EMPTY"] == ""


def test_parse_value_with_equals_sign(tmp_env):
    path = tmp_env("URL=http://example.com?foo=bar\n")
    result = parse_env_file(path)
    assert result["URL"] == "http://example.com?foo=bar"


def test_file_not_found_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="Env file not found"):
        parse_env_file(tmp_path / "missing.env")


def test_invalid_line_raises(tmp_env):
    path = tmp_env("THIS IS INVALID\n")
    with pytest.raises(EnvParseError, match="Invalid syntax"):
        parse_env_file(path)
