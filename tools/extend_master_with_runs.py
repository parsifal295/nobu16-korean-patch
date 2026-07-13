#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_offset(v: str) -> int:
    v = (v or "").strip()
    if v.lower().startswith("0x"):
        return int(v, 16)
    return int(v)


def main() -> int:
    ap = argparse.ArgumentParser(description="Append run-based rows to master catalog")
    ap.add_argument("--master-csv", required=True)
    ap.add_argument("--runs-csv", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--encoding", default="utf16le_run")
    ap.add_argument("--status-default", default="todo")
    args = ap.parse_args()

    master_path = Path(args.master_csv)
    runs_path = Path(args.runs_csv)
    out_path = Path(args.out_csv)

    with master_path.open("r", encoding="utf-8-sig", newline="") as f:
        mr = csv.DictReader(f)
        master_rows = list(mr)
        fieldnames = mr.fieldnames or []

    required_master = {
        "id",
        "file",
        "encoding",
        "offset_hex",
        "offset",
        "allocated_bytes",
        "max_chars_est",
        "original_en",
        "translated_ko",
        "status",
        "notes",
    }
    miss = sorted(required_master - set(fieldnames))
    if miss:
        raise ValueError(f"master missing columns: {miss}")

    keyset = set()
    for r in master_rows:
        keyset.add((str(Path(r["file"]).resolve()), parse_offset(r["offset"])))

    with runs_path.open("r", encoding="utf-8-sig", newline="") as f:
        rr = csv.DictReader(f)
        run_rows = list(rr)

    appended = 0
    for r in run_rows:
        file_path = str(Path(r["file"]).resolve())
        off = parse_offset(r["offset"])
        key = (file_path, off)
        if key in keyset:
            continue

        alloc = int(r["allocated_bytes"])
        tr = r.get("translated_ko", "")
        st = (r.get("status") or "").strip() or args.status_default
        note = r.get("notes", "")

        master_rows.append(
            {
                "id": str(len(master_rows) + 1),
                "file": file_path,
                "encoding": args.encoding,
                "offset_hex": f"0x{off:X}",
                "offset": str(off),
                "allocated_bytes": str(alloc),
                "max_chars_est": str(alloc // 2),
                "original_en": r.get("original_en", ""),
                "translated_ko": tr,
                "status": st if tr.strip() else (st if st.lower() == "keep" else "todo"),
                "notes": note,
            }
        )
        keyset.add(key)
        appended += 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(master_rows)

    print(f"master_rows={len(master_rows)}")
    print(f"appended={appended}")
    print(f"out={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
