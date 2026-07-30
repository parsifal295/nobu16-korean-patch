#!/usr/bin/env python3
"""Promote the conservative PK-only subset of full-candidate exact blockers.

The full-candidate audit blocks exact-reuse rows when a Base/PK pair proof is
not transferable.  This builder deliberately does not inherit that Base
runtime proof.  It independently proves that the PK source, current Korean,
and final candidate have identical exact control closures, that the final
literal line envelope does not expand beyond current Korean, and that no hard
grammar/layout risk evidence exists anywhere in the source closure.

Tracked outputs contain coordinates, counts, predicates, and hashes only.  The
private verification overlay also contains no dialogue text and remains below
``tmp/``.  Steam is read only and is never a write target.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
DECISIONS_DIR = DIALOGUE_TMP / "decisions"
OVERLAY_DIR = DECISIONS_DIR / "runtime_verification_overlays"
FULL_AUDIT_PATH = (
    WORKSTREAM / "build_pk_msggame_full_candidate_runtime_vm_audit_v1.py"
)
EXACT_COVERAGE_PATH = (
    WORKSTREAM / "public" / "pk_msggame_runtime_vm_coverage.v1.json"
)
FULL_COVERAGE_PATH = (
    WORKSTREAM
    / "public"
    / "pk_msggame_full_candidate_runtime_vm_coverage.v1.json"
)
INTEGRATED_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.pre_pk_only_checkpoint.private.v1.jsonl"
)
INTEGRATED_REPORT_PATH = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration.pre_pk_only_checkpoint.source_free.v1.json"
)
INTEGRATED_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM / "build_runtime_vm_pre_pk_only_checkpoint_v2.py"
)
SEMANTIC_OVERRIDE_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM / "pk_semantic_flattening_3421.source_free.v1.json"
)
DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_msggame_exact_blocked_pk_only_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_msggame_exact_blocked_pk_only_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    OVERLAY_DIR
    / "pk_msggame_exact_blocked_pk_only_closure_verified.private.v1.jsonl"
)
LIVE_STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

AUDIT_SCHEMA = (
    "nobu16.kr.pk-msggame-exact-blocked-pk-only-closure-coverage.v1"
)
PROMOTION_SCHEMA = (
    "nobu16.kr.pk-msggame-exact-blocked-pk-only-closure-promotion.v1"
)
OVERLAY_ROW_SCHEMA = (
    "nobu16.kr.pk-msggame-exact-blocked-pk-only-closure-overlay-row.v1"
)
METHOD = "reversed_vm_pk_only_exact_blocked_closure_nonexpansion_analysis"

EXPECTED_BLOCKED_ROWS = 2_320
EXPECTED_BLOCKED_RECORDS = 1_618
EXPECTED_SAFE_ROWS = 1_536
EXPECTED_SAFE_RECORDS = 1_128
EXPECTED_REMAINING_ROWS = 784
EXPECTED_REMAINING_RECORDS = 490
EXPECTED_BLOCKED_COORDINATE_SHA256 = (
    "31795756CA5D3C68E05C4CC1BEE726D9E4869D1EB3FAF512F115F72613AAAFD8"
)
EXPECTED_BLOCKED_RECORD_SHA256 = (
    "023105EA5F2F54DD309601A628189808BB31C20D54744A5438FB6107A8C6815D"
)
EXPECTED_SAFE_COORDINATE_SHA256 = (
    "37D72476B42334E9B938657D4B4DB0D8194054CE7D9FC77C76A283EF1C14753B"
)
EXPECTED_SAFE_RECORD_SHA256 = (
    "464186C1EC6B93CBE3A62003848E389ABE18B61F2B8906AD885486FA5BD9FB7F"
)
EXPECTED_REMAINING_COORDINATE_SHA256 = (
    "5D10C7ACECD8FBD4E846F4F85FA05BA4270BC7E3C9AD36CE1BE5E8C0BBB0B178"
)
EXPECTED_REMAINING_RECORD_SHA256 = (
    "034AD2D4893D5424BF9D6FD3790DEE30666AF4B1350F37210F924AFA1298C400"
)
EXPECTED_SOURCE_FINAL_CONTROL_TAINT_ROWS = 13
EXPECTED_SOURCE_FINAL_CONTROL_TAINT_RECORDS = 7
EXPECTED_SOURCE_FINAL_CONTROL_TAINT_COORDINATE_SHA256 = (
    "3811287253C5634BA0A9B3A6FDE6FEF97429F0727271F7EFB1A5C0F87494AC1A"
)
EXPECTED_FULL_COVERAGE_FILE_SHA256 = (
    "DB596688BF87AE07F04E80FE83CB194541A74B1DACE56423A2A39DDF715089A0"
)
EXPECTED_FULL_COVERAGE_PAYLOAD_SHA256 = (
    "9A524E15B20B3B96E764BD09607F14C663B5F9A61B65A42FB3A6FE2A8C6B5E73"
)
EXPECTED_EXACT_COVERAGE_FILE_SHA256 = (
    "97B96240F7EEE1A20567398623C477B02AF27C851E2B2F86C4A12FF4FEBDC2BC"
)
EXPECTED_EXACT_COVERAGE_PAYLOAD_SHA256 = (
    "91924E0909594F477A56CD9C48AE8B200C730E6CE28E1395DAF6EBD961065FD6"
)
EXPECTED_INTEGRATED_PRIVATE_SHA256 = (
    "29ECB2446AD89D0F9F122B280D2E66DAB2A36F2F0050174239EB4D1F0D27E757"
)
EXPECTED_INTEGRATED_REPORT_FILE_SHA256 = (
    "126D47703C38F58B28B887150AEAEDF1366303257AAC119BE798665174769D0B"
)
EXPECTED_INTEGRATED_BUILDER_SHA256 = (
    "2AC133BA38B7FB79B0274D7DA023A803FF4B32DC93441B59EA14E0E86AA5B656"
)
EXPECTED_INTEGRATED_RUNTIME_PENDING = 10_288
EXPECTED_INTEGRATED_PK_PROMOTIONS = 10_395
EXPECTED_SEMANTIC_OVERRIDE_PUBLIC_SHA256 = (
    "7D2DECA73B1D37AD741BC0D101028FE3E2CC0383526973B15325AD5F0E77E9F1"
)

HARD_TRUE_GRAMMAR_RISK_FIELDS = frozenset(
    {
        "caller_rewrite_required",
        "caller_rewrite_required_before_runtime_approval",
        "future_caller_rewrite_required_before_runtime_approval",
        "pk_specific_morphology_divergence",
        "runtime_morphology_conflict_detected",
    }
)
HARD_FALSE_GRAMMAR_RISK_FIELDS = frozenset(
    {"all_speaker_branches_grammatical"}
)


class PkOnlyClosureError(ValueError):
    """Raised when the independent PK-only proof or a binding drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PkOnlyClosureError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FULL_AUDIT = load_module("pk_exact_blocked_pk_only_full_audit", FULL_AUDIT_PATH)
