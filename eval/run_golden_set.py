"""Run the CP3 Golden Set and prepare a reviewer CSV.

Usage:
    python eval/run_golden_set.py --base-url http://localhost:8000

The script does not decide whether a case passes. It stores each generated result
and leaves T/N/K/H for an independent reviewer to score.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent
CASES_PATH = ROOT / "golden_set.json"
RESULTS_TEMPLATE = ROOT / "results-template.csv"
OUTPUT_DIR = ROOT / "runs"


def wait_for_sources(client: httpx.Client, base_url: str, session_id: str, timeout: int) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = client.get(f"{base_url}/api/sessions/{session_id}")
        response.raise_for_status()
        session = response.json()
        if session["status"] in {"sources_ready", "error"}:
            return session
        time.sleep(2)
    raise TimeoutError(f"Timed out waiting for session {session_id}")


def run_case(client: httpx.Client, base_url: str, case: dict, timeout: int) -> dict:
    response = client.post(
        f"{base_url}/api/sessions",
        json={key: case[key] for key in ("topic", "learning_goal", "audience", "duration_minutes")},
    )
    response.raise_for_status()
    session_id = response.json()["id"]

    response = client.post(f"{base_url}/api/sessions/{session_id}/search")
    response.raise_for_status()
    session = wait_for_sources(client, base_url, session_id, timeout)
    if session["status"] == "error":
        return {"case": case, "session_id": session_id, "error": session.get("error", "search failed")}

    response = client.post(f"{base_url}/api/sessions/{session_id}/script", timeout=timeout)
    response.raise_for_status()
    return {"case": case, "session_id": session_id, "result": response.json()}


def write_review_csv(cases: list[dict], rows: list[dict], path: Path, run_at: str) -> None:
    fieldnames = [
        "case_id", "type", "run_at", "pass", "T_source", "N_source",
        "K_script", "H_control", "error_codes", "observed_output", "reviewer_note",
    ]
    by_case = {row["case"]["case_id"]: row for row in rows}
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for case in cases:
            row = by_case[case["case_id"]]
            result = row.get("result", {})
            writer.writerow({
                "case_id": case["case_id"],
                "type": case["type"],
                "run_at": run_at,
                "pass": "",
                "T_source": "",
                "N_source": "",
                "K_script": "",
                "H_control": "",
                "error_codes": "RETRIEVAL-FAIL" if row.get("error") else "",
                "observed_output": json.dumps({
                    "session_id": row.get("session_id"),
                    "error": row.get("error"),
                    "script": result.get("json_content") if result else None,
                }, ensure_ascii=False),
                "reviewer_note": "",
            })


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all 24 CP3 ScriptScout cases")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    run_at = datetime.now(timezone.utc).isoformat()
    run_dir = OUTPUT_DIR / datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    rows = []

    with httpx.Client(base_url=args.base_url.rstrip("/"), timeout=args.timeout) as client:
        for index, case in enumerate(cases, start=1):
            print(f"[{index:02d}/{len(cases)}] {case['case_id']} {case['topic']}")
            try:
                row = run_case(client, "", case, args.timeout)
            except Exception as exc:
                row = {"case": case, "error": f"{type(exc).__name__}: {exc}"}
            rows.append(row)
            (run_dir / f"{case['case_id']}.json").write_text(
                json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    write_review_csv(cases, rows, run_dir / "results.csv", run_at)
    print(f"\nSaved raw outputs and review sheet to: {run_dir}")
    print("Fill T_source, N_source, K_script, H_control, pass, error_codes, and reviewer_note independently.")


if __name__ == "__main__":
    main()
