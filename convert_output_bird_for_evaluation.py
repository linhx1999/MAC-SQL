#!/usr/bin/env python3
"""Convert MAC-SQL output JSONL to the indexed Mini-Dev evaluation format."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


BIRD_SEPARATOR = "\t----- bird -----\t"


def load_jsonl(input_path: Path) -> list[Any]:
    """Load non-empty JSONL records from ``input_path``."""
    records: list[Any] = []
    with input_path.open(encoding="utf-8") as input_file:
        for line_number, line in enumerate(input_file, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"invalid JSON on line {line_number} of {input_path}"
                ) from error
    return records


def convert_predictions(
    records: list[Any], expected_count: int | None = None
) -> tuple[dict[str, str], int, int]:
    """Convert JSONL records while preserving their original BIRD indices."""
    predictions: dict[int, str] = {}

    for line_index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise TypeError(f"record on line {line_index} must be a JSON object")

        idx = record.get("idx")
        if isinstance(idx, bool) or not isinstance(idx, int) or idx < 0:
            raise ValueError(
                f"'idx' on line {line_index} must be a non-negative integer"
            )
        if idx in predictions:
            raise ValueError(f"duplicate idx {idx} on line {line_index}")

        db_id = record.get("db_id")
        if not isinstance(db_id, str) or not db_id.strip():
            raise ValueError(
                f"'db_id' for idx {idx} must be a non-empty string"
            )

        prediction_sql = record.get("pred", "")
        if prediction_sql is None:
            prediction_sql = ""
        if not isinstance(prediction_sql, str):
            raise TypeError(f"'pred' for idx {idx} must be a string or null")
        if BIRD_SEPARATOR in prediction_sql:
            raise ValueError(
                f"'pred' for idx {idx} contains the BIRD separator"
            )

        predictions[idx] = f"{prediction_sql}{BIRD_SEPARATOR}{db_id}"

    inferred_count = max(predictions, default=-1) + 1
    output_count = inferred_count if expected_count is None else expected_count
    if output_count < 0:
        raise ValueError("--expected-count must be non-negative")
    if predictions and max(predictions) >= output_count:
        raise ValueError(
            f"idx {max(predictions)} is outside --expected-count {output_count}"
        )

    converted: dict[str, str] = {}
    missing_record_count = 0
    empty_sql_count = 0
    for idx in range(output_count):
        prediction = predictions.get(idx)
        if prediction is None:
            prediction = BIRD_SEPARATOR
            missing_record_count += 1
        if prediction.startswith(BIRD_SEPARATOR):
            empty_sql_count += 1
        converted[str(idx)] = prediction

    return converted, missing_record_count, empty_sql_count


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Convert MAC-SQL output_bird.json JSONL into the indexed JSON "
            "object expected by Mini-Dev evaluation."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
    )
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "converted prediction file (default: <input directory>/"
            "<input stem>_converted.json)"
        ),
    )
    parser.add_argument(
        "--expected-count",
        type=int,
        help=(
            "number of output entries; missing indices are filled with empty "
            "SQL (default: highest idx + 1)"
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Load, convert, and save predictions."""
    args = parse_args()
    output_path = args.output or args.input.with_name(
        f"{args.input.stem}_converted.json"
    )

    records = load_jsonl(args.input)
    converted, missing_record_count, empty_sql_count = convert_predictions(
        records, args.expected_count
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(converted, output_file, ensure_ascii=False, indent=2)
        output_file.write("\n")

    print(f"Converted {len(converted)} predictions: {output_path}")
    print(
        f"Empty SQL: {empty_sql_count} "
        f"(including {missing_record_count} missing records)"
    )


if __name__ == "__main__":
    main()