BASE_AUDIT = FULL_AUDIT.BASE_AUDIT
ENGINE = FULL_AUDIT.ENGINE


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return FULL_AUDIT.canonical_sha256(value)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def canonical_jsonl(rows: Sequence[Mapping[str, Any]]) -> str:
    return "".join(
        json.dumps(
            row,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for row in rows
    )


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"required JSON is absent: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    require(path.is_file(), f"required JSONL is absent: {path}")
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


def live_steam_hash() -> str | None:
    return (
        sha256_bytes(LIVE_STEAM_PK.read_bytes())
        if LIVE_STEAM_PK.is_file()
        else None
    )


def coordinate_digest(coordinates: Iterable[str]) -> str:
    return FULL_AUDIT.coordinate_digest(list(coordinates))


def record_digest(records: Iterable[tuple[int, int]]) -> str:
    return canonical_sha256([list(record) for record in sorted(set(records))])


def record_key(record: tuple[int, int]) -> str:
    return f"{record[0]}:{record[1]}"


def parse_record_key(value: str) -> tuple[int, int]:
    parts = value.split(":")
    require(
        len(parts) == 2 and all(part.isdigit() for part in parts),
        f"invalid record key: {value}",
    )
    return int(parts[0]), int(parts[1])


def seal_report(report: Mapping[str, Any]) -> dict[str, Any]:
    sealed = copy.deepcopy(dict(report))
    guards = sealed.setdefault("guards", {})
    require(isinstance(guards, dict), "report guards are not an object")
    guards.pop("report_payload_sha256", None)
    guards["report_payload_sha256"] = canonical_sha256(sealed)
    return sealed


def validate_seal(report: Mapping[str, Any]) -> None:
    unsealed = copy.deepcopy(dict(report))
    guards = unsealed.get("guards")
    require(isinstance(guards, dict), "sealed report guards are absent")
    expected = guards.pop("report_payload_sha256", None)
    require(expected == canonical_sha256(unsealed), "report payload seal drifted")


def source_decision_rows(
    *,
    full_metadata: Mapping[str, Any],
) -> tuple[
    list[dict[str, Any]],
    dict[str, Any],
]:
    paths = sorted(DECISIONS_DIR.glob("pk_msggame*.private.v1.jsonl"))
    require(
        len(paths) == FULL_AUDIT.EXPECTED_SOURCE_SEGMENTS,
        f"PK source segment count drifted: {len(paths)}",
    )
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    segment_guards: list[dict[str, Any]] = []
    for path in paths:
        values = read_jsonl(path)
        for row in values:
            coordinate = str(row.get("coordinate"))
            require(
                row.get("resource") == "pk_msggame" and coordinate not in seen,
                f"invalid or duplicate PK source decision: {coordinate}",
            )
            seen.add(coordinate)
            rows.append(row)
        segment_guards.append(
            {
                "name": path.name,
                "row_count": len(values),
                "sha256": sha256_bytes(path.read_bytes()),
            }
        )
    require(
        len(rows) == len(seen) == FULL_AUDIT.EXPECTED_PK_ROWS,
        f"PK source decision universe drifted: {len(rows)}",
    )
    rows.sort(
        key=lambda row: BASE_AUDIT.parse_literal_coordinate(row["coordinate"])
    )
    (
        semantic_private_content,
        semantic_public_content,
        semantic_report,
        semantic_row,
    ) = FULL_AUDIT.SEMANTIC_OVERRIDE.build_outputs()
    FULL_AUDIT.SEMANTIC_OVERRIDE.validate_outputs(
        semantic_private_content,
        semantic_public_content,
        semantic_report,
        semantic_row,
    )
    semantic_coordinate = str(semantic_row["coordinate"])
    semantic_matches = [
        index
        for index, row in enumerate(rows)
        if str(row["coordinate"]) == semantic_coordinate
    ]
    require(
        len(semantic_matches) == 1,
        "semantic override coordinate is absent or duplicated",
    )
    rows[semantic_matches[0]] = semantic_row
    reflow_overrides, reflow_metadata = (
        FULL_AUDIT.REFLOW_OVERRIDE.load_overrides(rows)
    )
    consumed: set[str] = set()
    for index, row in enumerate(rows):
        coordinate = str(row["coordinate"])
        override = reflow_overrides.get(coordinate)
        if override is None:
            continue
        rows[index] = override
        consumed.add(coordinate)
    require(
        consumed == set(reflow_overrides),
        "relative reflow override universe was not fully applied",
    )
    replacement_manifest = [
        {
            "coordinate": str(row["coordinate"]),
            "translation_utf16le_sha256": ENGINE.sha256_text(
                str(row["translation"])
            ),
        }
        for row in rows
        if isinstance(row.get("translation"), str)
    ]
    require(
        canonical_sha256(replacement_manifest)
        == full_metadata["replacement_manifest_sha256"],
        "effective PK-only source replacement manifest drifted",
    )
    return rows, {
        "source_decision_segment_count": len(paths),
        "source_decision_segment_universe_sha256": canonical_sha256(
            segment_guards
        ),
        "source_decision_coordinate_universe_sha256": coordinate_digest(seen),
        "semantic_override_rows": 1,
        "relative_reflow_override_rows": len(reflow_overrides),
        "relative_reflow_private_sha256": reflow_metadata[
            "private_file_sha256"
        ],
        "relative_reflow_public_sha256": reflow_metadata[
            "public_file_sha256"
        ],
        "relative_reflow_manifest_sha256": reflow_metadata[
            "override_manifest_sha256"
        ],
    }


def nested_hard_risks(value: Any) -> set[str]:
    risks: set[str] = set()
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, Mapping):
            for key, child in item.items():
                if key in HARD_TRUE_GRAMMAR_RISK_FIELDS and child is True:
                    risks.add(str(key))
                elif key in HARD_FALSE_GRAMMAR_RISK_FIELDS and child is False:
                    risks.add(str(key))
                elif key == "line_count_preserved" and child is False:
                    risks.add("line_count_not_preserved")
                if isinstance(child, (Mapping, list)):
                    stack.append(child)
        elif isinstance(item, list):
            stack.extend(item)
    return risks


