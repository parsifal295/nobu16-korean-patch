#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


KNOWN_BY_OFFSET = {
    # msggame run offsets with stable/clear meaning
    0xE0D8: " (최대 ",
    0x38643: "나, 노부나가",
    0x6B9B0: "도움말 > ",
    0x892FA: "노부나가",
    0x8930C: "의 야망",
}


def parse_off(v: str) -> int:
    s = (v or "").strip()
    if s.lower().startswith("0x"):
        return int(s, 16)
    return int(s)


def main() -> int:
    ap = argparse.ArgumentParser(description="Fill known-safe msggame run translations by offset")
    ap.add_argument("--input-csv", required=True)
    ap.add_argument("--output-csv", required=True)
    ap.add_argument("--overwrite", action="store_true", default=False)
    args = ap.parse_args()

    in_path = Path(args.input_csv)
    out_path = Path(args.output_csv)

    with in_path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        rows = list(r)
        fields = r.fieldnames or []

    if not fields:
        raise ValueError("empty csv header")

    updated = 0
    skipped_exists = 0
    missing = 0
    touched = set()

    for row in rows:
        off = parse_off(row["offset"])
        ko = KNOWN_BY_OFFSET.get(off)
        if ko is None:
            continue
        touched.add(off)

        cur = row.get("translated_ko", "")
        if cur.strip() and not args.overwrite:
            skipped_exists += 1
            continue

        row["translated_ko"] = ko
        row["status"] = "translated"
        note = (row.get("notes", "") or "").strip()
        tag = "known_terms_v3"
        row["notes"] = f"{note}; {tag}" if note else tag
        updated += 1

    for off in KNOWN_BY_OFFSET:
        if off not in touched:
            missing += 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"in={in_path}")
    print(f"out={out_path}")
    print(f"updated={updated}")
    print(f"skipped_existing={skipped_exists}")
    print(f"missing_offsets={missing}")
    print(f"known_total={len(KNOWN_BY_OFFSET)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
