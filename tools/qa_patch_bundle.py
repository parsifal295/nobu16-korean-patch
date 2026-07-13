#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import date
from pathlib import Path


def encode_text(text: str, enc: str) -> bytes:
    if enc == "utf16le":
        return text.encode("utf-16-le") + b"\x00\x00"
    if enc == "utf16be":
        return text.encode("utf-16-be") + b"\x00\x00"
    if enc == "utf16le_run":
        return text.encode("utf-16-le")
    raise ValueError(f"unknown encoding: {enc}")


def decode_terminated(data: bytes, offset: int, alloc: int, enc: str) -> str:
    end = min(len(data), offset + alloc)
    out: list[str] = []
    i = offset
    while i + 1 < end:
        if enc == "utf16le":
            code = data[i] | (data[i + 1] << 8)
        else:
            code = (data[i] << 8) | data[i + 1]
        if code == 0:
            break
        out.append(chr(code))
        i += 2
    return "".join(out)


def decode_run(data: bytes, offset: int, alloc: int) -> str:
    end = min(len(data), offset + alloc)
    chunk = data[offset:end]
    if len(chunk) % 2:
        chunk = chunk[:-1]
    return chunk.decode("utf-16-le", errors="replace")


def is_fragment_like(src: str) -> bool:
    if not src:
        return True
    if src[0].islower() or src[0] == " ":
        return True
    if src[-1].isalpha() and src[-1].islower():
        return True
    return False


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="QA checker for patched catalog bundle")
    ap.add_argument("--catalog-csv", required=True)
    ap.add_argument("--src-root", default="/mnt/f/games/nobu16")
    ap.add_argument(
        "--patched-root",
        required=True,
        help="Root containing patched tree, e.g. releases/<name> or patches/master_<tag>",
    )
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--out-md", required=True)
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    src_root = Path(args.src_root).resolve()
    patched_root = Path(args.patched_root).resolve()

    with Path(args.catalog_csv).open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    issues: list[dict[str, str]] = []
    checked = 0
    by_kind = Counter()
    fragment_like = 0
    untranslated_ascii = 0

    file_cache_src: dict[Path, bytes] = {}
    file_cache_patched: dict[Path, bytes] = {}

    for row in rows:
        ko = (row.get("translated_ko") or "").strip()
        if not ko:
            continue
        checked += 1

        src_file = Path(row["file"]).resolve()
        if not src_file.is_relative_to(src_root):
            issues.append(
                {
                    "severity": "error",
                    "kind": "path_outside_src_root",
                    "id": row.get("id", ""),
                    "file": str(src_file),
                    "offset_hex": row.get("offset_hex", ""),
                    "detail": "catalog file is outside src-root",
                }
            )
            by_kind["path_outside_src_root"] += 1
            continue

        rel = src_file.relative_to(src_root)
        patched_file = patched_root / rel
        if not patched_file.exists():
            issues.append(
                {
                    "severity": "error",
                    "kind": "missing_patched_file",
                    "id": row.get("id", ""),
                    "file": str(patched_file),
                    "offset_hex": row.get("offset_hex", ""),
                    "detail": "patched file not found",
                }
            )
            by_kind["missing_patched_file"] += 1
            continue

        if src_file not in file_cache_src:
            file_cache_src[src_file] = src_file.read_bytes()
        if patched_file not in file_cache_patched:
            file_cache_patched[patched_file] = patched_file.read_bytes()

        src_data = file_cache_src[src_file]
        patch_data = file_cache_patched[patched_file]
        if len(src_data) != len(patch_data):
            issues.append(
                {
                    "severity": "error",
                    "kind": "size_mismatch",
                    "id": row.get("id", ""),
                    "file": str(patched_file),
                    "offset_hex": row.get("offset_hex", ""),
                    "detail": f"src={len(src_data)} patched={len(patch_data)}",
                }
            )
            by_kind["size_mismatch"] += 1
            continue

        off = int(row["offset"])
        alloc = int(row["allocated_bytes"])
        enc = row["encoding"]
        src_en = row.get("original_en", "")
        ko_full = row.get("translated_ko", "")

        enc_bytes = encode_text(ko_full, enc)
        if len(enc_bytes) > alloc:
            issues.append(
                {
                    "severity": "error",
                    "kind": "encoded_overflow",
                    "id": row.get("id", ""),
                    "file": str(patched_file),
                    "offset_hex": row.get("offset_hex", ""),
                    "detail": f"encoded={len(enc_bytes)} alloc={alloc}",
                }
            )
            by_kind["encoded_overflow"] += 1
            continue

        src_chunk = src_data[off : off + alloc]
        patched_chunk = patch_data[off : off + alloc]
        if src_chunk == patched_chunk and ko_full.strip() != src_en.strip():
            issues.append(
                {
                    "severity": "warning",
                    "kind": "unchanged_chunk",
                    "id": row.get("id", ""),
                    "file": str(patched_file),
                    "offset_hex": row.get("offset_hex", ""),
                    "detail": "chunk is unchanged after patch",
                }
            )
            by_kind["unchanged_chunk"] += 1

        if enc == "utf16le_run":
            if not patched_chunk.startswith(enc_bytes):
                issues.append(
                    {
                        "severity": "error",
                        "kind": "run_prefix_mismatch",
                        "id": row.get("id", ""),
                        "file": str(patched_file),
                        "offset_hex": row.get("offset_hex", ""),
                        "detail": "patched run does not start with encoded ko text",
                    }
                )
                by_kind["run_prefix_mismatch"] += 1
            decoded = decode_run(patch_data, off, alloc).rstrip(" ")
            if decoded.rstrip() != ko_full.rstrip():
                issues.append(
                    {
                        "severity": "warning",
                        "kind": "decoded_ko_mismatch",
                        "id": row.get("id", ""),
                        "file": str(patched_file),
                        "offset_hex": row.get("offset_hex", ""),
                        "detail": f"decoded={decoded!r} csv={ko_full!r}",
                    }
                )
                by_kind["decoded_ko_mismatch"] += 1
        else:
            decoded = decode_terminated(patch_data, off, alloc, enc)
            if decoded.rstrip() != ko_full.rstrip():
                issues.append(
                    {
                        "severity": "warning",
                        "kind": "decoded_ko_mismatch",
                        "id": row.get("id", ""),
                        "file": str(patched_file),
                        "offset_hex": row.get("offset_hex", ""),
                        "detail": f"decoded={decoded!r} csv={ko_full!r}",
                    }
                )
                by_kind["decoded_ko_mismatch"] += 1

        if is_fragment_like(src_en):
            fragment_like += 1
        if ko_full.isascii():
            untranslated_ascii += 1

    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        fields = ["severity", "kind", "id", "file", "offset_hex", "detail"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(issues)

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    sev = Counter(i["severity"] for i in issues)
    lines: list[str] = []
    lines.append(f"# Patch QA Report ({date.today().isoformat()})")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- checked_rows: `{checked}`")
    lines.append(f"- issues_total: `{len(issues)}`")
    lines.append(f"- errors: `{sev.get('error', 0)}`")
    lines.append(f"- warnings: `{sev.get('warning', 0)}`")
    lines.append(f"- fragment_like_source_rows: `{fragment_like}`")
    lines.append(f"- ascii_only_translations: `{untranslated_ascii}`")
    lines.append("")
    lines.append("## Issue Kinds")
    lines.append("")
    if by_kind:
        for k, v in by_kind.most_common():
            lines.append(f"- `{k}`: {v}")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    lines.append(f"- issues_csv: `{out_csv}`")
    lines.append(f"- report_md: `{out_md}`")
    lines.append("")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"checked={checked}")
    print(f"issues={len(issues)}")
    print(f"errors={sev.get('error', 0)}")
    print(f"warnings={sev.get('warning', 0)}")
    print(f"fragment_like={fragment_like}")
    print(f"ascii_only_translations={untranslated_ascii}")
    print(f"out_csv={out_csv}")
    print(f"out_md={out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
