"""Command line interface: ``kafka-namer [-n COUNT] [--seed SEED] ...``"""

import argparse
import random
import sys

from kafka_namer.generator import generate_names


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate two-word names for Kafka clusters.")
    parser.add_argument("-n", "--count", type=int, default=1, help="number of names to generate (default: 1)")
    parser.add_argument("--seed", type=int, default=None, help="seed for reproducible output")
    parser.add_argument("--separator", default="-", help="string placed between words (default: '-')")
    parser.add_argument("--prefix", default=None, help="optional prefix, e.g. an environment such as 'prod'")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.count < 1:
        print("error: --count must be at least 1", file=sys.stderr)
        return 2

    rng = random.Random(args.seed)
    try:
        names = generate_names(args.count, rng=rng, separator=args.separator, prefix=args.prefix)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print("\n".join(names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
