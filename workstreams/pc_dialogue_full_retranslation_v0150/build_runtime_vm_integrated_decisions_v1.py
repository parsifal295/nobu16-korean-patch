#!/usr/bin/env python3
"""Integrate proved Base/PK VM promotions into one private decision universe.

The dialogue-bearing merged JSONL remains below ``tmp/``.  The tracked report
contains only coordinates, counts, and cryptographic guards.  This builder
never writes the Steam installation and deliberately leaves unproved PK rows
pending.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name
DECISIONS_DIR = OUTPUT_ROOT / "decisions"
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
PROGRESS_BUILDER_PATH = WORKSTREAM / "build_progress_source_free_v0150.py"
CONTROL_REPAIRS_PATH = WORKSTREAM / "runtime_control_repairs.source_free.v1.json"
BASE_VERIFIED_PATH = OUTPUT_ROOT / "base_msggame_runtime_vm_verified.private.v1.jsonl"
BASE_PROMOTION_PATH = (
    REPO
    / "workstreams"
    / "base_msggame_runtime_vm_audit_v1"
    / "public"
    / "base_msggame_runtime_vm_promotion.v1.json"
)
PK_OVERLAY_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "build_pk_msggame_runtime_verified_overlay_v1.py"
)
PK_OVERLAY_PATH = (
    DECISIONS_DIR
    / "runtime_verification_overlays"
    / "pk_msggame_exact_reuse_runtime_vm_verified.private.v1.jsonl"
)
PK_PROMOTION_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_msggame_runtime_vm_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = OUTPUT_ROOT / "runtime_vm_integrated.private.v1.jsonl"
DEFAULT_PUBLIC_OUTPUT = WORKSTREAM / "runtime_vm_integration.source_free.v1.json"

SCHEMA = "nobu16.kr.pc-dialogue-runtime-vm-integration.v1"
CONTROL_REPAIRS_SCHEMA = (
    "nobu16.kr.pc-dialogue-full-retranslation-runtime-control-repairs.v1"
)
EXPECTED_VISIBLE_ROWS = 52_803
EXPECTED_BASE_ROWS = 23_765
EXPECTED_PK_ROWS = 29_038
EXPECTED_BASE_PROMOTIONS = 15_651
EXPECTED_PK_AUDIT_PROMOTIONS = 4_717
EXPECTED_PK_INTEGRATED_PROMOTIONS = 4_669
EXPECTED_PK_FULL_CANDIDATE_SIBLING_EXCLUSIONS = 48
EXPECTED_PK_FULL_CANDIDATE_SIBLING_EXCLUSION_DIGEST = (
    "DD24887C06E3F0C6738EF5425A1C49BA3883D92B08E9522A65C4B6B5E7C0C559"
)
EXPECTED_PENDING_AFTER = 16_015
RUNTIME_MUTABLE_FIELDS = frozenset(
    {
        "scope_classification",
        "runtime_review",
        "runtime_vm_verification",
    }
)


class IntegrationError(ValueError):
    """Raised when a decision or verification binding drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise IntegrationError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module("pc_dialogue_runtime_vm_integration_engine", ENGINE_PATH)