def component_signatures(record: Any) -> list[dict[str, Any]]:
    return [
        FULL_AUDIT.pk_component_signature(component)
        for component in BASE_AUDIT.decode_record(record)
    ]


def literal_line_counts(record: Any) -> list[int]:
    return [
        literal.text.count("\n") + 1
        for literal in BASE_AUDIT.parse_record_literals(record)
    ]


def closure_guard(
    root: tuple[int, int],
    *,
    inputs: Any,
    decisions_by_record: Mapping[
        tuple[int, int],
        Sequence[Mapping[str, Any]],
    ],
) -> dict[str, Any]:
    queue: deque[tuple[int, int]] = deque([root])
    seen: set[tuple[int, int]] = set()
    proof_records: list[dict[str, Any]] = []
    proof_edges: list[dict[str, Any]] = []
    failure_codes: set[str] = set()
    grammar_risk_keys: set[str] = set()
    line_expansion_count = 0
    call_count = 0
    jump_count = 0
    while queue:
        coordinate = queue.popleft()
        if coordinate in seen:
            continue
        seen.add(coordinate)
        source = inputs.pk_source_records.get(coordinate)
        current = inputs.pk_current_records.get(coordinate)
        final = inputs.pk_candidate_records.get(coordinate)
        if source is None or current is None or final is None:
            failure_codes.add("closure_record_missing")
            continue
        try:
            source_components = BASE_AUDIT.decode_record(source)
            source_signatures = [
                FULL_AUDIT.pk_component_signature(component)
                for component in source_components
            ]
            current_signatures = component_signatures(current)
            final_signatures = component_signatures(final)
            current_lines = literal_line_counts(current)
            final_lines = literal_line_counts(final)
        except BASE_AUDIT.AuditError:
            failure_codes.add("closure_decode_failure")
            continue
        if source_signatures != current_signatures:
            failure_codes.add("source_current_control_mismatch")
        if source_signatures != final_signatures:
            failure_codes.add("source_final_control_mismatch")
        if current_signatures != final_signatures:
            failure_codes.add("current_final_control_mismatch")
        if len(current_lines) != len(final_lines):
            failure_codes.add("literal_count_mismatch")
        expanded_slots = [
            literal_id
            for literal_id, (before, after) in enumerate(
                zip(current_lines, final_lines)
            )
            if after > before
        ]
        if expanded_slots:
            failure_codes.add("layout_or_line_envelope_risk")
            line_expansion_count += len(expanded_slots)
        record_risks: set[str] = set()
        decision_hashes: list[str] = []
        for decision in decisions_by_record.get(coordinate, ()):
            record_risks.update(nested_hard_risks(decision))
            decision_hashes.append(canonical_sha256(decision))
        if "line_count_not_preserved" in record_risks:
            failure_codes.add("layout_or_line_envelope_risk")
            record_risks.remove("line_count_not_preserved")
        if record_risks:
            failure_codes.add("grammar_risk")
            grammar_risk_keys.update(record_risks)
        proof_records.append(
            {
                "coordinate": list(coordinate),
                "source_record_sha256": sha256_bytes(source.data),
                "current_record_sha256": sha256_bytes(current.data),
                "final_record_sha256": sha256_bytes(final.data),
                "source_component_sha256": canonical_sha256(
                    source_signatures
                ),
                "current_component_sha256": canonical_sha256(
                    current_signatures
                ),
                "final_component_sha256": canonical_sha256(
                    final_signatures
                ),
                "current_line_counts": current_lines,
                "final_line_counts": final_lines,
                "expanded_literal_slots": expanded_slots,
                "grammar_risk_keys": sorted(record_risks),
                "decision_evidence_sha256": canonical_sha256(
                    sorted(decision_hashes)
                ),
            }
        )
        for occurrence, component in enumerate(source_components):
            if component["kind"] not in {"call", "jump"}:
                continue
            target = tuple(component["target"])
            proof_edges.append(
                {
                    "source": list(coordinate),
                    "occurrence": occurrence,
                    "kind": component["kind"],
                    "operand": component["operand"],
                    "target": list(target),
                }
            )
            if component["kind"] == "call":
                call_count += 1
            else:
                jump_count += 1
            queue.append(target)
    proof = {
        "root": list(root),
        "records": sorted(
            proof_records,
            key=lambda item: item["coordinate"],
        ),
        "edges": sorted(
            proof_edges,
            key=lambda item: (
                item["source"],
                item["occurrence"],
                item["kind"],
            ),
        ),
        "failure_codes": sorted(failure_codes),
        "grammar_risk_keys": sorted(grammar_risk_keys),
    }
    return {
        "proof_sha256": canonical_sha256(proof),
        "visited_record_count": len(seen),
        "0143_occurrences": call_count,
        "014a_occurrences": jump_count,
        "source_current_control_equal": (
            "source_current_control_mismatch" not in failure_codes
            and "closure_record_missing" not in failure_codes
            and "closure_decode_failure" not in failure_codes
        ),
        "source_final_control_equal": (
            "source_final_control_mismatch" not in failure_codes
            and "closure_record_missing" not in failure_codes
            and "closure_decode_failure" not in failure_codes
        ),
        "current_final_control_equal": (
            "current_final_control_mismatch" not in failure_codes
            and "closure_record_missing" not in failure_codes
            and "closure_decode_failure" not in failure_codes
        ),
        "final_line_envelope_not_above_current": (
            "layout_or_line_envelope_risk" not in failure_codes
            and "literal_count_mismatch" not in failure_codes
        ),
        "hard_grammar_risk_absent": "grammar_risk" not in failure_codes,
        "line_expansion_count": line_expansion_count,
        "grammar_risk_keys": sorted(grammar_risk_keys),
        "failure_codes": sorted(failure_codes),
    }


