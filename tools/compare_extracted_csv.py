#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def load_csv(path: Path):
    rows = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            r["offset"] = int(r["offset"])
            r["length_chars"] = int(r["length_chars"])
            rows.append(r)
    return rows


def index_rows(rows):
    idx = defaultdict(list)
    for r in rows:
        stem = Path(r["file"]).name
        idx[(stem, r["offset"])].append(r)
    return idx


def choose_best(rows):
    rows = sorted(rows, key=lambda x: (x["encoding"] != "utf16le_a0", -x["length_chars"]))
    return rows[0]


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare extracted text CSVs by file+offset")
    ap.add_argument("--base", required=True, help="Base CSV (e.g. EN)")
    ap.add_argument("--target", required=True, help="Target CSV (e.g. SC/TC)")
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--sample-size", type=int, default=80)
    args = ap.parse_args()

    base_rows = load_csv(Path(args.base))
    tgt_rows = load_csv(Path(args.target))

    ib = index_rows(base_rows)
    it = index_rows(tgt_rows)

    keys = sorted(set(ib.keys()) & set(it.keys()))
    pairs = []
    for k in keys:
        br = choose_best(ib[k])
        tr = choose_best(it[k])
        if br["text"] != tr["text"]:
            pairs.append(
                {
                    "file": k[0],
                    "offset": k[1],
                    "base_encoding": br["encoding"],
                    "target_encoding": tr["encoding"],
                    "base_text": br["text"],
                    "target_text": tr["text"],
                }
            )

    payload = {
        "base": args.base,
        "target": args.target,
        "shared_offsets": len(keys),
        "different_text_offsets": len(pairs),
        "samples": pairs[: args.sample_size],
    }

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    out_md = Path(args.out_md)
    lines = []
    lines.append(f"# Compare Report: {args.base} vs {args.target}")
    lines.append("")
    lines.append(f"- shared_offsets: {len(keys)}")
    lines.append(f"- different_text_offsets: {len(pairs)}")
    lines.append("")
    lines.append("## Samples")
    lines.append("")
    for item in pairs[: args.sample_size]:
        lines.append(f"- {item['file']} @ 0x{item['offset']:X}")
        lines.append(f"  - base: {item['base_text']}")
        lines.append(f"  - target: {item['target_text']}")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"shared_offsets={len(keys)}")
    print(f"different_offsets={len(pairs)}")
    print(f"json: {out_json}")
    print(f"md: {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
