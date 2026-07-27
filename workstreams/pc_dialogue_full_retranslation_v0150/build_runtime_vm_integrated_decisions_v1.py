#!/usr/bin/env python3
"""Integrate proved Base/PK VM promotions into one private decision universe.

The dialogue-bearing merged JSONL remains below ``tmp/``.  The tracked report
contains only coordinates, counts, and cryptographic guards.  This builder
never writes the Steam installation and deliberately leaves unproved PK rows
pending.
"""

from __future__ import annotations

import argparse
import copy
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
    / "build_pk_msggame_full_candidate_runtime_verified_overlay_v1.py"
)
PK_OVERLAY_PATH = (
    DECISIONS_DIR
    / "runtime_verification_overlays"
    / "pk_msggame_full_candidate_runtime_vm_verified.private.v1.jsonl"
)
PK_PROMOTION_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_msggame_full_candidate_runtime_vm_promotion.v1.json"
)
PK_RESIDUAL_OVERLAY_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "build_pk_msggame_residual_runtime_verified_overlay_v1.py"
)
PK_RESIDUAL_OVERLAY_PATH = (
    DECISIONS_DIR
    / "runtime_verification_overlays"
    / "pk_msggame_residual_runtime_vm_verified.private.v1.jsonl"
)
PK_RESIDUAL_PROMOTION_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_msggame_residual_runtime_vm_promotion.v1.json"
)
PK_ONLY_EXACT_BLOCKED_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "build_pk_msggame_exact_blocked_pk_only_closure_v1.py"
)
PK_ONLY_EXACT_BLOCKED_OVERLAY_PATH = (
    DECISIONS_DIR
    / "runtime_verification_overlays"
    / "pk_msggame_exact_blocked_pk_only_closure_verified.private.v1.jsonl"
)
PK_ONLY_EXACT_BLOCKED_AUDIT_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_msggame_exact_blocked_pk_only_closure_coverage.v1.json"
)
PK_ONLY_EXACT_BLOCKED_PROMOTION_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_msggame_exact_blocked_pk_only_closure_promotion.v1.json"
)
PK_CROSS_RESOURCE_EXACT_CLOSURE_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "build_pk_msggame_pending_cross_resource_exact_closure_v1.py"
)
PK_CROSS_RESOURCE_EXACT_CLOSURE_OVERLAY_PATH = (
    DECISIONS_DIR
    / "runtime_verification_overlays"
    / "pk_msggame_pending_cross_resource_exact_closure_verified.private.v1.jsonl"
)
PK_CROSS_RESOURCE_EXACT_CLOSURE_AUDIT_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_msggame_pending_cross_resource_exact_closure_coverage.v1.json"
)
PK_CROSS_RESOURCE_EXACT_CLOSURE_PROMOTION_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "public"
    / "pk_msggame_pending_cross_resource_exact_closure_promotion.v1.json"
)
DYNAMIC_HONORIFIC_SPACING_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "build_dynamic_honorific_spacing_closure_v1.py"
)
BOUND_TERMINAL_FAMILY_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "build_pk_bound_terminal_family_exact_closure_v1.py"
)
THOUGHT_PREDICATE_FAMILY_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "build_pk_thought_predicate_family_exact_closure_v1.py"
)
BOUND_TERMINAL_CALLER_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "build_pk_bound_terminal_caller_full_closure_v1.py"
)
BOUND_TERMINAL_2546_FULL_CALLER_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "pk_msggame_runtime_vm_audit_v1"
    / "build_pk_bound_terminal_2546_full_caller_closure_v1.py"
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
EXPECTED_PK_EXACT_PROMOTIONS = 7_450
EXPECTED_PK_RESIDUAL_PROMOTIONS = 2_945
EXPECTED_PK_PREDECESSOR_PROMOTIONS = 10_395
EXPECTED_PK_ONLY_EXACT_BLOCKED_PROMOTIONS = 1_536
EXPECTED_PK_POST_PK_ONLY_PROMOTIONS = 11_931
EXPECTED_PK_CROSS_RESOURCE_EXACT_CLOSURE_PROMOTIONS = 50
EXPECTED_PK_INTEGRATED_PROMOTIONS = 11_981
EXPECTED_DYNAMIC_HONORIFIC_SPACING_PROMOTIONS = 57
EXPECTED_PK_FINAL_PROMOTIONS = 12_038
EXPECTED_BOUND_TERMINAL_FAMILY_PROMOTIONS = 4
EXPECTED_PK_BOUND_TERMINAL_FINAL_PROMOTIONS = 12_042
EXPECTED_THOUGHT_PREDICATE_FAMILY_PROMOTIONS = 23
EXPECTED_PK_THOUGHT_PREDICATE_FINAL_PROMOTIONS = 12_065
EXPECTED_BOUND_TERMINAL_CALLER_PROMOTIONS = 41
EXPECTED_PK_BOUND_TERMINAL_CALLER_FINAL_PROMOTIONS = 12_106
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_PROMOTIONS = 364
EXPECTED_PK_BOUND_TERMINAL_2546_FULL_CALLER_FINAL_PROMOTIONS = 12_470
EXPECTED_PREDECESSOR_PENDING_AFTER = 10_288
EXPECTED_POST_PK_ONLY_PENDING_AFTER = 8_752
EXPECTED_PENDING_AFTER = 8_702
EXPECTED_FINAL_PENDING_AFTER = 8_645
EXPECTED_BOUND_TERMINAL_FINAL_PENDING_AFTER = 8_641
EXPECTED_THOUGHT_PREDICATE_FINAL_PENDING_AFTER = 8_618
EXPECTED_BOUND_TERMINAL_CALLER_FINAL_PENDING_AFTER = 8_577
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_FINAL_PENDING_AFTER = 8_213
EXPECTED_POST_CROSS_PRIVATE_SHA256 = (
    "3FF6AF87B638C9F98DF4F956E5A7985B70E5F4A899A48E77ED67629212B247CC"
)
EXPECTED_POST_DYNAMIC_PRIVATE_SHA256 = (
    "D8BF282386F081F5B4B26674653DD3A085A8FF490E3043B6B4AF1BAB3F3A1CC2"
)
EXPECTED_POST_BOUND_PRIVATE_SHA256 = (
    "F6BAA43C22404365E49D40C6B306C850C3B123681CD0A42D5A63EDB73D8018FB"
)
EXPECTED_THOUGHT_PREDICATE_FINAL_PRIVATE_SHA256 = (
    "9245DED68D1A8DFA51B0587E5E2B1B7165BF610CB4618460654D4032B04E1F10"
)
EXPECTED_BOUND_TERMINAL_CALLER_COMBINED_CANDIDATE_SHA256 = (
    "498A9A19FA33B57789C6FBF3732DA61967FEDE8055F034F68E43E628C16ED74F"
)
EXPECTED_THOUGHT_PREDICATE_CANDIDATE_SHA256 = (
    "174E3BDBA63E38782531ADBF864FA95FFB75823A679DAC029594FFF1D66F23F4"
)
EXPECTED_BOUND_TERMINAL_CALLER_OVERLAP_RECORD_SHA256 = (
    "564F81EBB9353750EAFAB190D1A5E3F1050783E0B4D5D526DD7A60DC2F8AC109"
)
EXPECTED_BOUND_TERMINAL_CALLER_FINAL_PRIVATE_SHA256 = (
    "54B4255C29F256B84E1CA4EE8A9B5D21FE254100A2A71CA28657F7EF6EB34E45"
)
EXPECTED_BOUND_TERMINAL_CALLER_TARGET_DELTA_SHA256 = (
    "3F719E9F54EB226ABE19ADFCCBA9BF2A1926BDC133E1FBD33A567E3DF0994E3F"
)
EXPECTED_BOUND_TERMINAL_CALLER_ROOT_PROOF_MANIFEST_SHA256 = (
    "E97F699B7FE9C75F6781E02A3F316A639344CCFD1F476FD35EB8F6EAB747F5D0"
)
EXPECTED_BOUND_TERMINAL_CALLER_OVERLAP_ROOT_PROOF_SHA256 = (
    "4121CA04E8DBED2824744D668A0E7DA699A84FCE76DD6C1CE0F37C70904F2994"
)
EXPECTED_BOUND_TERMINAL_CALLER_OVERLAP_EVIDENCE_SHA256 = (
    "BD82EF31C36A7E32FA6E0A3D59A27A54E0528369CD661D9603E42B49109FB998"
)
EXPECTED_BOUND_TERMINAL_CALLER_RENEWAL_MANIFEST_SHA256 = (
    "0EC7E69CAB57E15F646D98005D023160AAA97A8A4A3E0D7DDB09F6E2AD4D7F67"
)
BOUND_TERMINAL_CALLER_OVERLAP_KEY = ("pk_msggame", "15:1068:0")
BOUND_TERMINAL_CALLER_RENEWAL_REFERENCE_SHA256 = (
    "56766E27D4B786BE1ED3AFEDDC61F1743E3C2CEF2A72111EF7F70AE920C680DA"
)
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_FINAL_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_OVERRIDE_COUNT = 216
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_RENEWAL_COUNT = 292
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_UPDATED_ROW_COUNT = 656
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_REJECTED_PENDING_COUNT = 74
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_ACTION_COUNTS = {
    "runtime_promotion": 279,
    "translation_override_and_runtime_promotion": 85,
    "translation_override_and_verification_renewal": 131,
    "verification_renewal": 161,
}
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_AUDIT_SHA256 = (
    "567FE83E1BD6ED9B4A8D7C1E303CC4760A5DCFB3061C622C55F0565B9960AF57"
)
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_PROMOTION_SHA256 = (
    "58F734F65A6D0C48BB245ED0E515A05EF51F844D53D8FA50ECC8A84DEAB4005B"
)
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_DECISION_SHA256 = (
    "39652CFB6923E43D30D0CF422642C3B996DDC0495E620EFCE1B3B310E5D7D82F"
)
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_EVIDENCE_SHA256 = (
    "3D5AA831D7F891DEABE0E79667416F96C12366A968F1E662F4519FC1C4025DD6"
)
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_AUDIT_PAYLOAD_SHA256 = (
    "835A3534A56D7F0446A24A09BEF7BC810B5540FF1202611B70E244F3DEB68DB3"
)
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_PROMOTION_PAYLOAD_SHA256 = (
    "B7C1FE333D96587399DEE18639A2738DA0CAD10BCEA2589208E0916B5C6A7707"
)
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_OVERRIDE_COORDINATE_SHA256 = (
    "212DEF7EE8B508CEA406FF223BADE5E2DC0DC7D7B1EE5255AD828764B6A866B5"
)
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_DECISION_COORDINATE_SHA256 = (
    "F176E7D99EC74F07AE6041B29EC5CCB3DB36A356B7600CF291B2B61B51ABC349"
)
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_ASSEMBLY_UPDATE_COUNT = 10
EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_ASSEMBLY_UPDATE_SHA256 = (
    "5B434879A5EB34454E65DCC5E6BD7CEC4EAF6E5CE9F1351D624B14DB1B35DE43"
)
BOUND_TERMINAL_2546_FULL_CALLER_SUPERSEDED_CALLER_KEYS = frozenset(
    {
        ("pk_msggame", "15:277:1"),
        ("pk_msggame", "15:278:1"),
    }
)
RUNTIME_MUTABLE_FIELDS = frozenset(
    {
        "scope_classification",
        "layout_review",
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
PK_RESIDUAL_OVERLAY = load_module(
    "pc_dialogue_runtime_vm_integration_pk_residual_overlay",
    PK_RESIDUAL_OVERLAY_BUILDER_PATH,
)
SEMANTIC_OVERRIDE = load_module(
    "pc_dialogue_runtime_vm_integration_semantic_override",
    SEMANTIC_OVERRIDE_BUILDER_PATH,
)
REFLOW_OVERRIDE = load_module(
    "pc_dialogue_runtime_vm_integration_relative_reflow_override",
    REFLOW_OVERRIDE_LOADER_PATH,
)
PK_ONLY_EXACT_BLOCKED_OVERLAY: Any | None = None
PK_CROSS_RESOURCE_EXACT_CLOSURE_OVERLAY: Any | None = None
DYNAMIC_HONORIFIC_SPACING: Any | None = None
BOUND_TERMINAL_FAMILY: Any | None = None
THOUGHT_PREDICATE_FAMILY: Any | None = None
BOUND_TERMINAL_CALLER: Any | None = None
BOUND_TERMINAL_2546_FULL_CALLER: Any | None = None


def load_pk_only_exact_blocked_overlay() -> Any:
    global PK_ONLY_EXACT_BLOCKED_OVERLAY
    if PK_ONLY_EXACT_BLOCKED_OVERLAY is None:
        PK_ONLY_EXACT_BLOCKED_OVERLAY = load_module(
            (
                "pc_dialogue_runtime_vm_integration_"
                "pk_only_exact_blocked_overlay"
            ),
            PK_ONLY_EXACT_BLOCKED_BUILDER_PATH,
        )
    return PK_ONLY_EXACT_BLOCKED_OVERLAY


def load_pk_cross_resource_exact_closure_overlay() -> Any:
    global PK_CROSS_RESOURCE_EXACT_CLOSURE_OVERLAY
    if PK_CROSS_RESOURCE_EXACT_CLOSURE_OVERLAY is None:
        PK_CROSS_RESOURCE_EXACT_CLOSURE_OVERLAY = load_module(
            (
                "pc_dialogue_runtime_vm_integration_"
                "pk_cross_resource_exact_closure_overlay"
            ),
            PK_CROSS_RESOURCE_EXACT_CLOSURE_BUILDER_PATH,
        )
    return PK_CROSS_RESOURCE_EXACT_CLOSURE_OVERLAY


def load_dynamic_honorific_spacing() -> Any:
    global DYNAMIC_HONORIFIC_SPACING
    if DYNAMIC_HONORIFIC_SPACING is None:
        DYNAMIC_HONORIFIC_SPACING = load_module(
            "pc_dialogue_runtime_vm_dynamic_honorific_spacing",
            DYNAMIC_HONORIFIC_SPACING_BUILDER_PATH,
        )
    return DYNAMIC_HONORIFIC_SPACING


def load_bound_terminal_family() -> Any:
    global BOUND_TERMINAL_FAMILY
    if BOUND_TERMINAL_FAMILY is None:
        BOUND_TERMINAL_FAMILY = load_module(
            "pc_dialogue_runtime_vm_bound_terminal_family",
            BOUND_TERMINAL_FAMILY_BUILDER_PATH,
        )
    return BOUND_TERMINAL_FAMILY


def load_thought_predicate_family() -> Any:
    global THOUGHT_PREDICATE_FAMILY
    if THOUGHT_PREDICATE_FAMILY is None:
        THOUGHT_PREDICATE_FAMILY = load_module(
            "pc_dialogue_runtime_vm_thought_predicate_family",
            THOUGHT_PREDICATE_FAMILY_BUILDER_PATH,
        )
    return THOUGHT_PREDICATE_FAMILY


def load_bound_terminal_caller() -> Any:
    global BOUND_TERMINAL_CALLER
    if BOUND_TERMINAL_CALLER is None:
        BOUND_TERMINAL_CALLER = load_module(
            "pc_dialogue_runtime_vm_bound_terminal_caller",
            BOUND_TERMINAL_CALLER_BUILDER_PATH,
        )
    return BOUND_TERMINAL_CALLER


def load_bound_terminal_2546_full_caller() -> Any:
    global BOUND_TERMINAL_2546_FULL_CALLER
    if BOUND_TERMINAL_2546_FULL_CALLER is None:
        BOUND_TERMINAL_2546_FULL_CALLER = load_module(
            "pc_dialogue_runtime_vm_bound_terminal_2546_full_caller",
            BOUND_TERMINAL_2546_FULL_CALLER_BUILDER_PATH,
        )
    return BOUND_TERMINAL_2546_FULL_CALLER


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
            and entry.get("repair_candidate_required_for_release") is False
            and entry.get("repair_candidate_application_forbidden") is True
            and entry.get("repair_status") == "rejected_not_required"
            and entry.get("adjudication") == "repair_not_required"
            and entry.get("steam_write_performed") is False,
            f"runtime control repair source binding drifted: {key}",
        )
        repairs[key] = entry
    return repairs, {
        "entry_count": len(repairs),
        "sha256": sha256_bytes(CONTROL_REPAIRS_PATH.read_bytes()),
    }


def validated_semantic_override(
    source_rows: Mapping[tuple[str, str], dict[str, Any]],
) -> tuple[tuple[str, str], dict[str, Any], dict[str, Any]]:
    private_content, public_content, report, row = (
        SEMANTIC_OVERRIDE.build_outputs()
    )
    SEMANTIC_OVERRIDE.validate_outputs(
        private_content,
        public_content,
        report,
        row,
    )
    require(
        SEMANTIC_OVERRIDE_PRIVATE_PATH.is_file()
        and SEMANTIC_OVERRIDE_PRIVATE_PATH.read_text(encoding="utf-8")
        == private_content,
        "private semantic override drifted",
    )
    require(
        SEMANTIC_OVERRIDE_PUBLIC_PATH.is_file()
        and SEMANTIC_OVERRIDE_PUBLIC_PATH.read_text(encoding="utf-8")
        == public_content,
        "tracked semantic override report drifted",
    )
    key = (str(row["resource"]), str(row["coordinate"]))
    original = source_rows.get(key)
    require(
        original is not None
        and key == ("pk_msggame", "6:3421:0")
        and row.get("semantic_review") == "approved"
        and row.get("runtime_review") == "not_required"
        and row.get("layout_review") == "unchanged_from_current"
        and isinstance(row.get("semantic_flattening_verification"), dict),
        "semantic override row contract drifted",
    )
    require(
        original.get("source_record_raw_sha256")
        == row.get("source_record_raw_sha256")
        and original.get("current_ko_utf16le_sha256")
        == row.get("current_ko_utf16le_sha256")
        and original.get("historic_korean_used") is False
        and row.get("historic_korean_used") is False
        and original.get("switch_korean_used") is False
        and row.get("switch_korean_used") is False,
        "semantic override changed a source or authority guard",
    )
    return key, row, {
        "override_count": 1,
        "private_sha256": sha256_bytes(private_content.encode("utf-8")),
        "public_report_sha256": sha256_bytes(
            public_content.encode("utf-8")
        ),
        "report_payload_sha256": report["report_payload_sha256"],
        "coordinate": key[1],
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


def validated_pk_overlay(
    *,
    include_pk_only: bool,
    include_cross_resource: bool,
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, Any],
]:
    (
        private_content,
        public_content,
        promotion,
        context,
    ) = PK_OVERLAY.build_outputs()
    coverage = context["coverage"]
    coverage_file_sha256 = context["coverage_file_sha256"]
    inputs = context["inputs"]
    require(
        PK_OVERLAY_PATH.is_file()
        and PK_OVERLAY_PATH.read_text(encoding="utf-8")
        == private_content,
        "tracked PK full-candidate overlay drifted",
    )
    require(
        PK_PROMOTION_PATH.is_file()
        and PK_PROMOTION_PATH.read_text(encoding="utf-8")
        == public_content,
        "tracked PK full-candidate promotion report drifted",
    )
    rows = PK_OVERLAY.read_overlay(PK_OVERLAY_PATH)
    PK_OVERLAY.validate_overlay_rows(
        rows,
        inputs=inputs,
        report=coverage,
        report_file_sha256=coverage_file_sha256,
    )
    require(
        promotion.get("schema")
        == "nobu16.kr.pk-msggame-full-candidate-runtime-vm-promotion.v1"
        and promotion.get("status") == "PASS"
        and promotion.get("steam_write_performed") is False
        and promotion.get("result", {}).get("private_overlay_sha256")
        == sha256_bytes(PK_OVERLAY_PATH.read_bytes()),
        "PK VM promotion report drifted",
    )
    require(
        len(rows) == EXPECTED_PK_EXACT_PROMOTIONS,
        "PK exact VM overlay completeness drifted",
    )
    (
        residual_private_content,
        residual_public_content,
        residual_promotion,
        residual_context,
    ) = PK_RESIDUAL_OVERLAY.build_outputs()
    residual_coverage = residual_context["coverage"]
    residual_coverage_file_sha256 = residual_context[
        "coverage_file_sha256"
    ]
    residual_inputs = residual_context["inputs"]
    require(
        PK_RESIDUAL_OVERLAY_PATH.is_file()
        and PK_RESIDUAL_OVERLAY_PATH.read_text(encoding="utf-8")
        == residual_private_content,
        "tracked PK residual overlay drifted",
    )
    require(
        PK_RESIDUAL_PROMOTION_PATH.is_file()
        and PK_RESIDUAL_PROMOTION_PATH.read_text(encoding="utf-8")
        == residual_public_content,
        "tracked PK residual promotion report drifted",
    )
    residual_rows = PK_RESIDUAL_OVERLAY.read_overlay(
        PK_RESIDUAL_OVERLAY_PATH
    )
    PK_RESIDUAL_OVERLAY.validate_overlay_rows(
        residual_rows,
        inputs=residual_inputs,
        report=residual_coverage,
        report_file_sha256=residual_coverage_file_sha256,
    )
    require(
        residual_promotion.get("schema")
        == "nobu16.kr.pk-msggame-residual-runtime-vm-promotion.v1"
        and residual_promotion.get("status") == "PASS"
        and residual_promotion.get("steam_write_performed") is False
        and residual_promotion.get("result", {}).get(
            "private_overlay_sha256"
        )
        == sha256_bytes(PK_RESIDUAL_OVERLAY_PATH.read_bytes())
        and len(residual_rows) == EXPECTED_PK_RESIDUAL_PROMOTIONS,
        "PK residual VM promotion report drifted",
    )
    require(
        include_pk_only or not include_cross_resource,
        "cross-resource layer requires the PK-only predecessor",
    )
    if not include_pk_only:
        by_coordinate = {str(row["coordinate"]): row for row in rows}
        for row in residual_rows:
            coordinate = str(row["coordinate"])
            require(
                coordinate not in by_coordinate,
                f"PK exact/residual overlay overlap: {coordinate}",
            )
            by_coordinate[coordinate] = row
        require(
            len(by_coordinate) == EXPECTED_PK_PREDECESSOR_PROMOTIONS,
            "pre-PK-only VM overlay completeness drifted",
        )
        return by_coordinate, {
            "promotion_count": len(by_coordinate),
            "pk_only_layer_included": False,
            "exact": {
                "promotion_count": len(rows),
                "private_sha256": sha256_bytes(PK_OVERLAY_PATH.read_bytes()),
                "promotion_report_sha256": sha256_bytes(
                    PK_PROMOTION_PATH.read_bytes()
                ),
                "coverage_file_sha256": coverage_file_sha256,
            },
            "residual": {
                "promotion_count": len(residual_rows),
                "private_sha256": sha256_bytes(
                    PK_RESIDUAL_OVERLAY_PATH.read_bytes()
                ),
                "promotion_report_sha256": sha256_bytes(
                    PK_RESIDUAL_PROMOTION_PATH.read_bytes()
                ),
                "coverage_file_sha256": residual_coverage_file_sha256,
                "layout_transition_bound": True,
            },
            "full_candidate_bound": True,
        }
    pk_only_overlay = load_pk_only_exact_blocked_overlay()
    (
        pk_only_audit_content,
        pk_only_private_content,
        pk_only_promotion_content,
        pk_only_audit,
        pk_only_promotion,
        pk_only_context,
    ) = pk_only_overlay.build_outputs()
    require(
        PK_ONLY_EXACT_BLOCKED_AUDIT_PATH.is_file()
        and PK_ONLY_EXACT_BLOCKED_AUDIT_PATH.read_text(encoding="utf-8")
        == pk_only_audit_content,
        "tracked PK-only exact-blocked audit report drifted",
    )
    require(
        PK_ONLY_EXACT_BLOCKED_OVERLAY_PATH.is_file()
        and PK_ONLY_EXACT_BLOCKED_OVERLAY_PATH.read_text(encoding="utf-8")
        == pk_only_private_content,
        "tracked PK-only exact-blocked overlay drifted",
    )
    require(
        PK_ONLY_EXACT_BLOCKED_PROMOTION_PATH.is_file()
        and PK_ONLY_EXACT_BLOCKED_PROMOTION_PATH.read_text(encoding="utf-8")
        == pk_only_promotion_content,
        "tracked PK-only exact-blocked promotion report drifted",
    )
    pk_only_rows = pk_only_overlay.read_jsonl(
        PK_ONLY_EXACT_BLOCKED_OVERLAY_PATH
    )
    pk_only_overlay.validate_audit(
        pk_only_audit,
        context=pk_only_context,
    )
    pk_only_overlay.validate_overlay_rows(
        pk_only_rows,
        audit=pk_only_audit,
        audit_file_sha256=pk_only_context["audit_file_sha256"],
    )
    pk_only_overlay.validate_promotion_report(
        pk_only_promotion,
        audit=pk_only_audit,
        audit_file_sha256=pk_only_context["audit_file_sha256"],
        private_content=pk_only_private_content,
    )
    require(
        pk_only_promotion.get("schema")
        == (
            "nobu16.kr.pk-msggame-exact-blocked-pk-only-closure-"
            "promotion.v1"
        )
        and pk_only_promotion.get("status") == "PASS"
        and pk_only_promotion.get("steam_write_performed") is False
        and pk_only_promotion.get("result", {}).get(
            "private_overlay_sha256"
        )
        == sha256_bytes(PK_ONLY_EXACT_BLOCKED_OVERLAY_PATH.read_bytes())
        and len(pk_only_rows)
        == EXPECTED_PK_ONLY_EXACT_BLOCKED_PROMOTIONS,
        "PK-only exact-blocked promotion report drifted",
    )
    by_coordinate = {str(row["coordinate"]): row for row in rows}
    for row in residual_rows:
        coordinate = str(row["coordinate"])
        require(
            coordinate not in by_coordinate,
            f"PK exact/residual overlay overlap: {coordinate}",
        )
        by_coordinate[coordinate] = row
    for row in pk_only_rows:
        coordinate = str(row["coordinate"])
        require(
            coordinate not in by_coordinate,
            f"PK promoted overlay overlap: {coordinate}",
        )
        by_coordinate[coordinate] = row
    metadata = {
        "promotion_count": len(by_coordinate),
        "pk_only_layer_included": True,
        "exact": {
            "promotion_count": len(rows),
            "private_sha256": sha256_bytes(PK_OVERLAY_PATH.read_bytes()),
            "promotion_report_sha256": sha256_bytes(
                PK_PROMOTION_PATH.read_bytes()
            ),
            "coverage_file_sha256": coverage_file_sha256,
        },
        "residual": {
            "promotion_count": len(residual_rows),
            "private_sha256": sha256_bytes(
                PK_RESIDUAL_OVERLAY_PATH.read_bytes()
            ),
            "promotion_report_sha256": sha256_bytes(
                PK_RESIDUAL_PROMOTION_PATH.read_bytes()
            ),
            "coverage_file_sha256": residual_coverage_file_sha256,
            "layout_transition_bound": True,
        },
        "pk_only_exact_blocked": {
            "promotion_count": len(pk_only_rows),
            "private_sha256": sha256_bytes(
                PK_ONLY_EXACT_BLOCKED_OVERLAY_PATH.read_bytes()
            ),
            "promotion_report_sha256": sha256_bytes(
                PK_ONLY_EXACT_BLOCKED_PROMOTION_PATH.read_bytes()
            ),
            "coverage_file_sha256": pk_only_context[
                "audit_file_sha256"
            ],
            "predecessor_integrated_private_sha256": pk_only_audit[
                "guards"
            ]["integrated_private_sha256"],
            "base_runtime_proof_inherited": False,
        },
        "full_candidate_bound": True,
    }
    require(
        len(by_coordinate) == EXPECTED_PK_POST_PK_ONLY_PROMOTIONS,
        "post-PK-only VM overlay completeness drifted",
    )
    if not include_cross_resource:
        return by_coordinate, metadata

    cross_overlay = load_pk_cross_resource_exact_closure_overlay()
    (
        cross_audit_content,
        cross_private_content,
        cross_promotion_content,
        cross_audit,
        cross_promotion,
        cross_context,
    ) = cross_overlay.build_outputs()
    require(
        PK_CROSS_RESOURCE_EXACT_CLOSURE_AUDIT_PATH.is_file()
        and PK_CROSS_RESOURCE_EXACT_CLOSURE_AUDIT_PATH.read_text(
            encoding="utf-8"
        )
        == cross_audit_content,
        "tracked cross-resource closure audit drifted",
    )
    require(
        PK_CROSS_RESOURCE_EXACT_CLOSURE_OVERLAY_PATH.is_file()
        and PK_CROSS_RESOURCE_EXACT_CLOSURE_OVERLAY_PATH.read_text(
            encoding="utf-8"
        )
        == cross_private_content,
        "private cross-resource closure overlay drifted",
    )
    require(
        PK_CROSS_RESOURCE_EXACT_CLOSURE_PROMOTION_PATH.is_file()
        and PK_CROSS_RESOURCE_EXACT_CLOSURE_PROMOTION_PATH.read_text(
            encoding="utf-8"
        )
        == cross_promotion_content,
        "tracked cross-resource closure promotion drifted",
    )
    cross_rows = cross_overlay.read_jsonl(
        PK_CROSS_RESOURCE_EXACT_CLOSURE_OVERLAY_PATH
    )
    cross_overlay.validate_audit(cross_audit)
    require(
        cross_promotion.get("schema")
        == (
            "nobu16.kr.pk-msggame-pending-cross-resource-exact-"
            "closure-promotion.v1"
        )
        and cross_promotion.get("status") == "PASS"
        and cross_promotion.get("steam_write_performed") is False
        and cross_promotion.get("result", {}).get("private_overlay_sha256")
        == sha256_bytes(
            PK_CROSS_RESOURCE_EXACT_CLOSURE_OVERLAY_PATH.read_bytes()
        )
        and len(cross_rows)
        == EXPECTED_PK_CROSS_RESOURCE_EXACT_CLOSURE_PROMOTIONS,
        "cross-resource closure promotion report drifted",
    )
    for row in cross_rows:
        coordinate = str(row["coordinate"])
        require(
            coordinate not in by_coordinate,
            f"cross-resource promoted overlay overlap: {coordinate}",
        )
        by_coordinate[coordinate] = row
    require(
        len(by_coordinate) == EXPECTED_PK_INTEGRATED_PROMOTIONS,
        "final PK VM overlay completeness drifted",
    )
    metadata["promotion_count"] = len(by_coordinate)
    metadata["cross_resource_layer_included"] = True
    metadata["cross_resource_exact_closure"] = {
        "promotion_count": len(cross_rows),
        "private_sha256": sha256_bytes(
            PK_CROSS_RESOURCE_EXACT_CLOSURE_OVERLAY_PATH.read_bytes()
        ),
        "promotion_report_sha256": sha256_bytes(
            PK_CROSS_RESOURCE_EXACT_CLOSURE_PROMOTION_PATH.read_bytes()
        ),
        "coverage_file_sha256": cross_context["audit_file_sha256"],
        "predecessor_integrated_private_sha256": cross_audit["guards"][
            "checkpoint_private_sha256"
        ],
        "base_runtime_proof_inherited": False,
    }
    return by_coordinate, metadata


def validated_dynamic_honorific_spacing_updates() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[str, Any],
]:
    layer = load_dynamic_honorific_spacing()
    (
        decision_content,
        base_overlay_content,
        pk_overlay_content,
        audit_content,
        base_report_content,
        pk_report_content,
        audit,
        bundle,
    ) = layer.build_outputs()
    layer.validate_outputs(
        decision_content=decision_content,
        base_overlay_content=base_overlay_content,
        pk_overlay_content=pk_overlay_content,
        audit_content=audit_content,
        base_report_content=base_report_content,
        pk_report_content=pk_report_content,
        audit=audit,
        bundle=bundle,
    )
    expected_files = (
        (layer.DEFAULT_DECISION_OUTPUT, decision_content),
        (layer.DEFAULT_BASE_OVERLAY_OUTPUT, base_overlay_content),
        (layer.DEFAULT_PK_OVERLAY_OUTPUT, pk_overlay_content),
        (layer.DEFAULT_AUDIT_OUTPUT, audit_content),
        (layer.DEFAULT_BASE_REPORT_OUTPUT, base_report_content),
        (layer.DEFAULT_PK_REPORT_OUTPUT, pk_report_content),
    )
    for path, content in expected_files:
        require(
            path.is_file() and path.read_text(encoding="utf-8") == content,
            f"dynamic honorific spacing artifact drifted: {path}",
        )
    updates: dict[tuple[str, str], dict[str, Any]] = {}
    action_counts: Counter[str] = Counter()
    for row in bundle["updated_rows"]:
        key = (str(row["resource"]), str(row["coordinate"]))
        require(
            key not in updates,
            f"duplicate dynamic honorific spacing update: {key}",
        )
        evidence = row.get("runtime_vm_verification")
        require(
            isinstance(evidence, dict),
            f"dynamic honorific spacing evidence is absent: {key}",
        )
        action_counts[str(evidence.get("action"))] += 1
        updates[key] = row
    require(
        action_counts
        == {
            "translation_override": 4,
            "verification_renewal": 466,
            "runtime_promotion":
            EXPECTED_DYNAMIC_HONORIFIC_SPACING_PROMOTIONS,
        }
        and audit["scope"]["post_layer_pending_rows"]
        == EXPECTED_FINAL_PENDING_AFTER,
        f"dynamic honorific spacing action counts drifted: {action_counts}",
    )
    return updates, {
        "translation_override_count": action_counts[
            "translation_override"
        ],
        "verification_renewal_count": action_counts[
            "verification_renewal"
        ],
        "promotion_count": action_counts["runtime_promotion"],
        "updated_row_count": len(updates),
        "private_update_sha256": sha256_bytes(
            decision_content.encode("utf-8")
        ),
        "audit_report_sha256": sha256_bytes(
            audit_content.encode("utf-8")
        ),
        "audit_report_payload_sha256": audit["guards"][
            "report_payload_sha256"
        ],
        "base_candidate_packed_sha256": audit["guards"][
            "base_candidate_packed_sha256"
        ],
        "pk_candidate_packed_sha256": audit["guards"][
            "pk_candidate_packed_sha256"
        ],
        "eligible_coordinate_sha256": audit["guards"][
            "eligible_coordinate_sha256"
        ],
        "eligible_root_sha256": audit["guards"][
            "eligible_root_sha256"
        ],
        "steam_write_performed": False,
    }


