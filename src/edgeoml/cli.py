from __future__ import annotations

import argparse
import json
from typing import Sequence

from .io import read_json, read_jsonl, write_json, write_jsonl
from .matrix import build_matrix
from .metrics import evaluate_records
from .receipt import validate_receipt


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="edgeoml")
    commands = parser.add_subparsers(dest="command", required=True)

    matrix = commands.add_parser("matrix", help="generate a deterministic run matrix")
    matrix.add_argument("--config", required=True)
    matrix.add_argument("--output", required=True)

    evaluate = commands.add_parser("evaluate", help="score prediction JSONL")
    evaluate.add_argument("--input", required=True)
    evaluate.add_argument("--output", required=True)

    receipt = commands.add_parser(
        "validate-receipt", help="validate EdgeOML evidence receipt structure"
    )
    receipt.add_argument("--input", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.command == "matrix":
        runs = build_matrix(read_json(args.config))
        write_jsonl(args.output, runs)
        print(json.dumps({"runs": len(runs), "output": args.output}))
        return 0

    if args.command == "evaluate":
        summary = evaluate_records(read_jsonl(args.input))
        write_json(args.output, summary)
        print(json.dumps(summary, sort_keys=True))
        return 0

    if args.command == "validate-receipt":
        errors = validate_receipt(read_json(args.input))
        print(json.dumps({"valid": not errors, "errors": errors}, sort_keys=True))
        return 1 if errors else 0

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
