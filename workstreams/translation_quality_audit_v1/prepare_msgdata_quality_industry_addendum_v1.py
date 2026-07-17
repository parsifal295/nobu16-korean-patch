#!/usr/bin/env python3
"""Build source-gated corrections for three unambiguous resource/industry labels.

The entries are visible UI labels where the current Korean retained a Japanese
reading (including one unrelated place-name reading) despite unambiguous local
PC EN/SC/TC context.  No game resource is written and no Switch Korean source
is read.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import prepare_msgdata_quality_trait_semantic_addendum_v1 as trait
from prepare_msgdata_quality_semantic_findings_v1 import (
    Candidate,
    DIRECT_EXISTING,
    SEMANTIC_EXISTING,
    TMP_ROOT,
    atomic_write,
    read_existing_ids,
    safe_under,
)


TERRAIN_EXISTING = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgdata_quality_semantic_addendum.v1.jsonl"
READING_EXISTING = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgdata_quality_reading_addendum.v1.jsonl"
TERMINOLOGY_EXISTING = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgdata_quality_terminology_addendum.v1.jsonl"
FACILITY_EXISTING = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgdata_quality_facility_addendum.v1.jsonl"
TRAIT_EXISTING = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgdata_quality_trait_semantic_addendum.v1.jsonl"
DEFAULT_OUTPUT = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgdata_quality_industry_addendum.v1.jsonl"


CANDIDATES: dict[int, Candidate] = {
    17787: Candidate(
        "\u91d1\u5c71",
        "\uac00\ub098\uc57c\ub9c8",
        "\uae08\uad11",
        "semantic_mistranslation",
        "\uc790\uc6d0 \uc2dc\uc124\uba85 \u91d1\u5c71\uc5d0 \ubcc4\ub3c4\uc758 \uc9c0\uba85 \ub3c5\uc74c \uac00\ub098\uc57c\ub9c8\uac00 \ub4e4\uc5b4\uac14\ub2e4. PC EN Gold Mine\uc640 \uc9dd\uc744 \uc774\ub8e8\ub294 17788\ubc88 Silver Mine=\uc740\uad11\uc5d0 \ub9de\ucd98 \uae08\uad11\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
        (17788,),
    ),
    17789: Candidate(
        "\u99ac",
        "\uc6b0\ub9c8",
        "\ub9d0",
        "visible_japanese_reading",
        "\uc790\uc6d0 \ud56d\ubaa9\uba85 \u99ac\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Horse\uc5d0 \ub9de\ucd98 \ud55c\uad6d\uc5b4 \ub9d0\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    17800: Candidate(
        "\u5927\u935b\u51b6\u753a",
        "\uc624\uce74\uc9c0\ub9c8\uce58",
        "\ud070 \ub300\uc7a5\uac04",
        "visible_japanese_reading",
        "\uc0b0\uc5c5 \uc2dc\uc124\uba85 \u5927\u935b\u51b6\u753a\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Big Forge\uc640 \uae30\uc874 17799\ubc88 Forge=\ub300\uc7a5\uac04 \ub9c8\uc744\uc5d0 \ub9de\ucd98 \ud070 \ub300\uc7a5\uac04\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
        (17799,),
    ),
}


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    existing_sources = (
        DIRECT_EXISTING,
        SEMANTIC_EXISTING,
        TERRAIN_EXISTING,
        READING_EXISTING,
        TERMINOLOGY_EXISTING,
        FACILITY_EXISTING,
        TRAIT_EXISTING,
    )
    existing_by_file = {path.name: read_existing_ids(path) for path in existing_sources}
    existing = set().union(*existing_by_file.values())
    overlap = sorted(existing.intersection(CANDIDATES))
    if overlap:
        raise ValueError(f"industry addendum overlaps existing msgdata candidates: {overlap}")

    # Reuse the shared validator through the preceding addendum builder.  It
    # checks exact source/current text and hashes, runtime tokens, escape bytes,
    # newlines, and whitespace before any JSONL is written.
    original_candidates = trait.CANDIDATES
    try:
        trait.CANDIDATES = CANDIDATES
        rows, summary = trait.build_rows()
    finally:
        trait.CANDIDATES = original_candidates

    summary["existing_trait_addendum_id_count"] = len(existing_by_file[TRAIT_EXISTING.name])
    summary["overlap_with_existing_candidate_ids"] = []
    return rows, summary


def main() -> int:
    parser = argparse.ArgumentParser()
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
