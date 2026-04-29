"""Command-line interface for envdiff."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envdiff.comparator import compare_envs
from envdiff.parser import EnvParseError, parse_env_file
from envdiff.reporter import ReportError, report_exit_code, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files and highlight missing or mismatched keys.",
    )
    parser.add_argument("left", help="First .env file (the reference).")
    parser.add_argument("right", help="Second .env file (compared against reference).")
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json", "markdown"],
        default="text",
        dest="fmt",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        default=None,
        help="Write report to FILE instead of stdout.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour codes in text output.",
    )
    return parser


def run(argv: Optional[List[str]] = None) -> int:
    """Parse *argv*, run the comparison and return an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        left_env = parse_env_file(args.left)
        right_env = parse_env_file(args.right)
    except EnvParseError as exc:
        print(f"envdiff: parse error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"envdiff: {exc}", file=sys.stderr)
        return 2

    result = compare_envs(left_env, right_env)

    try:
        write_report(
            result,
            fmt=args.fmt,
            output_path=args.output,
            color=not args.no_color,
        )
    except ReportError as exc:
        print(f"envdiff: {exc}", file=sys.stderr)
        return 2

    return report_exit_code(result)


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
