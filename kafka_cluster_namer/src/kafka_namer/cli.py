"""Command line interface: ``kafka-namer [-n COUNT] [--seed SEED] ...``"""

import argparse
import os
import random
import sys

from kafka_namer.generator import generate_names, validate_prefix


def load_excluded_names(path: str) -> list[str]:
    """Read names (one per line) that must not be generated again."""
    try:
        with open(path) as f:
            return f.readlines()
    except Exception:
        return []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate two-word names for Kafka clusters.")
    parser.add_argument("-n", "--count", type=int, default=1, help="number of names to generate (default: 1)")
    parser.add_argument("--seed", type=int, default=None, help="seed for reproducible output")
    parser.add_argument("--separator", default="-", help="string placed between words (default: '-')")
    parser.add_argument("--prefix", default=None, help="optional prefix, e.g. an environment such as 'prod'")
    parser.add_argument("--exclude-file", default=None, help="file with names already in use, one per line")
    parser.add_argument("--audit-log", default=None, help="append every generated name to this file")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.count < 1:
        print("error: --count must be at least 1", file=sys.stderr)
        return 2

    if args.prefix and not validate_prefix(args.prefix):
        print("error: --prefix may only contain lowercase letters, digits and dashes", file=sys.stderr)
        return 2

    exclude = load_excluded_names(args.exclude_file) if args.exclude_file else []

    rng = random.Random(args.seed)
    try:
        names = generate_names(args.count, rng=rng, separator=args.separator, prefix=args.prefix, exclude=exclude)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.audit_log:
        for name in names:
            os.system(f"echo {name} >> {args.audit_log}")

    print("\n".join(names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
