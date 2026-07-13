#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path


WORD_RE = re.compile(r"[A-Za-z]+")
SAFE_PUNCT_END = tuple(".!?:;>) ]")

# Suggestion map is intentionally conservative; it only proposes clearly recognizable UI tokens.
DEFAULT_SUGGEST_KO_BY_ORIG = {
    "right": "우측",
}


@dataclass
class RunRow:
    id: str
    file: str
    offset: int
    offset_hex: str
    allocated_bytes: int
    max_chars_est: int
    original_en: str
    translated_ko: str
    status: str
    notes: str


def parse_off(s: str) -> int:
    s = (s or "").strip()
    if s.lower().startswith("0x"):
        return int(s, 16)
    return int(s)


def load_runs(path: Path) -> list[RunRow]:
    rows: list[RunRow] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(
                RunRow(
                    id=row["id"],
                    file=row["file"],
                    offset=parse_off(row["offset"]),
                    offset_hex=row.get("offset_hex", f"0x{parse_off(row['offset']):X}"),
                    allocated_bytes=int(row["allocated_bytes"]),
                    max_chars_est=int(row.get("max_chars_est") or (int(row["allocated_bytes"]) // 2)),
                    original_en=row.get("original_en", ""),
                    translated_ko=row.get("translated_ko", ""),
                    status=row.get("status", ""),
                    notes=row.get("notes", ""),
                )
            )
    rows.sort(key=lambda x: x.offset)
    return rows


def load_context_map(path: Path) -> dict[int, str]:
    out: dict[int, str] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            out[parse_off(row["offset"])] = row.get("mixed_context_en", "")
    return out


def is_likely_truncated(text: str) -> tuple[bool, str]:
    if not text:
        return True, "empty"
    if text[0].islower() or text[0] == " ":
        return True, "start-fragment"
    if text[-1].isalpha() and not text.endswith(SAFE_PUNCT_END):
        return True, "end-fragment"
    return False, ""


def confidence_bucket(text: str, translated: bool) -> tuple[str, float]:
    if translated:
        return "done", 1000.0
    words = WORD_RE.findall(text)
    letters = sum(c.isalpha() for c in text)
    spaces = text.count(" ")
    punct = sum(c in ".,:;!?-_/[](){}'\"&%+$*=<>|@#" for c in text)
    trunc, _ = is_likely_truncated(text)
    score = letters * 1.1 + len(words) * 8 + spaces * 1.2 + punct * 0.3 - (20 if trunc else 0)

    if not trunc and len(words) >= 2 and len(text) >= 10:
        return "high", score
    if trunc and (len(text) <= 6 or len(words) <= 1):
        return "low", score
    if len(words) >= 1 and len(text) >= 7:
        return "medium", score
    return "low", score


def neighbors(rows: list[RunRow], idx: int, radius: int = 0x80) -> str:
    base = rows[idx].offset
    parts: list[str] = []
    for j in range(max(0, idx - 6), min(len(rows), idx + 7)):
        if j == idx:
            continue
        r = rows[j]
        if abs(r.offset - base) <= radius:
            parts.append(f"{r.offset_hex}:{r.original_en}")
    return " | ".join(parts)


def load_suggest_map(path: Path | None) -> dict[str, str]:
    merged = dict(DEFAULT_SUGGEST_KO_BY_ORIG)
    if path is None:
        return merged
    if not path.exists():
        raise FileNotFoundError(f"suggest map not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("suggest map must be a JSON object")
    for k, v in payload.items():
        if not isinstance(k, str) or not isinstance(v, str):
            continue
        merged[k] = v
    return merged


def write_pack(
    rows: list[RunRow],
    ctx_map: dict[int, str],
    suggest_map: dict[str, str],
    out_csv: Path,
) -> list[dict[str, str]]:
    out_rows: list[dict[str, str]] = []
    for i, r in enumerate(rows):
        tr = (r.translated_ko or "").strip()
        trunc, trunc_reason = is_likely_truncated(r.original_en)
        bucket, score = confidence_bucket(r.original_en, translated=bool(tr))
        suggested = ""
        suggest_reason = ""
        if not tr:
            suggested = suggest_map.get(r.original_en, "")
            if suggested:
                suggest_reason = "safe_ui_token"

        out_rows.append(
            {
                "id": r.id,
                "file": r.file,
                "offset_hex": r.offset_hex,
                "offset": str(r.offset),
                "allocated_bytes": str(r.allocated_bytes),
                "max_chars_est": str(r.max_chars_est),
                "original_en": r.original_en,
                "translated_ko": r.translated_ko,
                "status": r.status,
                "review_bucket": bucket,
                "review_score": f"{score:.2f}",
                "truncation_hint": trunc_reason if trunc else "",
                "mixed_context_en": ctx_map.get(r.offset, ""),
                "neighbor_runs": neighbors(rows, i),
                "suggested_ko": suggested,
                "suggest_reason": suggest_reason,
                "notes": r.notes,
            }
        )

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        fields = [
            "id",
            "file",
            "offset_hex",
            "offset",
            "allocated_bytes",
            "max_chars_est",
            "original_en",
            "translated_ko",
            "status",
            "review_bucket",
            "review_score",
            "truncation_hint",
            "mixed_context_en",
            "neighbor_runs",
            "suggested_ko",
            "suggest_reason",
            "notes",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)
    return out_rows


def write_md(out_rows: list[dict[str, str]], out_md: Path, src_runs: Path, src_ctx: Path) -> None:
    by_bucket = Counter(r["review_bucket"] for r in out_rows)
    untranslated = [r for r in out_rows if not (r.get("translated_ko") or "").strip()]
    hi = [r for r in untranslated if r["review_bucket"] == "high"]
    med = [r for r in untranslated if r["review_bucket"] == "medium"]
    sug = [r for r in untranslated if (r.get("suggested_ko") or "").strip()]

    lines: list[str] = []
    lines.append(f"# msggame Review Pack ({date.today().isoformat()})")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- runs_csv: `{src_runs}`")
    lines.append(f"- context_csv: `{src_ctx}`")
    lines.append(f"- total_rows: `{len(out_rows)}`")
    lines.append("")
    lines.append("## Bucket Summary")
    lines.append("")
    for k in ("done", "high", "medium", "low"):
        lines.append(f"- `{k}`: {by_bucket.get(k, 0)}")
    lines.append("")
    lines.append("## Suggested Tokens")
    lines.append("")
    if sug:
        for r in sug[:20]:
            lines.append(f"- {r['offset_hex']} `{r['original_en']}` -> `{r['suggested_ko']}`")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## High Candidates (Untranslated)")
    lines.append("")
    if hi:
        for r in hi[:20]:
            lines.append(
                f"- {r['offset_hex']} `{r['original_en']}` (score={r['review_score']}, trunc={r['truncation_hint'] or 'no'})"
            )
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## Medium Candidates (Top 20)")
    lines.append("")
    med_sorted = sorted(med, key=lambda x: float(x["review_score"]), reverse=True)
    if med_sorted:
        for r in med_sorted[:20]:
            lines.append(
                f"- {r['offset_hex']} `{r['original_en']}` (score={r['review_score']}, trunc={r['truncation_hint'] or 'no'})"
            )
    else:
        lines.append("- (none)")
    lines.append("")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build msggame review pack for safer translation expansion")
    ap.add_argument("--runs-csv", required=True)
    ap.add_argument("--context-csv", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--suggest-map", help="JSON object map: original_en -> suggested_ko")
    args = ap.parse_args()

    runs_csv = Path(args.runs_csv)
    context_csv = Path(args.context_csv)
    out_csv = Path(args.out_csv)
    out_md = Path(args.out_md)
    suggest_map = load_suggest_map(Path(args.suggest_map) if args.suggest_map else None)

    rows = load_runs(runs_csv)
    ctx_map = load_context_map(context_csv)
    out_rows = write_pack(rows, ctx_map, suggest_map, out_csv)
    write_md(out_rows, out_md, runs_csv, context_csv)

    by_bucket = Counter(r["review_bucket"] for r in out_rows)
    suggested = sum(1 for r in out_rows if (r.get("suggested_ko") or "").strip())
    print(f"rows={len(out_rows)}")
    print(f"bucket_done={by_bucket.get('done', 0)}")
    print(f"bucket_high={by_bucket.get('high', 0)}")
    print(f"bucket_medium={by_bucket.get('medium', 0)}")
    print(f"bucket_low={by_bucket.get('low', 0)}")
    print(f"suggested={suggested}")
    print(f"suggest_map_size={len(suggest_map)}")
    print(f"out_csv={out_csv}")
    print(f"out_md={out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
