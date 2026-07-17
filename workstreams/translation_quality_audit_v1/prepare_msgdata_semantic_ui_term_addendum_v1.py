#!/usr/bin/env python3
"""Build three PC-only, source-gated visible ``msgdata`` term repairs.

This narrow review set is limited to short live labels with direct PC
JP/EN/SC/TC evidence and ordinary Korean UI anchors.  It excludes personal
names and leaves all game resources untouched.  Switch Korean and historic
Korean backups are never read.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import prepare_msgdata_quality_reading_addendum_v1 as reading
from prepare_msgdata_quality_semantic_findings_v1 import (
    Candidate,
    TMP_ROOT,
    atomic_write,
    safe_under,
)


DEFAULT_OUTPUT = (
    TMP_ROOT
    / "translation_quality_audit_v1"
    / "semantic"
    / "msgdata_semantic_ui_term_addendum.v1.jsonl"
)


CANDIDATES: dict[int, Candidate] = {
    24397: Candidate(
        "\u9ad8\u5bb6",
        "\ub2e4\uce74\uc774\uc5d0",
        "\uba85\ubb38\uac00",
        "visible_category_semantic_mapping",
        "This visible social-category slot is between Samurai and Priest. PC EN says Aristocrat and PC SC/TC say a distinguished family; live Korean cognate trait labels at 21258 and 26558 use the Korean semantic term rather than the unrelated personal-name reading Takaie.",
        (21258, 26558),
    ),
    24443: Candidate(
        "\u4f5c\u4e8b",
        "\uc791\uc0ac",
        "\uac74\ucd95",
        "visible_trait_semantic_mapping",
        "The exact same source label and adjacent UI group are already rendered as \u2018\uac74\ucd95\u2019 in live PC msgui 1824. PC EN says Civil Construction and PC SC/TC say construction work. The bare label therefore follows its direct UI counterpart; the distinct compound \u4f5c\u4e8b\u5949\u884c remains the separate title \u2018\uacf5\uc0ac \ubd09\ud589\u2019.",
        (26552,),
    ),
    25501: Candidate(
        "\u30c7\u30e1\u30ea\u30c3\u30c8\u6253\u6d88",
        "\ub370\uba54\ub9ac\ud2b8\uc6b0\uce58\ucf00\uc2dc",
        "\ubd88\uc774\uc775 \ubb34\ud6a8",
        "visible_effect_semantic_mapping",
        "PC EN says Negates demerits and PC SC/TC describe removing a weakness. Nearby live Korean effect labels consistently use the Korean nullification form \u2018\ubb34\ud6a8\u2019; the current Japanese phonetic rendering is not a Korean UI term.",
        (25494, 25505, 25510),
    ),
}


UI_SLOT_CONTEXT: dict[int, dict[str, object]] = {
    24397: {
        "slot_kind": "visible_social_category_label",
        "adjacent_category_ids": [24396, 24398, 24399, 24400, 24401, 24402, 24403, 24404],
        "semantic_anchor_ids": [21258, 26558],
        "personal_name_false_friend_id": 7633,
    },
    24443: {
        "slot_kind": "visible_trait_label",
        "adjacent_trait_ids": [24442, 24444, 24445],
        "same_source_msgui_anchor_id": 1824,
        "same_term_compound_anchor_id": 26552,
    },
    25501: {
        "slot_kind": "visible_effect_label",
        "adjacent_effect_ids": [25494, 25503, 25505, 25510, 25513],
        "korean_nullification_anchor_ids": [25494, 25505, 25510],
    },
}


def existing_candidate_ids() -> set[int]:
    """Return IDs from all current msgdata candidate files except this output."""
    result: set[int] = set()
    audit_root = TMP_ROOT / "translation_quality_audit_v1"
    for directory in (audit_root / "semantic", audit_root / "proposals"):
        for path in directory.glob("msgdata*.jsonl"):
            if path.resolve() == DEFAULT_OUTPUT.resolve():
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line:
                    continue
                identifier = json.loads(line).get("id")
                if isinstance(identifier, int):
                    result.add(identifier)
    return result


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    existing = existing_candidate_ids()
    overlap = sorted(existing.intersection(CANDIDATES))
    if overlap:
        raise ValueError(f"semantic UI-term addendum overlaps existing msgdata candidates: {overlap}")

    # Reuse the established source/current hash, PC-reference, formatting, and
    # Korean-integrity validator.  The complete candidate universe was checked
    # above because this new review file is independent of earlier addenda.
    original_candidates = reading.CANDIDATES
    try:
        reading.CANDIDATES = CANDIDATES
        rows, summary = reading.build_rows()
    finally:
        reading.CANDIDATES = original_candidates

    for row in rows:
        identifier = row["id"]
        row["ui_slot_context"] = UI_SLOT_CONTEXT[identifier]
        row["candidate_scope"] = "visible_main_ui_label_or_effect_only"
        row["switch_korean_translation_used"] = False
        row["historic_korean_backup_used"] = False
        row["game_files_written"] = False
    summary["existing_all_msgdata_candidate_id_count"] = len(existing)
    summary["overlap_with_existing_candidate_ids"] = []
    return rows, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true", help="validate only; write no files")
    parser.add_argument("--write", action="store_true", help="write the ASCII JSONL below tmp")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.validate and args.write:
        parser.error("choose either --validate or --write")
    rows, summary = build_rows()
    if args.validate:
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    if args.write:
        output = safe_under(args.output, TMP_ROOT)
        payload = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows)
        if any(byte > 0x7F for byte in payload.encode("utf-8")):
            raise ValueError("JSONL payload is not ASCII-only")
        atomic_write(output, payload)
        print(json.dumps({**summary, "output": str(output), "output_bytes": output.stat().st_size}, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    for row in rows:
        print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
