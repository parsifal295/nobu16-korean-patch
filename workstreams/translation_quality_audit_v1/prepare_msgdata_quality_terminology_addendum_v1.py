#!/usr/bin/env python3
"""Build a small, source-gated terminology addendum for ``msgdata``.

This keeps two Korean readings whose current text is a Japanese phonetic
rendering separate from the previously emitted terrain and UI-reading sets.
It reads the pristine PC Japanese source and current Steam Korean source only;
PC EN/SC/TC are contextual evidence.  It never reads Switch Korean data and
never writes a game resource.
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
DEFAULT_OUTPUT = (
    TMP_ROOT
    / "translation_quality_audit_v1"
    / "semantic"
    / "msgdata_quality_terminology_addendum.v1.jsonl"
)


# These are main visible labels, not the adjacent ruby-reading fields.  The
# Korean replacements are ordinary Korean readings of the original Hanja and
# retain the exact runtime/whitespace profile of the current resource.
CANDIDATES: dict[int, Candidate] = {
    24408: Candidate(
        "\u4e00\u5411\u5b97",
        "\uc787\ucf54\uc885",
        "\uc77c\ud5a5\uc885",
        "visible_japanese_reading",
        "\uc885\ud30c\uba85 \u4e00\u5411\u5b97\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744 PC EN Ikk\u014d-sh\u016b\uc640 \ud55c\uad6d\uc5b4 \ubd88\uad50 \uc6a9\uc5b4\uc5d0 \ub9de\ucd98 \uc77c\ud5a5\uc885\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4.",
    ),
    24421: Candidate(
        "\u4e7e\u5764",
        "\uac90\ucf58",
        "\uac74\uace4",
        "visible_japanese_reading",
        "\ud2b9\uc131\uba85 \u4e7e\u5764\uc758 \uc77c\ubcf8\uc5b4 \ub3c5\uc74c\uc744, \ud55c\uc790\uc5b4 \uac74\uace4\uc758 \ud55c\uad6d\uc5b4 \ub3c5\uc74c\uc73c\ub85c \uad50\uccb4\ud55c\ub2e4. PC EN All or Nothing\uacfc \ub3d9\uc77c \uc6d0\ubb38\uc758 \uc758\ubbf8\ub97c \ubcf4\uc874\ud55c\ub2e4.",
    ),
}


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    existing_sources = (
        DIRECT_EXISTING,
        SEMANTIC_EXISTING,
        TERRAIN_EXISTING,
        READING_EXISTING,
    )
    existing_by_file = {path.name: read_existing_ids(path) for path in existing_sources}
    existing = set().union(*existing_by_file.values())
    overlap = sorted(existing.intersection(CANDIDATES))
    if overlap:
        raise ValueError(f"terminology addendum overlaps existing msgdata candidates: {overlap}")

    # Reuse the complete source/current hash and formatting validator.  Its
    # configurable fourth candidate source is switched to the prior UI-reading
    # file, while the terrain file was checked just above.
    original_candidates = reading.CANDIDATES
    original_core_existing = reading.CORE_EXISTING
    try:
        reading.CANDIDATES = CANDIDATES
        reading.CORE_EXISTING = READING_EXISTING
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
