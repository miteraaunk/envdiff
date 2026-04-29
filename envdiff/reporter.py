"""Report generation: write diff results to files or stdout in various formats."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from envdiff.comparator import DiffResult
from envdiff.formatter import format_result


class ReportError(Exception):
    """Raised when a report cannot be written."""


def write_report(
    result: DiffResult,
    fmt: str = "text",
    output_path: Optional[str] = None,
    *,
    color: bool = True,
) -> None:
    """Format *result* and write it to *output_path* or stdout.

    Args:
        result:      The diff result to report on.
        fmt:         Output format – one of ``text``, ``json``, ``markdown``.
        output_path: File path to write to.  ``None`` means stdout.
        color:       Whether to emit ANSI colour codes (text format only).

    Raises:
        ReportError: If the output file cannot be written.
    """
    content = format_result(result, fmt=fmt, color=color)

    if output_path is None:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
        return

    path = Path(output_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise ReportError(f"Cannot write report to '{output_path}': {exc}") from exc


def report_exit_code(result: DiffResult) -> int:
    """Return a shell-friendly exit code derived from *result*.

    Returns:
        0 if there are no differences, 1 otherwise.
    """
    from envdiff.comparator import has_differences

    return 1 if has_differences(result) else 0
