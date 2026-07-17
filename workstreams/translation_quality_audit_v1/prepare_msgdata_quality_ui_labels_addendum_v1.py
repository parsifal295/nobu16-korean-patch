#!/usr/bin/env python3
"""Build source-gated corrections for repeated visible ``msgdata`` UI labels.

This is a narrow, read-only audit addendum.  It revisits label slots outside
the facility/trait blocks and only emits cases corroborated by the pristine PC
Japanese text and the installed PC EN/SC/TC resources.  It deliberately skips
personal names, place names, historical proper names, and prose/event text.
No game resource is written and no Switch or historic Korean resource is read.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import prepare_msgdata_quality_industry_addendum_v1 as industry
from prepare_msgdata_quality_semantic_findings_v1 import (
    Candidate,
    DIRECT_EXISTING,
    SEMANTIC_EXISTING,
    TMP_ROOT,
    atomic_write,
    read_existing_ids,
    safe_under,
)


SEMANTIC_ADDENDUM = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgdata_quality_semantic_addendum.v1.jsonl"
READING_ADDENDUM = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgdata_quality_reading_addendum.v1.jsonl"
TERMINOLOGY_ADDENDUM = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgdata_quality_terminology_addendum.v1.jsonl"
FACILITY_ADDENDUM = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgdata_quality_facility_addendum.v1.jsonl"
TRAIT_ADDENDUM = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgdata_quality_trait_semantic_addendum.v1.jsonl"
INDUSTRY_ADDENDUM = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgdata_quality_industry_addendum.v1.jsonl"
DEFAULT_OUTPUT = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgdata_quality_ui_labels_addendum.v1.jsonl"


# Entries are only visible labels: castle/map categories, battle-command
# labels, and achievement labels.  The nearby kana/ruby slots are intentionally
# excluded, even where their Korean text is the same Japanese pronunciation.
CANDIDATES: dict[int, Candidate] = {
    9937: Candidate(
        "\u9928",
        "\uc57c\uce74\ud0c0",
        "\uad00",
        "visible_japanese_reading",
        "\uc131 \uc720\ud615 \ud45c\uc2dc \u9928\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Palace\uc640 SC\u00b7TC\uc758 \u9928 \ud45c\uae30\uc5d0 \ub9de\ucd98 \ud55c\uad6d\uc5b4 \ud55c\uc790\uc74c \uad00\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
        (9939,),
    ),
    9938: Candidate(
        "\u5fa1\u6240",
        "\uace0\uc1fc",
        "\uc5b4\uc18c",
        "visible_japanese_reading",
        "\uc131 \uc720\ud615 \ud45c\uc2dc \u5fa1\u6240\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Palace\uc5d0 \ub9de\ucd98 \ud55c\uad6d\uc5b4 \uc5b4\uc18c\ub85c \uad50\uccb4\ud55c\ub2e4. \uc131\ud558 \uc2dc\uc124 \ud45c\uc2dc 24091\ubc88\uacfc \ub3d9\uc77c \uc6a9\uc5b4\ub85c \uc77c\uce58\uc2dc\ud0a8\ub2e4.",
        (24091,),
    ),
    9939: Candidate(
        "\u9928",
        "\uc57c\uce74\ud0c0",
        "\uad00",
        "visible_japanese_reading",
        "9937\ubc88\uacfc \ub3d9\uc77c\ud55c \uc131 \uc720\ud615 \ud45c\uc2dc \u9928\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 \ud55c\uad6d\uc5b4 \ud55c\uc790\uc74c \uad00\uc73c\ub85c \ud1b5\uc77c\ud55c\ub2e4.",
        (9937,),
    ),
    9940: Candidate(
        "\u5fa1\u574a",
        "\uc2a4\ub2d8",
        "\uc0ac\ucc30",
        "incorrect_semantic_mapping",
        "\uc131 \uc720\ud615 \ud45c\uc2dc \u5fa1\u574a\uc740 \uc2b9\ub824\uac00 \uc544\ub2cc \uc808\u00b7\uc0ac\ucc30\uc744 \ub73b\ud55c\ub2e4. PC EN Temple\uacfc \uc77c\ubcf8 \ubd88\uad50 \uc0ac\ucc30 \uc6a9\ub840\uc5d0 \ub9de\ucd98 \uc0ac\ucc30\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    15197: Candidate(
        "\u65e9\u99c6",
        "\ud558\uc57c\uac00\ucf00",
        "\uc9c8\uc8fc",
        "visible_japanese_reading",
        "\uc804\ud22c \uba85\ub839 \ud45c\uc2dc \u65e9\u99c6\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Speedy\uc640 SC\u00b7TC\uc758 \u98db\u99b3 \uc758\ubbf8\uc5d0 \ub9de\ucd98 \uc9c8\uc8fc\ub85c \uad50\uccb4\ud55c\ub2e4.",
        (15679,),
    ),
    15276: Candidate(
        "\u8d64\u5099\u3048",
        "\uc544\uce74\uc870\ub098\uc5d0",
        "\uc801\ube44",
        "visible_japanese_reading",
        "\uc804\ud22c \ud2b9\uc131 \ud45c\uc2dc \u8d64\u5099\u3048\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Red Cavalry\uc640 SC\u00b7TC\uc758 \u8d64\u5099 \uc758\ubbf8\uc5d0 \ub9de\ucd98 \uc801\ube44\ub85c \uad50\uccb4\ud55c\ub2e4. \ub3d9\uc77c \ud2b9\uc131\uba85 24478\u00b725502\ubc88\uacfc \ud1b5\uc77c\ud55c\ub2e4.",
        (24478, 24502),
    ),
    15289: Candidate(
        "\u6b66\u7530\u4e4b\u8d64\u5099",
        "\ub2e4\ucf00\ub2e4\uc758 \uc544\uce74\uc870\ub098\uc5d0",
        "\ub2e4\ucf00\ub2e4\uc758 \uc801\ube44",
        "visible_japanese_reading",
        "\uc804\ud22c \ud2b9\uc131 \ud45c\uc2dc \u6b66\u7530\u4e4b\u8d64\u5099\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c \uc77c\ubd80\ub97c, PC EN Red Cavalry Rider\uc640 SC\u00b7TC\uc758 \u6b66\u7530\u4e4b\u8d64\u5099\uc5d0 \ub9de\ucd98 \ub2e4\ucf00\ub2e4\uc758 \uc801\ube44\ub85c \uad50\uccb4\ud55c\ub2e4.",
        (15276,),
    ),
    15679: Candidate(
        "\u65e9\u99c6",
        "\ud558\uc57c\uac00\ucf00",
        "\uc9c8\uc8fc",
        "visible_japanese_reading",
        "15197\ubc88\uacfc \ub3d9\uc77c\ud55c \uc804\ud22c \uba85\ub839 \ud45c\uc2dc \u65e9\u99c6\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 \uc9c8\uc8fc\ub85c \ud1b5\uc77c\ud55c\ub2e4.",
        (15197,),
    ),
    15758: Candidate(
        "\u8d64\u5099",
        "\uc544\uce74\uc870\ub098\uc5d0",
        "\uc801\ube44",
        "visible_japanese_reading",
        "\uc804\ud22c \ud2b9\uc131 \ucd95\uc57d \ud45c\uc2dc \u8d64\u5099\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Red Cavalry\uc640 SC\u00b7TC\uc758 \u8d64\u5099\uc5d0 \ub9de\ucd98 \uc801\ube44\ub85c \uad50\uccb4\ud55c\ub2e4.",
        (15276,),
    ),
    15771: Candidate(
        "\u8d64\u5099",
        "\uc544\uce74\uc870\ub098\uc5d0",
        "\uc801\ube44",
        "visible_japanese_reading",
        "\uc804\ud22c \ud2b9\uc131 \ucd95\uc57d \ud45c\uc2dc \u8d64\u5099\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Red Cavalry Rider\uc640 SC\u00b7TC\uc758 \u8d64\u5099\uc5d0 \ub9de\ucd98 \uc801\ube44\ub85c \uad50\uccb4\ud55c\ub2e4.",
        (15289,),
    ),
    17142: Candidate(
        "\u5c71",
        "\uc57c\ub9c8",
        "\uc0b0",
        "visible_japanese_reading",
        "\ub9f5 \uc9c0\ud615 \ud45c\uc2dc \u5c71\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Mountains\uc640 SC\u00b7TC\uc758 \u5c71\u5730 \uc758\ubbf8\uc5d0 \ub9de\ucd98 \uc0b0\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
        (17155,),
    ),
    17143: Candidate(
        "\u68ee",
        "\ubaa8\ub9ac",
        "\uc232",
        "visible_japanese_reading",
        "\ub9f5 \uc9c0\ud615 \ud45c\uc2dc \u68ee\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Forest\uc640 SC\u00b7TC\uc758 \u68ee\u6797 \uc758\ubbf8\uc5d0 \ub9de\ucd98 \uc232\ub85c \uad50\uccb4\ud55c\ub2e4. \ub3d9\uc77c \uc9c0\ud615\uba85 20789\ubc88\uacfc \ud1b5\uc77c\ud55c\ub2e4.",
        (20789,),
    ),
    17154: Candidate(
        "\u68ee",
        "\ubaa8\ub9ac",
        "\uc232",
        "visible_japanese_reading",
        "17143\ubc88\uacfc \ub3d9\uc77c\ud55c \ub9f5 \uc9c0\ud615 \ud45c\uc2dc \u68ee\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 \uc232\ub85c \ud1b5\uc77c\ud55c\ub2e4.",
        (17143,),
    ),
    17155: Candidate(
        "\u5c71",
        "\uc57c\ub9c8",
        "\uc0b0",
        "visible_japanese_reading",
        "17142\ubc88\uacfc \ub3d9\uc77c\ud55c \ub9f5 \uc9c0\ud615 \ud45c\uc2dc \u5c71\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 \uc0b0\uc73c\ub85c \ud1b5\uc77c\ud55c\ub2e4.",
        (17142,),
    ),
    25722: Candidate(
        "\u6570\u5bc4\u8005",
        "\uc2a4\ud0a4\uc0e4",
        "\ud48d\ub958\uac1d",
        "visible_japanese_reading",
        "\uc5c5\uc801 \ud45c\uc2dc \u6570\u5bc4\u8005\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC SC\u00b7TC\uc758 \u98a8\u96c5\u4e4b\u58eb\uc640 \uc6d0\ubb38\uc758 \uc758\ubbf8\uc5d0 \ub9de\ucd98 \ud48d\ub958\uac1d\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
}


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    existing_sources = (
        DIRECT_EXISTING,
        SEMANTIC_EXISTING,
        SEMANTIC_ADDENDUM,
        READING_ADDENDUM,
        TERMINOLOGY_ADDENDUM,
        FACILITY_ADDENDUM,
        TRAIT_ADDENDUM,
        INDUSTRY_ADDENDUM,
    )
    existing_by_file = {path.name: read_existing_ids(path) for path in existing_sources}
    existing = set().union(*existing_by_file.values())
    overlap = sorted(existing.intersection(CANDIDATES))
    if overlap:
        raise ValueError(f"UI-label addendum overlaps existing msgdata candidates: {overlap}")

    # Reuse the preceding builder's complete validation: exact pristine/current
    # gates, input file hashes, token/escape/newline/whitespace preservation,
    # Hangul integrity, and ASCII-only JSONL serialization.
    original_candidates = industry.CANDIDATES
    try:
        industry.CANDIDATES = CANDIDATES
        rows, summary = industry.build_rows()
    finally:
        industry.CANDIDATES = original_candidates

    summary["existing_industry_addendum_id_count"] = len(
        existing_by_file[INDUSTRY_ADDENDUM.name]
    )
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
        payload = "".join(
            json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows
        )
        if any(byte > 0x7F for byte in payload.encode("utf-8")):
            raise ValueError("JSONL payload is not ASCII-only")
        atomic_write(output, payload)
        print(
            json.dumps(
                {**summary, "output": str(output), "output_bytes": output.stat().st_size},
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    for row in rows:
        print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
