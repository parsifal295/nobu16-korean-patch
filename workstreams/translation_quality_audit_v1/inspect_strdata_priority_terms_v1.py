#!/usr/bin/env python3
"""Read-only context extractor for the strdata semantic-quality audit.

The source of truth is exactly one pristine PC Japanese resource.  The live
Steam Korean string is the candidate target.  Current PC SC/TC strings are
shown only as coordinate-matched supplemental context.  No Switch Korean text
or historic Korean backup is read, and this helper never writes any file.
"""

from __future__ import annotations

import hashlib
import json
import sys
import argparse
from collections import defaultdict
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
LIVE_KO = STEAM / "MSG" / "JP" / "strdata.bin"
LIVE_SC = STEAM / "MSG" / "SC" / "strdata.bin"
LIVE_TC = STEAM / "MSG" / "TC" / "strdata.bin"

sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "workstreams" / "strdata"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata  # noqa: E402


# Each tuple is (stable label, pristine-JP source stem/term, Korean risk term).
# ``討ち取`` deliberately uses the source stem: it covers all 21 conjugated
# uses, whereas the dictionary form alone appears only 14 times.
PRIORITY_TERMS = (
    ("uchitoru_tobeol", "討ち取", "토벌"),
    ("utare_tobeol", "討たれ", "토벌"),
    ("rakujou_nakseong", "落城", "낙성"),
    ("baishin_baesin", "陪臣", "배신"),
    ("self_harm_jaehae", "自害", "자해"),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load(path: Path) -> dict[tuple[int, int], str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    archive = parse_raw_strdata(raw)
    return coordinate_texts(archive)


def coordinate_key(coordinate: tuple[int, int]) -> tuple[int, int]:
    return coordinate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", choices=[item[0] for item in PRIORITY_TERMS])
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--risk-only", action="store_true")
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()
    if args.offset < 0 or args.limit is not None and args.limit < 0:
        raise SystemExit("offset and limit must be non-negative")

    jp = load(PRISTINE_JP)
    ko = load(LIVE_KO)
    sc = load(LIVE_SC)
    tc = load(LIVE_TC)
    if not (set(jp) == set(ko) == set(sc) == set(tc)):
        raise SystemExit("strdata coordinate mismatch across current PC resources")

    per_coordinate: dict[tuple[int, int], list[dict[str, object]]] = defaultdict(list)
    term_summary: dict[str, dict[str, int]] = {}
    for label, jp_term, ko_term in PRIORITY_TERMS:
        jp_matches = {coordinate for coordinate, text in jp.items() if jp_term in text}
        ko_matches = {coordinate for coordinate in jp_matches if ko_term in ko[coordinate]}
        term_summary[label] = {
            "jp_term_match_count": len(jp_matches),
            "ko_risk_term_match_count_within_jp_context": len(ko_matches),
        }
        # Context review is source-led.  Do not sweep unrelated uses of a
        # Korean word such as lawful "bandit suppression" into this queue.
        for coordinate in jp_matches:
            per_coordinate[coordinate].append(
                {
                    "label": label,
                    "jp_term": jp_term,
                    "ko_risk_term": ko_term,
                    "jp_term_present": True,
                    "ko_risk_term_present": coordinate in ko_matches,
                }
            )

    provenance = {
        "pristine_jp_pc_sha256": sha256_file(PRISTINE_JP),
        "live_steam_ko_sha256": sha256_file(LIVE_KO),
        "live_pc_sc_sha256": sha256_file(LIVE_SC),
        "live_pc_tc_sha256": sha256_file(LIVE_TC),
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
        "coordinate_count": len(jp),
        "term_summary": term_summary,
    }
    print("@@SUMMARY@@" + json.dumps(provenance, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    if args.summary_only:
        return
    coordinates = sorted(per_coordinate, key=coordinate_key)
    if args.label is not None:
        coordinates = [
            coordinate
            for coordinate in coordinates
            if any(target["label"] == args.label for target in per_coordinate[coordinate])
        ]
    if args.risk_only:
        coordinates = [
            coordinate
            for coordinate in coordinates
            if any(
                target["ko_risk_term_present"]
                and (args.label is None or target["label"] == args.label)
                for target in per_coordinate[coordinate]
            )
        ]
    coordinates = coordinates[args.offset : None if args.limit is None else args.offset + args.limit]
    for coordinate in coordinates:
        print(
            "@@ROW@@"
            + json.dumps(
                {
                    "block": coordinate[0],
                    "id": coordinate[1],
                    "targets": per_coordinate[coordinate],
                    "jp": jp[coordinate],
                    "ko": ko[coordinate],
                    "sc": sc[coordinate],
                    "tc": tc[coordinate],
                },
                ensure_ascii=True,
                separators=(",", ":"),
            )
        )


if __name__ == "__main__":
    main()