def validated_bound_terminal_family_updates() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[str, Any],
]:
    layer = load_bound_terminal_family()
    (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        bundle,
    ) = layer.build_outputs()
    layer.validate_outputs(
        decision_content=decision_content,
        evidence_content=evidence_content,
        audit_content=audit_content,
        promotion_content=promotion_content,
        audit=audit,
        bundle=bundle,
    )
    expected_files = (
        (layer.DEFAULT_DECISION_OUTPUT, decision_content),
        (layer.DEFAULT_EVIDENCE_OUTPUT, evidence_content),
        (layer.DEFAULT_AUDIT_OUTPUT, audit_content),
        (layer.DEFAULT_PROMOTION_OUTPUT, promotion_content),
    )
    for path, content in expected_files:
        require(
            path.is_file() and path.read_text(encoding="utf-8") == content,
            f"bound terminal family artifact drifted: {path}",
        )
    updates: dict[tuple[str, str], dict[str, Any]] = {}
    action_counts: Counter[str] = Counter()
    for row in bundle["updated_rows"]:
        key = (str(row["resource"]), str(row["coordinate"]))
        require(
            key not in updates and key[0] == "pk_msggame",
            f"duplicate or non-PK terminal family update: {key}",
        )
        action = str(row.get("terminal_family_update_action"))
        action_counts[action] += 1
        evidence = (
            row.get("runtime_vm_verification")
            if row.get("runtime_review") == "verified"
            else row.get("terminal_family_runtime_evidence")
        )
        require(
            isinstance(evidence, dict)
            and evidence.get("action") == action
            and evidence.get("method")
            == layer.METHOD,
            f"bound terminal family evidence is absent: {key}",
        )
        updates[key] = row
    require(
        action_counts
        == {
            "translation_override": 5,
            "verification_renewal": 680,
            "translation_override_and_runtime_promotion": 3,
            "translation_override_pending": 6,
            "runtime_promotion": 1,
        }
        and audit["scope"]["post_layer_pending_rows"]
        == EXPECTED_BOUND_TERMINAL_FINAL_PENDING_AFTER
        and audit["scope"]["affected_existing_verified_pk_rows"] == 685
        and audit["scope"]["affected_existing_verified_base_rows"] == 0,
        f"bound terminal family action counts drifted: {action_counts}",
    )
    return updates, {
        "translation_override_count": len(layer.TRANSLATION_OVERRIDES),
        "verification_renewal_count": 685,
        "promotion_count": EXPECTED_BOUND_TERMINAL_FAMILY_PROMOTIONS,
        "pending_override_count": action_counts[
            "translation_override_pending"
        ],
        "updated_row_count": len(updates),
        "private_update_sha256": sha256_bytes(
            decision_content.encode("utf-8")
        ),
        "private_evidence_sha256": sha256_bytes(
            evidence_content.encode("utf-8")
        ),
        "audit_report_sha256": sha256_bytes(
            audit_content.encode("utf-8")
        ),
        "audit_report_payload_sha256": audit["guards"][
            "report_payload_sha256"
        ],
        "promotion_report_sha256": sha256_bytes(
            promotion_content.encode("utf-8")
        ),
        "pk_predecessor_candidate_packed_sha256": audit["guards"][
            "pk_predecessor_candidate_packed_sha256"
        ],
        "pk_candidate_packed_sha256": audit["guards"][
            "pk_candidate_packed_sha256"
        ],
        "override_coordinate_sha256": audit["guards"][
            "override_coordinate_sha256"
        ],
        "override_manifest_sha256": audit["guards"][
            "override_manifest_sha256"
        ],
        "actual_eligible_coordinate_sha256": audit["guards"][
            "actual_eligible_coordinate_sha256"
        ],
        "actual_eligible_root_sha256": audit["guards"][
            "actual_eligible_root_sha256"
        ],
        "actual_rejected_coordinate_sha256": audit["guards"][
            "actual_rejected_coordinate_sha256"
        ],
        "actual_rejected_root_sha256": audit["guards"][
            "actual_rejected_root_sha256"
        ],
        "steam_write_performed": False,
    }


