"""Command-line interface for envdiff."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from envdiff.comparator import compare_envs
from envdiff.filter import build_filter_config
from envdiff.formatter import format_result
from envdiff.parser import EnvParseError, parse_env_file
from envdiff.reporter import ReportError, report_exit_code, write_report


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments.",
    )
    p.add_argument("left", help="First .env file (reference)")
    p.add_argument("right", help="Second .env file (target)")
    p.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write report to FILE instead of stdout",
    )
    p.add_argument(
        "--prefix",
        metavar="PREFIX",
        help="Only compare keys starting with PREFIX",
    )
    p.add_argument(
        "--include",
        metavar="PATTERN",
        action="append",
        help="Glob pattern of keys to include (repeatable)",
    )
    p.add_argument(
        "--exclude",
        metavar="PATTERN",
        action="append",
        help="Glob pattern of keys to exclude (repeatable)",
    )
    return p


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        left_env = parse_env_file(args.left)
        right_env = parse_env_file(args.right)
    except EnvParseError as exc:
        print(f"envdiff: parse error: {exc}", file=sys.stderr)
        return 2

    filter_cfg = build_filter_config(
        include=args.include,
        exclude=args.exclude,
        prefix=args.prefix,
    )

    result = compare_envs(left_env, right_env, filter_config=filter_cfg)
    formatted = format_result(result, fmt=args.fmt, left=args.left, right=args.right)

    try:
        write_report(formatted, output=args.output)
    except ReportError as exc:
        print(f"envdiff: output error: {exc}", file=sys.stderr)
        return 2

    return report_exit_code(result)


def main() -> None:  # pragma: no cover
    sys.exit(run())