def load_integrated_ledger() -> tuple[
    dict[str, dict[str, Any]],
    dict[str, Any],
]:
    integrated_sha256 = sha256_bytes(INTEGRATED_PRIVATE_PATH.read_bytes())
    report_file_sha256 = sha256_bytes(INTEGRATED_REPORT_PATH.read_bytes())
    builder_sha256 = sha256_bytes(INTEGRATED_BUILDER_PATH.read_bytes())
    require(
        integrated_sha256 == EXPECTED_INTEGRATED_PRIVATE_SHA256,
        f"predecessor integrated private ledger drifted: {integrated_sha256}",
    )
    require(
        report_file_sha256 == EXPECTED_INTEGRATED_REPORT_FILE_SHA256,
        "predecessor integrated source-free report drifted: "
        f"{report_file_sha256}",
    )
    require(
        builder_sha256 == EXPECTED_INTEGRATED_BUILDER_SHA256,
        f"predecessor integrated builder drifted: {builder_sha256}",
    )
    report = read_json(INTEGRATED_REPORT_PATH)
    require(
        report.get("schema")
        == "nobu16.kr.pc-dialogue-runtime-vm-integration.v1"
        and report.get("status") == "PASS"
        and report.get("result", {}).get(
            "private_integrated_decision_sha256"
        )
        == integrated_sha256
        and report.get("steam_write_performed") is False,
        "predecessor integrated ledger report binding failed",
    )
    require(
        report.get("result", {}).get("runtime_review_pending")
        == EXPECTED_INTEGRATED_RUNTIME_PENDING
        and report.get("promotions", {}).get("pk_msggame", {}).get(
            "promotion_count"
        )
        == EXPECTED_INTEGRATED_PK_PROMOTIONS
        and report.get("promotions", {}).get("pk_msggame", {}).get(
            "pk_only_layer_included"
        )
        is False
        and report.get("validation", {}).get("pk_only_layer_included")
        is False
        and report.get("validation", {}).get(
            "pk_only_predecessor_checkpoint_rebuilt_and_matched"
        )
        is False,
        "predecessor integrated checkpoint boundary drifted",
    )
    pk_rows: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(INTEGRATED_PRIVATE_PATH):
        if row.get("resource") != "pk_msggame":
            continue
        coordinate = str(row.get("coordinate"))
        require(
            coordinate not in pk_rows,
            f"duplicate integrated PK coordinate: {coordinate}",
        )
        pk_rows[coordinate] = row
    require(
        len(pk_rows) == FULL_AUDIT.EXPECTED_PK_ROWS,
        f"integrated PK row universe drifted: {len(pk_rows)}",
    )
    return pk_rows, {
        "integrated_private_sha256": integrated_sha256,
        "integrated_report_file_sha256": report_file_sha256,
        "integrated_report_payload_sha256": canonical_sha256(report),
        "integrated_builder_sha256": builder_sha256,
        "integrated_runtime_pending": report["result"][
            "runtime_review_pending"
        ],
        "integrated_pk_promotions": report["promotions"]["pk_msggame"][
            "promotion_count"
        ],
    }


def input_context() -> dict[str, Any]:
    full_content, full_report, inputs, full_metadata = (
        FULL_AUDIT.build_outputs()
    )
    require(
        FULL_COVERAGE_PATH.is_file()
        and FULL_COVERAGE_PATH.read_text(encoding="utf-8") == full_content,
        "tracked full-candidate coverage report drifted",
    )
    full_file_sha256 = sha256_bytes(full_content.encode("utf-8"))
    require(
        full_file_sha256 == EXPECTED_FULL_COVERAGE_FILE_SHA256
        and full_report["guards"]["report_payload_sha256"]
        == EXPECTED_FULL_COVERAGE_PAYLOAD_SHA256,
        "full-candidate coverage binding drifted",
    )
    exact_report = read_json(EXACT_COVERAGE_PATH)
    exact_file_sha256 = sha256_bytes(EXACT_COVERAGE_PATH.read_bytes())
    require(
        exact_file_sha256 == EXPECTED_EXACT_COVERAGE_FILE_SHA256
        and exact_report.get("guards", {}).get("report_payload_sha256")
        == EXPECTED_EXACT_COVERAGE_PAYLOAD_SHA256,
        "exact coverage binding drifted",
    )
    source_rows, source_metadata = source_decision_rows(
        full_metadata=full_metadata
    )
    require(
        source_metadata["source_decision_segment_universe_sha256"]
        == full_report["guards"][
            "source_decision_segment_universe_sha256"
        ]
        == full_metadata["source_decision_segment_universe_sha256"],
        "source decision segment universe drifted",
    )
    semantic_public_sha256 = sha256_bytes(
        SEMANTIC_OVERRIDE_PUBLIC_PATH.read_bytes()
    )
    require(
        semantic_public_sha256 == EXPECTED_SEMANTIC_OVERRIDE_PUBLIC_SHA256
        == full_report["guards"]["semantic_override_public_sha256"],
        "semantic override public binding drifted",
    )
    integrated_rows, integrated_metadata = load_integrated_ledger()
    source_by_coordinate = {
        str(row["coordinate"]): row
        for row in source_rows
    }
    decisions_by_record: defaultdict[
        tuple[int, int],
        list[dict[str, Any]],
    ] = defaultdict(list)
    for row in source_rows:
        coordinate = BASE_AUDIT.parse_literal_coordinate(row["coordinate"])
        decisions_by_record[coordinate[:2]].append(row)
    return {
        "full_content": full_content,
        "full_report": full_report,
        "inputs": inputs,
        "full_metadata": full_metadata,
        "exact_report": exact_report,
        "source_rows": source_rows,
        "source_by_coordinate": source_by_coordinate,
        "source_metadata": source_metadata,
        "decisions_by_record": decisions_by_record,
        "integrated_rows": integrated_rows,
        "integrated_metadata": integrated_metadata,
        "input_hashes": {
            "exact_coverage_file_sha256": exact_file_sha256,
            "exact_coverage_payload_sha256": exact_report["guards"][
                "report_payload_sha256"
            ],
            "full_coverage_file_sha256": full_file_sha256,
            "full_coverage_payload_sha256": full_report["guards"][
                "report_payload_sha256"
            ],
            "full_candidate_packed_sha256": full_report[
                "candidate_scope"
            ]["literal_candidate_packed_sha256"],
            "source_decision_segment_universe_sha256": source_metadata[
                "source_decision_segment_universe_sha256"
            ],
            "semantic_override_private_sha256": full_report["guards"][
                "semantic_override_private_sha256"
            ],
            "semantic_override_public_sha256": semantic_public_sha256,
            "semantic_override_report_payload_sha256": full_report[
                "guards"
            ]["semantic_override_report_payload_sha256"],
            "relative_reflow_private_sha256": source_metadata[
                "relative_reflow_private_sha256"
            ],
            "relative_reflow_public_sha256": source_metadata[
                "relative_reflow_public_sha256"
            ],
            "relative_reflow_manifest_sha256": source_metadata[
                "relative_reflow_manifest_sha256"
            ],
            **integrated_metadata,
        },
    }


