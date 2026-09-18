"""Summarize an independently reviewed CP3 results CSV.

Usage:
    python eval/score_results.py eval/runs/20260918-120000/results.csv

The reviewer must fill T_source, N_source, K_script, H_control with 0/1.
A case passes only when all four dimensions equal 1.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

DIMENSIONS = ("T_source", "N_source", "K_script", "H_control")


def as_bit(value: str) -> int:
    value = value.strip()
    if value not in {"0", "1"}:
        raise ValueError(f"Expected 0 or 1, got {value!r}")
    return int(value)


def rate(passed: int, total: int) -> str:
    return f"{passed / total:.1%}" if total else "n/a"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a reviewed CP3 results CSV")
    parser.add_argument("results_csv", type=Path)
    args = parser.parse_args()

    with args.results_csv.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise SystemExit("Results CSV has no rows")

    invalid = [row.get("case_id", "?") for row in rows if any(row.get(dim, "").strip() not in {"0", "1"} for dim in DIMENSIONS)]
    if invalid:
        raise SystemExit("Missing or invalid dimension scores for: " + ", ".join(invalid))

    dimension_totals = Counter()
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    errors = Counter()
    for row in rows:
        scores = {dimension: as_bit(row[dimension]) for dimension in DIMENSIONS}
        row["passed"] = str(all(scores.values()))
        for dimension, score in scores.items():
            dimension_totals[dimension] += score
        groups[row.get("type", "unknown")].append(row)
        for error_code in row.get("error_codes", "").split(","):
            error_code = error_code.strip()
            if error_code:
                errors[error_code] += 1

    passed = sum(row["passed"] == "True" for row in rows)
    print(f"Cases: {passed}/{len(rows)} passed ({rate(passed, len(rows))})")
    print("Dimensions: " + " | ".join(f"{name} {dimension_totals[name]}/{len(rows)}" for name in DIMENSIONS))
    print("\nBy group:")
    for group, group_rows in groups.items():
        group_passed = sum(row["passed"] == "True" for row in group_rows)
        print(f"- {group}: {group_passed}/{len(group_rows)} ({rate(group_passed, len(group_rows))})")
    print("\nError codes:")
    if errors:
        for code, count in errors.most_common():
            print(f"- {code}: {count}")
    else:
        print("- none recorded")


if __name__ == "__main__":
    main()
