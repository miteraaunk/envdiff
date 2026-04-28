"""Command-line interface for envdiff."""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from envdiff.comparator import compare_envs
from envdiff.formatter import OutputFormat, format_result
from envdiff.parser import EnvParseError, parse_env_file


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments and highlight differences.",
    )
    parser.add_argument("left", type=Path, help="First .env file (e.g. .env.development)")
    parser.add_argument("right", type=Path, help="Second .env file (e.g. .env.production)")
    parser.add_argument(
        "--format",
        dest="fmt",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--left-label",
        default=None,
        help="Display label for the left file (default: filename)",
    )
    parser.add_argument(
        "--right-label",
        default=None,
        help="Display label for the right file (default: filename)",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 when differences are found",
    )
    return parser


def run(args: Namespace) -> int:
    """Execute the comparison and print results. Returns exit code."""
    left_label: str = args.left_label or args.left.name
    right_label: str = args.right_label or args.right.name
    fmt: OutputFormat = args.fmt  # type: ignore[assignment]

    try:
        left_env = parse_env_file(args.left)
        right_env = parse_env_file(args.right)
    except EnvParseError as exc:
        print(f"envdiff: parse error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"envdiff: cannot read file: {exc}", file=sys.stderr)
        return 2

    result = compare_envs(left_env, right_env)
    output = format_result(result, fmt=fmt, left_label=left_label, right_label=right_label)
    print(output, end="")

    if args.exit_code and result.diffs:
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":  # pragma: no cover
    main()
