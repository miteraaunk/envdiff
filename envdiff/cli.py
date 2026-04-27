"""Command-line interface for envdiff."""

import sys
import argparse
from pathlib import Path

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.comparator import compare_envs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files and highlight missing or mismatched keys.",
    )
    parser.add_argument("left", type=Path, help="First .env file (e.g. .env.dev)")
    parser.add_argument("right", type=Path, help="Second .env file (e.g. .env.prod)")
    parser.add_argument(
        "--no-values",
        action="store_true",
        help="Hide actual values in mismatch output",
    )
    return parser


def run(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        left_env = parse_env_file(args.left)
    except (EnvParseError, OSError) as exc:
        print(f"Error reading {args.left}: {exc}", file=sys.stderr)
        return 1

    try:
        right_env = parse_env_file(args.right)
    except (EnvParseError, OSError) as exc:
        print(f"Error reading {args.right}: {exc}", file=sys.stderr)
        return 1

    result = compare_envs(
        left_env,
        right_env,
        left_label=args.left.name,
        right_label=args.right.name,
    )

    if args.no_values:
        for key in sorted(result.value_mismatches):
            result.value_mismatches[key] = ("***", "***")

    if result.has_differences:
        print(result.summary())
        return 2

    print(result.summary())
    return 0


def main():
    sys.exit(run())


if __name__ == "__main__":
    main()