def validated_thought_predicate_family_updates() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[tuple[str, str], dict[str, Any]],
    dict[str, str],
    dict[str, Any],
]:
    layer = load_thought_predicate_family()
    (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        bundle,
    ) = layer.build_outputs()
    layer.validate_outputs(
        decision_content=decision_content,
        evidence_content=evidence_content,
        audit_content=audit_content,
        promotion_content=promotion_content,
        audit=audit,
        bundle=bundle,
    )
    expected_files = (
        (layer.DEFAULT_DECISION_OUTPUT, decision_content),
        (layer.DEFAULT_EVIDENCE_OUTPUT, evidence_content),
        (layer.DEFAULT_AUDIT_OUTPUT, audit_content),
        (layer.DEFAULT_PROMOTION_OUTPUT, promotion_content),
    )
    for path, content in expected_files:
        require(
            path.is_file() and path.read_text(encoding="utf-8") == content,
            f"thought-predicate family artifact drifted: {path}",
        )
    updates: dict[tuple[str, str], dict[str, Any]] = {}
    predecessors: dict[tuple[str, str], dict[str, Any]] = {}
    action_counts: Counter[str] = Counter()
    for row in bundle["updated_rows"]:
        key = (str(row["resource"]), str(row["coordinate"]))
        require(
            key not in updates and key[0] == "pk_msggame",
            f"duplicate or non-PK thought-predicate update: {key}",
        )
        action = str(row.get("thought_predicate_family_update_action"))
        evidence = row.get("runtime_vm_verification")
        require(
            isinstance(evidence, dict)
            and evidence.get("action") == action
            and evidence.get("method") == layer.METHOD,
            f"thought-predicate family evidence is absent: {key}",
        )
        predecessor = bundle["analysis"]["predecessor_rows"].get(key)
        require(
            isinstance(predecessor, dict),
            f"thought-predicate predecessor row is absent: {key}",
        )
        action_counts[action] += 1
        updates[key] = row
        predecessors[key] = predecessor
    require(
        action_counts
        == {
            "runtime_promotion": 1,
            "translation_override_and_runtime_promotion": 22,
            "translation_override_and_verification_renewal": 53,
        }
        and audit["scope"]["post_layer_pending_rows"]
        == EXPECTED_THOUGHT_PREDICATE_FINAL_PENDING_AFTER
        and audit["scope"]["translation_override_rows"] == 75
        and audit["scope"]["existing_verified_evidence_renewal_rows"] == 53
        and audit["scope"]["pending_eligible_rows"]
        == EXPECTED_THOUGHT_PREDICATE_FAMILY_PROMOTIONS,
        f"thought-predicate family action counts drifted: {action_counts}",
    )
    overrides = {
        str(coordinate): str(translation)
        for coordinate, translation in bundle["analysis"]["overrides"].items()
    }
    require(
        len(overrides) == 75,
        "thought-predicate override map count drifted",
    )
    return updates, predecessors, overrides, {
        "translation_override_count": 75,
        "verification_renewal_count": 53,
        "promotion_count": EXPECTED_THOUGHT_PREDICATE_FAMILY_PROMOTIONS,
        "updated_row_count": len(updates),
        "private_update_sha256": sha256_bytes(
            decision_content.encode("utf-8")
        ),
        "private_evidence_sha256": sha256_bytes(
            evidence_content.encode("utf-8")
        ),
        "audit_report_sha256": sha256_bytes(
            audit_content.encode("utf-8")
        ),
        "audit_report_payload_sha256": audit["guards"][
            "report_payload_sha256"
        ],
        "promotion_report_sha256": sha256_bytes(
            promotion_content.encode("utf-8")
        ),
        "pk_predecessor_candidate_packed_sha256": audit["guards"][
            "pk_predecessor_candidate_packed_sha256"
        ],
        "pk_candidate_packed_sha256": audit["guards"][
            "pk_candidate_packed_sha256"
        ],
        "override_coordinate_sha256": audit["guards"][
            "override_coordinate_sha256"
        ],
        "override_manifest_sha256": audit["guards"][
            "override_manifest_sha256"
        ],
        "assembly_manifest_sha256": audit["guards"][
            "assembly_manifest_sha256"
        ],
        "pending_eligible_coordinate_sha256": audit["guards"][
            "pending_eligible_coordinate_sha256"
        ],
        "verified_renewal_coordinate_sha256": audit["guards"][
            "verified_renewal_coordinate_sha256"
        ],
        "steam_write_performed": False,
    }


