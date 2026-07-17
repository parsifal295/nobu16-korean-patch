#!/usr/bin/env python3
"""Build source-gated labor-resource terminology corrections for msgdata.

Only main display/effect slots are considered. The Japanese term is a
construction-resource Labor, but seven live Korean labels use personal effort
instead of the consistently used construction-resource word. Adjacent
kana/ruby slots stay out of scope.

This script reads pristine PC Japanese/current Steam PC Korean and PC EN/SC/TC
context only. It never reads Switch or historic Korean data and never writes
a game resource.
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
    / "msgdata_labor_terminology_addendum.v1.jsonl"
)


# Main display/effect records plus their localized Korean reading counterparts.
CANDIDATES: dict[int, Candidate] = {
    21552: Candidate(
        "\u6700\u5927\u52b4\u529b",
        "\ucd5c\ub300 \ub178\ub825",
        "\ucd5c\ub300 \ub178\ub3d9\ub825",
        "resource_term_consistency",
        "Max Labor is a construction-resource capacity. Equivalent live Korean UI labels at 23052, 28148, and 29216 use the resource term \u2018\ub178\ub3d9\ub825\u2019 rather than personal effort \u2018\ub178\ub825\u2019.",
        (23052, 28148, 29216),
    ),
    22052: Candidate(
        "\u3055\u3044\u3060\u3044\u308d\u3046\u308a\u3087\u304f",
        "\ucd5c\ub300\ub178\ub825",
        "\ucd5c\ub300\ub178\ub3d9\ub825",
        "localized_parallel_reading_term_consistency",
        "This paired reading slot is already localized in Korean rather than retaining Japanese kana: it mirrors the main Max Labor label at 21552. Keeping the same construction-resource term prevents the parallel UI slot from retaining personal effort \u2018\ub178\ub825\u2019.",
        (21552, 23052, 28148, 29216),
    ),
    21627: Candidate(
        "\u300c\u57ce\u4e0b\u65b9\u91dd\u300d\u52b4\u529b\u6d88\u8cbb\u306a\u3057",
        "\u300c\uc131\ud558 \ubc29\uce68\u300d \ub178\ub825 \uc18c\ube44 \uc5c6\uc74c",
        "\u300c\uc131\ud558 \ubc29\uce68\u300d \ub178\ub3d9\ub825 \uc18c\ube44 \uc5c6\uc74c",
        "resource_term_consistency",
        "The castle-town-plan effect concerns construction-resource consumption; PC EN says No Labor Consumption and current Korean construction-effect labels use \u2018\ub178\ub3d9\ub825\u2019.",
        (26461, 26511, 28145),
    ),
    22127: Candidate(
        "\u3058\u3087\u3046\u304b\u307b\u3046\u3057\u3093\u308d\u3046\u308a\u3087\u3046\u3057\u3087\u3046\u3072\u306a\u3057",
        "\uc131\ud558 \ubc29\uce68 \ub178\ub825 \uc18c\ube44 \uc5c6\uc74c",
        "\uc131\ud558 \ubc29\uce68 \ub178\ub3d9\ub825 \uc18c\ube44 \uc5c6\uc74c",
        "localized_parallel_reading_term_consistency",
        "This paired reading slot is already localized in Korean and mirrors the castle-town-plan Labor-consumption label at 21627. It receives the same construction-resource term while retaining its existing spacing profile.",
        (21627, 22627, 23127, 26461, 26511, 28145),
    ),
    22552: Candidate(
        "\u52b4\u529b%+d",
        "\ub178\ub825%+d",
        "\ub178\ub3d9\ub825%+d",
        "resource_term_consistency",
        "This numeric Labor effect label is aligned to the current Korean equivalent at 26513 while preserving the exact runtime percent token.",
        (26513, 28145),
    ),
    22627: Candidate(
        "\u300c\u57ce\u4e0b\u65b9\u91dd\u300d\u8a2d\u5b9a\u306b\u3088\u308b\u52b4\u529b\u6d88\u8cbb\u306a\u3057",
        "\u300c\uc131\ud558 \ubc29\uce68\u300d \uc124\uc815\uc5d0 \uc758\ud55c \ub178\ub825 \uc18c\ube44 \uc5c6\uc74c",
        "\u300c\uc131\ud558 \ubc29\uce68\u300d \uc124\uc815\uc5d0 \uc758\ud55c \ub178\ub3d9\ub825 \uc18c\ube44 \uc5c6\uc74c",
        "resource_term_consistency",
        "Detailed display form of the same castle-town-plan Labor-consumption effect. The construction resource is normalized to \u2018\ub178\ub3d9\ub825\u2019.",
        (26461, 26511, 28145),
    ),
    23127: Candidate(
        "\u300c\u57ce\u4e0b\u65b9\u91dd\u300d\u8a2d\u5b9a\u306b\u3088\u308b\u52b4\u529b\u6d88\u8cbb\u306a\u3057",
        "\u300c\uc131\ud558 \ubc29\uce68\u300d \uc124\uc815\uc5d0 \uc758\ud55c \ub178\ub825 \uc18c\ube44 \uc5c6\uc74c",
        "\u300c\uc131\ud558 \ubc29\uce68\u300d \uc124\uc815\uc5d0 \uc758\ud55c \ub178\ub3d9\ub825 \uc18c\ube44 \uc5c6\uc74c",
        "resource_term_consistency",
        "A second visible effect label for the same castle-town-plan Labor-consumption effect; it receives the same construction-resource term.",
        (26461, 26511, 28145),
    ),
    24249: Candidate(
        "\u6700\u5927\u52b4\u529b",
        "\ucd5c\ub300 \ub178\ub825",
        "\ucd5c\ub300 \ub178\ub3d9\ub825",
        "resource_term_consistency",
        "Facility-effect label for the same construction resource. It aligns with current Korean Max Labor labels at 23052, 28148, and 29216.",
        (23052, 28148, 29216),
    ),
    26228: Candidate(
        "\u52b4\u529b",
        "\ub178\ub825",
        "\ub178\ub3d9\ub825",
        "resource_term_consistency",
        "System resource label. PC EN says Labor and equivalent current Korean effect labels use the construction-resource term \u2018\ub178\ub3d9\ub825\u2019.",
        (26463, 26513, 28145),
    ),
}


UI_SLOT_CONTEXT: dict[int, dict[str, object]] = {
    21552: {
        "slot_kind": "main_policy_effect_label",
        "localized_parallel_reading_id": 22052,
        "same_resource_display_ids": [23052, 28148, 29216],
    },
    22052: {
        "slot_kind": "localized_parallel_reading_label",
        "main_display_id": 21552,
        "same_resource_display_ids": [23052, 28148, 29216],
    },
    21627: {
        "slot_kind": "main_castle_town_plan_effect_label",
        "localized_parallel_reading_id": 22127,
        "same_resource_display_ids": [22627, 23127, 26461, 26511, 28145],
    },
    22127: {
        "slot_kind": "localized_parallel_reading_label",
        "main_display_id": 21627,
        "same_resource_display_ids": [22627, 23127, 26461, 26511, 28145],
    },
    22552: {
        "slot_kind": "main_numeric_policy_effect_label",
        "same_resource_display_ids": [26513, 28145],
    },
    22627: {
        "slot_kind": "main_castle_town_plan_effect_detail",
        "localized_parallel_reading_id": 22127,
        "same_resource_display_ids": [21627, 23127, 26461, 26511, 28145],
    },
    23127: {
        "slot_kind": "main_castle_town_plan_effect_description",
        "localized_parallel_reading_id": 22127,
        "same_resource_display_ids": [21627, 22627, 26461, 26511, 28145],
    },
    24249: {
        "slot_kind": "main_facility_effect_label",
        "same_resource_display_ids": [23052, 28148, 29216],
    },
    26228: {
        "slot_kind": "main_system_resource_label",
        "same_resource_display_ids": [26463, 26513, 28145],
    },
}


def existing_candidate_ids() -> set[int]:
    """Return numeric IDs from every current msgdata candidate artifact."""
    directories = (
        TMP_ROOT / "translation_quality_audit_v1" / "semantic",
        TMP_ROOT / "translation_quality_audit_v1" / "proposals",
    )
    result: set[int] = set()
    for directory in directories:
        for path in directory.glob("msgdata*.jsonl"):
            if path.resolve() == DEFAULT_OUTPUT.resolve():
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                if line:
                    identifier = json.loads(line).get("id")
                    if isinstance(identifier, int):
                        result.add(identifier)
    return result


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    existing = existing_candidate_ids()
    overlap = sorted(existing.intersection(CANDIDATES))
    if overlap:
        raise ValueError(f"labor terminology addendum overlaps existing msgdata candidates: {overlap}")

    # Reuse the full source/current hash, PC-reference, and format-profile
    # validator from the preceding source-gated quality builders.
    original_candidates = reading.CANDIDATES
    try:
        reading.CANDIDATES = CANDIDATES
        rows, summary = reading.build_rows()
    finally:
        reading.CANDIDATES = original_candidates

    for row in rows:
        identifier = row["id"]
        row["ui_slot_context"] = UI_SLOT_CONTEXT[identifier]
        row["candidate_scope"] = "main_display_effect_or_localized_parallel_reading_slot"
    summary["existing_all_msgdata_candidate_id_count"] = len(existing)
    summary["localized_parallel_reading_ids_included"] = [22052, 22127]
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
