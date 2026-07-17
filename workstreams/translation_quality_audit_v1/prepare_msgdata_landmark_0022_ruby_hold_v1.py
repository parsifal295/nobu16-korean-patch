#!/usr/bin/env python3
"""Document why msgdata ID 26433 remains a HOLD in the landmark audit.

The landmark name at 26383 is already covered by a visible-name candidate.
ID 26433 is its paired Japanese-reading slot, not a second display-name slot.
This read-only report records the PC-only structural evidence so a later audit
does not accidentally replace one auxiliary ruby/search value in isolation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from prepare_msgdata_quality_semantic_findings_v1 import (
    LIVE_KO,
    PRISTINE_JP,
    REFERENCE_FILES,
    TMP_ROOT,
    atomic_write,
    load_texts,
    safe_under,
    sha256_file,
    text_hash,
)


VISIBLE_NAME_ID = 26383
RUBY_ID = 26433
PRIMARY_EFFECT_ID = 26483
SECONDARY_EFFECT_ID = 26533
BLOCK_SIZE = 50
VISIBLE_NAME_BASE = 26361
RUBY_BASE = VISIBLE_NAME_BASE + BLOCK_SIZE
PRIMARY_EFFECT_BASE = RUBY_BASE + BLOCK_SIZE
SECONDARY_EFFECT_BASE = PRIMARY_EFFECT_BASE + BLOCK_SIZE

EXISTING_VISIBLE_CANDIDATE = (
    TMP_ROOT
    / "translation_quality_audit_v1"
    / "semantic"
    / "msgdata_quality_findings.v1.jsonl"
)
DEFAULT_OUTPUT = (
    TMP_ROOT
    / "translation_quality_audit_v1"
    / "semantic"
    / "msgdata_landmark_0022_ruby_hold.v1.json"
)


def read_visible_candidate() -> dict[str, object]:
    if not EXISTING_VISIBLE_CANDIDATE.is_file():
        raise ValueError(f"visible-name candidate is absent: {EXISTING_VISIBLE_CANDIDATE}")
    matches: list[dict[str, object]] = []
    for number, line in enumerate(
        EXISTING_VISIBLE_CANDIDATE.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line:
            continue
        row = json.loads(line)
        if row.get("id") == VISIBLE_NAME_ID:
            matches.append(row)
    if len(matches) != 1:
        raise ValueError(f"expected one visible-name candidate for {VISIBLE_NAME_ID}, got {len(matches)}")
    row = matches[0]
    if row.get("ko") != "LANDMARK_NAME_0022":
        raise ValueError("visible-name candidate current-KO gate changed")
    if row.get("proposed_ko") != "\uac00\uba54\ub2e4 \ud558\uce58\ub9cc\uad81":
        raise ValueError("visible-name candidate proposal changed")
    return row


def build_report() -> dict[str, object]:
    jp = load_texts(PRISTINE_JP)
    ko = load_texts(LIVE_KO)
    references = {language: load_texts(path) for language, path in REFERENCE_FILES.items()}
    if len(jp) != len(ko) or any(len(table) != len(jp) for table in references.values()):
        raise ValueError("PC msgdata table cardinalities differ")
    if SECONDARY_EFFECT_BASE + BLOCK_SIZE > len(jp):
        raise ValueError("landmark block extends outside msgdata")

    expected = {
        VISIBLE_NAME_ID: ("\u4e80\u7530\u516b\u5e61\u5bae", "LANDMARK_NAME_0022"),
        RUBY_ID: ("\u304b\u3081\u3060\u306f\u3061\u307e\u3093\u3050\u3046", "LANDMARK_NAME_0022"),
        PRIMARY_EFFECT_ID: ("\u5a01\u98a8\u306e\u52b9\u679c\u7bc4\u56f2\u304c\u62e1\u5927", "LANDMARK_NAME_0022"),
        SECONDARY_EFFECT_ID: ("\u5a01\u98a8\u306e\u52b9\u679c\u7bc4\u56f2\u304c\u62e1\u5927", "LANDMARKEFFECT_DESC_0022"),
    }
    for identifier, (source, current) in expected.items():
        if jp[identifier] != source:
            raise ValueError(f"{identifier}: pristine JP source gate failed")
        if ko[identifier] != current:
            raise ValueError(f"{identifier}: current Steam Korean gate failed")

    landmark_index = VISIBLE_NAME_ID - VISIBLE_NAME_BASE
    if landmark_index != RUBY_ID - RUBY_BASE:
        raise ValueError("visible-name and ruby slot index differ")
    if landmark_index != PRIMARY_EFFECT_ID - PRIMARY_EFFECT_BASE:
        raise ValueError("visible-name and primary-effect slot index differ")
    if landmark_index != SECONDARY_EFFECT_ID - SECONDARY_EFFECT_BASE:
        raise ValueError("visible-name and secondary-effect slot index differ")

    ruby_rows = list(range(RUBY_BASE, RUBY_BASE + BLOCK_SIZE))
    non_identifier_ruby = [
        identifier
        for identifier in ruby_rows
        if not ko[identifier].startswith("LANDMARK_NAME_")
    ]
    if not non_identifier_ruby:
        raise ValueError("no populated peer ruby rows to establish the slot pattern")
    if any(any("\uac00" <= char <= "\ud7a3" for char in ko[identifier]) for identifier in ruby_rows):
        raise ValueError("ruby peer pattern changed: expected no Hangul in the whole reading block")
    if not all(any("\u3040" <= char <= "\u30ff" for char in jp[identifier]) for identifier in non_identifier_ruby):
        raise ValueError("populated peer ruby sources no longer contain Japanese readings")

    visible_candidate = read_visible_candidate()
    file_hashes = {
        "live_steam_ko": sha256_file(LIVE_KO),
        "pristine_pc_jp": sha256_file(PRISTINE_JP),
        **{language.lower(): sha256_file(path) for language, path in REFERENCE_FILES.items()},
    }
    paired = {}
    for label, identifier in (
        ("visible_name", VISIBLE_NAME_ID),
        ("ruby_reading", RUBY_ID),
        ("primary_effect", PRIMARY_EFFECT_ID),
        ("secondary_effect", SECONDARY_EFFECT_ID),
    ):
        paired[label] = {
            "id": identifier,
            "jp": jp[identifier],
            "ko": ko[identifier],
            "jp_utf16le_sha256": text_hash(jp[identifier]),
            "ko_utf16le_sha256": text_hash(ko[identifier]),
            "pc_target_contexts": {
                "en": references["EN"][identifier],
                "sc": references["SC"][identifier],
                "tc": references["TC"][identifier],
            },
        }

    return {
        "schema": "nobu16.kr.translation-quality-hold.v1",
        "resource": "MSG_PK/JP/msgdata.bin",
        "disposition": "hold",
        "hold_id": RUBY_ID,
        "reason": (
            "ID 26433 is the +50 paired Japanese-reading/ruby slot for the visible "
            "landmark name at ID 26383. The 50-row ruby block has no Hangul in the "
            "current Korean resource; its populated peer values are auxiliary "
            "romanized readings. Replace the visible name only, unless a later "
            "runtime check establishes that this auxiliary field is rendered to users."
        ),
        "structural_layout": {
            "visible_name_block": [VISIBLE_NAME_BASE, VISIBLE_NAME_BASE + BLOCK_SIZE - 1],
            "ruby_reading_block": [RUBY_BASE, RUBY_BASE + BLOCK_SIZE - 1],
            "primary_effect_block": [PRIMARY_EFFECT_BASE, PRIMARY_EFFECT_BASE + BLOCK_SIZE - 1],
            "secondary_effect_block": [SECONDARY_EFFECT_BASE, SECONDARY_EFFECT_BASE + BLOCK_SIZE - 1],
            "paired_landmark_index": landmark_index,
            "ruby_peer_row_count": len(ruby_rows),
            "ruby_peer_hangul_count": 0,
            "ruby_peer_populated_nonidentifier_count": len(non_identifier_ruby),
        },
        "paired_rows": paired,
        "covered_visible_name_candidate": {
            "id": VISIBLE_NAME_ID,
            "current_ko": visible_candidate["ko"],
            "proposed_ko": visible_candidate["proposed_ko"],
            "current_hash": visible_candidate["current_hash"],
            "candidate_file": str(EXISTING_VISIBLE_CANDIDATE),
        },
        "already_prepared_effect_candidate_ids": [PRIMARY_EFFECT_ID, SECONDARY_EFFECT_ID],
        "file_sha256": file_hashes,
        "source_gates": "all_exact_match",
        "current_ko_gates": "all_exact_match",
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true", help="validate only; write no files")
    parser.add_argument("--write", action="store_true", help="write the hold report below tmp")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.validate and args.write:
        parser.error("choose either --validate or --write")

    report = build_report()
    if args.validate:
        print(json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    if args.write:
        output = safe_under(args.output, TMP_ROOT)
        payload = json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
        if any(byte > 0x7F for byte in payload.encode("utf-8")):
            raise ValueError("hold-report payload is not ASCII-only")
        atomic_write(output, payload)
        print(json.dumps({"output": str(output), "output_bytes": output.stat().st_size}, ensure_ascii=True))
        return 0
    print(json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