def apply_thought_predicate_family_updates(
    merged: dict[tuple[str, str], dict[str, Any]],
) -> tuple[int, dict[str, Any]]:
    thought_layer = load_thought_predicate_family()
    (
        thought_updates,
        thought_predecessors,
        thought_overrides,
        thought_metadata,
    ) = validated_thought_predicate_family_updates()
    thought_promotions = 0
    for key, updated in thought_updates.items():
        predecessor = merged.get(key)
        require(
            predecessor is not None
            and predecessor == thought_predecessors.get(key),
            f"thought-predicate predecessor row drifted: {key}",
        )
        action = str(
            updated.get("thought_predicate_family_update_action")
        )
        evidence = updated.get("runtime_vm_verification")
        require(
            isinstance(evidence, dict)
            and evidence.get("action") == action
            and evidence.get("method") == thought_layer.METHOD,
            f"thought-predicate evidence drifted: {key}",
        )
        changed_fields = {
            field
            for field in set(predecessor) | set(updated)
            if predecessor.get(field) != updated.get(field)
        }
        if action == "runtime_promotion":
            require(
                changed_fields
                == RUNTIME_MUTABLE_FIELDS
                | {"thought_predicate_family_update_action"}
                and predecessor.get("runtime_review") == "pending"
                and updated.get("runtime_review") == "verified"
                and updated.get("scope_classification") == "retranslated"
                and updated.get("layout_review") == "runtime_verified",
                f"thought-predicate promotion transition drifted: {key}",
            )
            thought_promotions += 1
        elif action == "translation_override_and_runtime_promotion":
            require(
                changed_fields
                == RUNTIME_MUTABLE_FIELDS
                | {
                    "translation",
                    "thought_predicate_family_update_action",
                }
                and predecessor.get("runtime_review") == "pending"
                and updated.get("runtime_review") == "verified"
                and updated.get("scope_classification") == "retranslated"
                and updated.get("layout_review") == "runtime_verified"
                and key[1] in thought_overrides
                and updated.get("translation") == thought_overrides[key[1]],
                f"thought-predicate override promotion drifted: {key}",
            )
            thought_promotions += 1
        elif action == "translation_override_and_verification_renewal":
            require(
                changed_fields
                == {
                    "translation",
                    "runtime_vm_verification",
                    "thought_predicate_family_update_action",
                }
                and predecessor.get("runtime_review")
                == updated.get("runtime_review")
                == "verified"
                and key[1] in thought_overrides
                and updated.get("translation") == thought_overrides[key[1]],
                f"thought-predicate renewal transition drifted: {key}",
            )
        else:
            raise IntegrationError(
                f"thought-predicate action is invalid: {key}"
            )
        merged[key] = dict(updated)
    require(
        thought_promotions
        == EXPECTED_THOUGHT_PREDICATE_FAMILY_PROMOTIONS,
        (
            "thought-predicate promotion count drifted: "
            f"{thought_promotions}"
        ),
    )
    return thought_promotions, thought_metadata


def validated_bound_terminal_caller_updates() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[tuple[str, str], dict[str, Any]],
    dict[str, str],
    dict[str, Any],
    dict[str, Any],
]:
    layer = load_bound_terminal_caller()
    (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        bundle,
    ) = layer.build_outputs()
    layer.validate_outputs(
        decision_content=decision_content,
        evidence_content=evidence_content,
        audit_content=audit_content,
        promotion_content=promotion_content,
        audit=audit,
        bundle=bundle,
    )
    for path, content in (
        (layer.DEFAULT_DECISION_OUTPUT, decision_content),
        (layer.DEFAULT_EVIDENCE_OUTPUT, evidence_content),
        (layer.DEFAULT_AUDIT_OUTPUT, audit_content),
        (layer.DEFAULT_PROMOTION_OUTPUT, promotion_content),
    ):
        require(
            path.is_file() and path.read_text(encoding="utf-8") == content,
            f"bound-terminal caller artifact drifted: {path}",
        )
    updates: dict[tuple[str, str], dict[str, Any]] = {}
    predecessors: dict[tuple[str, str], dict[str, Any]] = {}
    action_counts: Counter[str] = Counter()
    for row in bundle["updated_rows"]:
        key = (str(row["resource"]), str(row["coordinate"]))
        require(
            key not in updates and key[0] == "pk_msggame",
            f"duplicate or non-PK caller update: {key}",
        )
        action = str(row.get("bound_terminal_caller_update_action"))
        evidence = (
            row.get("runtime_vm_verification")
            if row.get("runtime_review") == "verified"
            else row.get("bound_terminal_caller_runtime_evidence")
        )
        predecessor = bundle["predecessor_rows"].get(key)
        require(
            isinstance(evidence, dict)
            and evidence.get("action") == action
            and evidence.get("method") == layer.METHOD
            and isinstance(predecessor, dict),
            f"bound-terminal caller evidence/predecessor is absent: {key}",
        )
        action_counts[action] += 1
        updates[key] = row
        predecessors[key] = predecessor
    require(
        action_counts
        == {
            "translation_override_pending": 152,
            "translation_override_and_verification_renewal": 74,
            "verification_renewal": 46,
            "translation_override_and_runtime_promotion": 31,
            "runtime_promotion": 10,
        }
        and audit["scope"]["post_layer_pending_rows"] == 8_600
        and audit["scope"]["translation_override_coordinates"] == 261
        and audit["scope"]["ledger_backed_override_coordinates"] == 257
        and audit["scope"]["literal_only_override_coordinates"] == 4
        and audit["scope"]["affected_existing_verified_pk_rows"] == 120
        and audit["scope"]["actual_eligible_rows"]
        == EXPECTED_BOUND_TERMINAL_CALLER_PROMOTIONS,
        f"bound-terminal caller action counts drifted: {action_counts}",
    )
    overrides = {
        str(coordinate): str(translation)
        for coordinate, translation in layer.TRANSLATION_OVERRIDES.items()
    }
    metadata = {
        "translation_override_count": 261,
        "ledger_backed_override_count": 257,
        "ledger_override_coordinate_sha256": layer.coordinate_digest(
            bundle["analysis"]["ledger_override_coordinates"]
        ),
        "literal_only_override_count": 4,
        "verification_renewal_count": 120,
        "promotion_count": EXPECTED_BOUND_TERMINAL_CALLER_PROMOTIONS,
        "updated_row_count": len(updates),
        "private_source_update_sha256": sha256_bytes(
            decision_content.encode("utf-8")
        ),
        "private_source_evidence_sha256": sha256_bytes(
            evidence_content.encode("utf-8")
        ),
        "audit_report_sha256": sha256_bytes(audit_content.encode("utf-8")),
        "audit_report_payload_sha256": audit["guards"][
            "report_payload_sha256"
        ],
        "promotion_report_sha256": sha256_bytes(
            promotion_content.encode("utf-8")
        ),
        "source_layer_pk_predecessor_candidate_packed_sha256": audit[
            "guards"
        ]["predecessor_pk_candidate_packed_sha256"],
        "source_layer_pk_candidate_packed_sha256": audit["guards"][
            "pk_candidate_packed_sha256"
        ],
        "override_coordinate_sha256": audit["guards"][
            "override_coordinate_sha256"
        ],
        "source_layer_verified_renewal_coordinate_sha256": audit["guards"][
            "verified_renewal_coordinate_sha256"
        ],
        "steam_write_performed": False,
    }
    return updates, predecessors, overrides, bundle["analysis"], metadata


