#!/usr/bin/env python3
"""Convert MAC-SQL Spider JSONL predictions to the Spider evaluation format."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path(
    "/home/linhx/workspace/kouan/MAC-SQL/outputs/"
    "macsql_spider_dev_qwen3.6-35b-a3b/"
    "macsql_spider_dev_qwen3.6-35b-a3b.json"
)
def load_predictions(path: Path) -> list[dict[str, Any]]:
    """Load MAC-SQL's JSONL output."""
    records = []
    with path.open(encoding="utf-8") as input_file:
        for line_number, line in enumerate(input_file, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSON at line {line_number}") from error
            if not isinstance(record, dict):
                raise TypeError(f"line {line_number} must contain a JSON object")
            records.append(record)
    return records


def convert_predictions(records: list[dict[str, Any]]) -> list[str]:
    """Return one normalized SQL prediction per sample, ordered by ``idx``."""
    indexed_predictions: dict[int, str] = {}
    for line_number, record in enumerate(records, start=1):
        index = record.get("idx")
        prediction = record.get("pred")
        if not isinstance(index, int) or isinstance(index, bool) or index < 0:
            raise TypeError(f"idx at line {line_number} must be a non-negative integer")
        if index in indexed_predictions:
            raise ValueError(f"duplicate idx {index} at line {line_number}")
        if not isinstance(prediction, str) or not prediction.strip():
            raise ValueError(f"pred at line {line_number} must be a non-empty string")
        indexed_predictions[index] = re.sub(r"\s+", " ", prediction).strip()

    expected_indices = list(range(len(indexed_predictions)))
    actual_indices = sorted(indexed_predictions)
    if actual_indices != expected_indices:
        missing = sorted(set(expected_indices) - set(actual_indices))
        raise ValueError(f"prediction indices must be contiguous from 0; missing: {missing}")

    return [indexed_predictions[index] for index in expected_indices]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert MAC-SQL Spider JSONL output to one SQL statement per line."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument(
        "--output",
        type=Path,
        help="output path (default: input file with its suffix changed to .txt)",
    )
    return parser.parse_args()


def main() -> None:
    """Load, validate, convert, and save predictions."""
    args = parse_args()
    output_path = args.output or args.input.with_suffix(".txt")
    predictions = convert_predictions(load_predictions(args.input))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as output_file:
        for prediction in predictions:
            output_file.write(prediction + "\n")
    print(f"Converted {len(predictions)} predictions: {output_path}")


if __name__ == "__main__":
    main()
