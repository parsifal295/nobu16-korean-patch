#!/usr/bin/env python3
"""Read-only source-led cross-check for five msgbre translation risk mappings.

This verifies only the coordinate where the pristine PC Japanese source has a
listed expression and the live Steam Korean target has its corresponding risk
word.  Existing msgbre candidate IDs are loaded from the prior review JSONL so
that already-covered coordinates are not reviewed or added again.  The helper
does not read Switch Korean or historic Korean text and never writes a file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
)
LIVE = STEAM / "MSG_PK"
EXISTING = REPO / "tmp" / "translation_quality_audit_v1" / "semantic" / "msgbre_findings.v1.jsonl"

sys.path.insert(0, str(REPO / "tools"))
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


# The last mapping remains review-only: 本領 commonly means a hereditary
# holding/territory, so its Korean rendering must never be auto-replaced.
MAPPINGS = (
    ("utare_tobeol", "討たれ", "토벌"),
    ("uchitoru_tobeol", "討ち取", "토벌"),
    ("rakujou_nakseong", "落城", "낙성"),
    ("baishin_baesin", "陪臣", "배신"),
    ("honryou_bonryeong", "本領", "본령"),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load(path: Path) -> list[str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def existing_candidate_ids() -> set[int]:
    if not EXISTING.is_file():
        raise SystemExit(f"existing candidate file is absent: {EXISTING}")
    identifiers: set[int] = set()
    for number, line in enumerate(EXISTING.read_text(encoding="ascii").splitlines(), start=1):
        if not line:
            continue
        row = json.loads(line)
        identifier = row.get("id")
        if not isinstance(identifier, int):
            raise SystemExit(f"existing candidate row {number}: missing integer id")
        if identifier in identifiers:
            raise SystemExit(f"existing candidate row {number}: duplicate id {identifier}")
        identifiers.add(identifier)
    return identifiers


def context_window(text: str, marker: str, radius: int = 110) -> str:
    """Return enough surrounding context for review without dumping biographies."""
    position = text.find(marker)
    if position < 0:
        return text[: radius * 2]
    start = max(0, position - radius)
    end = min(len(text), position + len(marker) + radius)
    prefix = "..." if start else ""
    suffix = "..." if end < len(text) else ""
    return prefix + text[start:end] + suffix


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", choices=[item[0] for item in MAPPINGS])
    parser.add_argument("--only-missing", action="store_true")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    if args.offset < 0 or args.limit is not None and args.limit < 0:
        raise SystemExit("offset and limit must be non-negative")

    jp = load(PRISTINE / "JP" / "msgbre.bin")
    ko = load(LIVE / "JP" / "msgbre.bin")
    en = load(LIVE / "EN" / "msgbre.bin")
    sc = load(LIVE / "SC" / "msgbre.bin")
    tc = load(LIVE / "TC" / "msgbre.bin")
    if not (len(jp) == len(ko) == len(en) == len(sc) == len(tc)):
        raise SystemExit("msgbre table count mismatch across PC resources")
    candidates = existing_candidate_ids()

    by_label: dict[str, list[int]] = {}
    label_metadata: dict[str, tuple[str, str]] = {}
    for label, jp_term, ko_term in MAPPINGS:
        identifiers = [
            identifier
            for identifier, (jp_text, ko_text) in enumerate(zip(jp, ko))
            if jp_term in jp_text and ko_term in ko_text
        ]
        by_label[label] = identifiers
        label_metadata[label] = (jp_term, ko_term)

    summary = {
        "resource": "MSG_PK/JP/msgbre.bin",
        "coordinate_count": len(jp),
        "pristine_jp_pc_sha256": sha256_file(PRISTINE / "JP" / "msgbre.bin"),
        "live_steam_ko_sha256": sha256_file(LIVE / "JP" / "msgbre.bin"),
        "existing_candidate_id_count": len(candidates),
        "mappings": {
            label: {
                "jp_term": jp_term,
                "ko_risk_term": ko_term,
                "source_led_risk_count": len(by_label[label]),
                "already_candidate_count": sum(identifier in candidates for identifier in by_label[label]),
                "missing_candidate_ids": [identifier for identifier in by_label[label] if identifier not in candidates],
            }
            for label, (jp_term, ko_term) in label_metadata.items()
        },
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
    }
    print("@@SUMMARY@@" + json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    if args.summary_only:
        return 0

    labels = [args.label] if args.label else [item[0] for item in MAPPINGS]
    output: list[tuple[str, int]] = []
    for label in labels:
        for identifier in by_label[label]:
            if not args.only_missing or identifier not in candidates:
                output.append((label, identifier))
    output = output[args.offset : None if args.limit is None else args.offset + args.limit]
    for label, identifier in output:
        jp_term, ko_term = label_metadata[label]
        if args.compact:
            context = {
                "jp_context": context_window(jp[identifier], jp_term),
                "ko_context": context_window(ko[identifier], ko_term),
            }
        else:
            context = {
                "jp": jp[identifier],
                "ko": ko[identifier],
                "en": en[identifier],
                "sc": sc[identifier],
                "tc": tc[identifier],
            }
        print(
            "@@ROW@@"
            + json.dumps(
                {
                    "label": label,
                    "id": identifier,
                    "jp_term": jp_term,
                    "ko_risk_term": ko_term,
                    "already_candidate": identifier in candidates,
                    **context,
                },
                ensure_ascii=True,
                separators=(",", ":"),
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