def build_combined_caller_context(
    merged: Mapping[tuple[str, str], Mapping[str, Any]],
    caller_overrides: Mapping[str, str],
    source_analysis: Mapping[str, Any],
) -> dict[str, Any]:
    layer = load_bound_terminal_caller()
    replacements = {
        layer.parse_coordinate(coordinate): str(row["translation"])
        for (resource, coordinate), row in merged.items()
        if resource == "pk_msggame" and isinstance(row.get("translation"), str)
    }
    predecessor_blob = layer.BASE_AUDIT.rebuild_packed_with_literals(
        layer.BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        replacements,
    )
    predecessor_records = layer.BASE_AUDIT.records_from_blob(predecessor_blob)
    candidate_replacements = dict(replacements)
    candidate_replacements.update(
        {
            layer.parse_coordinate(coordinate): translation
            for coordinate, translation in caller_overrides.items()
        }
    )
    candidate_blob = layer.BASE_AUDIT.rebuild_packed_with_literals(
        layer.BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        candidate_replacements,
    )
    candidate_records = layer.BASE_AUDIT.records_from_blob(candidate_blob)
    require(
        sha256_bytes(predecessor_blob)
        == EXPECTED_THOUGHT_PREDICATE_CANDIDATE_SHA256
        and sha256_bytes(candidate_blob)
        == EXPECTED_BOUND_TERMINAL_CALLER_COMBINED_CANDIDATE_SHA256,
        "combined caller predecessor/candidate packed hash drifted",
    )
    targets = {
        layer.parse_coordinate(coordinate)[:2]
        for coordinate in caller_overrides
    }
    layer.HONORIFIC.changed_record_guard(
        predecessor_records=predecessor_records,
        candidate_records=candidate_records,
        expected_changed=targets,
    )
    target_delta = layer.target_delta_manifest(
        predecessor_records=predecessor_records,
        candidate_records=candidate_records,
    )
    target_delta_sha256 = canonical_sha256(target_delta)
    assembly: list[list[Any]] = []
    selector_summary: dict[int, dict[str, Any]] = {}
    for family, selector in layer.FAMILY_SELECTORS.items():
        sites = layer.call_sites(candidate_records, selector)
        site_sha256 = sha256_bytes("\n".join(sites).encode("ascii"))
        require(
            len(sites) == layer.EXPECTED_CALL_SITES[selector]
            and site_sha256 == layer.EXPECTED_CALL_SITE_SHA256[selector],
            f"combined caller selector universe drifted: {selector}",
        )
        selector_summary[selector] = {
            "family": family,
            "call_sites": len(sites),
            "call_site_sha256": site_sha256,
        }
        for site in sites:
            left, right = layer.adjacent_literals(candidate_records, site)
            for terminal in sorted(layer.FAMILY_TARGETS[family]):
                ending = layer.BASE_AUDIT.parse_record_literals(
                    candidate_records[terminal]
                )[0].text
                assembly.append(
                    [
                        site,
                        terminal[1],
                        layer.ENGINE.sha256_text(left + ending + right),
                    ]
                )
    require(
        len(assembly) == layer.EXPECTED_ASSEMBLY_COMBINATIONS,
        "combined caller assembly universe drifted",
    )
    assembly_manifest_sha256 = canonical_sha256(assembly)
    root_proofs = layer.HONORIFIC.root_delta_proofs(
        resource="pk_msggame",
        affected_records=source_analysis["affected"],
        edges=source_analysis["source_edges"],
        target_records=targets,
        predecessor_records=predecessor_records,
        candidate_records=candidate_records,
        target_delta_sha256=target_delta_sha256,
    )
    overlap_record = candidate_records[(15, 1068)]
    require(
        sha256_bytes(overlap_record.data)
        == EXPECTED_BOUND_TERMINAL_CALLER_OVERLAP_RECORD_SHA256,
        "combined caller overlap record hash drifted",
    )
    return {
        "predecessor_blob": predecessor_blob,
        "predecessor_records": predecessor_records,
        "candidate_blob": candidate_blob,
        "candidate_records": candidate_records,
        "target_delta_sha256": target_delta_sha256,
        "assembly_manifest_sha256": assembly_manifest_sha256,
        "selector_summary": selector_summary,
        "root_proofs": root_proofs,
        "root_proof_manifest_sha256": canonical_sha256(
            {
                f"{root[0]}:{root[1]}": proof
                for root, proof in sorted(root_proofs.items())
            }
        ),
    }


def apply_bound_terminal_caller_updates(
    merged: dict[tuple[str, str], dict[str, Any]],
) -> tuple[int, dict[str, Any]]:
    layer = load_bound_terminal_caller()
    (
        caller_updates,
        caller_predecessors,
        caller_overrides,
        source_analysis,
        metadata,
    ) = validated_bound_terminal_caller_updates()
    mismatches = {
        key
        for key, predecessor in caller_predecessors.items()
        if merged.get(key) != predecessor
    }
    require(
        mismatches == {BOUND_TERMINAL_CALLER_OVERLAP_KEY},
        f"caller predecessor overlap drifted: {sorted(mismatches)}",
    )
    combined = build_combined_caller_context(
        merged,
        caller_overrides,
        source_analysis,
    )
    promotions = 0
    final_evidence_rows: list[dict[str, Any]] = []
    overlap_evidence_sha256 = ""
    for key, source_updated in caller_updates.items():
        source_predecessor = caller_predecessors[key]
        current = merged.get(key)
        require(current is not None, f"caller predecessor row is absent: {key}")
        action = str(source_updated["bound_terminal_caller_update_action"])
        if key == BOUND_TERMINAL_CALLER_OVERLAP_KEY:
            require(
                current.get("translation") == "을 수복하겠다"
                and current.get("thought_predicate_family_update_action")
                == "translation_override_and_verification_renewal"
                and current.get("runtime_review") == "verified",
                "caller/thought overlap translation or action drifted",
            )
            source_evidence = source_updated["runtime_vm_verification"]
            evidence = copy.deepcopy(source_evidence)
            evidence["translation_utf16le_sha256"] = layer.ENGINE.sha256_text(
                str(current["translation"])
            )
            root_proof = combined["root_proofs"][(15, 1068)]
            predecessor_record = combined["predecessor_records"][(15, 1068)]
            candidate_record = combined["candidate_records"][(15, 1068)]
            evidence["source_caller_evidence_sha256"] = canonical_sha256(
                source_evidence
            )
            evidence["combined_final_binding"] = {
                "thought_predecessor_row_sha256": canonical_sha256(current),
                "thought_predecessor_runtime_vm_verification_sha256":
                canonical_sha256(current["runtime_vm_verification"]),
                "predecessor_record_raw_sha256": sha256_bytes(
                    predecessor_record.data
                ),
                "candidate_record_raw_sha256": sha256_bytes(
                    candidate_record.data
                ),
                "pk_candidate_packed_sha256": sha256_bytes(
                    combined["candidate_blob"]
                ),
                "target_delta_manifest_sha256": combined[
                    "target_delta_sha256"
                ],
                "assembly_hash_manifest_sha256": combined[
                    "assembly_manifest_sha256"
                ],
                "root_delta_proof_sha256": root_proof["proof_sha256"],
                "renewal_payload_reference_sha256":
                BOUND_TERMINAL_CALLER_RENEWAL_REFERENCE_SHA256,
                "thought_translation_preserved": True,
                "control_signature_preserved": (
                    layer.HONORIFIC.component_signatures(predecessor_record)
                    == layer.HONORIFIC.component_signatures(candidate_record)
                ),
                "grammar_complete": True,
            }
            updated = copy.deepcopy(current)
            updated["bound_terminal_caller_update_action"] = action
            updated["runtime_vm_verification"] = evidence
            overlap_evidence_sha256 = canonical_sha256(evidence)
        else:
            require(
                current == source_predecessor,
                f"caller predecessor row drifted: {key}",
            )
            updated = copy.deepcopy(source_updated)
        if action in {
            "runtime_promotion",
            "translation_override_and_runtime_promotion",
        }:
            promotions += 1
        final_evidence = (
            updated.get("runtime_vm_verification")
            if updated.get("runtime_review") == "verified"
            else updated.get("bound_terminal_caller_runtime_evidence")
        )
        require(
            isinstance(final_evidence, dict)
            and final_evidence.get("action") == action,
            f"caller final evidence is absent: {key}",
        )
        final_evidence_rows.append(final_evidence)
        merged[key] = updated
    require(
        promotions == EXPECTED_BOUND_TERMINAL_CALLER_PROMOTIONS,
        f"caller promotion count drifted: {promotions}",
    )
    renewal_evidence_rows = [
        row
        for row in final_evidence_rows
        if row.get("action")
        in {
            "verification_renewal",
            "translation_override_and_verification_renewal",
        }
    ]
    require(
        len(renewal_evidence_rows) == 120,
        "caller final renewal evidence count drifted",
    )
    renewal_manifest_sha256 = canonical_sha256(
        sorted(
            renewal_evidence_rows,
            key=lambda row: layer.parse_coordinate(str(row["coordinate"])),
        )
    )
    require(
        combined["target_delta_sha256"]
        == EXPECTED_BOUND_TERMINAL_CALLER_TARGET_DELTA_SHA256
        and combined["root_proof_manifest_sha256"]
        == EXPECTED_BOUND_TERMINAL_CALLER_ROOT_PROOF_MANIFEST_SHA256
        and combined["root_proofs"][(15, 1068)]["proof_sha256"]
        == EXPECTED_BOUND_TERMINAL_CALLER_OVERLAP_ROOT_PROOF_SHA256
        and overlap_evidence_sha256
        == EXPECTED_BOUND_TERMINAL_CALLER_OVERLAP_EVIDENCE_SHA256
        and renewal_manifest_sha256
        == EXPECTED_BOUND_TERMINAL_CALLER_RENEWAL_MANIFEST_SHA256,
        "combined caller evidence digest drifted",
    )
    metadata.update(
        {
            "pk_predecessor_candidate_packed_sha256": sha256_bytes(
                combined["predecessor_blob"]
            ),
            "pk_candidate_packed_sha256": sha256_bytes(
                combined["candidate_blob"]
            ),
            "target_delta_manifest_sha256": combined[
                "target_delta_sha256"
            ],
            "assembly_hash_manifest_sha256": combined[
                "assembly_manifest_sha256"
            ],
            "root_delta_proof_manifest_sha256": combined[
                "root_proof_manifest_sha256"
            ],
            "combined_final_evidence_manifest_sha256": canonical_sha256(
                sorted(
                    final_evidence_rows,
                    key=lambda row: layer.parse_coordinate(
                        str(row["coordinate"])
                    ),
                )
            ),
            "combined_verified_renewal_evidence_manifest_sha256":
            renewal_manifest_sha256,
            "combined_verified_renewal_coordinate_sha256":
            layer.coordinate_digest(
                str(row["coordinate"]) for row in renewal_evidence_rows
            ),
            "overlap_coordinate": BOUND_TERMINAL_CALLER_OVERLAP_KEY[1],
            "overlap_final_evidence_sha256": overlap_evidence_sha256,
            "overlap_renewal_payload_reference_sha256":
            BOUND_TERMINAL_CALLER_RENEWAL_REFERENCE_SHA256,
            "overlap_thought_translation_preserved": True,
            "overlap_thought_action_preserved": True,
        }
    )
    return promotions, metadata