def original_blocker_summary(
    blocked: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    taint_rows = Counter(
        taint
        for adjudication in blocked.values()
        for taint in adjudication["taints"]
    )
    reason_rows = Counter(
        reason
        for adjudication in blocked.values()
        for reason in adjudication["reason_codes"]
    )
    records = {
        BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        for coordinate in blocked
    }
    taint_records = {
        taint: sum(
            any(
                taint in adjudication["taints"]
                for coordinate, adjudication in blocked.items()
                if BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
                == record
            )
            for record in records
        )
        for taint in sorted(taint_rows)
    }
    reason_records = {
        reason: sum(
            any(
                reason in adjudication["reason_codes"]
                for coordinate, adjudication in blocked.items()
                if BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
                == record
            )
            for record in records
        )
        for reason in sorted(reason_rows)
    }
    row_combinations = Counter(
        "+".join(adjudication["taints"])
        for adjudication in blocked.values()
    )
    record_combinations: Counter[str] = Counter()
    for record in records:
        combined: set[str] = set()
        for coordinate, adjudication in blocked.items():
            if BASE_AUDIT.parse_literal_coordinate(coordinate)[:2] == record:
                combined.update(adjudication["taints"])
        record_combinations.update(["+".join(sorted(combined))])
    return {
        "taint_row_counts": dict(sorted(taint_rows.items())),
        "taint_record_counts": dict(sorted(taint_records.items())),
        "reason_row_counts": dict(sorted(reason_rows.items())),
        "reason_record_counts": dict(sorted(reason_records.items())),
        "taint_combination_row_counts": dict(
            sorted(row_combinations.items())
        ),
        "taint_combination_record_counts": dict(
            sorted(record_combinations.items())
        ),
    }


def candidate_translation_hash(
    coordinate: str,
    *,
    inputs: Any,
) -> str:
    block_id, record_id, literal_id = (
        BASE_AUDIT.parse_literal_coordinate(coordinate)
    )
    literals = BASE_AUDIT.parse_record_literals(
        inputs.pk_candidate_records[(block_id, record_id)]
    )
    require(
        literal_id < len(literals),
        f"candidate literal is absent: {coordinate}",
    )
    return sha256_bytes(literals[literal_id].text.encode("utf-16-le"))


def build_audit(context: Mapping[str, Any]) -> dict[str, Any]:
    full_report = context["full_report"]
    inputs = context["inputs"]
    blocked = {
        coordinate: adjudication
        for coordinate, adjudication in full_report[
            "row_adjudications"
        ].items()
        if adjudication["status"] == "blocked"
    }
    require(
        len(blocked) == EXPECTED_BLOCKED_ROWS
        and coordinate_digest(blocked) == EXPECTED_BLOCKED_COORDINATE_SHA256,
        "full-candidate blocked coordinate universe drifted",
    )
    roots = sorted(
        {
            BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
            for coordinate in blocked
        }
    )
    require(
        len(roots) == EXPECTED_BLOCKED_RECORDS
        and record_digest(roots) == EXPECTED_BLOCKED_RECORD_SHA256,
        "full-candidate blocked record universe drifted",
    )
    closure_guards = {
        record_key(root): closure_guard(
            root,
            inputs=inputs,
            decisions_by_record=context["decisions_by_record"],
        )
        for root in roots
    }
    row_adjudications: dict[str, dict[str, Any]] = {}
    for coordinate in sorted(
        blocked,
        key=BASE_AUDIT.parse_literal_coordinate,
    ):
        root = BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        closure = closure_guards[record_key(root)]
        failure_codes = set(closure["failure_codes"])
        if blocked[coordinate]["layout_change_pending"]:
            failure_codes.add("layout_or_line_envelope_risk")
        predicates = {
            "source_current_control_equal": closure[
                "source_current_control_equal"
            ],
            "source_final_control_equal": closure[
                "source_final_control_equal"
            ],
            "current_final_control_equal": closure[
                "current_final_control_equal"
            ],
            "final_line_envelope_not_above_current": closure[
                "final_line_envelope_not_above_current"
            ],
            "explicit_layout_change_pending_absent": (
                blocked[coordinate]["layout_change_pending"] is False
            ),
            "hard_grammar_risk_absent": closure[
                "hard_grammar_risk_absent"
            ],
            "base_runtime_proof_inherited": False,
        }
        safe = (
            all(
                value
                for key, value in predicates.items()
                if key != "base_runtime_proof_inherited"
            )
            and not failure_codes
        )
        integrated = context["integrated_rows"].get(coordinate)
        require(
            isinstance(integrated, dict)
            and integrated.get("runtime_review") == "pending"
            and integrated.get("scope_classification")
            == "runtime_fragment_pending"
            and integrated.get("semantic_review") == "approved",
            f"blocked exact row is not pending in integrated ledger: {coordinate}",
        )
        translation_hash = candidate_translation_hash(
            coordinate,
            inputs=inputs,
        )
        require(
            sha256_bytes(
                str(integrated["translation"]).encode("utf-16-le")
            )
            == translation_hash,
            f"integrated/final translation drifted: {coordinate}",
        )
        source_decision = context["source_by_coordinate"].get(coordinate)
        require(
            isinstance(source_decision, dict)
            and canonical_sha256(source_decision)
            == canonical_sha256(integrated),
            f"integrated/source exact decision drifted: {coordinate}",
        )
        row_adjudications[coordinate] = {
            "root": list(root),
            "status": (
                "pk_only_promotion_eligible"
                if safe
                else "manual_review_required"
            ),
            "proof_predicates": predicates,
            "failure_codes": sorted(failure_codes),
            "grammar_risk_keys": closure["grammar_risk_keys"],
            "closure_proof_sha256": closure["proof_sha256"],
            "translation_utf16le_sha256": translation_hash,
            "source_decision_sha256": canonical_sha256(source_decision),
            "integrated_row_sha256": canonical_sha256(integrated),
            "predecessor_layout_review": integrated["layout_review"],
            "original_full_candidate_taints": blocked[coordinate]["taints"],
            "original_full_candidate_reason_codes": blocked[coordinate][
                "reason_codes"
            ],
        }
    safe = [
        coordinate
        for coordinate, adjudication in row_adjudications.items()
        if adjudication["status"] == "pk_only_promotion_eligible"
    ]
    remaining = [
        coordinate
        for coordinate, adjudication in row_adjudications.items()
        if adjudication["status"] == "manual_review_required"
    ]
    safe_records = {
        BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        for coordinate in safe
    }
    remaining_records = {
        BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        for coordinate in remaining
    }
    require(
        len(safe) == EXPECTED_SAFE_ROWS
        and len(safe_records) == EXPECTED_SAFE_RECORDS
        and coordinate_digest(safe) == EXPECTED_SAFE_COORDINATE_SHA256
        and record_digest(safe_records) == EXPECTED_SAFE_RECORD_SHA256,
        "PK-only safe universe drifted",
    )
    require(
        len(remaining) == EXPECTED_REMAINING_ROWS
        and len(remaining_records) == EXPECTED_REMAINING_RECORDS
        and coordinate_digest(remaining)
        == EXPECTED_REMAINING_COORDINATE_SHA256
        and record_digest(remaining_records)
        == EXPECTED_REMAINING_RECORD_SHA256,
        "PK-only remaining universe drifted",
    )
    control_tainted = [
        coordinate
        for coordinate, adjudication in row_adjudications.items()
        if not adjudication["proof_predicates"][
            "source_final_control_equal"
        ]
    ]
    control_tainted_records = {
        BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        for coordinate in control_tainted
    }
    require(
        len(control_tainted) == EXPECTED_SOURCE_FINAL_CONTROL_TAINT_ROWS
        and len(control_tainted_records)
        == EXPECTED_SOURCE_FINAL_CONTROL_TAINT_RECORDS
        and coordinate_digest(control_tainted)
        == EXPECTED_SOURCE_FINAL_CONTROL_TAINT_COORDINATE_SHA256,
        "mandatory source-final control exclusion drifted",
    )
    failure_row_counts: Counter[str] = Counter()
    failure_record_counts: Counter[str] = Counter()
    row_combinations: Counter[str] = Counter()
    record_combinations: Counter[str] = Counter()
    for adjudication in row_adjudications.values():
        failure_row_counts.update(adjudication["failure_codes"])
        row_combinations.update(
            [
                "+".join(adjudication["failure_codes"])
                if adjudication["failure_codes"]
                else "PASS"
            ]
        )
    for root in roots:
        root_rows = [
            adjudication
            for coordinate, adjudication in row_adjudications.items()
            if BASE_AUDIT.parse_literal_coordinate(coordinate)[:2] == root
        ]
        combined = sorted(
            set().union(
                *(
                    set(adjudication["failure_codes"])
                    for adjudication in root_rows
                )
            )
        )
        failure_record_counts.update(combined)
        record_combinations.update(
            ["+".join(combined) if combined else "PASS"]
        )
    report = {
        "schema": AUDIT_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "scope": {
            "full_candidate_blocked_rows": len(blocked),
            "full_candidate_blocked_records": len(roots),
            "pk_only_promotion_eligible_rows": len(safe),
            "pk_only_promotion_eligible_records": len(safe_records),
            "manual_review_remaining_rows": len(remaining),
            "manual_review_remaining_records": len(remaining_records),
            "per_row_game_playback_required": 0,
        },
        "proof_policy": {
            "source_current_final_exact_control_closure_required": True,
            "call_and_jump_operands_and_targets_compared_exactly": True,
            "final_per_literal_line_count_must_not_exceed_current": True,
            "explicit_layout_change_pending_excluded": True,
            "hard_grammar_risk_evidence_excluded": True,
            "base_runtime_pair_proof_inherited": False,
            "base_donor_taints_ignored_only_after_independent_pk_proof": True,
        },
        "hard_grammar_risk_policy": {
            "true_is_risk": sorted(HARD_TRUE_GRAMMAR_RISK_FIELDS),
            "false_is_risk": sorted(HARD_FALSE_GRAMMAR_RISK_FIELDS),
        },
        "original_blockers": original_blocker_summary(blocked),
        "pk_only_failures": {
            "failure_row_counts": dict(sorted(failure_row_counts.items())),
            "failure_record_counts": dict(
                sorted(failure_record_counts.items())
            ),
            "combination_row_counts": dict(sorted(row_combinations.items())),
            "combination_record_counts": dict(
                sorted(record_combinations.items())
            ),
            "mandatory_source_final_control_exclusion_rows": len(
                control_tainted
            ),
            "mandatory_source_final_control_exclusion_records": len(
                control_tainted_records
            ),
        },
        "guards": {
            **context["input_hashes"],
            "blocked_coordinate_universe_sha256": coordinate_digest(
                blocked
            ),
            "blocked_record_universe_sha256": record_digest(roots),
            "eligible_coordinate_universe_sha256": coordinate_digest(safe),
            "eligible_record_universe_sha256": record_digest(safe_records),
            "remaining_coordinate_universe_sha256": coordinate_digest(
                remaining
            ),
            "remaining_record_universe_sha256": record_digest(
                remaining_records
            ),
            "source_final_control_taint_coordinate_sha256": (
                coordinate_digest(control_tainted)
            ),
            "closure_guard_universe_sha256": canonical_sha256(
                closure_guards
            ),
            "row_adjudication_universe_sha256": canonical_sha256(
                row_adjudications
            ),
        },
        "closure_guards": closure_guards,
        "row_adjudications": row_adjudications,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_translated_dialogue_text": False,
            "contains_complete_game_resource": False,
            "contains_only_coordinates_hashes_counts_and_predicates": True,
        },
        "promotion": {
            "runtime_promotion_performed": False,
            "steam_write_performed": False,
        },
    }
    return seal_report(report)


