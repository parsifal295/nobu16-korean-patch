#!/usr/bin/env python3
"""Read-only accounting helper for CJK/Kana residuals in live strdata KO.

The scanner reads current Steam PC KO plus coordinate-matched pristine PC JP
and current PC SC/TC only for review context.  Existing direct and semantic
proposal IDs are loaded solely to prevent duplicate work.  It never reads
Switch Korean/historic Korean text and never writes a file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_JP = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG"
    / "JP"
    / "strdata.bin"
)
LIVE_ROOT = STEAM / "MSG"
DIRECT_PROPOSALS = REPO / "tmp" / "translation_quality_audit_v1" / "proposals" / "strdata_ko.jsonl"
SEMANTIC_PROPOSALS = REPO / "tmp" / "translation_quality_audit_v1" / "semantic" / "strdata_quality_findings.v1.jsonl"

sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "workstreams" / "strdata"))
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata  # noqa: E402


KANA_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f]")
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load(path: Path) -> dict[tuple[int, int], str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return coordinate_texts(parse_raw_strdata(raw))


def jsonl_coordinates(path: Path) -> set[tuple[int, int]]:
    if not path.is_file():
        return set()
    values: set[tuple[int, int]] = set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        row = json.loads(line)
        try:
            coordinate = (int(row["block"]), int(row["id"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise SystemExit(f"{path}:{number}: missing strdata coordinate") from exc
        if coordinate in values:
            raise SystemExit(f"{path}:{number}: duplicate coordinate {coordinate}")
        values.add(coordinate)
    return values


def window(text: str, positions: list[int], radius: int = 110) -> str:
    if not positions:
        return text
    start = max(0, positions[0] - radius)
    end = min(len(text), positions[-1] + radius + 1)
    return ("..." if start else "") + text[start:end] + ("..." if end < len(text) else "")


def residual_info(text: str) -> tuple[list[str], list[str], list[int]]:
    han = HAN_RE.findall(text)
    kana = KANA_RE.findall(text)
    positions = [
        index
        for index, character in enumerate(text)
        if HAN_RE.fullmatch(character) or KANA_RE.fullmatch(character)
    ]
    return han, kana, positions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--only-uncovered", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    if args.offset < 0 or args.limit is not None and args.limit < 0:
        raise SystemExit("offset and limit must be non-negative")

    jp = load(PRISTINE_JP)
    ko = load(LIVE_ROOT / "JP" / "strdata.bin")
    sc = load(LIVE_ROOT / "SC" / "strdata.bin")
    tc = load(LIVE_ROOT / "TC" / "strdata.bin")
    if not (set(jp) == set(ko) == set(sc) == set(tc)):
        raise SystemExit("strdata coordinate mismatch across PC resources")
    direct = jsonl_coordinates(DIRECT_PROPOSALS)
    semantic = jsonl_coordinates(SEMANTIC_PROPOSALS)

    rows: list[dict[str, object]] = []
    all_han: Counter[str] = Counter()
    all_kana: Counter[str] = Counter()
    for coordinate in sorted(ko):
        han, kana, positions = residual_info(ko[coordinate])
        if not (han or kana):
            continue
        all_han.update(han)
        all_kana.update(kana)
        covered_by = []
        if coordinate in direct:
            covered_by.append("direct_proposal")
        if coordinate in semantic:
            covered_by.append("semantic_proposal")
        rows.append(
            {
                "block": coordinate[0],
                "id": coordinate[1],
                "han_characters": han,
                "kana_characters": kana,
                "residual_character_count": len(han) + len(kana),
                "covered_by_existing_proposal": covered_by,
                "positions": positions,
            }
        )

    summary = {
        "coordinate_count": len(ko),
        "residual_coordinate_count": len(rows),
        # The original inventory's 45/6 values count flagged coordinates, not
        # individual glyphs.  Keep both measures explicit but do not emit a
        # massive per-codepoint table in ordinary review output.
        "han_flag_coordinate_count": sum(bool(row["han_characters"]) for row in rows),
        "kana_flag_coordinate_count": sum(bool(row["kana_characters"]) for row in rows),
        "han_glyph_count": sum(all_han.values()),
        "kana_glyph_count": sum(all_kana.values()),
        "residual_glyph_count": sum(all_han.values()) + sum(all_kana.values()),
        "covered_coordinate_count": sum(bool(row["covered_by_existing_proposal"]) for row in rows),
        "uncovered_coordinate_count": sum(not row["covered_by_existing_proposal"] for row in rows),
        "pristine_jp_pc_sha256": sha256_file(PRISTINE_JP),
        "live_steam_ko_sha256": sha256_file(LIVE_ROOT / "JP" / "strdata.bin"),
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
    }
    print("@@SUMMARY@@" + json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    if args.summary_only:
        return 0
    output_rows = [
        row for row in rows if not args.only_uncovered or not row["covered_by_existing_proposal"]
    ]
    output_rows = output_rows[args.offset : None if args.limit is None else args.offset + args.limit]
    for row in output_rows:
        coordinate = (int(row["block"]), int(row["id"]))
        if args.compact:
            payload = {
                **row,
                "ko_context": window(ko[coordinate], list(row["positions"])),
                "jp_context": window(jp[coordinate], list(row["positions"])),
            }
        else:
            payload = {
                **row,
                "jp": jp[coordinate],
                "ko": ko[coordinate],
                "sc": sc[coordinate],
                "tc": tc[coordinate],
            }
        print("@@ROW@@" + json.dumps(payload, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