PK_OVERLAY = load_module(
    "pc_dialogue_runtime_vm_integration_pk_overlay",
    PK_OVERLAY_BUILDER_PATH,
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def canonical_jsonl(rows: Sequence[Mapping[str, Any]]) -> str:
    return "".join(
        json.dumps(
            row,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for row in rows
    )


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"required JSON is absent: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    require(path.is_file(), f"required JSONL is absent: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line:
            continue
        value = json.loads(line)
        require(
            isinstance(value, dict),
            f"{path}:{line_number} is not an object",
        )
        rows.append(value)
    return rows


def coordinate_sort_key(row: Mapping[str, Any]) -> tuple[int, int, int, int]:
    resource = str(row["resource"])
    resource_ordinal = 0 if resource == "base_msggame" else 1
    coordinate = ENGINE.parse_coordinate(
        row.get("coordinate"),
        "decision.coordinate",
    )
    return (resource_ordinal, *coordinate)


def immutable_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in row.items()
        if key not in RUNTIME_MUTABLE_FIELDS
    }


def segment_id(path: Path) -> str:
    suffix = ".private.v1.jsonl"
    require(path.name.endswith(suffix), f"unexpected decision filename: {path}")
    return path.name[: -len(suffix)]


def load_source_decisions(
    prepared: Any,
) -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[str, Path],
    str,
]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    segment_paths: dict[str, Path] = {}
    segment_guards: list[dict[str, Any]] = []
    paths = sorted(DECISIONS_DIR.glob("*.private.v1.jsonl"))
    require(paths, f"no source decision segments below {DECISIONS_DIR}")
    for path in paths:
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        identifier = segment_id(path)
        require(identifier not in segment_paths, f"duplicate segment id: {identifier}")
        segment_paths[identifier] = path
        file_rows = load_jsonl(path)
        for row in file_rows:
            key = (str(row["resource"]), str(row["coordinate"]))
            require(key not in rows, f"duplicate source decision coordinate: {key}")
            rows[key] = row
        segment_guards.append(
            {
                "segment_id": identifier,
                "row_count": len(file_rows),
                "sha256": sha256_bytes(path.read_bytes()),
            }
        )
    require(
        len(rows) == EXPECTED_VISIBLE_ROWS,
        f"source decision universe drifted: {len(rows)}",
    )
    return rows, segment_paths, canonical_sha256(segment_guards)


def validate_runtime_only_transition(
    original: Mapping[str, Any],
    promoted: Mapping[str, Any],
    *,
    label: str,
) -> None:
    require(
        immutable_row(original) == immutable_row(promoted),
        f"{label} changed a semantic or layout decision",
    )


def load_control_repairs(
    source_rows: Mapping[tuple[str, str], dict[str, Any]],
    segment_paths: Mapping[str, Path],
) -> tuple[dict[tuple[str, str], dict[str, Any]], dict[str, Any]]:
    ledger = load_json(CONTROL_REPAIRS_PATH)
    require(
        ledger.get("schema") == CONTROL_REPAIRS_SCHEMA
        and ledger.get("release_target") == "0.15.0"
        and ledger.get("source_text_present") is False
        and ledger.get("semantic_decision_count_delta") == 0,
        "runtime control repair ledger metadata drifted",
    )
    entries = ledger.get("entries")
    require(isinstance(entries, list), "runtime control repair entries are absent")
    repairs: dict[tuple[str, str], dict[str, Any]] = {}
    for entry in entries:
        require(isinstance(entry, dict), "runtime control repair entry is malformed")
        key = (str(entry.get("resource")), str(entry.get("coordinate")))
        require(key in source_rows and key not in repairs, f"invalid repair key: {key}")
        source = source_rows[key]
        identifier = str(entry.get("source_decision_segment_id"))
        path = segment_paths.get(identifier)
        require(path is not None, f"repair source segment is absent: {identifier}")
        require(
            entry.get("source_decision_file_sha256")
            == sha256_bytes(path.read_bytes())
            and entry.get("source_decision_row_canonical_sha256")
            == canonical_sha256(source)
            and entry.get("original_scope_classification")
            == source.get("scope_classification")
            and entry.get("original_runtime_review")
            == source.get("runtime_review")
            and entry.get("repair_candidate_required_for_release") is True
            and entry.get("steam_write_performed") is False,
            f"runtime control repair source binding drifted: {key}",
        )
        repairs[key] = entry
    return repairs, {
        "entry_count": len(repairs),
        "sha256": sha256_bytes(CONTROL_REPAIRS_PATH.read_bytes()),
    }