def validate_audit(
    report: Mapping[str, Any],
    *,
    context: Mapping[str, Any],
) -> None:
    validate_seal(report)
    require(
        report.get("schema") == AUDIT_SCHEMA
        and report.get("status") == "PASS",
        "PK-only closure audit schema/status drifted",
    )
    scope = report.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("full_candidate_blocked_rows")
        == EXPECTED_BLOCKED_ROWS
        and scope.get("pk_only_promotion_eligible_rows")
        == EXPECTED_SAFE_ROWS
        and scope.get("manual_review_remaining_rows")
        == EXPECTED_REMAINING_ROWS,
        "PK-only closure audit counts drifted",
    )
    require(
        report["guards"]["full_coverage_file_sha256"]
        == EXPECTED_FULL_COVERAGE_FILE_SHA256
        and report["guards"]["exact_coverage_file_sha256"]
        == EXPECTED_EXACT_COVERAGE_FILE_SHA256
        and report["guards"]["integrated_private_sha256"]
        == EXPECTED_INTEGRATED_PRIVATE_SHA256
        and report["guards"]["semantic_override_public_sha256"]
        == EXPECTED_SEMANTIC_OVERRIDE_PUBLIC_SHA256,
        "PK-only closure upstream binding drifted",
    )
    require(
        report.get("promotion", {}).get("runtime_promotion_performed")
        is False
        and report.get("promotion", {}).get("steam_write_performed")
        is False,
        "PK-only audit attempted promotion or Steam write",
    )


