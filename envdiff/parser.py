"""Parser for .env files.

Handles reading and parsing of .env file format, including:
- KEY=VALUE pairs
- Comments (lines starting with #)
- Empty lines
- Quoted values
"""

import re
from pathlib import Path
from typing import Dict


ENV_LINE_RE = re.compile(
    r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$'
)


class EnvParseError(Exception):
    """Raised when an .env file cannot be parsed."""


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def parse_env_file(path: str | Path) -> Dict[str, str]:
    """Parse an .env file and return a dict of key-value pairs.

    Args:
        path: Path to the .env file.

    Returns:
        Dictionary mapping environment variable names to their values.

    Raises:
        FileNotFoundError: If the file does not exist.
        EnvParseError: If a non-comment, non-empty line cannot be parsed.
    """
    env_path = Path(path)
    if not env_path.exists():
        raise FileNotFoundError(f"Env file not found: {env_path}")

    result: Dict[str, str] = {}

    with env_path.open(encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()

            # Skip blank lines and comments
            if not line or line.startswith("#"):
                continue

            match = ENV_LINE_RE.match(line)
            if not match:
                raise EnvParseError(
                    f"Invalid syntax at {env_path}:{lineno}: {raw_line.rstrip()!r}"
                )

            key = match.group("key")
            value = _strip_quotes(match.group("value").strip())
            result[key] = value

    return result
