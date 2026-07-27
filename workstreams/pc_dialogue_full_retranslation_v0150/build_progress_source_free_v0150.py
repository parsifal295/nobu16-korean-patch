#!/usr/bin/env python3
"""Build and validate the source-free v0.15.0 retranslation progress ledger."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name
DECISIONS_DIR = OUTPUT_ROOT / "decisions"
QUEUE_PATH = OUTPUT_ROOT / "review_queue.private.v1.jsonl"
BATCHES_PATH = OUTPUT_ROOT / "review_batches.source_free.v1.json"
CANDIDATE_MANIFEST = OUTPUT_ROOT / "candidate" / "candidate_manifest.source_free.v1.json"
PROGRESS_PATH = WORKSTREAM / "progress.source_free.v1.json"
CONTROL_REPAIRS_PATH = WORKSTREAM / "runtime_control_repairs.source_free.v1.json"
RUNTIME_VM_INTEGRATED_DECISIONS = (
    OUTPUT_ROOT / "runtime_vm_integrated.private.v1.jsonl"
)
RUNTIME_VM_INTEGRATION_REPORT = (
    WORKSTREAM / "runtime_vm_integration.source_free.v1.json"
)
SEMANTIC_OVERRIDE_BUILDER_PATH = (
    WORKSTREAM / "build_pk_semantic_flattening_override_3421_v1.py"
)
SEMANTIC_OVERRIDE_PRIVATE_PATH = (
    OUTPUT_ROOT
    / "semantic_overrides"
    / "pk_msggame_3421_semantic_override.private.v1.jsonl"
)
SEMANTIC_OVERRIDE_PUBLIC_PATH = (
    WORKSTREAM / "pk_semantic_flattening_3421.source_free.v1.json"
)
REFLOW_OVERRIDE_LOADER_PATH = (
    WORKSTREAM / "load_pk_relative_reflow_override_v1.py"
)
CONTROL_REPAIRS_SCHEMA = (
    "nobu16.kr.pc-dialogue-full-retranslation-runtime-control-repairs.v1"
)
RUNTIME_VM_INTEGRATION_SCHEMA = (
    "nobu16.kr.pc-dialogue-runtime-vm-integration.v1"
)
RUNTIME_REVIEW_STATES = {"not_required", "verified", "pending"}
BOUND_TERMINAL_OVERRIDE_COORDINATES = frozenset(
    {
        ("pk_msggame", f"0:{record_id}:0")
        for record_id in (
            *range(1916, 1923),
            *range(2546, 2553),
        )
    }
)


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_progress_engine", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


def load_semantic_override_builder() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_progress_semantic_override",
        SEMANTIC_OVERRIDE_BUILDER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"cannot import {SEMANTIC_OVERRIDE_BUILDER_PATH}"
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SEMANTIC_OVERRIDE = load_semantic_override_builder()


def load_reflow_override_loader() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_progress_relative_reflow_override",
        REFLOW_OVERRIDE_LOADER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"cannot import {REFLOW_OVERRIDE_LOADER_PATH}"
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


REFLOW_OVERRIDE = load_reflow_override_loader()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise RuntimeError(f"required JSONL is absent: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RuntimeError(f"{path}:{line_number} is not a JSON object")
        rows.append(value)
    return rows


def coordinate_key(value: str) -> tuple[int, int, int]:
    parts = tuple(int(part) for part in value.split(":"))
    if len(parts) != 3:
        raise RuntimeError(f"invalid decision coordinate: {value}")
    return parts


def batch_key(value: str) -> tuple[str, int]:
    resource, ordinal = value.rsplit("-B", 1)
    return resource, int(ordinal)


def segment_id(path: Path) -> str:
    suffix = ".private.v1.jsonl"
    if not path.name.endswith(suffix):
        raise RuntimeError(f"unexpected decision filename: {path.name}")
    return path.name[: -len(suffix)]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_row_sha256(row: dict[str, Any]) -> str:
    encoded = json.dumps(
        row,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(encoded)


def coordinate_digest(values: Sequence[str]) -> str:
    coordinates = sorted(set(values), key=coordinate_key)
    return sha256_bytes(
        "".join(f"{coordinate}\n" for coordinate in coordinates).encode(
            "ascii"
        )
    )


def runtime_immutable_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in row.items()
        if key
        not in {
            "scope_classification",
            "layout_review",
            "runtime_review",
            "runtime_vm_verification",
            "terminal_family_runtime_evidence",
            "terminal_family_update_action",
            "terminal_family_exact_override_evidence",
            "thought_predicate_family_update_action",
        }
    }


def load_runtime_vm_integration(
    prepared: Any,
) -> tuple[dict[tuple[str, str], dict[str, Any]], dict[str, Any]]:
    if not RUNTIME_VM_INTEGRATION_REPORT.is_file():
        raise RuntimeError(
            "source-free runtime VM integration report is absent: "
            f"{RUNTIME_VM_INTEGRATION_REPORT}"
        )
    if not RUNTIME_VM_INTEGRATED_DECISIONS.is_file():
        raise RuntimeError(
            "private runtime VM integrated decisions are absent: "
            f"{RUNTIME_VM_INTEGRATED_DECISIONS}"
        )
    report_bytes = RUNTIME_VM_INTEGRATION_REPORT.read_bytes()
    report = json.loads(report_bytes.decode("utf-8"))
    if (
        not isinstance(report, dict)
        or report.get("schema") != RUNTIME_VM_INTEGRATION_SCHEMA
        or report.get("status") != "PASS"
        or report.get("release_target") != "0.15.0"
        or report.get("steam_write_performed") is not False
    ):
        raise RuntimeError("runtime VM integration report metadata drifted")
    private_sha256 = sha256_bytes(RUNTIME_VM_INTEGRATED_DECISIONS.read_bytes())
    result = report.get("result")
    if (
        not isinstance(result, dict)
        or result.get("private_integrated_decision_sha256") != private_sha256
        or result.get("semantic_review_approved")
        != len(prepared.visible_targets)
    ):
        raise RuntimeError("runtime VM integrated decision guard drifted")
    ENGINE.validate_decisions(
        prepared,
        RUNTIME_VM_INTEGRATED_DECISIONS,
        require_complete=False,
    )
    rows = load_jsonl(RUNTIME_VM_INTEGRATED_DECISIONS)
    by_coordinate: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (str(row["resource"]), str(row["coordinate"]))
        if key in by_coordinate:
            raise RuntimeError(
                f"duplicate runtime VM integrated decision: {key}"
            )
        by_coordinate[key] = row
    pending = sum(
        row.get("runtime_review") == "pending"
        for row in by_coordinate.values()
    )
    if (
        len(by_coordinate) != len(prepared.visible_targets)
        or result.get("runtime_review_pending") != pending
        or result.get("fully_candidate_eligible")
        != len(by_coordinate) - pending
    ):
        raise RuntimeError("runtime VM integration result counts drifted")
    metadata = {
        "path": RUNTIME_VM_INTEGRATION_REPORT.relative_to(REPO).as_posix(),
        "schema": RUNTIME_VM_INTEGRATION_SCHEMA,
        "sha256": sha256_bytes(report_bytes),
        "private_integrated_decision_sha256": private_sha256,
        "promoted_total": report["promotions"]["promoted_total"],
        "runtime_review_pending_after": pending,
        "bound_terminal_family_layer_included": report["promotions"][
            "pk_msggame"
        ].get("bound_terminal_family_layer_included")
        is True,
        "bound_terminal_family": report["promotions"]["pk_msggame"].get(
            "bound_terminal_family"
        ),
        "thought_predicate_family_layer_included": report["promotions"][
            "pk_msggame"
        ].get("thought_predicate_family_layer_included")
        is True,
        "thought_predicate_family": report["promotions"]["pk_msggame"].get(
            "thought_predicate_family"
        ),
        "steam_write_performed": False,
    }
    return by_coordinate, metadata


def load_control_repairs() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[str, Any],
]:
    if not CONTROL_REPAIRS_PATH.is_file():
        raise RuntimeError(
            "source-free runtime control repair ledger is absent: "
            f"{CONTROL_REPAIRS_PATH}"
        )
    raw_bytes = CONTROL_REPAIRS_PATH.read_bytes()
    ledger = json.loads(raw_bytes.decode("utf-8"))
    if not isinstance(ledger, dict):
        raise RuntimeError("runtime control repair ledger is not a JSON object")
    if (
        ledger.get("schema") != CONTROL_REPAIRS_SCHEMA
        or ledger.get("release_target") != "0.15.0"
        or ledger.get("source_text_present") is not False
        or ledger.get("semantic_decision_count_delta") != 0
    ):
        raise RuntimeError("runtime control repair ledger metadata drifted")
    entries = ledger.get("entries")
    if not isinstance(entries, list):
        raise RuntimeError("runtime control repair entries are not a list")

    repairs: dict[tuple[str, str], dict[str, Any]] = {}
    required_keys = {
        "resource",
        "coordinate",
        "record_coordinate",
        "source_decision_segment_id",
        "source_decision_file_sha256",
        "source_decision_row_canonical_sha256",
        "original_scope_classification",
        "original_runtime_review",
        "effective_scope_classification",
        "effective_runtime_review",
        "override_reason",
        "repair_builder",
        "repair_evidence_schema",
        "repair_candidate_sha256",
        "repair_candidate_required_for_release",
        "repair_candidate_application_forbidden",
        "repair_status",
        "adjudication",
        "semantic_decision_duplicate_added",
        "steam_write_performed",
    }
    allowed_keys = required_keys | {"semantic_override_report"}
    for ordinal, entry in enumerate(entries):
        if (
            not isinstance(entry, dict)
            or not required_keys.issubset(entry)
            or not set(entry).issubset(allowed_keys)
        ):
            raise RuntimeError(
                f"runtime control repair entry {ordinal} shape drifted"
            )
        resource = str(entry["resource"])
        coordinate = str(entry["coordinate"])
        parts = coordinate_key(coordinate)
        if str(entry["record_coordinate"]) != f"{parts[0]}:{parts[1]}":
            raise RuntimeError(
                f"runtime control repair record coordinate drifted: {coordinate}"
            )
        original_scope = str(entry["original_scope_classification"])
        effective_scope = str(entry["effective_scope_classification"])
        original_runtime = str(entry["original_runtime_review"])
        effective_runtime = str(entry["effective_runtime_review"])
        if (
            original_scope not in ENGINE.SCOPE_CLASSIFICATIONS
            or effective_scope not in ENGINE.SCOPE_CLASSIFICATIONS
            or original_runtime not in RUNTIME_REVIEW_STATES
            or effective_runtime not in RUNTIME_REVIEW_STATES
        ):
            raise RuntimeError(
                f"runtime control repair classification is invalid: "
                f"{resource}:{coordinate}"
            )
        if (
            entry["semantic_decision_duplicate_added"] is not False
            or entry["steam_write_performed"] is not False
            or entry["repair_candidate_required_for_release"] is not False
            or entry["repair_candidate_application_forbidden"] is not True
            or entry["repair_status"] != "rejected_not_required"
            or entry["adjudication"] != "repair_not_required"
            or effective_scope != original_scope
            or effective_runtime != original_runtime
        ):
            raise RuntimeError(
                f"runtime control repair safety state drifted: "
                f"{resource}:{coordinate}"
            )
        key = (resource, coordinate)
        if key in repairs:
            raise RuntimeError(f"duplicate runtime control repair: {key}")
        repairs[key] = entry

    metadata = {
        "path": CONTROL_REPAIRS_PATH.relative_to(REPO).as_posix(),
        "schema": CONTROL_REPAIRS_SCHEMA,
        "sha256": sha256_bytes(raw_bytes),
        "source_text_present": False,
        "entry_count": len(entries),
        "semantic_decision_count_delta": 0,
    }
    return repairs, metadata


def load_semantic_override() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[str, Any],
]:
    private_content, public_content, report, row = (
        SEMANTIC_OVERRIDE.build_outputs()
    )
    SEMANTIC_OVERRIDE.validate_outputs(
        private_content,
        public_content,
        report,
        row,
    )
    if (
        not SEMANTIC_OVERRIDE_PRIVATE_PATH.is_file()
        or SEMANTIC_OVERRIDE_PRIVATE_PATH.read_text(encoding="utf-8")
        != private_content
        or not SEMANTIC_OVERRIDE_PUBLIC_PATH.is_file()
        or SEMANTIC_OVERRIDE_PUBLIC_PATH.read_text(encoding="utf-8")
        != public_content
    ):
        raise RuntimeError("semantic override artifacts drifted")
    key = (str(row["resource"]), str(row["coordinate"]))
    if (
        key != ("pk_msggame", "6:3421:0")
        or row.get("semantic_review") != "approved"
    ):
        raise RuntimeError("semantic override row contract drifted")
    return {key: row}, {
        "coordinate": key[1],
        "override_count": 1,
        "private_sha256": sha256_bytes(
            private_content.encode("utf-8")
        ),
        "public_report_sha256": sha256_bytes(
            public_content.encode("utf-8")
        ),
        "report_payload_sha256": report["report_payload_sha256"],
    }


def build_progress() -> dict[str, Any]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    decision_paths = sorted(DECISIONS_DIR.glob("*.private.v1.jsonl"))
    if not decision_paths:
        raise RuntimeError(f"no private decision segments found below {DECISIONS_DIR}")
    control_repairs, control_repair_metadata = load_control_repairs()
    consumed_control_repairs: set[tuple[str, str]] = set()
    semantic_overrides, semantic_override_metadata = (
        load_semantic_override()
    )
    consumed_semantic_overrides: set[tuple[str, str]] = set()
    pk_effective_source_rows: list[dict[str, Any]] = []
    for path in decision_paths:
        for row in load_jsonl(path):
            if row.get("resource") != "pk_msggame":
                continue
            key = ("pk_msggame", str(row["coordinate"]))
            pk_effective_source_rows.append(
                semantic_overrides.get(key, row)
            )
    (
        reflow_by_coordinate,
        relative_reflow_metadata,
    ) = REFLOW_OVERRIDE.load_overrides(pk_effective_source_rows)
    reflow_overrides = {
        ("pk_msggame", coordinate): row
        for coordinate, row in reflow_by_coordinate.items()
    }
    consumed_reflow_overrides: set[tuple[str, str]] = set()
    runtime_vm_integrated, runtime_vm_integration_metadata = (
        load_runtime_vm_integration(prepared)
    )
    thought_predicate_metadata = runtime_vm_integration_metadata.get(
        "thought_predicate_family"
    )
    if (
        runtime_vm_integration_metadata.get(
            "thought_predicate_family_layer_included"
        )
        is not True
        or not isinstance(thought_predicate_metadata, dict)
    ):
        raise RuntimeError(
            "thought-predicate family integration metadata is absent"
        )
    thought_predicate_override_coordinates = {
        key
        for key, integrated_row in runtime_vm_integrated.items()
        if integrated_row.get("thought_predicate_family_update_action")
        in {
            "translation_override_and_runtime_promotion",
            "translation_override_and_verification_renewal",
        }
    }
    if (
        len(thought_predicate_override_coordinates)
        != thought_predicate_metadata.get("translation_override_count")
        or any(
            resource != "pk_msggame"
            for resource, _coordinate
            in thought_predicate_override_coordinates
        )
        or coordinate_digest(
            [
                coordinate
                for _resource, coordinate
                in thought_predicate_override_coordinates
            ]
        )
        != thought_predicate_metadata.get("override_coordinate_sha256")
    ):
        raise RuntimeError(
            "thought-predicate semantic override universe drifted"
        )
    consumed_runtime_vm_integrated: set[tuple[str, str]] = set()
    consumed_dynamic_honorific_overrides: set[
        tuple[str, str]
    ] = set()
    consumed_bound_terminal_overrides: set[tuple[str, str]] = set()
    consumed_thought_predicate_overrides: set[tuple[str, str]] = set()

    queue_rows = load_jsonl(QUEUE_PATH)
    batch_catalog_raw = json.loads(BATCHES_PATH.read_text(encoding="utf-8"))
    batch_catalog = {row["batch_id"]: row for row in batch_catalog_raw["batches"]}
    target_to_batch: dict[tuple[str, str], str] = {}
    for queue_row in queue_rows:
        resource = str(queue_row["resource"])
        batch_id = str(queue_row["batch_id"])
        for target in queue_row["target_literals"]:
            if target["visible"]:
                target_to_batch[(resource, str(target["coordinate"]))] = batch_id

    all_rows: list[dict[str, Any]] = []
    segments: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    batch_decisions: Counter[str] = Counter()
    batch_pending: Counter[str] = Counter()
    batch_eligible: Counter[str] = Counter()
    scope_classification_counts: Counter[str] = Counter()
    batch_scope_classifications: defaultdict[str, Counter[str]] = defaultdict(Counter)

    for path in decision_paths:
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        rows = load_jsonl(path)
        if not rows:
            raise RuntimeError(f"decision segment is empty: {path}")
        resources = {str(row["resource"]) for row in rows}
        if len(resources) != 1:
            raise RuntimeError(f"decision segment mixes resources: {path}")
        resource = next(iter(resources))
        coordinates = sorted((str(row["coordinate"]) for row in rows), key=coordinate_key)
        queue_batch_ids: set[str] = set()
        runtime_counts: Counter[str] = Counter()
        segment_scope_counts: Counter[str] = Counter()
        segment_control_override_count = 0

        for row in rows:
            key = (resource, str(row["coordinate"]))
            if key in seen:
                raise RuntimeError(f"duplicate decision across segments: {key}")
            seen.add(key)
            if row["semantic_review"] != "approved":
                raise RuntimeError(f"unapproved decision in {path}: {key}")
            if row["switch_korean_used"] or row["historic_korean_used"]:
                raise RuntimeError(f"prohibited Korean authority flag in {path}: {key}")
            classification = str(row["scope_classification"])
            if classification not in ENGINE.SCOPE_CLASSIFICATIONS:
                raise RuntimeError(f"invalid scope classification in {path}: {key}")
            runtime_review = str(row["runtime_review"])
            if runtime_review not in RUNTIME_REVIEW_STATES:
                raise RuntimeError(f"invalid runtime review in {path}: {key}")
            effective_row = semantic_overrides.get(key, row)
            if effective_row is not row:
                classification = str(effective_row["scope_classification"])
                runtime_review = str(effective_row["runtime_review"])
                consumed_semantic_overrides.add(key)
            reflowed = reflow_overrides.get(key)
            if reflowed is not None:
                effective_row = reflowed
                classification = str(effective_row["scope_classification"])
                runtime_review = str(effective_row["runtime_review"])
                consumed_reflow_overrides.add(key)
            repair = control_repairs.get(key)
            if repair is not None:
                if (
                    str(repair["source_decision_segment_id"])
                    != segment_id(path)
                    or str(repair["source_decision_file_sha256"])
                    != sha256_bytes(path.read_bytes())
                    or str(repair["source_decision_row_canonical_sha256"])
                    != canonical_row_sha256(row)
                    or str(repair["original_scope_classification"])
                    != classification
                    or str(repair["original_runtime_review"])
                    != runtime_review
                ):
                    raise RuntimeError(
                        f"runtime control repair source binding drifted: {key}"
                    )
                effective_row = dict(effective_row)
                classification = str(
                    repair["effective_scope_classification"]
                )
                runtime_review = str(repair["effective_runtime_review"])
                effective_row["scope_classification"] = classification
                effective_row["runtime_review"] = runtime_review
                consumed_control_repairs.add(key)
                segment_control_override_count += 1
            integrated_row = runtime_vm_integrated.get(key)
            if integrated_row is None:
                raise RuntimeError(
                    f"runtime VM integrated decision is absent: {key}"
                )
            immutable_integrated_row = integrated_row
            if (
                integrated_row.get(
                    "runtime_boundary_leading_space_inserted"
                )
                is True
            ):
                evidence = integrated_row.get("runtime_vm_verification")
                expected_method = (
                    ENGINE.BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD
                    if resource == "base_msggame"
                    else ENGINE.PK_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD
                )
                if (
                    key
                    not in ENGINE.RUNTIME_BOUNDARY_LEADING_SPACE_COORDINATES
                    or effective_row.get("translation") != "공"
                    or integrated_row.get("translation") != " 공"
                    or not isinstance(evidence, dict)
                    or evidence.get("method") != expected_method
                    or evidence.get("action") != "translation_override"
                    or not isinstance(
                        effective_row.get("honorific_spacing_evidence"),
                        dict,
                    )
                    or not isinstance(
                        integrated_row.get("honorific_spacing_evidence"),
                        dict,
                    )
                    or integrated_row["honorific_spacing_evidence"].get(
                        "boundary_space_literal_owned"
                    )
                    is not True
                ):
                    raise RuntimeError(
                        "dynamic honorific semantic override drifted: "
                        f"{key}"
                    )
                immutable_integrated_row = dict(integrated_row)
                immutable_integrated_row["translation"] = effective_row[
                    "translation"
                ]
                immutable_integrated_row["honorific_spacing_evidence"] = (
                    effective_row["honorific_spacing_evidence"]
                )
                immutable_integrated_row.pop(
                    "runtime_boundary_leading_space_inserted"
                )
                consumed_dynamic_honorific_overrides.add(key)
            terminal_override_evidence = integrated_row.get(
                "terminal_family_exact_override_evidence"
            )
            if terminal_override_evidence is not None:
                terminal_runtime_evidence = (
                    integrated_row.get("runtime_vm_verification")
                    if integrated_row.get("runtime_review") == "verified"
                    else integrated_row.get(
                        "terminal_family_runtime_evidence"
                    )
                )
                if (
                    key not in BOUND_TERMINAL_OVERRIDE_COORDINATES
                    or not isinstance(terminal_override_evidence, dict)
                    or terminal_override_evidence.get("bound_ending_only")
                    is not True
                    or terminal_override_evidence.get(
                        "lexical_predicate_removed"
                    )
                    is not True
                    or terminal_override_evidence.get(
                        "caller_predicate_stem_required"
                    )
                    is not True
                    or not isinstance(terminal_runtime_evidence, dict)
                    or terminal_runtime_evidence.get("method")
                    != ENGINE.PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_VERIFICATION_METHOD
                    or terminal_runtime_evidence.get("action")
                    != integrated_row.get("terminal_family_update_action")
                    or terminal_runtime_evidence.get(
                        "translation_utf16le_sha256"
                    )
                    != ENGINE.sha256_text(
                        str(integrated_row.get("translation"))
                    )
                ):
                    raise RuntimeError(
                        f"bound terminal semantic override drifted: {key}"
                    )
                immutable_integrated_row = dict(
                    immutable_integrated_row
                )
                immutable_integrated_row["translation"] = effective_row[
                    "translation"
                ]
                if (
                    integrated_row.get("runtime_assembly_evidence")
                    != effective_row.get("runtime_assembly_evidence")
                ):
                    immutable_integrated_row[
                        "runtime_assembly_evidence"
                    ] = effective_row.get("runtime_assembly_evidence")
                consumed_bound_terminal_overrides.add(key)
            thought_predicate_action = integrated_row.get(
                "thought_predicate_family_update_action"
            )
            if thought_predicate_action in {
                "translation_override_and_runtime_promotion",
                "translation_override_and_verification_renewal",
            }:
                thought_evidence = integrated_row.get(
                    "runtime_vm_verification"
                )
                if (
                    key not in thought_predicate_override_coordinates
                    or not isinstance(thought_evidence, dict)
                    or thought_evidence.get("method")
                    != ENGINE.PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_VERIFICATION_METHOD
                    or thought_evidence.get("action")
                    != thought_predicate_action
                    or thought_evidence.get(
                        "updated_translation_utf16le_sha256"
                    )
                    != ENGINE.sha256_text(
                        str(integrated_row.get("translation"))
                    )
                    or thought_evidence.get(
                        "full_incoming_closure_verified"
                    )
                    is not True
                    or thought_evidence.get(
                        "grammar_complete_for_all_registers"
                    )
                    is not True
                    or thought_evidence.get(
                        "actual_current_relative_nonexpanding"
                    )
                    is not True
                ):
                    raise RuntimeError(
                        f"thought-predicate semantic override drifted: {key}"
                    )
                immutable_integrated_row = dict(
                    immutable_integrated_row
                )
                immutable_integrated_row["translation"] = effective_row[
                    "translation"
                ]
                consumed_thought_predicate_overrides.add(key)
            if runtime_immutable_row(effective_row) != runtime_immutable_row(
                immutable_integrated_row
            ):
                raise RuntimeError(
                    f"runtime VM integration changed semantic decision data: {key}"
                )
            if (
                runtime_review == "pending"
                and integrated_row.get("runtime_review") == "verified"
            ):
                evidence = integrated_row.get("runtime_vm_verification")
                if not isinstance(evidence, dict):
                    raise RuntimeError(
                        f"runtime VM promotion lacks row evidence: {key}"
                    )
                predecessor_binding = evidence.get(
                    "predecessor_integrated_binding"
                )
                dynamic_predecessor_renewal = (
                    evidence.get("method")
                    in {
                        ENGINE.BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD,
                        ENGINE.PK_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD,
                    }
                    and evidence.get("action")
                    in {"translation_override", "verification_renewal"}
                    and isinstance(predecessor_binding, dict)
                    and isinstance(
                        predecessor_binding.get(
                            "previous_runtime_vm_verification_sha256"
                        ),
                        str,
                    )
                    and evidence.get("scope_transition")
                    == {
                        "from": integrated_row.get(
                            "scope_classification"
                        ),
                        "to": integrated_row.get(
                            "scope_classification"
                        ),
                    }
                    and evidence.get("layout_transition")
                    == {
                        "from": integrated_row.get("layout_review"),
                        "to": integrated_row.get("layout_review"),
                    }
                )
                terminal_predecessor_renewal = (
                    evidence.get("method")
                    == ENGINE.PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_VERIFICATION_METHOD
                    and evidence.get("action")
                    in {"translation_override", "verification_renewal"}
                    and evidence.get(
                        "preexisting_verified_evidence_renewed"
                    )
                    is True
                    and isinstance(predecessor_binding, dict)
                    and isinstance(
                        predecessor_binding.get(
                            "previous_runtime_vm_verification_sha256"
                        ),
                        str,
                    )
                )
                thought_predecessor_renewal = (
                    evidence.get("method")
                    == ENGINE.PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_VERIFICATION_METHOD
                    and evidence.get("action")
                    == "translation_override_and_verification_renewal"
                    and evidence.get("predecessor_runtime_review")
                    == "verified"
                )
                if (
                    evidence.get("action")
                    in {"translation_override", "verification_renewal"}
                    and evidence.get("method")
                    in {
                        ENGINE.BASE_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD,
                        ENGINE.PK_DYNAMIC_HONORIFIC_SPACING_RUNTIME_VM_VERIFICATION_METHOD,
                    }
                    and not dynamic_predecessor_renewal
                ):
                    raise RuntimeError(
                        "dynamic runtime evidence did not bind its verified "
                        f"predecessor: {key}"
                    )
                if (
                    evidence.get("action")
                    == "translation_override_and_verification_renewal"
                    and evidence.get("method")
                    == ENGINE.PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_VERIFICATION_METHOD
                    and not thought_predecessor_renewal
                ):
                    raise RuntimeError(
                        "thought-predicate runtime evidence did not bind its "
                        f"verified predecessor: {key}"
                    )
                if (
                    evidence.get("action")
                    in {"translation_override", "verification_renewal"}
                    and evidence.get("method")
                    == ENGINE.PK_BOUND_TERMINAL_FAMILY_RUNTIME_VM_VERIFICATION_METHOD
                    and not terminal_predecessor_renewal
                ):
                    raise RuntimeError(
                        "terminal runtime evidence did not bind its verified "
                        f"predecessor: {key}"
                    )
                if integrated_row.get("layout_review") != effective_row.get(
                    "layout_review"
                ):
                    if not (
                        effective_row.get("layout_review")
                        in {"runtime_pending", "unchanged_from_current"}
                        and integrated_row.get("layout_review")
                        == "runtime_verified"
                        and evidence.get("method")
                        in {
                            (
                                "reversed_vm_residual_full_closure_"
                                "nonexpansion_analysis"
                            ),
                            (
                                "reversed_vm_cross_resource_exact_"
                                "closure_analysis"
                            ),
                            (
                                "reversed_vm_dynamic_honorific_"
                                "spacing_closure_analysis"
                            ),
                            (
                                "reversed_vm_pk_bound_terminal_family_"
                                "exact_closure_analysis"
                            ),
                            (
                                "reversed_vm_pk_thought_predicate_family_"
                                "exact_closure_analysis"
                            ),
                        }
                        and (
                            evidence.get("layout_transition")
                            == {
                                "from": effective_row.get("layout_review"),
                                "to": "runtime_verified",
                            }
                            or (
                                evidence.get("method")
                                == (
                                    "reversed_vm_pk_bound_terminal_"
                                    "family_exact_closure_analysis"
                                )
                                and evidence.get(
                                    "actual_promotion_binding",
                                    {},
                                ).get(
                                    "manual_full_assembly_verified"
                                )
                                is True
                            )
                        )
                        or (
                            dynamic_predecessor_renewal
                            and integrated_row.get("layout_review")
                            == "runtime_verified"
                        )
                        or (
                            terminal_predecessor_renewal
                            and integrated_row.get("runtime_review")
                            == "verified"
                        )
                        or (
                            thought_predecessor_renewal
                            and integrated_row.get("runtime_review")
                            == "verified"
                        )
                        or (
                            evidence.get("method")
                            == (
                                "reversed_vm_pk_thought_predicate_family_"
                                "exact_closure_analysis"
                            )
                            and evidence.get("action")
                            in {
                                "runtime_promotion",
                                (
                                    "translation_override_and_runtime_"
                                    "promotion"
                                ),
                            }
                            and evidence.get(
                                "grammar_complete_for_all_registers"
                            )
                            is True
                            and evidence.get(
                                "actual_current_relative_nonexpanding"
                            )
                            is True
                        )
                    ):
                        raise RuntimeError(
                            "unsupported runtime layout transition: "
                            f"{key}"
                        )
            elif integrated_row.get("runtime_review") != runtime_review:
                raise RuntimeError(
                    f"unsupported runtime VM state transition: {key}"
                )
            elif integrated_row.get("layout_review") != effective_row.get(
                "layout_review"
            ):
                raise RuntimeError(
                    f"layout changed without runtime promotion: {key}"
                )
            effective_row = integrated_row
            classification = str(effective_row["scope_classification"])
            runtime_review = str(effective_row["runtime_review"])
            consumed_runtime_vm_integrated.add(key)
            batch_id = target_to_batch.get(key)
            if batch_id is None:
                raise RuntimeError(f"decision target is absent from private queue: {key}")
            queue_batch_ids.add(batch_id)
            batch_decisions[batch_id] += 1
            runtime_counts[runtime_review] += 1
            segment_scope_counts[classification] += 1
            scope_classification_counts[classification] += 1
            batch_scope_classifications[batch_id][classification] += 1
            if runtime_review == "pending":
                batch_pending[batch_id] += 1
            else:
                batch_eligible[batch_id] += 1
            all_rows.append(effective_row)

        segments.append(
            {
                "segment_id": segment_id(path),
                "resource": resource,
                "first_coordinate": coordinates[0],
                "last_coordinate": coordinates[-1],
                "decision_count": len(rows),
                "semantic_review_approved": len(rows),
                "runtime_review_not_required": runtime_counts["not_required"],
                "runtime_review_verified": runtime_counts["verified"],
                "runtime_review_pending": runtime_counts["pending"],
                "scope_classification_counts": {
                    classification: segment_scope_counts[classification]
                    for classification in sorted(ENGINE.SCOPE_CLASSIFICATIONS)
                },
                **(
                    {
                        "runtime_control_override_count":
                        segment_control_override_count
                    }
                    if segment_control_override_count
                    else {}
                ),
                "queue_batch_ids": sorted(queue_batch_ids, key=batch_key),
                "switch_korean_used": False,
                "historic_korean_used": False,
                "steam_write_performed": False,
            }
        )

    if consumed_control_repairs != set(control_repairs):
        missing = sorted(set(control_repairs) - consumed_control_repairs)
        raise RuntimeError(
            f"runtime control repairs were not bound to decisions: {missing}"
        )
    if consumed_semantic_overrides != set(semantic_overrides):
        missing = sorted(
            set(semantic_overrides) - consumed_semantic_overrides
        )
        raise RuntimeError(
            f"semantic overrides were not bound to decisions: {missing}"
        )
    if consumed_reflow_overrides != set(reflow_overrides):
        missing = sorted(
            set(reflow_overrides) - consumed_reflow_overrides
        )
        raise RuntimeError(
            f"relative reflow overrides were not bound to decisions: {missing}"
        )
    if consumed_runtime_vm_integrated != set(runtime_vm_integrated):
        missing = sorted(
            set(runtime_vm_integrated) - consumed_runtime_vm_integrated
        )
        raise RuntimeError(
            "runtime VM integrated decisions were not bound to source segments: "
            f"{missing[:8]}"
        )
    if (
        consumed_dynamic_honorific_overrides
        != ENGINE.RUNTIME_BOUNDARY_LEADING_SPACE_COORDINATES
    ):
        missing = sorted(
            ENGINE.RUNTIME_BOUNDARY_LEADING_SPACE_COORDINATES
            - consumed_dynamic_honorific_overrides
        )
        extra = sorted(
            consumed_dynamic_honorific_overrides
            - ENGINE.RUNTIME_BOUNDARY_LEADING_SPACE_COORDINATES
        )
        raise RuntimeError(
            "dynamic honorific overrides were not exactly consumed: "
            f"missing={missing} extra={extra}"
        )
    runtime_vm_integration_metadata[
        "dynamic_honorific_spacing_override_count"
    ] = len(consumed_dynamic_honorific_overrides)
    if (
        consumed_bound_terminal_overrides
        != BOUND_TERMINAL_OVERRIDE_COORDINATES
    ):
        missing = sorted(
            BOUND_TERMINAL_OVERRIDE_COORDINATES
            - consumed_bound_terminal_overrides
        )
        extra = sorted(
            consumed_bound_terminal_overrides
            - BOUND_TERMINAL_OVERRIDE_COORDINATES
        )
        raise RuntimeError(
            "bound terminal overrides were not exactly consumed: "
            f"missing={missing} extra={extra}"
        )
    runtime_vm_integration_metadata[
        "bound_terminal_family_override_count"
    ] = len(consumed_bound_terminal_overrides)
    if (
        consumed_thought_predicate_overrides
        != thought_predicate_override_coordinates
    ):
        missing = sorted(
            thought_predicate_override_coordinates
            - consumed_thought_predicate_overrides
        )
        extra = sorted(
            consumed_thought_predicate_overrides
            - thought_predicate_override_coordinates
        )
        raise RuntimeError(
            "thought-predicate overrides were not exactly consumed: "
            f"missing={missing} extra={extra}"
        )
    runtime_vm_integration_metadata[
        "thought_predicate_family_override_count"
    ] = len(consumed_thought_predicate_overrides)

    touched_batch_ids = sorted(batch_decisions, key=batch_key)
    queue_batch_coverage: list[dict[str, Any]] = []
    for batch_id in touched_batch_ids:
        catalog = batch_catalog[batch_id]
        visible_count = int(catalog["visible_current_literal_count"])
        decision_count = batch_decisions[batch_id]
        if decision_count > visible_count:
            raise RuntimeError(f"decision count exceeds visible target count for {batch_id}")
        queue_batch_coverage.append(
            {
                "batch_id": batch_id,
                "resource": catalog["resource"],
                "first_record_coordinate": catalog["first_record_coordinate"],
                "last_record_coordinate": catalog["last_record_coordinate"],
                "visible_target_count": visible_count,
                "decision_count": decision_count,
                "runtime_review_pending": batch_pending[batch_id],
                "fully_candidate_eligible": batch_eligible[batch_id],
                "scope_classification_counts": {
                    classification: batch_scope_classifications[batch_id][classification]
                    for classification in sorted(ENGINE.SCOPE_CLASSIFICATIONS)
                },
                "semantic_complete": decision_count == visible_count,
            }
        )

    total_targets = len(prepared.visible_targets)
    approved = len(all_rows)
    pending = sum(row["runtime_review"] == "pending" for row in all_rows)
    eligible = approved - pending
    semantic_complete = approved == total_targets
    candidate_complete = semantic_complete and pending == 0 and CANDIDATE_MANIFEST.is_file()
    return {
        "schema": "nobu16.kr.pc-dialogue-full-retranslation-progress.v1",
        "release_target": "0.15.0",
        "mechanical_candidate_universe": total_targets,
        "scope_classification": {
            "status": "complete" if semantic_complete else "in_progress",
            "categories": [
                "retranslated",
                "runtime_fragment_pending",
                "confirmed_non_display",
            ],
        },
        "segment_naming_note": (
            "segment B-numbers are authoring work-package identifiers; "
            "queue_batch_ids records the generated review-queue batches"
        ),
        "runtime_control_repairs": {
            **control_repair_metadata,
            "consumed_entry_count": len(consumed_control_repairs),
            "effective_runtime_review_pending": sum(
                repair["effective_runtime_review"] == "pending"
                for repair in control_repairs.values()
            ),
        },
        "semantic_override": {
            **semantic_override_metadata,
            "consumed_override_count": len(
                consumed_semantic_overrides
            ),
        },
        "relative_reflow_override": {
            **relative_reflow_metadata,
            "consumed_override_count": len(
                consumed_reflow_overrides
            ),
        },
        "runtime_vm_integration": runtime_vm_integration_metadata,
        "segments": segments,
        "queue_batch_coverage": queue_batch_coverage,
        "totals": {
            "semantic_review_approved": approved,
            "runtime_review_pending": pending,
            "fully_candidate_eligible": eligible,
            "scope_classification_counts": {
                classification: scope_classification_counts[classification]
                for classification in sorted(ENGINE.SCOPE_CLASSIFICATIONS)
            },
            "semantic_completion": semantic_complete,
            "candidate_build_complete": candidate_complete,
        },
    }


def serialized_progress() -> str:
    return json.dumps(build_progress(), ensure_ascii=False, indent=2) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--validate", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.write and not args.validate:
        raise RuntimeError("choose --write, --validate, or both")
    content = serialized_progress()
    if args.write:
        ENGINE.atomic_write(PROGRESS_PATH, content)
    if args.validate:
        if not PROGRESS_PATH.is_file():
            raise RuntimeError(f"progress ledger is absent: {PROGRESS_PATH}")
        if PROGRESS_PATH.read_text(encoding="utf-8") != content:
            raise RuntimeError(f"progress ledger drift: {PROGRESS_PATH}")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment_count": len(json.loads(content)["segments"]),
                "semantic_review_approved": json.loads(content)["totals"]["semantic_review_approved"],
                "steam_write_performed": False,
                "output": str(PROGRESS_PATH),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