def overlay_row_guard_payload(
    coordinate: str,
    *,
    adjudication: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> dict[str, Any]:
    root = tuple(adjudication["root"])
    closure = audit["closure_guards"][record_key(root)]
    return {
        "coordinate": coordinate,
        "root": list(root),
        "translation_utf16le_sha256": adjudication[
            "translation_utf16le_sha256"
        ],
        "predecessor_layout_review": adjudication[
            "predecessor_layout_review"
        ],
        "source_decision_sha256": adjudication["source_decision_sha256"],
        "integrated_row_sha256": adjudication["integrated_row_sha256"],
        "closure_proof_sha256": closure["proof_sha256"],
        "proof_predicates": adjudication["proof_predicates"],
        "audit_file_sha256": audit_file_sha256,
        "audit_payload_sha256": audit["guards"]["report_payload_sha256"],
        "full_coverage_file_sha256": audit["guards"][
            "full_coverage_file_sha256"
        ],
        "full_coverage_payload_sha256": audit["guards"][
            "full_coverage_payload_sha256"
        ],
        "exact_coverage_file_sha256": audit["guards"][
            "exact_coverage_file_sha256"
        ],
        "semantic_override_private_sha256": audit["guards"][
            "semantic_override_private_sha256"
        ],
        "semantic_override_public_sha256": audit["guards"][
            "semantic_override_public_sha256"
        ],
        "integrated_private_sha256": audit["guards"][
            "integrated_private_sha256"
        ],
        "integrated_report_file_sha256": audit["guards"][
            "integrated_report_file_sha256"
        ],
        "base_runtime_proof_inherited": False,
    }


def expected_overlay_row(
    coordinate: str,
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> dict[str, Any]:
    adjudication = audit["row_adjudications"].get(coordinate)
    require(
        isinstance(adjudication, dict)
        and adjudication.get("status") == "pk_only_promotion_eligible"
        and adjudication.get("failure_codes") == [],
        f"unsafe PK-only row cannot be promoted: {coordinate}",
    )
    predicates = adjudication["proof_predicates"]
    require(
        predicates
        == {
            "source_current_control_equal": True,
            "source_final_control_equal": True,
            "current_final_control_equal": True,
            "final_line_envelope_not_above_current": True,
            "explicit_layout_change_pending_absent": True,
            "hard_grammar_risk_absent": True,
            "base_runtime_proof_inherited": False,
        },
        f"PK-only proof predicates are incomplete: {coordinate}",
    )
    row_guard = canonical_sha256(
        overlay_row_guard_payload(
            coordinate,
            adjudication=adjudication,
            audit=audit,
            audit_file_sha256=audit_file_sha256,
        )
    )
    return {
        "schema": OVERLAY_ROW_SCHEMA,
        "resource": "pk_msggame",
        "coordinate": coordinate,
        "status": "verified",
        "method": METHOD,
        "scope_transition": {
            "from": "runtime_fragment_pending",
            "to": "retranslated",
        },
        "translation_utf16le_sha256": adjudication[
            "translation_utf16le_sha256"
        ],
        "layout_review_binding": {
            "status": adjudication["predecessor_layout_review"],
        },
        "source_decision_binding": {
            "decision_sha256": adjudication["source_decision_sha256"],
        },
        "predecessor_integrated_binding": {
            "row_sha256": adjudication["integrated_row_sha256"],
            "private_integrated_decision_sha256": audit["guards"][
                "integrated_private_sha256"
            ],
            "source_free_report_file_sha256": audit["guards"][
                "integrated_report_file_sha256"
            ],
            "integrated_builder_sha256": audit["guards"][
                "integrated_builder_sha256"
            ],
        },
        "full_candidate_binding": {
            "exact_coverage_file_sha256": audit["guards"][
                "exact_coverage_file_sha256"
            ],
            "coverage_report_file_sha256": audit["guards"][
                "full_coverage_file_sha256"
            ],
            "coverage_report_payload_sha256": audit["guards"][
                "full_coverage_payload_sha256"
            ],
            "pk_full_candidate_packed_sha256": audit["guards"][
                "full_candidate_packed_sha256"
            ],
            "semantic_override_private_sha256": audit["guards"][
                "semantic_override_private_sha256"
            ],
            "semantic_override_public_sha256": audit["guards"][
                "semantic_override_public_sha256"
            ],
        },
        "pk_only_closure_binding": {
            "root": adjudication["root"],
            "closure_proof_sha256": adjudication[
                "closure_proof_sha256"
            ],
            "proof_predicates": predicates,
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256": audit["guards"][
                "report_payload_sha256"
            ],
            "row_verification_guard_sha256": row_guard,
        },
        "base_runtime_proof_inherited": False,
        "per_row_game_playback_required": False,
    }


def build_overlay_rows(
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> list[dict[str, Any]]:
    eligible = [
        coordinate
        for coordinate, adjudication in audit[
            "row_adjudications"
        ].items()
        if adjudication["status"] == "pk_only_promotion_eligible"
    ]
    eligible.sort(key=BASE_AUDIT.parse_literal_coordinate)
    require(
        len(eligible) == EXPECTED_SAFE_ROWS
        and coordinate_digest(eligible) == EXPECTED_SAFE_COORDINATE_SHA256,
        "overlay eligible universe drifted",
    )
    return [
        expected_overlay_row(
            coordinate,
            audit=audit,
            audit_file_sha256=audit_file_sha256,
        )
        for coordinate in eligible
    ]


def validate_overlay_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> None:
    require(
        list(rows)
        == build_overlay_rows(
            audit=audit,
            audit_file_sha256=audit_file_sha256,
        ),
        "PK-only verification overlay drifted",
    )


def build_promotion_report(
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    private_content: str,
) -> dict[str, Any]:
    report = {
        "schema": PROMOTION_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "input": {
            "full_candidate_blocked_rows": EXPECTED_BLOCKED_ROWS,
            "pk_only_promotion_eligible_rows": EXPECTED_SAFE_ROWS,
            "manual_review_remaining_rows": EXPECTED_REMAINING_ROWS,
            "full_candidate_packed_sha256": audit["guards"][
                "full_candidate_packed_sha256"
            ],
        },
        "result": {
            "private_overlay_rows": EXPECTED_SAFE_ROWS,
            "private_overlay_sha256": sha256_bytes(
                private_content.encode("utf-8")
            ),
            "eligible_coordinate_universe_sha256": audit["guards"][
                "eligible_coordinate_universe_sha256"
            ],
            "eligible_record_universe_sha256": audit["guards"][
                "eligible_record_universe_sha256"
            ],
            "remaining_rows": EXPECTED_REMAINING_ROWS,
            "remaining_coordinate_universe_sha256": audit["guards"][
                "remaining_coordinate_universe_sha256"
            ],
            "translation_body_copied": False,
        },
        "evidence": {
            "audit_report": (
                "workstreams/pk_msggame_runtime_vm_audit_v1/public/"
                "pk_msggame_exact_blocked_pk_only_closure_coverage.v1.json"
            ),
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256": audit["guards"][
                "report_payload_sha256"
            ],
            "closure_guard_universe_sha256": audit["guards"][
                "closure_guard_universe_sha256"
            ],
            "row_adjudication_universe_sha256": audit["guards"][
                "row_adjudication_universe_sha256"
            ],
            "full_candidate_coverage_file_sha256": audit["guards"][
                "full_coverage_file_sha256"
            ],
            "semantic_override_public_sha256": audit["guards"][
                "semantic_override_public_sha256"
            ],
            "predecessor_integrated_private_sha256": audit["guards"][
                "integrated_private_sha256"
            ],
        },
        "exclusion_policy": {
            "source_candidate_control_taint_rows_included": 0,
            "grammar_risk_rows_included": 0,
            "layout_or_line_envelope_risk_rows_included": 0,
            "unsafe_rows_included": 0,
            "base_runtime_proof_inherited": False,
        },
        "integration_boundary": {
            "overlay_is_not_a_full_dialogue_decision_file": True,
            "predecessor_integrated_checkpoint_is_immutable_input": True,
            "live_integrated_ledger_is_input": False,
        },
        "distribution_policy": {
            "tracked_reports_contain_commercial_source_text": False,
            "tracked_reports_contain_translated_dialogue_text": False,
            "private_overlay_contains_commercial_source_text": False,
            "private_overlay_contains_translated_dialogue_text": False,
            "private_overlay_stays_below_tmp": True,
        },
        "steam_write_performed": False,
        "guards": {},
    }
    return seal_report(report)


def validate_promotion_report(
    report: Mapping[str, Any],
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    private_content: str,
) -> None:
    validate_seal(report)
    require(
        report
        == build_promotion_report(
            audit=audit,
            audit_file_sha256=audit_file_sha256,
            private_content=private_content,
        ),
        "PK-only promotion report drifted",
    )


def build_outputs() -> tuple[
    str,
    str,
    str,
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    return build_outputs_from_context(input_context())


def build_outputs_from_context(
    context: Mapping[str, Any],
) -> tuple[
    str,
    str,
    str,
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    steam_before = live_steam_hash()
    audit = build_audit(context)
    validate_audit(audit, context=context)
    audit_content = canonical_json(audit)
    audit_file_sha256 = sha256_bytes(audit_content.encode("utf-8"))
    overlay_rows = build_overlay_rows(
        audit=audit,
        audit_file_sha256=audit_file_sha256,
    )
    validate_overlay_rows(
        overlay_rows,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
    )
    private_content = canonical_jsonl(overlay_rows)
    promotion = build_promotion_report(
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        private_content=private_content,
    )
    validate_promotion_report(
        promotion,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        private_content=private_content,
    )
    steam_after = live_steam_hash()
    require(
        steam_after == steam_before,
        "Steam PK msggame changed during PK-only closure build",
    )
    result_context = {
        **context,
        "audit": audit,
        "audit_file_sha256": audit_file_sha256,
        "overlay_rows": overlay_rows,
        "steam_hash_before": steam_before,
        "steam_hash_after": steam_after,
    }
    return (
        audit_content,
        private_content,
        canonical_json(promotion),
        audit,
        promotion,
        result_context,
    )


def require_private_output_scope(path: Path) -> None:
    root = DIALOGUE_TMP.resolve(strict=False)
    resolved = path.resolve(strict=False)
    require(
        resolved != root and root in resolved.parents,
        f"private output must stay below {root}: {resolved}",
    )


def require_public_output_scope(path: Path) -> None:
    root = WORKSTREAM.resolve(strict=False)
    resolved = path.resolve(strict=False)
    require(
        resolved != root and root in resolved.parents,
        f"public output must stay below {root}: {resolved}",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=DEFAULT_AUDIT_OUTPUT,
    )
    parser.add_argument(
        "--private-output",
        type=Path,
        default=DEFAULT_PRIVATE_OUTPUT,
    )
    parser.add_argument(
        "--promotion-output",
        type=Path,
        default=DEFAULT_PROMOTION_OUTPUT,
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")
    require_private_output_scope(args.private_output)
    require_public_output_scope(args.audit_output)
    require_public_output_scope(args.promotion_output)
    shared_context = input_context()
    first = build_outputs_from_context(shared_context)
    second = build_outputs_from_context(shared_context)
    require(first[0] == second[0], "two-run audit report drifted")
    require(first[1] == second[1], "two-run private overlay drifted")
    require(first[2] == second[2], "two-run promotion report drifted")
    (
        audit_content,
        private_content,
        promotion_content,
        audit,
        promotion,
        context,
    ) = first
    if args.write:
        ENGINE.atomic_write(args.audit_output, audit_content)
        ENGINE.atomic_write(args.private_output, private_content)
        ENGINE.atomic_write(args.promotion_output, promotion_content)
    if args.check:
        require(
            args.audit_output.is_file()
            and args.audit_output.read_text(encoding="utf-8")
            == audit_content,
            "tracked PK-only audit report drifted",
        )
        require(
            args.private_output.is_file()
            and args.private_output.read_text(encoding="utf-8")
            == private_content,
            "private PK-only overlay drifted",
        )
        require(
            args.promotion_output.is_file()
            and args.promotion_output.read_text(encoding="utf-8")
            == promotion_content,
            "tracked PK-only promotion report drifted",
        )
    validate_audit(audit, context=context)
    validate_overlay_rows(
        read_jsonl(args.private_output),
        audit=audit,
        audit_file_sha256=context["audit_file_sha256"],
    )
    validate_promotion_report(
        promotion,
        audit=audit,
        audit_file_sha256=context["audit_file_sha256"],
        private_content=private_content,
    )
    print(
        "PASS "
        f"promoted={audit['scope']['pk_only_promotion_eligible_rows']} "
        f"remaining={audit['scope']['manual_review_remaining_rows']} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        ValueError,
        PkOnlyClosureError,
        FULL_AUDIT.FullCandidateAuditError,
        ENGINE.RetranslationError,
        BASE_AUDIT.AuditError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
