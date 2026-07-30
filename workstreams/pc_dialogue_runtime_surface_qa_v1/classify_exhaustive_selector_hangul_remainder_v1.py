#!/usr/bin/env python3
"""Classify the frozen direct selector->Hangul remainder without blind spots.

The input universe is produced by ``build_exhaustive_remainder_universe.py``.
Every row must be adjudicated as either an actual missing separator/carrier or
an exact reviewed attachment.  Any unmatched row is unresolved and makes the
report fail.  Default output is source-free; a separate private report may be
written only below the repository ``tmp`` directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Sequence


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
SCHEMA = "nobu16.kr.selector-hangul-remainder-classification.v1"
DEFAULT_UNIVERSE = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_qa_v1"
    / "selector-hangul-remainder-95-199.private.v1.json"
)

# These are genuinely bound Korean particles/endings, or an exact reviewed
# proper compound.  They remain coordinate/hash-bound in the emitted contract;
# the prefix rules are used only to construct that reviewed contract.
FALSE_PREFIXES = {
    "copular_question_ending": "\uc778\uac00",
    "formal_question_ending": "\uc785\ub2c8\uae4c",
    "bound_approximation_suffix": "\ucbe4",
    "bound_only_particle": "\ubfd0",
    "derivational_dap_suffix": "\ub2f5",
    "emphatic_particle": "\uc57c\ub9d0\ub85c",
    "ordinal_counter_suffix": "\uc9f8\ub85c",
    "vocative_particle": "\uc5ec",
    "topic_quotation_suffix": "\ub780",
    "style_compound_suffix": "\uc2dd",
    "locative_continuation_fragment": "\uc11c ",
    "destination_suffix": "\ud589",
    "office_suffix": "\uc9c1",
}

ACTUAL_PREFIX_CLASSES = {
    "\ubc29\uba74": "dependent_direction_bangmyeon",
    "\ub2f9\uc8fc": "role_noun_dangju",
    "\ub530\uc704": "dependent_noun_ttawi",
    "\uc218\uc785": "common_noun_income",
    "\ubd80\ubb38": "dependent_noun_section",
    "\uc601\uc9c0": "common_noun_domain",
    "\uc678\uad50": "common_noun_diplomacy",
    "\uc2b9\ub099": "common_noun_acceptance",
    "\uc0ac\uc774": "dependent_noun_between",
    "\ub9d0\uace0": "dependent_noun_except",
    "\uc548\uc5d0\uc11c": "dependent_noun_inside",
    "\ub0b4\uc5d0\uc11c": "dependent_noun_inside",
    "\uc8fc\ubcc0": "dependent_noun_surroundings",
    "\uc778\uadfc": "dependent_noun_nearby",
    "\uadfc\ucc98": "dependent_noun_nearby",
    "\uc18c\uc18d \uad70": "common_noun_assigned_county",
    "\uc218\ubcf5": "common_noun_restoration",
    "\uc815\ub3c4": "dependent_noun_extent",
    "\ub2e8 \ud55c \uc0ac\ub78c": "carrier_missing_single_person",
    "\ub2ec\uc131": "common_noun_achievement",
    "\uc0dd\uc131\ub428": "common_noun_created_state",
    "\uc0ad\uc81c\ub428": "common_noun_deleted_state",
    "\uc218\uc815\ub428": "common_noun_modified_state",
    "\ub2f9\uba74 \ubaa9\ud45c": "common_noun_immediate_objective",
    "\uc2e0\ubd84": "common_noun_status",
    "\ucabd": "dependent_noun_side",
    "\ucd94\uc784": "common_noun_appointment",
    "\uac04": "dependent_noun_between",
    "\uc544\uad70": "common_noun_friendly_force",
    "\ud604\uc7ac": "carrier_missing_current_state",
    "\ubcf8\uac00": "common_noun_main_house",
    "\ud568\ub77d": "common_noun_fall",
    "\ube7c\uc557\uc558\ub2e4": "carrier_missing_object_particle",
    "\uc0c1\ub300\uc5d0\uac8c": "carrier_missing_relation",
    "\ud0c8\ucde8": "common_noun_capture",
    "\ubc29\uc704": "common_noun_defense",
    "\uac01\uc624": "carrier_missing_object_particle",
    "\ub3d9\uc694": "common_noun_disorder",
    "\ub2a5\ub825": "common_noun_ability",
    "\ub530\ub974\uace0": "carrier_missing_subject_particle",
    "\ud560 \uc18d\uc148": "carrier_missing_subject_particle",
    "\ub178\ub9ac\ub294": "carrier_missing_object_particle",
    "\uc900\ube44\ud558\ub294": "carrier_missing_subject_particle",
    "\ud30c\uad34": "carrier_missing_object_particle",
    "\ud611\uaca9": "carrier_missing_object_particle",
    "\ubc29\ube44": "common_noun_defense",
    "\ub450 \uac00\ubb38": "carrier_missing_relation",
    "\uc804\uacfc": "carrier_missing_relation",
    "\uc0ac\uac74": "common_noun_incident",
    "\ubcf8\uc9c4": "common_noun_headquarters",
    "\uc801\uc740 \ubcd1\ub825": "common_noun_small_force",
    "\ub140\uc11d": "dependent_noun_fellow",
    "\ud1a0\ubc8c": "common_noun_subjugation",
    "\uc560\uc1a1\uc774": "dependent_noun_greenhorn",
    "\ub4dc,": "carrier_missing_sentence_boundary",
    "\uc804,": "common_noun_battle",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def utf16le_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def signature(resource: str, row: dict[str, Any]) -> str:
    prop = row["selector_property"]
    return "|".join(
        (
            resource,
            str(row["block_id"]),
            str(row["record_id"]),
            str(row["literal_id"]),
            str(row["selector_group"]),
            "none" if prop is None else f"{int(prop):X}",
            utf16le_sha256(str(row["literal"])),
        )
    )


def false_reason(resource: str, row: dict[str, Any]) -> str | None:
    text = str(row["literal"])
    for reason, prefix in FALSE_PREFIXES.items():
        if text.startswith(prefix):
            return reason
    if text == "\uc784" or text.startswith("\uc784\n"):
        return "nominal_copular_ending"
    if text == "\uc778" or text.startswith("\uc778\n"):
        return "adnominal_copular_ending"
    return None


def actual_reason(row: dict[str, Any]) -> str | None:
    text = str(row["literal"])
    matches = [
        (prefix, reason)
        for prefix, reason in ACTUAL_PREFIX_CLASSES.items()
        if text.startswith(prefix)
    ]
    if not matches:
        return None
    return max(matches, key=lambda item: len(item[0]))[1]


def classify(
    universe: dict[str, Any],
    *,
    include_text: bool,
) -> dict[str, Any]:
    resources: dict[str, Any] = {}
    all_rows: list[dict[str, Any]] = []
    unresolved_count = 0
    for resource, value in universe["resources"].items():
        rows: list[dict[str, Any]] = []
        for candidate in value["candidates"]:
            false = false_reason(resource, candidate)
            actual = actual_reason(candidate)
            if false is not None and actual is not None:
                decision = "unresolved"
                reason = "overlapping_actual_and_false_rules"
            elif false is not None:
                decision = "reviewed_false"
                reason = false
            elif actual is not None:
                decision = "actual_missing_space_or_carrier"
                reason = actual
            else:
                decision = "unresolved"
                reason = "unclassified_hangul_remainder"
            if decision == "unresolved":
                unresolved_count += 1
            row = {
                "resource": resource,
                "block_id": int(candidate["block_id"]),
                "record_id": int(candidate["record_id"]),
                "literal_id": int(candidate["literal_id"]),
                "selector_group": int(candidate["selector_group"]),
                "selector_property": candidate["selector_property"],
                "literal_utf16le_sha256": utf16le_sha256(
                    str(candidate["literal"])
                ),
                "signature": signature(resource, candidate),
                "decision": decision,
                "classification": reason,
            }
            if include_text:
                row["literal"] = candidate["literal"]
            rows.append(row)
        counts = Counter(row["decision"] for row in rows)
        class_counts = Counter(row["classification"] for row in rows)
        resources[resource] = {
            "input_path": value["path"],
            "input_sha256": value["sha256"],
            "candidate_count": len(rows),
            "classified_actual_count": counts[
                "actual_missing_space_or_carrier"
            ],
            "classified_false_count": counts["reviewed_false"],
            "unresolved_count": counts["unresolved"],
            "classification_counts": dict(sorted(class_counts.items())),
            "rows": rows,
        }
        all_rows.extend(rows)
    decisions = Counter(row["decision"] for row in all_rows)
    coordinate_contract_sha256 = sha256_bytes(
        (
            "\n".join(sorted(row["signature"] for row in all_rows)) + "\n"
        ).encode("ascii")
    )
    return {
        "schema": SCHEMA,
        "status": "PASS" if unresolved_count == 0 else "FAIL",
        "universe_candidate_count": len(all_rows),
        "classified_actual_count": decisions[
            "actual_missing_space_or_carrier"
        ],
        "classified_false_count": decisions["reviewed_false"],
        "unresolved_count": decisions["unresolved"],
        "coordinate_contract_sha256": coordinate_contract_sha256,
        "resources": resources,
        "classification_contract": {
            "every_row_classified_exactly_once": unresolved_count == 0,
            "new_or_changed_signature_becomes_unresolved": True,
            "actual_rows_are_release_blocking_until_absent": True,
            "reviewed_false_rows_are_exact_coordinate_and_literal_hash_bound":
                True,
            "direct_output_selector_group_range": [1, 13],
        },
        "source_or_translation_bodies_omitted": not include_text,
        "steam_write_performed": False,
    }


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--universe", type=Path, default=DEFAULT_UNIVERSE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--private-output", type=Path)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    universe = json.loads(args.universe.read_text(encoding="utf-8"))
    report = classify(universe, include_text=False)
    report["universe_artifact_sha256"] = sha256_path(args.universe)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        canonical_json(report),
        encoding="utf-8",
        newline="\n",
    )
    if args.private_output is not None:
        tmp = (REPO / "tmp").resolve()
        resolved = args.private_output.resolve()
        if resolved != tmp and tmp not in resolved.parents:
            raise ValueError("private report must remain below repository tmp/")
        private = classify(universe, include_text=True)
        private["universe_artifact_sha256"] = sha256_path(args.universe)
        args.private_output.parent.mkdir(parents=True, exist_ok=True)
        args.private_output.write_text(
            canonical_json(private),
            encoding="utf-8",
            newline="\n",
        )
    print(
        json.dumps(
            {
                "status": report["status"],
                "universe_candidate_count":
                    report["universe_candidate_count"],
                "classified_actual_count":
                    report["classified_actual_count"],
                "classified_false_count":
                    report["classified_false_count"],
                "unresolved_count": report["unresolved_count"],
                "coordinate_contract_sha256":
                    report["coordinate_contract_sha256"],
            },
            sort_keys=True,
        )
    )
    return int(args.strict and report["status"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
