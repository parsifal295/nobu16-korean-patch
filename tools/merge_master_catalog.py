#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def parse_offset(raw: str) -> int:
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("empty offset")
    if raw.lower().startswith("0x"):
        return int(raw, 16)
    return int(raw)


def norm_abs(path_str: str) -> str:
    return str(Path(path_str).resolve())


def parse_source_spec(spec: str) -> tuple[Path, str | None]:
    # spec format:
    #   /path/to/source.csv
    #   /path/to/source.csv::/abs/or/rel/target/file.bin
    if "::" not in spec:
        return (Path(spec), None)
    left, right = spec.split("::", 1)
    return (Path(left), right.strip() or None)


def main() -> int:
    ap = argparse.ArgumentParser(description="Merge translated rows into master catalog")
    ap.add_argument("--master-csv", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument(
        "--source",
        action="append",
        default=[],
        help="Source CSV or CSV::target_file_path mapping (repeatable)",
    )
    args = ap.parse_args()

    master_path = Path(args.master_csv)
    out_path = Path(args.out_csv)
    if not master_path.exists():
        raise FileNotFoundError(master_path)
    if not args.source:
        raise ValueError("at least one --source is required")

    with master_path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        master_rows = list(r)
        headers = r.fieldnames or []

    required = {"file", "offset", "translated_ko", "status", "notes"}
    missing = sorted(required - set(headers))
    if missing:
        raise ValueError(f"master missing columns: {missing}")

    by_abs_key: dict[tuple[str, int], int] = {}
    by_name_key: dict[tuple[str, int], list[int]] = defaultdict(list)
    for idx, row in enumerate(master_rows):
        abs_file = norm_abs(row["file"])
        off = parse_offset(row["offset"])
        by_abs_key[(abs_file, off)] = idx
        by_name_key[(Path(abs_file).name.lower(), off)].append(idx)

    total_merged = 0
    per_source_stats: list[tuple[str, int, int]] = []

    for source_spec in args.source:
        src_csv, forced_file = parse_source_spec(source_spec)
        if not src_csv.exists():
            raise FileNotFoundError(src_csv)

        forced_abs = norm_abs(forced_file) if forced_file else None
        with src_csv.open("r", encoding="utf-8-sig", newline="") as f:
            r = csv.DictReader(f)
            src_rows = list(r)

        merged_here = 0
        for srow in src_rows:
            tr = (srow.get("translated_ko") or "").strip()
            st = (srow.get("status") or "").strip()
            nt = (srow.get("notes") or "").strip()
            if not tr and not st and not nt:
                continue

            src_file = (srow.get("file") or "").strip()
            abs_file = forced_abs or (norm_abs(src_file) if src_file else None)
            if abs_file is None:
                # no reliable file key in source row
                continue

            try:
                off = parse_offset(srow.get("offset", ""))
            except Exception:
                continue

            m_idx = by_abs_key.get((abs_file, off))
            if m_idx is None:
                # fallback by basename when absolute path differs
                cand = by_name_key.get((Path(abs_file).name.lower(), off), [])
                if len(cand) == 1:
                    m_idx = cand[0]
            if m_idx is None:
                continue

            m = master_rows[m_idx]
            if tr:
                m["translated_ko"] = tr
                if st:
                    m["status"] = st
                elif (m.get("status") or "").strip().lower() in ("", "todo"):
                    m["status"] = "done"
            elif st:
                m["status"] = st
            if nt:
                m["notes"] = nt
            merged_here += 1

        total_merged += merged_here
        per_source_stats.append((str(src_csv), merged_here, len(src_rows)))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(master_rows)

    print(f"master_entries={len(master_rows)}")
    print(f"merged_total={total_merged}")
    print(f"out={out_path}")
    for src, merged, total in per_source_stats:
        print(f"source {src}: merged={merged}/{total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
