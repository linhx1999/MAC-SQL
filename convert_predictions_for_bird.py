#!/usr/bin/env python3
"""Convert MAC-SQL predictions to the JSON format used by Mini-Dev evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


BIRD_SEPARATOR = "\t----- bird -----\t"


def convert_predictions(data: Any) -> dict[str, str]:
    """Convert ``[[question, prediction], ...]`` into an indexed JSON object."""
    if not isinstance(data, list):
        raise TypeError("input JSON must be a list of [question, prediction] pairs")

    converted: dict[str, str] = {}
    for index, item in enumerate(data):
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError(
                f"item {index} must be a two-element [question, prediction] list"
            )

        question, prediction = item
        if not isinstance(question, str):
            raise TypeError(f"question at item {index} must be a string")
        if not isinstance(prediction, str):
            raise TypeError(f"prediction at item {index} must be a string")
        if prediction.count(BIRD_SEPARATOR) != 1:
            raise ValueError(
                f"prediction at item {index} must contain exactly one "
                f"{BIRD_SEPARATOR!r} separator"
            )

        sql, db_id = prediction.split(BIRD_SEPARATOR)
        if not sql.strip():
            raise ValueError(f"SQL at item {index} must not be empty")
        if not db_id.strip():
            raise ValueError(f"database ID at item {index} must not be empty")

        converted[str(index)] = prediction

    return converted


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Convert MAC-SQL predict_dev.json to the indexed JSON object "
            "expected by mini_dev/evaluation/run_evaluation.sh."
        )
    )
    _ = parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="original MAC-SQL prediction file",
    )
    _ = parser.add_argument(
        "--output",
        type=Path,
        help=(
            "converted prediction file (default: <input directory>/"
            "<input stem>_converted.json)"
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Load, validate, convert, and save predictions."""
    args = parse_args()
    output_path = args.output or args.input.with_name(
        f"{args.input.stem}_converted{args.input.suffix}"
    )

    with args.input.open(encoding="utf-8") as input_file:
        data = json.load(input_file)

    converted = convert_predictions(data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(converted, output_file, ensure_ascii=False, indent=2)
        output_file.write("\n")

    print(f"Converted {len(converted)} predictions: {output_path}")


if __name__ == "__main__":
    main()
