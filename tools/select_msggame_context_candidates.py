#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


WORD_RE = re.compile(r"[A-Za-z]{2,}")


def score_context(s: str) -> float:
    if not s:
        return -1e9
    letters = sum(c.isalpha() for c in s)
    spaces = s.count(" ")
    digits = sum(c.isdigit() for c in s)
    punct = sum(c in ".,:;!?-'\"" for c in s)
    words = len(WORD_RE.findall(s))
    non_print = sum(ord(c) < 32 or ord(c) > 126 for c in s)
    return (
        letters * 1.2
        + words * 6.0
        + spaces * 1.0
        + punct * 0.5
        - digits * 2.0
        - non_print * 8.0
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Select higher-confidence msggame context rows")
    ap.add_argument("--input-csv", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--top-n", type=int, default=30)
    ap.add_argument("--min-context-len", type=int, default=20)
    args = ap.parse_args()

    with Path(args.input_csv).open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    scored = []
    for r in rows:
        ctx = r.get("mixed_context_en", "")
        if len(ctx) < args.min_context_len:
            continue
        s = score_context(ctx)
        scored.append((s, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    picked = [r for _, r in scored[: args.top_n]]

    out_path = Path(args.out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) + ["confidence_score"]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for s, r in scored[: args.top_n]:
            row = dict(r)
            row["confidence_score"] = f"{s:.2f}"
            w.writerow(row)

    print(f"input_rows={len(rows)}")
    print(f"candidates={len(scored)}")
    print(f"picked={len(picked)}")
    print(f"out={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
