#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

from edgeoml.io import read_jsonl, write_json
from edgeoml.metrics import evaluate_records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in args.inputs:
        for record in read_jsonl(path):
            grouped[str(record["condition"])].append(record)

    summary: dict[str, Any] = {
        "schema_version": "0.1",
        "pilot_label": "M4 LoRA pilot; not upstream OML full fine-tuning",
        "conditions": {},
    }
    for condition, records in sorted(grouped.items()):
        metrics = evaluate_records(records)
        latencies = [
            float(record["elapsed_ms"])
            for record in records
            if record.get("elapsed_ms") is not None
        ]
        metrics["median_elapsed_ms"] = median(latencies) if latencies else None
        summary["conditions"][condition] = metrics

    write_json(args.output, summary)
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