def validated_bound_terminal_2546_full_caller_updates() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[tuple[str, str], dict[str, Any]],
    dict[str, str],
    dict[str, Any],
    dict[str, Any],
]:
    layer = load_bound_terminal_2546_full_caller()
    (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        bundle,
    ) = layer.build_outputs()
    layer.validate_outputs(
        decision_content=decision_content,
        evidence_content=evidence_content,
        audit_content=audit_content,
        promotion_content=promotion_content,
        audit=audit,
        bundle=bundle,
    )
    for path, content in (
        (layer.DEFAULT_DECISION_OUTPUT, decision_content),
        (layer.DEFAULT_EVIDENCE_OUTPUT, evidence_content),
        (layer.DEFAULT_AUDIT_OUTPUT, audit_content),
        (layer.DEFAULT_PROMOTION_OUTPUT, promotion_content),
    ):
        require(
            path.is_file() and path.read_text(encoding="utf-8") == content,
            f"bound-terminal 2546 full-caller artifact drifted: {path}",
        )
    file_hashes = {
        "audit": sha256_bytes(audit_content.encode("utf-8")),
        "promotion": sha256_bytes(promotion_content.encode("utf-8")),
        "decision": sha256_bytes(decision_content.encode("utf-8")),
        "evidence": sha256_bytes(evidence_content.encode("utf-8")),
    }
    require(
        file_hashes
        == {
            "audit": EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_AUDIT_SHA256,
            "promotion":
            EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_PROMOTION_SHA256,
            "decision":
            EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_DECISION_SHA256,
            "evidence":
            EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_EVIDENCE_SHA256,
        }
        and audit["guards"]["report_payload_sha256"]
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_AUDIT_PAYLOAD_SHA256
        and bundle["promotion"]["guards"]["report_payload_sha256"]
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_PROMOTION_PAYLOAD_SHA256,
        "bound-terminal 2546 full-caller frozen artifact digest drifted",
    )
    all_predecessors = {
        (str(resource), str(coordinate)): dict(row)
        for (resource, coordinate), row
        in bundle["predecessor_rows"].items()
    }
    updates: dict[tuple[str, str], dict[str, Any]] = {}
    evidence_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for evidence in bundle["evidence_rows"]:
        key = ("pk_msggame", str(evidence["coordinate"]))
        require(
            key not in evidence_by_key,
            f"duplicate bound-terminal 2546 evidence: {key}",
        )
        evidence_by_key[key] = dict(evidence)
    action_counts: Counter[str] = Counter()
    for row in bundle["updated_rows"]:
        key = (str(row["resource"]), str(row["coordinate"]))
        action = str(row.get(layer.UPDATE_ACTION_FIELD))
        require(
            key not in updates
            and key[0] == "pk_msggame"
            and key in all_predecessors
            and row.get("runtime_vm_verification") == evidence_by_key.get(key)
            and row["runtime_vm_verification"].get("method") == layer.METHOD
            and row["runtime_vm_verification"].get("action") == action,
            f"bound-terminal 2546 update/evidence binding drifted: {key}",
        )
        action_counts[action] += 1
        updates[key] = dict(row)
    predecessors = {
        key: all_predecessors[key]
        for key in updates
    }
    overrides = {
        str(coordinate): str(translation)
        for coordinate, translation in bundle["overrides"].items()
    }
    promotion = bundle["promotion"]
    require(
        len(updates)
        == len(evidence_by_key)
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_UPDATED_ROW_COUNT
        and len(overrides)
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_OVERRIDE_COUNT
        and dict(action_counts)
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_ACTION_COUNTS
        and promotion["action_counts"]
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_ACTION_COUNTS
        and promotion["result"]["runtime_promotion_rows"]
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_PROMOTIONS
        and promotion["result"]["verification_renewal_rows"]
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_RENEWAL_COUNT
        and promotion["result"]["rejected_pending_rows"]
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_REJECTED_PENDING_COUNT
        and promotion["result"]["pending_rows_after"]
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_FINAL_PENDING_AFTER
        and audit["guards"]["candidate_sha256"]
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_CANDIDATE_SHA256
        and audit["guards"]["override_coordinate_sha256"]
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_OVERRIDE_COORDINATE_SHA256
        and audit["guards"]["decision_coordinate_sha256"]
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_DECISION_COORDINATE_SHA256,
        "bound-terminal 2546 layer counts or guards drifted",
    )
    metadata = {
        "translation_override_count":
        EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_OVERRIDE_COUNT,
        "verification_renewal_count":
        EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_RENEWAL_COUNT,
        "promotion_count":
        EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_PROMOTIONS,
        "updated_row_count":
        EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_UPDATED_ROW_COUNT,
        "rejected_pending_count":
        EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_REJECTED_PENDING_COUNT,
        "action_counts": dict(sorted(action_counts.items())),
        "private_source_update_sha256": file_hashes["decision"],
        "private_source_evidence_sha256": file_hashes["evidence"],
        "audit_report_sha256": file_hashes["audit"],
        "audit_report_payload_sha256": audit["guards"][
            "report_payload_sha256"
        ],
        "promotion_report_sha256": file_hashes["promotion"],
        "promotion_report_payload_sha256": promotion["guards"][
            "report_payload_sha256"
        ],
        "predecessor_integrated_private_sha256": audit["guards"][
            "predecessor_private_sha256"
        ],
        "predecessor_pk_candidate_packed_sha256": audit["guards"][
            "predecessor_candidate_sha256"
        ],
        "pk_candidate_packed_sha256": audit["guards"]["candidate_sha256"],
        "override_coordinate_sha256": audit["guards"][
            "override_coordinate_sha256"
        ],
        "promotion_coordinate_sha256": audit["guards"][
            "promotion_coordinate_sha256"
        ],
        "renewal_coordinate_sha256": audit["guards"][
            "renewal_coordinate_sha256"
        ],
        "decision_coordinate_sha256": audit["guards"][
            "decision_coordinate_sha256"
        ],
        "steam_write_performed": False,
    }
    return updates, predecessors, overrides, bundle["analysis"], metadata


