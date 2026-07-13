#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_off(v: str) -> int:
    s = (v or "").strip()
    if s.lower().startswith("0x"):
        return int(s, 16)
    return int(s)


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply review-pack suggested_ko into runs CSV")
    ap.add_argument("--runs-csv", required=True)
    ap.add_argument("--review-csv", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument(
        "--suggest-reason",
        default="safe_ui_token",
        help="Only apply rows with this suggest_reason (comma-separated allowed)",
    )
    ap.add_argument("--overwrite", action="store_true", default=False)
    args = ap.parse_args()

    reasons = {x.strip() for x in args.suggest_reason.split(",") if x.strip()}
    if not reasons:
        raise ValueError("empty suggest-reason filter")

    with Path(args.runs_csv).open("r", encoding="utf-8-sig", newline="") as f:
        rr = csv.DictReader(f)
        run_rows = list(rr)
        run_fields = rr.fieldnames or []

    review_by_offset: dict[int, dict[str, str]] = {}
    with Path(args.review_csv).open("r", encoding="utf-8-sig", newline="") as f:
        rv = csv.DictReader(f)
        for row in rv:
            review_by_offset[parse_off(row["offset"])] = row

    applied = 0
    skipped_no_suggestion = 0
    skipped_has_translation = 0
    missing_review = 0

    for row in run_rows:
        off = parse_off(row["offset"])
        rv = review_by_offset.get(off)
        if rv is None:
            missing_review += 1
            continue

        suggested = (rv.get("suggested_ko") or "").strip()
        reason = (rv.get("suggest_reason") or "").strip()
        if not suggested or reason not in reasons:
            skipped_no_suggestion += 1
            continue

        cur = (row.get("translated_ko") or "").strip()
        if cur and not args.overwrite:
            skipped_has_translation += 1
            continue

        row["translated_ko"] = suggested
        row["status"] = "translated"
        note = (row.get("notes", "") or "").strip()
        tag = f"from_review:{reason}"
        row["notes"] = f"{note}; {tag}" if note else tag
        applied += 1

    out_path = Path(args.out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=run_fields)
        w.writeheader()
        w.writerows(run_rows)

    print(f"runs={len(run_rows)}")
    print(f"applied={applied}")
    print(f"skipped_no_suggestion={skipped_no_suggestion}")
    print(f"skipped_has_translation={skipped_has_translation}")
    print(f"missing_review={missing_review}")
    print(f"out={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
