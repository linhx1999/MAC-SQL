"""Ordered Spider predictions from potentially unordered checkpoints."""
from __future__ import annotations


def prediction_lines(records: list[dict], count: int) -> list[str]:
    latest = {}
    for record in records:
        idx = record["idx"]
        if type(idx) is not int or not 0 <= idx < count:
            raise ValueError(f"Invalid Spider question index: {idx}")
        latest[idx] = record
    lines = []
    for idx in range(count):
        record = latest.get(idx, {})
        sql = record.get("pred")
        if record.get("error_type") or not isinstance(sql, str) or not sql.strip():
            sql = "SELECT * FROM __mac_failed_prediction__"
        lines.append(sql.replace("\r", " ").replace("\n", " ").replace("\t", " ").strip() + "\n")
    return lines