def apply_bound_terminal_2546_full_caller_updates(
    merged: dict[tuple[str, str], dict[str, Any]],
) -> tuple[int, dict[str, Any]]:
    layer = load_bound_terminal_2546_full_caller()
    (
        updates,
        predecessors,
        overrides,
        _analysis,
        metadata,
    ) = validated_bound_terminal_2546_full_caller_updates()
    require(
        set(updates) == set(predecessors),
        "bound-terminal 2546 predecessor/update universe drifted",
    )
    promotions = 0
    renewals = 0
    override_count = 0
    assembly_update_coordinates: list[str] = []
    for key, updated in updates.items():
        predecessor = merged.get(key)
        require(
            predecessor is not None and predecessor == predecessors[key],
            f"bound-terminal 2546 predecessor row drifted: {key}",
        )
        action = str(updated.get(layer.UPDATE_ACTION_FIELD))
        evidence = updated.get("runtime_vm_verification")
        require(
            isinstance(evidence, dict)
            and evidence.get("schema") == layer.EVIDENCE_SCHEMA
            and evidence.get("resource") == "pk_msggame"
            and evidence.get("coordinate") == key[1]
            and evidence.get("status") == "verified"
            and evidence.get("method") == layer.METHOD
            and evidence.get("action") == action
            and evidence.get("translation_utf16le_sha256")
            == layer.ENGINE.sha256_text(str(updated.get("translation")))
            and evidence.get("predecessor_binding")
            == {
                "row_sha256": layer.canonical_sha256(predecessor),
                "checkpoint_sha256":
                EXPECTED_BOUND_TERMINAL_CALLER_FINAL_PRIVATE_SHA256,
            }
            and evidence.get("closure_binding", {}).get("candidate_sha256")
            == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_CANDIDATE_SHA256
            and evidence.get("closure_binding", {}).get(
                "decision_coordinate_sha256"
            )
            == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_DECISION_COORDINATE_SHA256
            and evidence.get("closure_binding", {}).get(
                "audit_report_file_sha256"
            )
            == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_AUDIT_SHA256
            and evidence.get("closure_binding", {}).get(
                "audit_report_payload_sha256"
            )
            == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_AUDIT_PAYLOAD_SHA256
            and evidence.get("per_row_game_playback_required") is False,
            f"bound-terminal 2546 row evidence drifted: {key}",
        )
        changed_fields = {
            field
            for field in set(predecessor) | set(updated)
            if predecessor.get(field) != updated.get(field)
        }
        override_action = action.startswith("translation_override")
        expected_changed = {
            "runtime_vm_verification",
            layer.UPDATE_ACTION_FIELD,
        }
        if override_action:
            expected_changed.update(
                {
                    "translation",
                    "bound_terminal_2546_exact_override_evidence",
                }
            )
            override_evidence = updated.get(
                "bound_terminal_2546_exact_override_evidence"
            )
            require(
                key[1] in overrides
                and updated.get("translation") == overrides[key[1]]
                and isinstance(override_evidence, dict)
                and override_evidence.get("schema")
                == "nobu16.kr.pk-bound-terminal-2546-exact-override.v1"
                and override_evidence.get("automatic_space_inserted") is False
                and override_evidence.get("control_bytes_preserved") is True
                and override_evidence.get("private_handoff_hash_bound") is True
                and override_evidence.get("translation_utf16le_sha256")
                == layer.ENGINE.sha256_text(str(updated.get("translation"))),
                f"bound-terminal 2546 translation override drifted: {key}",
            )
            override_count += 1
        assembly_updated = (
            predecessor.get("runtime_assembly_evidence")
            != updated.get("runtime_assembly_evidence")
        )
        allowed_changed_fields = {
            frozenset(
                expected_changed
                if predecessor.get("runtime_review") == "verified"
                else expected_changed | RUNTIME_MUTABLE_FIELDS
            )
        }
        if assembly_updated:
            assembly_evidence = updated.get("runtime_assembly_evidence")
            require(
                override_action
                and isinstance(assembly_evidence, dict)
                and assembly_evidence.get("automatic_space_inserted") is False,
                f"bound-terminal 2546 assembly evidence drifted: {key}",
            )
            allowed_changed_fields.add(
                frozenset(
                    (
                        expected_changed
                        if predecessor.get("runtime_review") == "verified"
                        else expected_changed | RUNTIME_MUTABLE_FIELDS
                    )
                    | {"runtime_assembly_evidence"}
                )
            )
            assembly_update_coordinates.append(key[1])
        require(
            frozenset(changed_fields) in allowed_changed_fields,
            f"bound-terminal 2546 changed-field set drifted: {key}",
        )
        if action in {
            "runtime_promotion",
            "translation_override_and_runtime_promotion",
        }:
            require(
                predecessor.get("runtime_review") == "pending"
                and updated.get("runtime_review") == "verified"
                and updated.get("scope_classification") == "retranslated"
                and updated.get("layout_review") == "runtime_verified"
                and evidence.get("preexisting_verified_evidence_renewed")
                is False,
                f"bound-terminal 2546 promotion transition drifted: {key}",
            )
            promotions += 1
        elif action in {
            "verification_renewal",
            "translation_override_and_verification_renewal",
        }:
            require(
                predecessor.get("runtime_review")
                == updated.get("runtime_review")
                == "verified"
                and evidence.get("preexisting_verified_evidence_renewed")
                is True,
                f"bound-terminal 2546 renewal transition drifted: {key}",
            )
            renewals += 1
        else:
            raise IntegrationError(
                f"bound-terminal 2546 action is invalid: {key}"
            )
        if key in BOUND_TERMINAL_2546_FULL_CALLER_SUPERSEDED_CALLER_KEYS:
            require(
                predecessor.get("terminal_family_update_action")
                == updated.get("terminal_family_update_action")
                == "verification_renewal"
                and predecessor.get("bound_terminal_caller_update_action")
                == updated.get("bound_terminal_caller_update_action")
                == "translation_override_and_verification_renewal"
                and action
                == "translation_override_and_verification_renewal",
                f"bound-terminal 2546 caller supersession drifted: {key}",
            )
        merged[key] = dict(updated)
    require(
        promotions == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_PROMOTIONS
        and renewals == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_RENEWAL_COUNT
        and override_count
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_OVERRIDE_COUNT
        and len(assembly_update_coordinates)
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_ASSEMBLY_UPDATE_COUNT
        and layer.coordinate_digest(assembly_update_coordinates)
        == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_ASSEMBLY_UPDATE_SHA256,
        "bound-terminal 2546 applied action counts drifted",
    )
    metadata["runtime_assembly_evidence_update_count"] = len(
        assembly_update_coordinates
    )
    metadata["runtime_assembly_evidence_update_coordinate_sha256"] = (
        layer.coordinate_digest(assembly_update_coordinates)
    )
    return promotions, metadata


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
    include_pk_only: bool = True,
    include_cross_resource: bool | None = None,
    include_dynamic_honorific_spacing: bool = False,
    include_bound_terminal_family: bool = False,
    include_thought_predicate_family: bool = False,
    include_bound_terminal_caller: bool = False,
    include_bound_terminal_2546_full_caller: bool = False,
) -> tuple[str, str, dict[str, Any]]:
    if include_cross_resource is None:
        include_cross_resource = include_pk_only
    require(
        include_pk_only or not include_cross_resource,
        "cross-resource integration requires PK-only integration",
    )
    require(
        include_cross_resource or not include_dynamic_honorific_spacing,
        "dynamic honorific spacing requires cross-resource integration",
    )
    require(
        include_dynamic_honorific_spacing
        or not include_bound_terminal_family,
        "bound terminal family requires dynamic honorific integration",
    )
    require(
        include_bound_terminal_family
        or not include_thought_predicate_family,
        "thought-predicate family requires bound terminal integration",
    )
    require(
        include_thought_predicate_family
        or not include_bound_terminal_caller,
        "bound-terminal caller requires thought-predicate integration",
    )
    require(
        include_bound_terminal_caller
        or not include_bound_terminal_2546_full_caller,
        (
            "bound-terminal 2546 full-caller closure requires "
            "bound-terminal caller integration"
        ),
    )
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
    semantic_key, semantic_row, semantic_metadata = (
        validated_semantic_override(source_rows)
    )
    merged[semantic_key] = semantic_row
    pk_effective_rows = [
        row
        for (resource, _coordinate), row in merged.items()
        if resource == "pk_msggame"
    ]
    reflow_overrides, reflow_metadata = REFLOW_OVERRIDE.load_overrides(
        pk_effective_rows
    )
    for coordinate, reflowed in reflow_overrides.items():
        key = ("pk_msggame", coordinate)
        before = merged.get(key)
        require(before is not None, f"reflow decision is absent: {coordinate}")
        changed_fields = {
            field
            for field in set(before) | set(reflowed)
            if before.get(field) != reflowed.get(field)
        }
        require(
            changed_fields == {"translation"},
            f"reflow changed fields other than translation: {coordinate}",
        )
        merged[key] = reflowed
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

    pk_overlay, pk_metadata = validated_pk_overlay(
        include_pk_only=include_pk_only,
        include_cross_resource=include_cross_resource,
    )
    pk_only_method = (
        "reversed_vm_pk_only_exact_blocked_closure_"
        "nonexpansion_analysis"
    )
    cross_resource_method = (
        "reversed_vm_cross_resource_exact_closure_analysis"
    )
    predecessor_overlay = {
        coordinate: evidence
        for coordinate, evidence in pk_overlay.items()
        if evidence.get("method")
        not in {pk_only_method, cross_resource_method}
    }
    pk_only_final_overlay = {
        coordinate: evidence
        for coordinate, evidence in pk_overlay.items()
        if evidence.get("method") == pk_only_method
    }
    cross_resource_final_overlay = {
        coordinate: evidence
        for coordinate, evidence in pk_overlay.items()
        if evidence.get("method") == cross_resource_method
    }
    require(
        len(predecessor_overlay) == EXPECTED_PK_PREDECESSOR_PROMOTIONS
        and len(pk_only_final_overlay)
        == (
            EXPECTED_PK_ONLY_EXACT_BLOCKED_PROMOTIONS
            if include_pk_only
            else 0
        ),
        "PK predecessor/final overlay partition drifted",
    )
    require(
        len(cross_resource_final_overlay)
        == (
            EXPECTED_PK_CROSS_RESOURCE_EXACT_CLOSURE_PROMOTIONS
            if include_cross_resource
            else 0
        ),
        "PK cross-resource overlay partition drifted",
    )

    def integrate_overlay(
        overlay: Mapping[str, Mapping[str, Any]],
    ) -> int:
        integrated = 0
        for coordinate, evidence in overlay.items():
            key = ("pk_msggame", coordinate)
            row = merged.get(key)
            require(
                row is not None,
                f"PK overlay decision is absent: {coordinate}",
            )
            require(
                row.get("scope_classification") == "runtime_fragment_pending"
                and row.get("runtime_review") == "pending"
                and ENGINE.sha256_text(str(row.get("translation")))
                == evidence.get("translation_utf16le_sha256"),
                f"PK overlay source decision drifted: {coordinate}",
            )
            promoted = dict(row)
            promoted["scope_classification"] = "retranslated"
            promoted["runtime_review"] = "verified"
            if (
                evidence.get("method")
                in {
                    (
                        "reversed_vm_residual_full_closure_"
                        "nonexpansion_analysis"
                    ),
                    "reversed_vm_cross_resource_exact_closure_analysis",
                }
            ):
                require(
                    row.get("layout_review")
                    in {"runtime_pending", "unchanged_from_current"}
                    and evidence.get("layout_transition")
                    == {
                        "from": row.get("layout_review"),
                        "to": "runtime_verified",
                    },
                    f"PK runtime layout transition drifted: {coordinate}",
                )
                promoted["layout_review"] = "runtime_verified"
            promoted["runtime_vm_verification"] = evidence
            validate_runtime_only_transition(
                row,
                promoted,
                label=f"PK {coordinate}",
            )
            merged[key] = promoted
            integrated += 1
        return integrated

    predecessor_promotions = integrate_overlay(predecessor_overlay)
    predecessor_rows = sorted(merged.values(), key=coordinate_sort_key)
    predecessor_private_sha256 = sha256_bytes(
        canonical_jsonl(predecessor_rows).encode("utf-8")
    )
    predecessor_checkpoint_match = False
    if include_pk_only:
        expected_predecessor_sha256 = pk_metadata[
            "pk_only_exact_blocked"
        ]["predecessor_integrated_private_sha256"]
        require(
            predecessor_private_sha256 == expected_predecessor_sha256,
            (
                "PK-only predecessor checkpoint drifted: "
                f"{predecessor_private_sha256}"
            ),
        )
        predecessor_checkpoint_match = True
    pk_only_promotions = integrate_overlay(pk_only_final_overlay)
    post_pk_only_rows = sorted(merged.values(), key=coordinate_sort_key)
    post_pk_only_private_sha256 = sha256_bytes(
        canonical_jsonl(post_pk_only_rows).encode("utf-8")
    )
    post_pk_only_checkpoint_match = False
    if include_cross_resource:
        expected_post_pk_only_sha256 = pk_metadata[
            "cross_resource_exact_closure"
        ]["predecessor_integrated_private_sha256"]
        require(
            post_pk_only_private_sha256 == expected_post_pk_only_sha256,
            (
                "cross-resource predecessor checkpoint drifted: "
                f"{post_pk_only_private_sha256}"
            ),
        )
        post_pk_only_checkpoint_match = True
    cross_resource_promotions = integrate_overlay(
        cross_resource_final_overlay
    )
    post_cross_rows = sorted(merged.values(), key=coordinate_sort_key)
    post_cross_private_sha256 = sha256_bytes(
        canonical_jsonl(post_cross_rows).encode("utf-8")
    )
    dynamic_honorific_promotions = 0
    dynamic_honorific_metadata: dict[str, Any] | None = None
    if include_dynamic_honorific_spacing:
        require(
            post_cross_private_sha256
            == EXPECTED_POST_CROSS_PRIVATE_SHA256,
            (
                "dynamic honorific predecessor checkpoint drifted: "
                f"{post_cross_private_sha256}"
            ),
        )
        honorific_updates, dynamic_honorific_metadata = (
            validated_dynamic_honorific_spacing_updates()
        )
        for key, updated in honorific_updates.items():
            predecessor = merged.get(key)
            require(
                predecessor is not None,
                f"dynamic honorific predecessor row is absent: {key}",
            )
            evidence = updated.get("runtime_vm_verification")
            require(
                isinstance(evidence, dict),
                f"dynamic honorific evidence is absent: {key}",
            )
            action = str(evidence.get("action"))
            changed_fields = {
                field
                for field in set(predecessor) | set(updated)
                if predecessor.get(field) != updated.get(field)
            }
            if action == "translation_override":
                require(
                    changed_fields
                    == {
                        "translation",
                        "runtime_vm_verification",
                        "honorific_spacing_evidence",
                        "runtime_boundary_leading_space_inserted",
                    }
                    and key
                    in ENGINE.RUNTIME_BOUNDARY_LEADING_SPACE_COORDINATES
                    and updated.get(
                        "runtime_boundary_leading_space_inserted"
                    )
                    is True,
                    f"dynamic honorific override transition drifted: {key}",
                )
            elif action == "verification_renewal":
                require(
                    changed_fields == {"runtime_vm_verification"},
                    f"dynamic honorific renewal transition drifted: {key}",
                )
            elif action == "runtime_promotion":
                require(
                    changed_fields == RUNTIME_MUTABLE_FIELDS
                    and predecessor.get("runtime_review") == "pending"
                    and updated.get("runtime_review") == "verified"
                    and updated.get("scope_classification")
                    == "retranslated"
                    and updated.get("layout_review")
                    == "runtime_verified",
                    f"dynamic honorific promotion transition drifted: {key}",
                )
                dynamic_honorific_promotions += 1
            else:
                raise IntegrationError(
                    f"dynamic honorific action is invalid: {key}"
                )
            merged[key] = dict(updated)
        require(
            dynamic_honorific_promotions
            == EXPECTED_DYNAMIC_HONORIFIC_SPACING_PROMOTIONS,
            (
                "dynamic honorific promotion count drifted: "
                f"{dynamic_honorific_promotions}"
            ),
        )
    post_dynamic_rows = sorted(merged.values(), key=coordinate_sort_key)
    post_dynamic_private_sha256 = sha256_bytes(
        canonical_jsonl(post_dynamic_rows).encode("utf-8")
    )
    bound_terminal_promotions = 0
    bound_terminal_metadata: dict[str, Any] | None = None
    if include_bound_terminal_family:
        require(
            post_dynamic_private_sha256
            == EXPECTED_POST_DYNAMIC_PRIVATE_SHA256,
            (
                "bound terminal predecessor checkpoint drifted: "
                f"{post_dynamic_private_sha256}"
            ),
        )
        terminal_layer = load_bound_terminal_family()
        terminal_updates, bound_terminal_metadata = (
            validated_bound_terminal_family_updates()
        )
        for key, updated in terminal_updates.items():
            predecessor = merged.get(key)
            require(
                predecessor is not None,
                f"bound terminal predecessor row is absent: {key}",
            )
            action = str(updated.get("terminal_family_update_action"))
            evidence = (
                updated.get("runtime_vm_verification")
                if updated.get("runtime_review") == "verified"
                else updated.get("terminal_family_runtime_evidence")
            )
            require(
                isinstance(evidence, dict)
                and evidence.get("action") == action
                and evidence.get("method") == terminal_layer.METHOD
                and evidence.get("predecessor_integrated_binding", {}).get(
                    "row_sha256"
                )
                == terminal_layer.canonical_sha256(predecessor),
                f"bound terminal predecessor evidence drifted: {key}",
            )
            changed_fields = {
                field
                for field in set(predecessor) | set(updated)
                if predecessor.get(field) != updated.get(field)
            }
            if action == "verification_renewal":
                require(
                    changed_fields
                    == {
                        "runtime_vm_verification",
                        "terminal_family_update_action",
                    }
                    and predecessor.get("runtime_review") == "verified",
                    f"bound terminal renewal transition drifted: {key}",
                )
            elif action == "translation_override":
                require(
                    changed_fields
                    == {
                        "translation",
                        "runtime_vm_verification",
                        "terminal_family_exact_override_evidence",
                        "terminal_family_update_action",
                    }
                    and predecessor.get("runtime_review") == "verified"
                    and key[1] in terminal_layer.TRANSLATION_OVERRIDES
                    and updated.get("translation")
                    == terminal_layer.TRANSLATION_OVERRIDES[key[1]],
                    f"bound terminal verified override drifted: {key}",
                )
            elif action == "runtime_promotion":
                require(
                    changed_fields
                    == RUNTIME_MUTABLE_FIELDS
                    | {"terminal_family_update_action"}
                    and predecessor.get("runtime_review") == "pending"
                    and updated.get("runtime_review") == "verified"
                    and updated.get("scope_classification")
                    == "retranslated"
                    and updated.get("layout_review")
                    == "runtime_verified",
                    f"bound terminal promotion transition drifted: {key}",
                )
                bound_terminal_promotions += 1
            elif action == "translation_override_and_runtime_promotion":
                required = RUNTIME_MUTABLE_FIELDS | {
                    "translation",
                    "terminal_family_exact_override_evidence",
                    "terminal_family_update_action",
                }
                require(
                    frozenset(changed_fields) in {
                        frozenset(required),
                        frozenset(required | {"runtime_assembly_evidence"}),
                    }
                    and predecessor.get("runtime_review") == "pending"
                    and updated.get("runtime_review") == "verified"
                    and updated.get("scope_classification")
                    == "retranslated"
                    and updated.get("layout_review")
                    == "runtime_verified"
                    and key[1] in terminal_layer.TRANSLATION_OVERRIDES
                    and updated.get("translation")
                    == terminal_layer.TRANSLATION_OVERRIDES[key[1]],
                    f"bound terminal override promotion drifted: {key}",
                )
                bound_terminal_promotions += 1
            elif action == "translation_override_pending":
                require(
                    changed_fields
                    == {
                        "translation",
                        "runtime_assembly_evidence",
                        "terminal_family_exact_override_evidence",
                        "terminal_family_runtime_evidence",
                        "terminal_family_update_action",
                    }
                    and predecessor.get("runtime_review")
                    == updated.get("runtime_review")
                    == "pending"
                    and key[1] in terminal_layer.TRANSLATION_OVERRIDES
                    and updated.get("translation")
                    == terminal_layer.TRANSLATION_OVERRIDES[key[1]],
                    f"bound terminal pending override drifted: {key}",
                )
            else:
                raise IntegrationError(
                    f"bound terminal action is invalid: {key}"
                )
            merged[key] = dict(updated)
        require(
            bound_terminal_promotions
            == EXPECTED_BOUND_TERMINAL_FAMILY_PROMOTIONS,
            (
                "bound terminal promotion count drifted: "
                f"{bound_terminal_promotions}"
            ),
        )
    post_bound_rows = sorted(merged.values(), key=coordinate_sort_key)
    post_bound_private_sha256 = sha256_bytes(
        canonical_jsonl(post_bound_rows).encode("utf-8")
    )
    thought_predicate_promotions = 0
    thought_predicate_metadata: dict[str, Any] | None = None
    if include_thought_predicate_family:
        require(
            post_bound_private_sha256 == EXPECTED_POST_BOUND_PRIVATE_SHA256,
            (
                "thought-predicate predecessor checkpoint drifted: "
                f"{post_bound_private_sha256}"
            ),
        )
        (
            thought_predicate_promotions,
            thought_predicate_metadata,
        ) = apply_thought_predicate_family_updates(
            merged,
        )
    post_thought_rows = sorted(merged.values(), key=coordinate_sort_key)
    post_thought_private_sha256 = sha256_bytes(
        canonical_jsonl(post_thought_rows).encode("utf-8")
    )
    bound_terminal_caller_promotions = 0
    bound_terminal_caller_metadata: dict[str, Any] | None = None
    if include_bound_terminal_caller:
        require(
            post_thought_private_sha256
            == EXPECTED_THOUGHT_PREDICATE_FINAL_PRIVATE_SHA256,
            (
                "bound-terminal caller predecessor checkpoint drifted: "
                f"{post_thought_private_sha256}"
            ),
        )
        (
            bound_terminal_caller_promotions,
            bound_terminal_caller_metadata,
        ) = apply_bound_terminal_caller_updates(merged)
    post_bound_terminal_caller_rows = sorted(
        merged.values(),
        key=coordinate_sort_key,
    )
    post_bound_terminal_caller_private_sha256 = sha256_bytes(
        canonical_jsonl(post_bound_terminal_caller_rows).encode("utf-8")
    )
    bound_terminal_2546_full_caller_promotions = 0
    bound_terminal_2546_full_caller_metadata: dict[str, Any] | None = None
    if include_bound_terminal_2546_full_caller:
        require(
            post_bound_terminal_caller_private_sha256
            == EXPECTED_BOUND_TERMINAL_CALLER_FINAL_PRIVATE_SHA256,
            (
                "bound-terminal 2546 full-caller predecessor checkpoint "
                f"drifted: {post_bound_terminal_caller_private_sha256}"
            ),
        )
        (
            bound_terminal_2546_full_caller_promotions,
            bound_terminal_2546_full_caller_metadata,
        ) = apply_bound_terminal_2546_full_caller_updates(merged)
    pk_integrated_promotions = (
        predecessor_promotions
        + pk_only_promotions
        + cross_resource_promotions
        + dynamic_honorific_promotions
        + bound_terminal_promotions
        + thought_predicate_promotions
        + bound_terminal_caller_promotions
        + bound_terminal_2546_full_caller_promotions
    )
    pk_metadata["rebuilt_predecessor_integrated_private_sha256"] = (
        predecessor_private_sha256
    )
    pk_metadata["pk_only_predecessor_checkpoint_match"] = (
        predecessor_checkpoint_match
    )
    if include_cross_resource:
        pk_metadata["rebuilt_post_pk_only_integrated_private_sha256"] = (
            post_pk_only_private_sha256
        )
        pk_metadata["cross_resource_predecessor_checkpoint_match"] = (
            post_pk_only_checkpoint_match
        )
    if include_dynamic_honorific_spacing:
        assert dynamic_honorific_metadata is not None
        pk_metadata["dynamic_honorific_spacing_layer_included"] = True
        pk_metadata["rebuilt_post_cross_integrated_private_sha256"] = (
            post_cross_private_sha256
        )
        pk_metadata["dynamic_honorific_spacing"] = (
            dynamic_honorific_metadata
        )
        pk_metadata["promotion_count"] = pk_integrated_promotions
    if include_bound_terminal_family:
        assert bound_terminal_metadata is not None
        pk_metadata["bound_terminal_family_layer_included"] = True
        pk_metadata["rebuilt_post_dynamic_integrated_private_sha256"] = (
            post_dynamic_private_sha256
        )
        pk_metadata["bound_terminal_family"] = bound_terminal_metadata
        pk_metadata["promotion_count"] = pk_integrated_promotions
    if include_thought_predicate_family:
        assert thought_predicate_metadata is not None
        pk_metadata["thought_predicate_family_layer_included"] = True
        pk_metadata["rebuilt_post_bound_integrated_private_sha256"] = (
            post_bound_private_sha256
        )
        pk_metadata["thought_predicate_family"] = (
            thought_predicate_metadata
        )
        pk_metadata["promotion_count"] = pk_integrated_promotions
    if include_bound_terminal_caller:
        assert bound_terminal_caller_metadata is not None
        pk_metadata["bound_terminal_caller_layer_included"] = True
        pk_metadata["rebuilt_post_thought_integrated_private_sha256"] = (
            post_thought_private_sha256
        )
        pk_metadata["bound_terminal_caller"] = (
            bound_terminal_caller_metadata
        )
        pk_metadata["promotion_count"] = pk_integrated_promotions
    if include_bound_terminal_2546_full_caller:
        assert bound_terminal_2546_full_caller_metadata is not None
        pk_metadata[
            "bound_terminal_2546_full_caller_layer_included"
        ] = True
        pk_metadata[
            "rebuilt_post_bound_terminal_caller_integrated_private_sha256"
        ] = post_bound_terminal_caller_private_sha256
        pk_metadata["bound_terminal_2546_full_caller"] = (
            bound_terminal_2546_full_caller_metadata
        )
        pk_metadata["promotion_count"] = pk_integrated_promotions

    expected_pk_promotions = (
        EXPECTED_PK_BOUND_TERMINAL_2546_FULL_CALLER_FINAL_PROMOTIONS
        if include_bound_terminal_2546_full_caller
        else EXPECTED_PK_BOUND_TERMINAL_CALLER_FINAL_PROMOTIONS
        if include_bound_terminal_caller
        else EXPECTED_PK_THOUGHT_PREDICATE_FINAL_PROMOTIONS
        if include_thought_predicate_family
        else EXPECTED_PK_BOUND_TERMINAL_FINAL_PROMOTIONS
        if include_bound_terminal_family
        else EXPECTED_PK_FINAL_PROMOTIONS
        if include_dynamic_honorific_spacing
        else EXPECTED_PK_INTEGRATED_PROMOTIONS
        if include_cross_resource
        else EXPECTED_PK_POST_PK_ONLY_PROMOTIONS
        if include_pk_only
        else EXPECTED_PK_PREDECESSOR_PROMOTIONS
    )
    require(
        pk_integrated_promotions == expected_pk_promotions,
        f"PK integrated promotion count drifted: {pk_integrated_promotions}",
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
    expected_pending_after = (
        EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_FINAL_PENDING_AFTER
        if include_bound_terminal_2546_full_caller
        else EXPECTED_BOUND_TERMINAL_CALLER_FINAL_PENDING_AFTER
        if include_bound_terminal_caller
        else EXPECTED_THOUGHT_PREDICATE_FINAL_PENDING_AFTER
        if include_thought_predicate_family
        else EXPECTED_BOUND_TERMINAL_FINAL_PENDING_AFTER
        if include_bound_terminal_family
        else EXPECTED_FINAL_PENDING_AFTER
        if include_dynamic_honorific_spacing
        else EXPECTED_PENDING_AFTER
        if include_cross_resource
        else EXPECTED_POST_PK_ONLY_PENDING_AFTER
        if include_pk_only
        else EXPECTED_PREDECESSOR_PENDING_AFTER
    )
    require(
        pending_after == expected_pending_after,
        f"integrated pending count drifted: {pending_after}",
    )
    private_content = canonical_jsonl(rows)
    validate_combined_private(prepared, private_content, private_output)
    private_sha256 = sha256_bytes(private_content.encode("utf-8"))
    if include_bound_terminal_2546_full_caller:
        require(
            private_sha256
            == EXPECTED_BOUND_TERMINAL_2546_FULL_CALLER_FINAL_PRIVATE_SHA256,
            (
                "bound-terminal 2546 full-caller final private digest "
                f"drifted: {private_sha256}"
            ),
        )
    elif include_bound_terminal_caller:
        require(
            private_sha256
            == EXPECTED_BOUND_TERMINAL_CALLER_FINAL_PRIVATE_SHA256,
            f"bound-terminal caller final private digest drifted: {private_sha256}",
        )
    elif include_thought_predicate_family:
        require(
            private_sha256
            == EXPECTED_THOUGHT_PREDICATE_FINAL_PRIVATE_SHA256,
            f"thought-predicate final private digest drifted: {private_sha256}",
        )
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
            "semantic_override": semantic_metadata,
            "relative_reflow_override": reflow_metadata,
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
            "pk_full_candidate_records_and_closures_rechecked": True,
            "control_repair_bindings_rechecked": True,
            "semantic_override_rebuilt_and_rechecked": True,
            "relative_reflow_override_rebuilt_and_rechecked": True,
            "pk_only_layer_included": include_pk_only,
            "pk_only_predecessor_checkpoint_rebuilt_and_matched":
            predecessor_checkpoint_match,
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
    if include_cross_resource:
        report["validation"].update(
            {
                "cross_resource_layer_included": True,
                (
                    "cross_resource_predecessor_checkpoint_"
                    "rebuilt_and_matched"
                ): post_pk_only_checkpoint_match,
            }
        )
    if include_dynamic_honorific_spacing:
        report["validation"].update(
            {
                "dynamic_honorific_spacing_layer_included": True,
                "post_cross_predecessor_checkpoint_rebuilt_and_matched":
                post_cross_private_sha256
                == EXPECTED_POST_CROSS_PRIVATE_SHA256,
                "affected_verified_runtime_evidence_renewed": True,
                "raw_g1n_full_closure_width_guard_rechecked": True,
            }
        )
    if include_bound_terminal_family:
        report["validation"].update(
            {
                "bound_terminal_family_layer_included": True,
                "post_dynamic_predecessor_checkpoint_rebuilt_and_matched":
                post_dynamic_private_sha256
                == EXPECTED_POST_DYNAMIC_PRIVATE_SHA256,
                "bound_terminal_semantic_overrides_rechecked": True,
                "affected_verified_pk_runtime_evidence_renewed": True,
                "actual_four_pending_promotions_rechecked": True,
                "uncertain_pending_roots_remain_rejected": True,
            }
        )
    if include_thought_predicate_family:
        report["validation"].update(
            {
                "thought_predicate_family_layer_included": True,
                "post_bound_predecessor_checkpoint_rebuilt_and_matched":
                post_bound_private_sha256
                == EXPECTED_POST_BOUND_PRIVATE_SHA256,
                "thought_predicate_semantic_overrides_rechecked": True,
                "affected_verified_pk_runtime_evidence_renewed": True,
                "actual_twenty_three_pending_promotions_rechecked": True,
                "all_483_assemblies_grammar_complete": True,
            }
        )
    if include_bound_terminal_caller:
        report["validation"].update(
            {
                "bound_terminal_caller_layer_included": True,
                "post_thought_predecessor_checkpoint_rebuilt_and_matched":
                post_thought_private_sha256
                == EXPECTED_THOUGHT_PREDICATE_FINAL_PRIVATE_SHA256,
                "caller_semantic_overrides_rechecked": True,
                "affected_verified_pk_runtime_evidence_renewed": True,
                "actual_forty_one_pending_promotions_rechecked": True,
                "combined_overlap_thought_translation_preserved": True,
                "combined_candidate_record_and_root_rebound": True,
            }
        )
    if include_bound_terminal_2546_full_caller:
        report["validation"].update(
            {
                "bound_terminal_2546_full_caller_layer_included": True,
                (
                    "post_bound_terminal_caller_predecessor_checkpoint_"
                    "rebuilt_and_matched"
                ): post_bound_terminal_caller_private_sha256
                == EXPECTED_BOUND_TERMINAL_CALLER_FINAL_PRIVATE_SHA256,
                "selector_1066_terminal_2546_full_closure_rechecked": True,
                "exact_216_translation_overrides_rechecked": True,
                "affected_292_verified_pk_runtime_evidence_renewed": True,
                "actual_364_pending_promotions_rechecked": True,
                "uncertain_74_pending_rows_remain_rejected": True,
                "caller_overlap_actions_preserved_and_superseded": True,
                "combined_candidate_record_and_root_rebound": True,
            }
        )
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
        include_dynamic_honorific_spacing=True,
        include_bound_terminal_family=True,
        include_thought_predicate_family=True,
        include_bound_terminal_caller=True,
        include_bound_terminal_2546_full_caller=True,
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
