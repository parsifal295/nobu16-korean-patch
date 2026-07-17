#!/usr/bin/env python3
"""Prepare one PC-only base-event clarity correction for ``討死``.

The Korean hanja reading ``토사`` is technically intelligible but is not the
project's ordinary rendering for death in battle.  This row uses ``전사``,
which is also directly corroborated by the PC SC/TC event text.  It preserves
the exact one-line layout and every runtime/format field.

Only pristine PC Japanese and PC SC/TC/current Korean tables are read.  The
generator has no Switch path and writes just a private JSONL candidate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import prepare_haishin_false_friend_addendum_v1 as pc


OUTPUT = pc.SEMANTIC / "ev_strdata_battle_death_clarity_addendum.v1.jsonl"
ENTRY_ID = 13582
SOURCE_TERM = "討死"
CURRENT_TERM = "토사"
PROPOSED_TERM = "전사"


def build() -> tuple[list[dict[str, object]], dict[str, object]]:
    contexts, context_hashes = pc.load_resource_tables("ev_strdata")
    korean, korean_hash = pc.load_live_korean("ev_strdata")
    key = str(ENTRY_ID)
    if key not in korean or any(key not in table for table in contexts.values()):
        raise ValueError("base event coordinate is absent from a required PC table")
    source = contexts["JP"][key]
    current = korean[key]
    if SOURCE_TERM not in source or CURRENT_TERM not in current or current.count(CURRENT_TERM) != 1:
        raise ValueError("PC source/current term predicate differs")
    if "阵亡" not in contexts["SC"][key] or "陣亡" not in contexts["TC"][key]:
        raise ValueError("PC Chinese battle-death corroboration differs")
    proposed = current.replace(CURRENT_TERM, PROPOSED_TERM)
    if pc.profile(current) != pc.profile(proposed):
        raise ValueError("protected text format differs")
    if pc.visible_line_lengths(current) != pc.visible_line_lengths(proposed):
        raise ValueError("manual event layout length differs")
    if pc.CJK_OR_KANA_RE.search(proposed):
        raise ValueError("candidate retains CJK/Kana")
    row: dict[str, object] = {
        "allowed_format_delta": [],
        "confidence": "high",
        "current_hash": pc.text_hash(current),
        "format_validation": {
            "all_nontext_format_fields": "match",
            "candidate_visible_line_lengths": pc.visible_line_lengths(proposed),
            "current_visible_line_lengths": pc.visible_line_lengths(current),
            "manual_line_count_matches_current": True,
        },
        "id": ENTRY_ID,
        "issue_type": "battle_death_hanja_reading_clarity",
        "jp_source_hash": pc.text_hash(source),
        "ko": current,
        "pc_semantic_evidence": {
            "jp_term": SOURCE_TERM,
            "pc_sc_term": "阵亡",
            "pc_tc_term": "陣亡",
        },
        "proposed_ko": proposed,
        "rationale": "討死 means death in battle. 전사 is the established Korean rendering elsewhere in the PC text and is clearer than the isolated direct hanja reading 토사.",
        "reference_basis": ["pristine_pc_jp", "pc_sc", "pc_tc"],
        "reference_file_sha256": context_hashes,
        "resource": "ev_strdata",
        "source_file_sha256": context_hashes["JP"],
        "steam_ko_file_sha256": korean_hash,
        "switch_korean_translation_used": False,
    }
    return [row], {
        "candidate_count": 1,
        "candidate_id": ENTRY_ID,
        "game_files_written": False,
        "output": str(OUTPUT),
        "switch_korean_translation_used": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rows, summary = build()
    if args.write:
        payload = "".join(json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)
        pc.atomic_write(OUTPUT, payload)
        summary["output_sha256"] = pc.sha256_file(OUTPUT)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
