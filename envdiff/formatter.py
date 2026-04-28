"""Output formatters for envdiff comparison results."""

from __future__ import annotations

from typing import Literal

from envdiff.comparator import DiffResult

OutputFormat = Literal["text", "json", "markdown"]


def _status_symbol(status: str) -> str:
    return {"missing_left": "<", "missing_right": ">", "mismatch": "~"}.get(status, "?")


def format_text(result: DiffResult, left_label: str = "left", right_label: str = "right") -> str:
    """Human-readable text output."""
    if not result.diffs:
        return "No differences found.\n"

    lines: list[str] = []
    lines.append(f"Comparing {left_label!r} vs {right_label!r}\n")

    for key, status, left_val, right_val in result.diffs:
        sym = _status_symbol(status)
        if status == "missing_left":
            lines.append(f"  {sym} {key}  (only in {right_label}: {right_val!r})")
        elif status == "missing_right":
            lines.append(f"  {sym} {key}  (only in {left_label}: {left_val!r})")
        else:
            lines.append(f"  {sym} {key}  ({left_label}: {left_val!r}  |  {right_label}: {right_val!r})")

    lines.append(f"\n{len(result.diffs)} difference(s) found.")
    return "\n".join(lines) + "\n"


def format_json(result: DiffResult, left_label: str = "left", right_label: str = "right") -> str:
    """JSON output for machine consumption."""
    import json

    entries = []
    for key, status, left_val, right_val in result.diffs:
        entries.append(
            {
                "key": key,
                "status": status,
                left_label: left_val,
                right_label: right_val,
            }
        )

    payload = {
        "left": left_label,
        "right": right_label,
        "differences": entries,
        "count": len(entries),
    }
    return json.dumps(payload, indent=2) + "\n"


def format_markdown(result: DiffResult, left_label: str = "left", right_label: str = "right") -> str:
    """Markdown table output."""
    if not result.diffs:
        return "_No differences found._\n"

    lines: list[str] = []
    lines.append(f"## envdiff: `{left_label}` vs `{right_label}`\n")
    lines.append(f"| Key | Status | {left_label} | {right_label} |")
    lines.append("|-----|--------|" + "-" * (len(left_label) + 2) + "|" + "-" * (len(right_label) + 2) + "|")

    for key, status, left_val, right_val in result.diffs:
        lv = left_val if left_val is not None else "_missing_"
        rv = right_val if right_val is not None else "_missing_"
        lines.append(f"| `{key}` | {status} | {lv} | {rv} |")

    lines.append(f"\n_{len(result.diffs)} difference(s) found._")
    return "\n".join(lines) + "\n"


def format_result(
    result: DiffResult,
    fmt: OutputFormat = "text",
    left_label: str = "left",
    right_label: str = "right",
) -> str:
    """Dispatch to the appropriate formatter."""
    if fmt == "json":
        return format_json(result, left_label, right_label)
    if fmt == "markdown":
        return format_markdown(result, left_label, right_label)
    return format_text(result, left_label, right_label)