def validated_base_rows(
    prepared: Any,
    source_rows: Mapping[tuple[str, str], dict[str, Any]],
) -> tuple[dict[tuple[str, str], dict[str, Any]], dict[str, Any]]:
    promotion = load_json(BASE_PROMOTION_PATH)
    require(
        promotion.get("schema")
        == "nobu16.kr.base-msggame-runtime-vm-promotion.v1"
        and promotion.get("status") == "PASS"
        and promotion.get("steam_write_performed") is False,
        "Base VM promotion report drifted",
    )
    rows = load_jsonl(BASE_VERIFIED_PATH)
    require(len(rows) == EXPECTED_BASE_ROWS, "Base verified row count drifted")
    ENGINE.validate_decisions(prepared, BASE_VERIFIED_PATH, require_complete=False)
    result: dict[tuple[str, str], dict[str, Any]] = {}
    promoted_count = 0
    for row in rows:
        key = (str(row["resource"]), str(row["coordinate"]))
        require(key[0] == "base_msggame", f"non-Base row in Base merge: {key}")
        original = source_rows.get(key)
        require(original is not None, f"Base source row is absent: {key}")
        validate_runtime_only_transition(original, row, label=f"Base {key[1]}")
        if original["runtime_review"] == "pending":
            require(
                row.get("runtime_review") == "verified"
                and row.get("scope_classification") == "retranslated"
                and isinstance(row.get("runtime_vm_verification"), dict),
                f"Base pending row was not proved: {key}",
            )
            promoted_count += 1
        else:
            require(
                row.get("runtime_review") == original.get("runtime_review")
                and row.get("scope_classification")
                == original.get("scope_classification"),
                f"Base eligible row changed state: {key}",
            )
        require(key not in result, f"duplicate Base merged row: {key}")
        result[key] = row
    require(
        promoted_count == EXPECTED_BASE_PROMOTIONS,
        f"Base promotion count drifted: {promoted_count}",
    )
    require(
        promotion.get("result", {}).get("private_merged_decision_sha256")
        == sha256_bytes(BASE_VERIFIED_PATH.read_bytes()),
        "Base private merged file hash drifted",
    )
    return result, {
        "promotion_count": promoted_count,
        "private_sha256": sha256_bytes(BASE_VERIFIED_PATH.read_bytes()),
        "promotion_report_sha256": sha256_bytes(BASE_PROMOTION_PATH.read_bytes()),
    }


def validated_pk_overlay() -> tuple[
    dict[str, dict[str, Any]],
    dict[str, Any],
    Any,
]:
    inputs, coverage, coverage_file_sha256 = PK_OVERLAY.verified_audit()
    rows = PK_OVERLAY.read_overlay(PK_OVERLAY_PATH)
    PK_OVERLAY.validate_overlay_rows(
        rows,
        inputs=inputs,
        report=coverage,
        report_file_sha256=coverage_file_sha256,
    )
    promotion = load_json(PK_PROMOTION_PATH)
    require(
        promotion.get("schema")
        == "nobu16.kr.pk-msggame-runtime-vm-promotion.v1"
        and promotion.get("status") == "PASS"
        and promotion.get("steam_write_performed") is False
        and promotion.get("result", {}).get("private_overlay_sha256")
        == sha256_bytes(PK_OVERLAY_PATH.read_bytes()),
        "PK VM promotion report drifted",
    )
    by_coordinate = {str(row["coordinate"]): row for row in rows}
    require(
        len(by_coordinate) == len(rows) == EXPECTED_PK_AUDIT_PROMOTIONS,
        "PK VM overlay completeness drifted",
    )
    return by_coordinate, {
        "audit_promotion_eligible_count": len(rows),
        "private_sha256": sha256_bytes(PK_OVERLAY_PATH.read_bytes()),
        "promotion_report_sha256": sha256_bytes(PK_PROMOTION_PATH.read_bytes()),
        "coverage_file_sha256": coverage_file_sha256,
    }, inputs


def validate_combined_private(
    prepared: Any,
    content: str,
    private_output: Path,
) -> None:
    private_output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{private_output.name}.validate.",
        suffix=".jsonl",
        dir=private_output.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        ENGINE.validate_decisions(prepared, temporary, require_complete=False)
    finally:
        temporary.unlink(missing_ok=True)


