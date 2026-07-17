#!/usr/bin/env python3
"""Build a source-gated castle-town facility quality addendum for ``msgdata``.

Only clear visible facility labels are included: retained Japanese readings
with an established Korean equivalent, plus one directly supported semantic
misrendering.  The builder reads local pristine PC Japanese/current Steam
Korean resources and PC EN/SC/TC context only.  It does not read Switch Korean
data and does not write a game resource.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import prepare_msgdata_quality_reading_addendum_v1 as reading
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
DEFAULT_OUTPUT = (
    TMP_ROOT
    / "translation_quality_audit_v1"
    / "semantic"
    / "msgdata_quality_facility_addendum.v1.jsonl"
)


# These are main visible facility labels, not the adjacent Japanese reading
# fields.  Ambiguous facility names (e.g. cultural proper terms) remain out of
# scope.  All choices retain the current string's runtime/whitespace profile.
CANDIDATES: dict[int, Candidate] = {
    24076: Candidate(
        "\u8377\u99c4\u8a70\u6240",
        "\uc9d0\uc218\ub808 \ub300\uae30\uc18c",
        "\ubcf4\uae09\uc18c",
        "semantic_mistranslation",
        "\uc131\ud558 \ub9c8\uc744 \uc2dc\uc124\uba85 \u8377\u99c4\u8a70\u6240\ub97c PC EN Supply Station\uacfc SC\u00b7TC\uc758 \ubcf4\uae09\ud488 \uae30\uc9c0 \uc758\ubbf8\uc5d0 \ub9de\ucd98 \ubcf4\uae09\uc18c\ub85c \uad50\uccb4\ud55c\ub2e4. \ud604\uc7ac \uc9d0\uc218\ub808 \ub300\uae30\uc18c\ub294 \uc2dc\uc124\uc758 \uae30\ub2a5\uc744 \uc815\ud655\ud788 \ub098\ud0c0\ub0b4\uc9c0 \ubabb\ud55c\ub2e4.",
    ),
    24079: Candidate(
        "\u8336\u5c4b\u753a",
        "\ucc28\uc57c\ub9c8\uce58",
        "\ucc3b\uc9d1 \uac70\ub9ac",
        "visible_japanese_reading",
        "\uc131\ud558 \ub9c8\uc744 \uc2dc\uc124\uba85 \u8336\u5c4b\u753a\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Tea Town\uacfc \ud55c\uad6d\uc5b4 \ud45c\uae30\uc5d0 \ub9de\ucd98 \ucc3b\uc9d1 \uac70\ub9ac\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24083: Candidate(
        "\u7530\u7551",
        "\ub2e4\ubc14\ud0c0",
        "\ub17c\ubc2d",
        "visible_japanese_reading",
        "\uc131\ud558 \ub9c8\uc744 \uc2dc\uc124\uba85 \u7530\u7551\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC SC\u00b7TC\uc758 \ub18d\uc9c0 \uc758\ubbf8\uc5d0 \ub9de\ucd98 \ub17c\ubc2d\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24091: Candidate(
        "\u5fa1\u6240",
        "\uace0\uc1fc",
        "\uc5b4\uc18c",
        "visible_japanese_reading",
        "\uc131\ud558 \ub9c8\uc744 \uc2dc\uc124\uba85 \u5fa1\u6240\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744, \uc65c\uad6d \uc5ed\uc0ac\uc790\ub8cc\uc5d0\uc11c\ub3c4 \uc0ac\uc6a9\ub418\ub294 \ud55c\uad6d\uc5b4 \uace0\uc720 \ud45c\uae30 \uc5b4\uc18c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24105: Candidate(
        "\u685f\u6577",
        "\uc0ac\uc9c0\ud0a4",
        "\uad00\ub78c\uc11d",
        "visible_japanese_reading",
        "\uc131\ud558 \ub9c8\uc744 \uc2dc\uc124\uba85 \u685f\u6577\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 SC\u00b7TC\uc758 \uad00\uc911\uc11d \uc758\ubbf8\uc640 \ud55c\uad6d\uc5b4 \ud45c\uae30\uc5d0 \ub9de\ucd98 \uad00\ub78c\uc11d\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24107: Candidate(
        "\u5bbf\u5834",
        "\uc288\ucfe0\ubc14",
        "\uc5ed\ucc38",
        "visible_japanese_reading",
        "\uc131\ud558 \ub9c8\uc744 \uc2dc\uc124\uba85 \u5bbf\u5834\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744, \uac00\ub3c4\uc758 \uc219\ubc15\u00b7\uc6b4\uc1a1 \uac70\uc810\uc744 \ub73b\ud558\ub294 \ud55c\uad6d\uc5b4 \uc5ed\uc0ac \uc6a9\uc5b4 \uc5ed\ucc38\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
}


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    existing_sources = (
        DIRECT_EXISTING,
        SEMANTIC_EXISTING,
        TERRAIN_EXISTING,
        READING_EXISTING,
        TERMINOLOGY_EXISTING,
    )
    existing_by_file = {path.name: read_existing_ids(path) for path in existing_sources}
    existing = set().union(*existing_by_file.values())
    overlap = sorted(existing.intersection(CANDIDATES))
    if overlap:
        raise ValueError(f"facility addendum overlaps existing msgdata candidates: {overlap}")

    # Reuse the complete source/current hash and formatting validator.  The
    # terrain, UI-reading, and terminology sets were explicitly checked above.
    original_candidates = reading.CANDIDATES
    original_core_existing = reading.CORE_EXISTING
    try:
        reading.CANDIDATES = CANDIDATES
        reading.CORE_EXISTING = TERMINOLOGY_EXISTING
        rows, summary = reading.build_rows()
    finally:
        reading.CANDIDATES = original_candidates
        reading.CORE_EXISTING = original_core_existing

    summary.pop("existing_core_addendum_id_count", None)
    summary["existing_terrain_addendum_id_count"] = len(
        existing_by_file[TERRAIN_EXISTING.name]
    )
    summary["existing_reading_addendum_id_count"] = len(
        existing_by_file[READING_EXISTING.name]
    )
    summary["existing_terminology_addendum_id_count"] = len(
        existing_by_file[TERMINOLOGY_EXISTING.name]
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
