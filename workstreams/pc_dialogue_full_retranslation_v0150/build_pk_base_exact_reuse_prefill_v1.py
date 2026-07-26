#!/usr/bin/env python3
"""Prefill high-confidence PK dialogue from the completed Base policy.

The tracked builder contains no commercial dialogue.  It joins private
decisions and pinned archives by hashes, writes source-bearing rows only below
``tmp/``, and deliberately leaves dynamic rows pending until a PK-specific VM
coverage report proves their actual call closures.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OUTPUT = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
PUBLIC_REPORT = WORKSTREAM / "pk_base_exact_reuse_prefill.source_free.v1.json"
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
BASE_COVERAGE = (
    REPO
    / "workstreams"
    / "base_msggame_runtime_vm_audit_v1"
    / "public"
    / "base_msggame_runtime_vm_coverage.v1.json"
)

SCHEMA = "nobu16.kr.pk-msggame-base-exact-reuse-prefill.v1"
ROW_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-msggame-base-exact-reuse-row-prefill.v1"
)
EXPECTED_EXISTING_PK_DECISIONS = 1_799
EXPECTED_ROWS = 17_652
EXPECTED_ROUGH_STATIC = 7_884
EXPECTED_ROUGH_DYNAMIC = 9_768
# This donor comparison is deliberately narrower than the separate all-record
# overlap survey: only Base donors with the same exact source literal are
# eligible here, and their completed-candidate gaps are compared to the current
# PK gaps record-wide.  These counts must not be presented as the global
# Base-vs-PK matched/novel partition.  The later exact PK VM coverage may prove
# a larger subset through synchronized closure pairing, but this builder never
# promotes either subset.
EXPECTED_SOURCE_DONOR_MASKED_DYNAMIC_MATCH = 9_685
EXPECTED_SOURCE_DONOR_MASKED_DYNAMIC_MISMATCH = 83
EXPECTED_ANY_BASE_EXACT_DYNAMIC_MATCH = 7_039
EXPECTED_ANY_BASE_MASKED_DYNAMIC_MATCH = 9_743
EXPECTED_ANY_BASE_MASKED_DYNAMIC_NOVEL = 25
CONTROL_TARGET_RE = re.compile(b"\x01([\x43\x4A]).{4}", re.DOTALL)


class PrefillError(ValueError):
    """Raised when the pinned Base-to-PK reuse universe drifts."""


@dataclass(frozen=True)
class Donor:
    coordinate: str
    record_coordinate: tuple[int, int]
    source_text: str
    final_text: str
    source_record_sha256: str
    decision_sha256: str
    gap_template_sha256: str
    masked_gap_template_sha256: str


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PrefillError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def compact_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(compact_json_bytes(value))


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module("pk_base_exact_reuse_prefill_engine", ENGINE_PATH)


def coordinate_key(value: str) -> tuple[int, int, int]:
    parts = tuple(int(part) for part in value.split(":"))
    require(len(parts) == 3, f"invalid coordinate: {value}")
    return parts  # type: ignore[return-value]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    require(path.is_file(), f"required private JSONL is absent: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line:
            continue
        value = json.loads(line)
        require(isinstance(value, dict), f"{path}:{line_number} is not an object")
        rows.append(value)
    return rows


def record_map(archive: Any) -> dict[tuple[int, int], Any]:
    return ENGINE.archive_records(archive)


def literal_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps: list[bytes] = []
    cursor = 0
    for literal in literals:
        gaps.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


def gap_template(record: Any, *, mask_operands: bool) -> tuple[str, ...]:
    gaps = literal_gaps(record)
    if not mask_operands:
        return tuple(gap.hex().upper() for gap in gaps)
    return tuple(
        CONTROL_TARGET_RE.sub(
            lambda match: b"\x01" + match.group(1) + b"\xFF\xFF\xFF\xFF",
            gap,
        ).hex().upper()
        for gap in gaps
    )


def rough_dynamic(record: Any) -> bool:
    joined = b"".join(literal_gaps(record))
    return b"\x01\x43" in joined or b"\x02" in joined


def meaningful_source_length(value: str) -> int:
    normalized = unicodedata.normalize("NFKC", value)
    return sum(
        unicodedata.category(character)[0] not in {"P", "Z", "C"}
        for character in normalized
    )


def existing_pk_coordinates() -> set[str]:
    coordinates: set[str] = set()
    paths = sorted(DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl"))
    for path in paths:
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        for row in read_jsonl(path):
            require(row.get("resource") == "pk_msggame", f"{path} mixes resources")
            coordinate = row.get("coordinate")
            require(isinstance(coordinate, str), f"{path} row has no coordinate")
            require(coordinate not in coordinates, f"duplicate existing PK coordinate: {coordinate}")
            coordinates.add(coordinate)
    require(
        len(coordinates) == EXPECTED_EXISTING_PK_DECISIONS,
        f"existing PK decision universe drifted: {len(coordinates)}",
    )
    return coordinates


def build_base_final(
    prepared: Any,
    promoted_rows: list[dict[str, Any]],
) -> tuple[dict[tuple[int, int], Any], str]:
    current_blob = prepared.resources["base_msggame"].current_blob
    replacements: dict[tuple[int, int, int], str] = {}
    for row in promoted_rows:
        require(row.get("resource") == "base_msggame", "promoted Base file mixes resources")
        translation = row.get("translation")
        if isinstance(translation, str):
            replacements[coordinate_key(row["coordinate"])] = translation
    candidate = ENGINE.rebuild_packed_with_literals(current_blob, replacements)
    coverage = json.loads(BASE_COVERAGE.read_text(encoding="utf-8"))
    expected = coverage["candidate_build"]["fully_decided_candidate_packed_sha256"]
    require(sha256_bytes(candidate) == expected, "completed Base candidate hash drifted")
    return record_map(ENGINE.parse_packed_msggame(candidate).archive), expected


def build_donor_index(
    prepared: Any,
    promoted_rows: list[dict[str, Any]],
    base_final_records: dict[tuple[int, int], Any],
) -> dict[str, tuple[Donor, ...]]:
    source_records = record_map(prepared.resources["base_msggame"].pristine_archive)
    rows_by_coordinate = {
        str(row["coordinate"]): row
        for row in promoted_rows
    }
    donors: defaultdict[str, list[Donor]] = defaultdict(list)
    for coordinate, row in sorted(
        rows_by_coordinate.items(),
        key=lambda item: coordinate_key(item[0]),
    ):
        block_id, record_id, literal_id = coordinate_key(coordinate)
        source_record = source_records[(block_id, record_id)]
        source_literals = ENGINE.parse_record_literals(source_record)
        final_record = base_final_records[(block_id, record_id)]
        final_literals = ENGINE.parse_record_literals(final_record)
        require(literal_id < len(source_literals), f"Base source literal drifted: {coordinate}")
        require(literal_id < len(final_literals), f"Base final literal drifted: {coordinate}")
        require(row.get("semantic_review") == "approved", f"Base donor is unapproved: {coordinate}")
        require(row.get("historic_korean_used") is False, f"Base donor uses historic Korean: {coordinate}")
        require(row.get("switch_korean_used") is False, f"Base donor uses Switch Korean: {coordinate}")
        source_text = source_literals[literal_id].text
        final_text = final_literals[literal_id].text
        donors[source_text].append(
            Donor(
                coordinate=coordinate,
                record_coordinate=(block_id, record_id),
                source_text=source_text,
                final_text=final_text,
                source_record_sha256=sha256_bytes(source_record.data),
                decision_sha256=canonical_sha256(row),
                gap_template_sha256=canonical_sha256(gap_template(final_record, mask_operands=False)),
                masked_gap_template_sha256=canonical_sha256(
                    gap_template(final_record, mask_operands=True)
                ),
            )
        )
    return {
        source: tuple(sorted(values, key=lambda donor: coordinate_key(donor.coordinate)))
        for source, values in donors.items()
    }


def build_rows() -> tuple[Any, list[dict[str, Any]], bytes, dict[str, Any]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    existing = existing_pk_coordinates()
    promoted_rows = read_jsonl(BASE_PROMOTED)
    base_final_records, base_candidate_sha256 = build_base_final(
        prepared,
        promoted_rows,
    )
    donor_index = build_donor_index(prepared, promoted_rows, base_final_records)
    any_base_exact_templates = {
        canonical_sha256(gap_template(record, mask_operands=False))
        for record in base_final_records.values()
    }
    any_base_masked_templates = {
        canonical_sha256(gap_template(record, mask_operands=True))
        for record in base_final_records.values()
    }
    pk_source_records = record_map(prepared.resources["pk_msggame"].pristine_archive)
    pk_current_records = record_map(prepared.resources["pk_msggame"].current_archive)

    selected: list[tuple[dict[str, Any], Donor, bool, bool, bool, bool]] = []
    funnel = Counter()
    for key, target in sorted(prepared.visible_targets.items()):
        resource, block_id, record_id, literal_id = key
        if resource != "pk_msggame":
            continue
        coordinate = f"{block_id}:{record_id}:{literal_id}"
        if coordinate in existing:
            continue
        funnel["remaining"] += 1
        source_record = pk_source_records[(block_id, record_id)]
        current_record = pk_current_records[(block_id, record_id)]
        source_literals = ENGINE.parse_record_literals(source_record)
        current_literals = ENGINE.parse_record_literals(current_record)
        require(literal_id < len(source_literals), f"PK source literal drifted: {coordinate}")
        require(literal_id < len(current_literals), f"PK current literal drifted: {coordinate}")
        source_text = source_literals[literal_id].text
        current_text = current_literals[literal_id].text
        donors = donor_index.get(source_text, ())
        if not donors:
            continue
        funnel["exact_source"] += 1
        final_values = {donor.final_text for donor in donors}
        if len(final_values) != 1:
            continue
        funnel["unanimous_translation"] += 1
        translation = next(iter(final_values))
        if ENGINE.protected_signature(translation) != ENGINE.protected_signature(current_text):
            continue
        funnel["protected_signature"] += 1
        if meaningful_source_length(source_text) < 4:
            continue
        funnel["meaningful_length"] += 1

        pk_gap_sha256 = canonical_sha256(gap_template(current_record, mask_operands=False))
        pk_masked_sha256 = canonical_sha256(gap_template(current_record, mask_operands=True))
        masked_donors = [
            donor
            for donor in donors
            if donor.masked_gap_template_sha256 == pk_masked_sha256
        ]
        donor = (masked_donors or list(donors))[0]
        is_dynamic = rough_dynamic(current_record)
        masked_match = bool(masked_donors)
        any_base_exact_match = pk_gap_sha256 in any_base_exact_templates
        any_base_masked_match = pk_masked_sha256 in any_base_masked_templates
        layout_pending = translation.count("\n") != current_text.count("\n")
        row_pending = is_dynamic or layout_pending
        row = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256": target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
            "translation": translation,
            "semantic_review": "approved",
            "scope_classification": (
                "runtime_fragment_pending" if row_pending else "retranslated"
            ),
            "layout_review": (
                "runtime_pending" if layout_pending else "unchanged_from_current"
            ),
            "runtime_review": "pending" if row_pending else "not_required",
            "basis": (
                "exact pristine JP literal; unanimous completed Base final Korean; "
                "PK protected signature exact; source meaning length gate; "
                "PK bytecode retained; dynamic rows require separate PK VM approval"
            ),
            "historic_korean_used": False,
            "switch_korean_used": False,
            "base_exact_reuse_prefill": {
                "schema": ROW_EVIDENCE_SCHEMA,
                "base_coordinate": donor.coordinate,
                "base_source_record_raw_sha256": donor.source_record_sha256,
                "base_decision_sha256": donor.decision_sha256,
                "base_candidate_packed_sha256": base_candidate_sha256,
                "source_utf16le_sha256": sha256_bytes(source_text.encode("utf-16-le")),
                "translation_utf16le_sha256": sha256_bytes(translation.encode("utf-16-le")),
                "pk_source_gap_template_sha256": pk_gap_sha256,
                "pk_operand_masked_gap_template_sha256": pk_masked_sha256,
                "base_operand_masked_gap_template_sha256": donor.masked_gap_template_sha256,
                "exact_source_donor_operand_masked_template_match": masked_match,
                "any_base_candidate_exact_gap_template_match": any_base_exact_match,
                "any_base_candidate_operand_masked_gap_template_match": (
                    any_base_masked_match
                ),
                "layout_change_pending": layout_pending,
                "runtime_promotion_authorized": False,
            },
        }
        selected.append(
            (
                row,
                donor,
                is_dynamic,
                masked_match,
                any_base_exact_match,
                any_base_masked_match,
            )
        )

    require(funnel["remaining"] == 27_239, f"remaining PK universe drifted: {funnel}")
    require(funnel["exact_source"] == 22_397, f"exact-source funnel drifted: {funnel}")
    require(
        funnel["unanimous_translation"] == 19_636,
        f"translation convergence funnel drifted: {funnel}",
    )
    require(
        funnel["protected_signature"] == 19_515,
        f"protected-signature funnel drifted: {funnel}",
    )
    require(funnel["meaningful_length"] == EXPECTED_ROWS, f"length funnel drifted: {funnel}")

    selected.sort(key=lambda item: coordinate_key(item[0]["coordinate"]))
    rows = [item[0] for item in selected]
    rough_dynamic_count = sum(item[2] for item in selected)
    rough_static_count = len(rows) - rough_dynamic_count
    masked_dynamic_count = sum(item[2] and item[3] for item in selected)
    source_donor_masked_dynamic_mismatch_count = sum(
        item[2] and not item[3] for item in selected
    )
    any_base_exact_dynamic_match_count = sum(
        item[2] and item[4] for item in selected
    )
    any_base_masked_dynamic_match_count = sum(
        item[2] and item[5] for item in selected
    )
    any_base_masked_dynamic_novel_count = sum(
        item[2] and not item[5] for item in selected
    )
    require(len(rows) == EXPECTED_ROWS, "prefill row count drifted")
    require(rough_static_count == EXPECTED_ROUGH_STATIC, "rough static count drifted")
    require(rough_dynamic_count == EXPECTED_ROUGH_DYNAMIC, "rough dynamic count drifted")
    require(
        masked_dynamic_count == EXPECTED_SOURCE_DONOR_MASKED_DYNAMIC_MATCH,
        f"exact-source donor masked dynamic match count drifted: {masked_dynamic_count}",
    )
    require(
        source_donor_masked_dynamic_mismatch_count
        == EXPECTED_SOURCE_DONOR_MASKED_DYNAMIC_MISMATCH,
        "exact-source donor masked dynamic mismatch count drifted: "
        f"{source_donor_masked_dynamic_mismatch_count}",
    )
    require(
        any_base_exact_dynamic_match_count == EXPECTED_ANY_BASE_EXACT_DYNAMIC_MATCH,
        f"any-Base exact dynamic match count drifted: {any_base_exact_dynamic_match_count}",
    )
    require(
        any_base_masked_dynamic_match_count == EXPECTED_ANY_BASE_MASKED_DYNAMIC_MATCH,
        "any-Base operand-masked dynamic match count drifted: "
        f"{any_base_masked_dynamic_match_count}",
    )
    require(
        any_base_masked_dynamic_novel_count
        == EXPECTED_ANY_BASE_MASKED_DYNAMIC_NOVEL,
        "any-Base operand-masked dynamic novel count drifted: "
        f"{any_base_masked_dynamic_novel_count}",
    )

    mapping_source = [
        {
            "pk_coordinate": row["coordinate"],
            "base_coordinate": row["base_exact_reuse_prefill"]["base_coordinate"],
            "source_utf16le_sha256": row["base_exact_reuse_prefill"]["source_utf16le_sha256"],
            "translation_utf16le_sha256": row["base_exact_reuse_prefill"][
                "translation_utf16le_sha256"
            ],
            "masked_template_match": row["base_exact_reuse_prefill"][
                "exact_source_donor_operand_masked_template_match"
            ],
            "any_base_exact_template_match": row["base_exact_reuse_prefill"][
                "any_base_candidate_exact_gap_template_match"
            ],
            "any_base_masked_template_match": row["base_exact_reuse_prefill"][
                "any_base_candidate_operand_masked_gap_template_match"
            ],
        }
        for row in rows
    ]
    mapping_sha256 = canonical_sha256(mapping_source)
    for row in rows:
        row["base_exact_reuse_prefill"]["mapping_universe_sha256"] = mapping_sha256

    replacements = {
        coordinate_key(row["coordinate"]): row["translation"]
        for row in rows
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = ENGINE.rebuild_packed_with_literals(current_blob, replacements)
    candidate_records = record_map(ENGINE.parse_packed_msggame(candidate).archive)
    targeted_records = {(key[0], key[1]) for key in replacements}
    for record_key, current_record in pk_current_records.items():
        candidate_record = candidate_records[record_key]
        if record_key not in targeted_records:
            require(
                candidate_record.data == current_record.data,
                f"candidate changed outside scope: {record_key}",
            )
        else:
            require(
                literal_gaps(candidate_record) == literal_gaps(current_record),
                f"candidate changed PK bytecode gaps: {record_key}",
            )
    reverse = {
        key: ENGINE.parse_record_literals(pk_current_records[key[:2]])[key[2]].text
        for key in replacements
    }
    require(
        ENGINE.rebuild_packed_with_literals(candidate, reverse) == current_blob,
        "PK candidate reverse overlay drifted",
    )
    for key, translation in replacements.items():
        require(
            ENGINE.parse_record_literals(candidate_records[key[:2]])[key[2]].text
            == translation,
            f"PK candidate translation drifted: {key}",
        )

    report = {
        "schema": SCHEMA,
        "status": "PASS",
        "existing_pk_decisions_excluded": len(existing),
        "remaining_pk_rows": funnel["remaining"],
        "funnel": dict(funnel),
        "prefilled_rows": len(rows),
        "rough_static_rows": rough_static_count,
        "rough_dynamic_pending_rows": rough_dynamic_count,
        "exact_source_donor_operand_masked_dynamic_match_rows": masked_dynamic_count,
        "exact_source_donor_operand_masked_dynamic_mismatch_rows": (
            source_donor_masked_dynamic_mismatch_count
        ),
        "any_base_candidate_exact_dynamic_match_rows": (
            any_base_exact_dynamic_match_count
        ),
        "any_base_candidate_operand_masked_dynamic_match_rows": (
            any_base_masked_dynamic_match_count
        ),
        "any_base_candidate_operand_masked_dynamic_novel_rows": (
            any_base_masked_dynamic_novel_count
        ),
        "layout_change_pending_rows": sum(
            row["base_exact_reuse_prefill"]["layout_change_pending"]
            for row in rows
        ),
        "actual_runtime_pending_rows": sum(
            row["runtime_review"] == "pending"
            for row in rows
        ),
        "mapping_universe_sha256": mapping_sha256,
        "candidate_packed_sha256": sha256_bytes(candidate),
        "base_candidate_packed_sha256": base_candidate_sha256,
        "runtime_promotion_performed": False,
        "steam_write_performed": False,
    }
    return prepared, rows, candidate, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="reproduce and compare the private decisions and source-free report",
    )
    args = parser.parse_args()

    first = build_rows()
    second = build_rows()
    prepared, rows, candidate, report = first
    require(ENGINE.jsonl(rows) == ENGINE.jsonl(second[1]), "row reproduction drifted")
    require(candidate == second[2], "candidate reproduction drifted")
    require(report == second[3], "report reproduction drifted")
    decision_content = ENGINE.jsonl(rows)
    report_content = json.dumps(
        report,
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
    ) + "\n"
    if args.check:
        require(OUTPUT.is_file(), f"private prefill output is absent: {OUTPUT}")
        require(
            OUTPUT.read_text(encoding="utf-8") == decision_content,
            "private prefill output drifted",
        )
        require(PUBLIC_REPORT.is_file(), f"public report is absent: {PUBLIC_REPORT}")
        require(
            PUBLIC_REPORT.read_text(encoding="utf-8") == report_content,
            "source-free prefill report drifted",
        )
    else:
        ENGINE.atomic_write(OUTPUT, decision_content)
        ENGINE.atomic_write(PUBLIC_REPORT, report_content)
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    require(len(validated) == EXPECTED_ROWS, "engine validation count drifted")
    print(
        json.dumps(
            {
                **report,
                "mode": "check" if args.check else "write",
                "output": str(OUTPUT),
                "public_report": str(PUBLIC_REPORT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, PrefillError, ENGINE.RetranslationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
