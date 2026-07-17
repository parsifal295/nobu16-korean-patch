#!/usr/bin/env python3
"""Build source-gated, unambiguous trait-name quality corrections for ``msgdata``.

This narrow addendum covers only visible trait labels whose current Korean is
the Japanese reading and whose semantic Korean rendering is corroborated by
the local PC JP/EN/SC/TC resources.  Cultural proper names and terms with a
plausible but contestable localization are deliberately excluded.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import prepare_msgdata_quality_facility_addendum_v1 as facility
from prepare_msgdata_quality_semantic_findings_v1 import (
    Candidate,
    DIRECT_EXISTING,
    SEMANTIC_EXISTING,
    TMP_ROOT,
    atomic_write,
    read_existing_ids,
    safe_under,
)


TERRAIN_EXISTING = (
    TMP_ROOT
    / "translation_quality_audit_v1"
    / "semantic"
    / "msgdata_quality_semantic_addendum.v1.jsonl"
)
READING_EXISTING = (
    TMP_ROOT
    / "translation_quality_audit_v1"
    / "semantic"
    / "msgdata_quality_reading_addendum.v1.jsonl"
)
TERMINOLOGY_EXISTING = (
    TMP_ROOT
    / "translation_quality_audit_v1"
    / "semantic"
    / "msgdata_quality_terminology_addendum.v1.jsonl"
)
FACILITY_EXISTING = (
    TMP_ROOT
    / "translation_quality_audit_v1"
    / "semantic"
    / "msgdata_quality_facility_addendum.v1.jsonl"
)
DEFAULT_OUTPUT = (
    TMP_ROOT
    / "translation_quality_audit_v1"
    / "semantic"
    / "msgdata_quality_trait_semantic_addendum.v1.jsonl"
)


# 24478 and 24502 are duplicate visible slots of the same trait; retaining
# both prevents a corrected and an uncorrected rendering from coexisting.
CANDIDATES: dict[int, Candidate] = {
    24439: Candidate(
        "\u6709\u8077",
        "\uc720\uc18c\ucfe0",
        "\uc608\ubc95",
        "visible_japanese_reading",
        "\ud2b9\uc131\uba85 \u6709\u8077\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744, \uad81\uc815 \uc608\uc808\u00b7\uc758\ub840\ub97c \ub73b\ud558\ub294 \uc6a9\ub840\uc640 PC EN Civility\uc5d0 \ub9de\ucd98 \uc608\ubc95\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24462: Candidate(
        "\u53e4\u72f8",
        "\ud6c4\ub8e8\ub2e4\ub204\ud0a4",
        "\ub178\ud68c\ud55c \uc5ec\uc6b0",
        "visible_japanese_reading",
        "\ud2b9\uc131\uba85 \u53e4\u72f8\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Sly Fox\uc640 SC\u00b7TC\uc758 \u8001\u72d0\u72f8 \uc758\ubbf8\uc5d0 \ub9de\ucd98 \ub178\ud68c\ud55c \uc5ec\uc6b0\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24478: Candidate(
        "\u8d64\u5099\u3048",
        "\uc544\uce74\uc870\ub098\uc5d0",
        "\uc801\ube44",
        "visible_japanese_reading",
        "\ud2b9\uc131\uba85 \u8d64\u5099\u3048\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Red Cavalry\uc640 \uacbd\uae30\ubcd1\uc744 \ubd89\uc740 \uc0c9\uc73c\ub85c \ud1b5\uc77c\ud55c \ubd80\ub300\ub97c \ub73b\ud558\ub294 \ud55c\uad6d\uc5b4 \uc6a9\uc5b4 \uc801\ube44\ub85c \uad50\uccb4\ud55c\ub2e4.",
        (24502,),
    ),
    24502: Candidate(
        "\u8d64\u5099\u3048",
        "\uc544\uce74\uc870\ub098\uc5d0",
        "\uc801\ube44",
        "visible_japanese_reading",
        "\ubcf5\uc218 \ud2b9\uc131 \ubaa9\ub85d\uc5d0 \uc788\ub294 \ub3d9\uc77c \ud45c\uc2dc\uba85 \u8d64\u5099\u3048\ub97c 24478\ubc88과 \uac19\uc774 \ud55c\uad6d\uc5b4 \uc6a9\uc5b4 \uc801\ube44\ub85c \ud1b5\uc77c\ud55c\ub2e4.",
        (24478,),
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
    )
    existing_by_file = {path.name: read_existing_ids(path) for path in existing_sources}
    existing = set().union(*existing_by_file.values())
    overlap = sorted(existing.intersection(CANDIDATES))
    if overlap:
        raise ValueError(f"trait semantic addendum overlaps existing msgdata candidates: {overlap}")

    # The facility builder delegates the complete source/current hash and
    # formatting validation to the shared base validator.  Check its own prior
    # output above, then temporarily provide this independent candidate set.
    original_candidates = facility.CANDIDATES
    try:
        facility.CANDIDATES = CANDIDATES
        rows, summary = facility.build_rows()
    finally:
        facility.CANDIDATES = original_candidates

    summary["existing_facility_addendum_id_count"] = len(
        existing_by_file[FACILITY_EXISTING.name]
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