def build_outputs(
    *,
    steam_root: Path,
    base_pristine: Path,
    pk_pristine: Path,
    private_output: Path,
) -> tuple[str, str, dict[str, Any]]:
    prepared = ENGINE.prepare_artifacts(steam_root, base_pristine, pk_pristine)
    source_rows, segment_paths, segment_universe_sha256 = load_source_decisions(
        prepared
    )
    raw_counts = Counter(
        (str(row["resource"]), str(row["runtime_review"]))
        for row in source_rows.values()
    )
    repairs, repair_metadata = load_control_repairs(source_rows, segment_paths)
    merged = {key: dict(row) for key, row in source_rows.items()}
    for key, entry in repairs.items():
        merged[key]["scope_classification"] = entry[
            "effective_scope_classification"
        ]
        merged[key]["runtime_review"] = entry["effective_runtime_review"]

    effective_pending_before = sum(
        row["runtime_review"] == "pending" for row in merged.values()
    )
    base_rows, base_metadata = validated_base_rows(prepared, source_rows)
    merged.update(base_rows)

    pk_overlay, pk_metadata, pk_audit_inputs = validated_pk_overlay()
    pk_literal_replacements = {
        ENGINE.parse_coordinate(
            row["coordinate"],
            "PK integrated decision.coordinate",
        ): row["translation"]
        for row in merged.values()
        if row["resource"] == "pk_msggame"
        and isinstance(row.get("translation"), str)
    }
    full_pk_candidate = ENGINE.rebuild_packed_with_literals(
        prepared.resources["pk_msggame"].current_blob,
        pk_literal_replacements,
    )
    full_pk_candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(full_pk_candidate).archive
    )
    sibling_exclusions: list[str] = []
    pk_integrated_promotions = 0
    for coordinate, evidence in pk_overlay.items():
        key = ("pk_msggame", coordinate)
        row = merged.get(key)
        require(row is not None, f"PK overlay decision is absent: {coordinate}")
        require(
            row.get("scope_classification") == "runtime_fragment_pending"
            and row.get("runtime_review") == "pending"
            and ENGINE.sha256_text(str(row.get("translation")))
            == evidence.get("translation_utf16le_sha256"),
            f"PK overlay source decision drifted: {coordinate}",
        )
        block_id, record_id, _literal_id = ENGINE.parse_coordinate(
            coordinate,
            "PK overlay.coordinate",
        )
        record_key = (block_id, record_id)
        if (
            full_pk_candidate_records[record_key].data
            != pk_audit_inputs.pk_candidate_records[record_key].data
        ):
            sibling_exclusions.append(coordinate)
            continue
        promoted = dict(row)
        promoted["scope_classification"] = "retranslated"
        promoted["runtime_review"] = "verified"
        promoted["runtime_vm_verification"] = evidence
        validate_runtime_only_transition(
            row,
            promoted,
            label=f"PK {coordinate}",
        )
        merged[key] = promoted
        pk_integrated_promotions += 1

    sibling_exclusion_digest = sha256_bytes(
        "\n".join(sibling_exclusions).encode("ascii")
    )
    require(
        len(sibling_exclusions)
        == EXPECTED_PK_FULL_CANDIDATE_SIBLING_EXCLUSIONS
        and sibling_exclusion_digest
        == EXPECTED_PK_FULL_CANDIDATE_SIBLING_EXCLUSION_DIGEST,
        "PK full-candidate sibling exclusion universe drifted",
    )
    require(
        pk_integrated_promotions == EXPECTED_PK_INTEGRATED_PROMOTIONS,
        f"PK integrated promotion count drifted: {pk_integrated_promotions}",
    )
    pk_metadata.update(
        {
            "promotion_count": pk_integrated_promotions,
            "full_candidate_sibling_exclusion_count": len(
                sibling_exclusions
            ),
            "full_candidate_sibling_exclusion_coordinate_digest_sha256":
            sibling_exclusion_digest,
            "full_candidate_record_hashes_rechecked": True,
        }
    )

    rows = sorted(merged.values(), key=coordinate_sort_key)
    require(len(rows) == EXPECTED_VISIBLE_ROWS, "integrated row universe drifted")
    resource_counts = Counter(str(row["resource"]) for row in rows)
    require(
        resource_counts
        == {
            "base_msggame": EXPECTED_BASE_ROWS,
            "pk_msggame": EXPECTED_PK_ROWS,
        },
        f"integrated resource counts drifted: {resource_counts}",
    )
    pending_after = sum(row["runtime_review"] == "pending" for row in rows)
    require(
        pending_after == EXPECTED_PENDING_AFTER,
        f"integrated pending count drifted: {pending_after}",
    )
    private_content = canonical_jsonl(rows)
    validate_combined_private(prepared, private_content, private_output)
    private_sha256 = sha256_bytes(private_content.encode("utf-8"))
    coordinate_universe_sha256 = sha256_bytes(
        "\n".join(
            f"{row['resource']}:{row['coordinate']}" for row in rows
        ).encode("ascii")
    )
    report = {
        "schema": SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "input": {
            "visible_decision_rows": len(source_rows),
            "base_rows": raw_counts[("base_msggame", "pending")]
            + raw_counts[("base_msggame", "verified")]
            + raw_counts[("base_msggame", "not_required")],
            "pk_rows": raw_counts[("pk_msggame", "pending")]
            + raw_counts[("pk_msggame", "verified")]
            + raw_counts[("pk_msggame", "not_required")],
            "raw_runtime_pending": sum(
                count
                for (resource, state), count in raw_counts.items()
                if state == "pending"
            ),
            "effective_runtime_pending_after_control_repairs":
            effective_pending_before,
            "source_segment_universe_sha256": segment_universe_sha256,
            "runtime_control_repairs": repair_metadata,
        },
        "promotions": {
            "base_msggame": base_metadata,
            "pk_msggame": pk_metadata,
            "promoted_total": (
                base_metadata["promotion_count"]
                + pk_metadata["promotion_count"]
            ),
        },
        "result": {
            "private_integrated_decision_sha256": private_sha256,
            "coordinate_universe_sha256": coordinate_universe_sha256,
            "semantic_review_approved": len(rows),
            "runtime_review_pending": pending_after,
            "fully_candidate_eligible": len(rows) - pending_after,
            "candidate_ready": pending_after == 0,
        },
        "validation": {
            "normal_v0150_decision_validator_rechecked": True,
            "runtime_only_transitions_enforced": True,
            "base_candidate_record_guards_rechecked": True,
            "pk_overlay_rebuilt_and_rechecked": True,
            "pk_full_candidate_sibling_records_rechecked": True,
            "control_repair_bindings_rechecked": True,
            "per_row_game_playback_required_for_promotions": False,
            "representative_game_smoke_test_required_before_release": True,
        },
        "distribution_policy": {
            "private_integrated_decision_stays_below_tmp": True,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
        },
        "steam_write_performed": False,
    }
    return private_content, canonical_json(report), report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=ENGINE.DEFAULT_STEAM_ROOT)
    parser.add_argument(
        "--base-pristine",
        type=Path,
        default=ENGINE.DEFAULT_BASE_PRISTINE,
    )
    parser.add_argument(
        "--pk-pristine",
        type=Path,
        default=ENGINE.DEFAULT_PK_PRISTINE,
    )
    parser.add_argument(
        "--private-output",
        type=Path,
        default=DEFAULT_PRIVATE_OUTPUT,
    )
    parser.add_argument(
        "--public-output",
        type=Path,
        default=DEFAULT_PUBLIC_OUTPUT,
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")
    private_root = OUTPUT_ROOT.resolve(strict=False)
    resolved_private = args.private_output.resolve(strict=False)
    require(
        resolved_private != private_root and private_root in resolved_private.parents,
        f"private output must remain below {private_root}",
    )
    private_content, public_content, report = build_outputs(
        steam_root=args.steam_root,
        base_pristine=args.base_pristine,
        pk_pristine=args.pk_pristine,
        private_output=args.private_output,
    )
    if args.write:
        ENGINE.atomic_write(args.private_output, private_content)
        ENGINE.atomic_write(args.public_output, public_content)
    if args.check:
        require(
            args.private_output.is_file()
            and args.private_output.read_text(encoding="utf-8")
            == private_content,
            "private integrated decision file drifted",
        )
        require(
            args.public_output.is_file()
            and args.public_output.read_text(encoding="utf-8")
            == public_content,
            "source-free VM integration report drifted",
        )
    print(
        "PASS "
        f"rows={report['result']['semantic_review_approved']} "
        f"promoted={report['promotions']['promoted_total']} "
        f"pending={report['result']['runtime_review_pending']} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, IntegrationError, ENGINE.RetranslationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
