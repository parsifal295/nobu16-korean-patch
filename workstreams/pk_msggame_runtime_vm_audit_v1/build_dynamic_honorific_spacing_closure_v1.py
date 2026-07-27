#!/usr/bin/env python3
"""Repair four dynamic honorific boundaries and renew their VM closures.

The Base/PK message VM appends dynamic names and called literals without an
automatic separator.  Two semantic pairs therefore need one literal-owned
ASCII space before the Korean historical honorific.  This layer is deliberately
post-checkpoint: it changes only four translations, renews every already
verified row whose call/jump closure reaches those records, and promotes only
pending PK roots that independently pass grammar plus raw-G1N full-closure
current-relative width guards.

Tracked reports contain coordinates, counts, widths, predicates, and hashes
only.  Full updated decisions remain below ``tmp``.  Steam is read only.
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import hashlib
import importlib.util
import json
import re
import struct
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
OVERLAY_DIR = DIALOGUE_TMP / "decisions" / "runtime_verification_overlays"
OVERRIDE_DIR = DIALOGUE_TMP / "semantic_overrides"
CROSS_BUILDER_PATH = (
    WORKSTREAM / "build_pk_msggame_pending_cross_resource_exact_closure_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_cross_resource_checkpoint.private.v1.jsonl"
)
CHECKPOINT_REPORT_PATH = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration.post_cross_resource_checkpoint.source_free.v1.json"
)
CHECKPOINT_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM
    / "build_runtime_vm_post_cross_resource_checkpoint_v1.py"
)
GHIDRA_VM_CONTRACT_PATH = WORKSTREAM / "ghidra_pk_vm_contract.v1.json"
GHIDRA_LAYOUT_CONTRACT_PATH = (
    WORKSTREAM / "ghidra_pk_msggame_layout_contract.v1.json"
)
DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "dynamic_honorific_spacing_closure_coverage.v1.json"
)
DEFAULT_BASE_REPORT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "base_msggame_dynamic_honorific_spacing_delta.v1.json"
)
DEFAULT_PK_REPORT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_msggame_dynamic_honorific_spacing_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    OVERRIDE_DIR
    / "dynamic_honorific_spacing_integrated_decisions.private.v1.jsonl"
)
DEFAULT_BASE_OVERLAY_OUTPUT = (
    OVERLAY_DIR
    / "base_msggame_dynamic_honorific_spacing_delta_verified.private.v1.jsonl"
)
DEFAULT_PK_OVERLAY_OUTPUT = (
    OVERLAY_DIR
    / "pk_msggame_dynamic_honorific_spacing_closure_verified.private.v1.jsonl"
)
LIVE_STEAM_BASE = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin"
)
LIVE_STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

AUDIT_SCHEMA = (
    "nobu16.kr.dynamic-honorific-spacing-closure-coverage.v1"
)
BASE_REPORT_SCHEMA = (
    "nobu16.kr.base-msggame-dynamic-honorific-spacing-delta.v1"
)
PK_REPORT_SCHEMA = (
    "nobu16.kr.pk-msggame-dynamic-honorific-spacing-closure-promotion.v1"
)
BASE_OVERLAY_ROW_SCHEMA = (
    "nobu16.kr.base-msggame-dynamic-honorific-spacing-delta-row.v1"
)
PK_OVERLAY_ROW_SCHEMA = (
    "nobu16.kr.pk-msggame-dynamic-honorific-spacing-closure-row.v1"
)
BASE_METHOD = "reversed_vm_dynamic_honorific_spacing_delta_analysis"
PK_METHOD = "reversed_vm_dynamic_honorific_spacing_closure_analysis"

EXPECTED_CHECKPOINT_PRIVATE_SHA256 = (
    "3FF6AF87B638C9F98DF4F956E5A7985B70E5F4A899A48E77ED67629212B247CC"
)
EXPECTED_CHECKPOINT_REPORT_SHA256 = (
    "2D38AB416E87E83C5DBCF8485F18F970BC8F712693CE5ED8C7C59D9255D22D08"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256 = (
    "1993385F70DBF22D41798B9FEC008E89AB0EF2404C307526DEAA9E29DB079B48"
)
EXPECTED_GHIDRA_VM_CONTRACT_SHA256 = (
    "21DAF83330F278484BFB2462188804947A6C457F4B072DA80D7ADFBD3D13F461"
)
EXPECTED_GHIDRA_LAYOUT_CONTRACT_SHA256 = (
    "EE28501EE41586025518325DE5CEE9722B99E1063FBE7B8E9049DFA6E310F9AC"
)
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_702
EXPECTED_PREDECESSOR_PENDING_ROOTS = 5_191
EXPECTED_AFFECTED_PENDING_ROWS = 434
EXPECTED_AFFECTED_PENDING_ROOTS = 229
EXPECTED_ELIGIBLE_ROWS = 57
EXPECTED_ELIGIBLE_ROOTS = 40
EXPECTED_REJECTED_ROWS = 377
EXPECTED_REJECTED_ROOTS = 189
EXPECTED_PENDING_AFTER = 8_645
EXPECTED_ELIGIBLE_COORDINATE_SHA256 = (
    "C4887CCB23507CBB78B3CA430F4309716E989352DB12E479229E3F17154B6731"
)
EXPECTED_ELIGIBLE_ROOT_SHA256 = (
    "A33A4763DAA9ACAD8C8EC40734B4B574B57F5FEA9AE4F34527504E50DA4ADAD1"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "18F9E09F7D0FE71317733208B25B22EE47A45B5D927C2B583F6AA44B8019D41E"
)
EXPECTED_BASE_CANDIDATE_SHA256 = (
    "44828B27368FB74EF906DC167DCAF1BA54129A4313F7EDA3C0668777BB86E276"
)
EXPECTED_BASE_RENEWAL_ROWS = 420
EXPECTED_PK_RENEWAL_ROWS = 50
EXPECTED_BASE_RENEWAL_COORDINATE_SHA256 = (
    "322AD1F2983B7CD18600C1CD1D7E7C1AF08558B6CB4E61A65E53221E63D226A7"
)
EXPECTED_PK_RENEWAL_COORDINATE_SHA256 = (
    "A745E82291299FB947DB51074C8031279DEC9BF0B3E95D20B1B5F5DA3312A8B6"
)

BASE_TRANSLATION_OVERRIDES = {
    "0:1271:0": " 공",
    "0:1275:0": " 공",
}
PK_TRANSLATION_OVERRIDES = {
    "0:1325:0": " 공",
    "0:1329:0": " 공",
}
CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
JUMP_RE = re.compile(b"\x01\x4A(.{4})", re.DOTALL)
TRANSLATION_OVERRIDES = {
    **{
        ("base_msggame", coordinate): translation
        for coordinate, translation in BASE_TRANSLATION_OVERRIDES.items()
    },
    **{
        ("pk_msggame", coordinate): translation
        for coordinate, translation in PK_TRANSLATION_OVERRIDES.items()
    },
}


class HonorificSpacingError(ValueError):
    """Raised when the dynamic-honorific delta is not fully proved."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HonorificSpacingError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CROSS = load_module("dynamic_honorific_spacing_cross", CROSS_BUILDER_PATH)
BASE_AUDIT = CROSS.BASE_AUDIT
FULL_AUDIT = CROSS.FULL_AUDIT
ENGINE = CROSS.ENGINE


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return CROSS.canonical_sha256(value)


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(
        dict(value),
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
    ) + "\n"


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(
        json.dumps(
            dict(row),
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
    result: list[dict[str, Any]] = []
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
        result.append(value)
    return result


def coordinate_sort_key(
    key: tuple[str, str],
) -> tuple[int, int, int, int]:
    resource, coordinate = key
    return (
        0 if resource == "base_msggame" else 1,
        *BASE_AUDIT.parse_literal_coordinate(coordinate),
    )


def row_sort_key(row: Mapping[str, Any]) -> tuple[int, int, int, int]:
    return coordinate_sort_key(
        (str(row["resource"]), str(row["coordinate"]))
    )


def coordinate_digest(values: Iterable[str]) -> str:
    return CROSS.coordinate_digest(values)


def record_digest(values: Iterable[tuple[int, int]]) -> str:
    return CROSS.record_digest(values)


def live_hash(path: Path) -> str | None:
    return sha256_bytes(path.read_bytes()) if path.is_file() else None


def seal_report(report: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(report))
    guards = result.setdefault("guards", {})
    require(isinstance(guards, dict), "report guards are not an object")
    guards.pop("report_payload_sha256", None)
    guards["report_payload_sha256"] = canonical_sha256(result)
    return result


def validate_seal(report: Mapping[str, Any]) -> None:
    copy_value = copy.deepcopy(dict(report))
    guards = copy_value.get("guards")
    require(isinstance(guards, dict), "sealed report guards are absent")
    expected = guards.pop("report_payload_sha256", None)
    require(
        isinstance(expected, str)
        and expected == canonical_sha256(copy_value),
        "report payload seal drifted",
    )


def verify_contracts() -> dict[str, Any]:
    vm_sha256 = sha256_bytes(GHIDRA_VM_CONTRACT_PATH.read_bytes())
    layout_sha256 = sha256_bytes(GHIDRA_LAYOUT_CONTRACT_PATH.read_bytes())
    require(
        vm_sha256 == EXPECTED_GHIDRA_VM_CONTRACT_SHA256,
        f"Ghidra VM contract drifted: {vm_sha256}",
    )
    require(
        layout_sha256 == EXPECTED_GHIDRA_LAYOUT_CONTRACT_SHA256,
        f"Ghidra layout contract drifted: {layout_sha256}",
    )
    vm = read_json(GHIDRA_VM_CONTRACT_PATH)
    layout = read_json(GHIDRA_LAYOUT_CONTRACT_PATH)
    BASE_AUDIT.verify_contract(vm)
    require(
        vm.get("opcode_contract", {}).get("02", {}).get(
            "automatic_space_inserted"
        )
        is False
        and vm.get("opcode_contract", {}).get("0143", {}).get("semantics")
        == "push_return_address_then_call_record"
        and vm.get("opcode_contract", {}).get("014A", {}).get("semantics")
        == "jump_to_record"
        and layout.get("adjudication", {}).get(
            "current_relative_nonexpansion_remains_widget_independent"
        )
        is True
        and layout.get("adjudication", {}).get(
            "one_absolute_pixel_gate_applies_to_all_msggame_rows"
        )
        is False,
        "Ghidra append/layout contract drifted",
    )
    return {
        "vm_file_sha256": vm_sha256,
        "layout_file_sha256": layout_sha256,
        "program_sha256": vm["program"]["unpacked_exe_sha256"],
        "automatic_space_inserted": False,
        "current_relative_nonexpansion_widget_independent": True,
    }


def load_checkpoint() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[str, Any],
]:
    private_sha256 = sha256_bytes(CHECKPOINT_PRIVATE_PATH.read_bytes())
    report_sha256 = sha256_bytes(CHECKPOINT_REPORT_PATH.read_bytes())
    builder_sha256 = sha256_bytes(CHECKPOINT_BUILDER_PATH.read_bytes())
    require(
        private_sha256 == EXPECTED_CHECKPOINT_PRIVATE_SHA256,
        f"post-cross private checkpoint drifted: {private_sha256}",
    )
    require(
        report_sha256 == EXPECTED_CHECKPOINT_REPORT_SHA256,
        f"post-cross report checkpoint drifted: {report_sha256}",
    )
    require(
        builder_sha256 == EXPECTED_CHECKPOINT_BUILDER_SHA256,
        f"post-cross checkpoint builder drifted: {builder_sha256}",
    )
    report = read_json(CHECKPOINT_REPORT_PATH)
    require(
        report.get("schema")
        == "nobu16.kr.pc-dialogue-runtime-vm-integration.v1"
        and report.get("status") == "PASS"
        and report.get("result", {}).get(
            "private_integrated_decision_sha256"
        )
        == private_sha256
        and report.get("result", {}).get("runtime_review_pending")
        == EXPECTED_PREDECESSOR_PENDING
        and report.get("steam_write_performed") is False,
        "post-cross checkpoint contract drifted",
    )
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for row in read_jsonl(CHECKPOINT_PRIVATE_PATH):
        key = (str(row.get("resource")), str(row.get("coordinate")))
        require(
            key[0] in {"base_msggame", "pk_msggame"} and key not in rows,
            f"invalid or duplicate checkpoint row: {key}",
        )
        rows[key] = row
    pending_coordinates = [
        coordinate
        for (resource, coordinate), row in rows.items()
        if resource == "pk_msggame" and row.get("runtime_review") == "pending"
    ]
    pending_roots = {
        BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        for coordinate in pending_coordinates
    }
    require(
        len(rows) == EXPECTED_PREDECESSOR_ROWS
        and len(pending_coordinates) == EXPECTED_PREDECESSOR_PENDING
        and len(pending_roots) == EXPECTED_PREDECESSOR_PENDING_ROOTS,
        "post-cross checkpoint row/pending universe drifted",
    )
    for key, translation in TRANSLATION_OVERRIDES.items():
        row = rows.get(key)
        require(
            row is not None
            and row.get("translation") == translation.strip()
            and row.get("runtime_review") == "verified"
            and row.get("scope_classification") == "retranslated"
            and isinstance(row.get("runtime_vm_verification"), dict),
            f"honorific predecessor row drifted: {key}",
        )
    return rows, {
        "private_sha256": private_sha256,
        "report_file_sha256": report_sha256,
        "report_payload_sha256": canonical_sha256(report),
        "builder_sha256": builder_sha256,
        "pending_rows": len(pending_coordinates),
        "pending_roots": len(pending_roots),
    }


def build_candidate(
    *,
    resource: str,
    checkpoint_rows: Mapping[tuple[str, str], Mapping[str, Any]],
) -> tuple[bytes, dict[tuple[int, int], Any], dict[str, str]]:
    current_path = (
        BASE_AUDIT.DEFAULT_BASE_CURRENT
        if resource == "base_msggame"
        else BASE_AUDIT.DEFAULT_PK_CURRENT
    )
    replacements: dict[tuple[int, int, int], str] = {}
    for (row_resource, coordinate), row in checkpoint_rows.items():
        if row_resource != resource:
            continue
        translation = TRANSLATION_OVERRIDES.get(
            (resource, coordinate),
            row.get("translation"),
        )
        if isinstance(translation, str):
            replacements[
                BASE_AUDIT.parse_literal_coordinate(coordinate)
            ] = translation
    current_blob = current_path.read_bytes()
    candidate_blob = BASE_AUDIT.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    records = BASE_AUDIT.records_from_blob(candidate_blob)
    manifest = {
        coordinate: ENGINE.sha256_text(
            str(
                TRANSLATION_OVERRIDES.get(
                    (resource, coordinate),
                    row["translation"],
                )
            )
        )
        for (row_resource, coordinate), row in checkpoint_rows.items()
        if row_resource == resource and isinstance(row.get("translation"), str)
    }
    return candidate_blob, records, manifest


def graph_edges(
    records: Mapping[tuple[int, int], Any],
    *,
    conservative_operand_scan: bool = False,
) -> dict[tuple[int, int], tuple[tuple[int, int], ...]]:
    edges: dict[tuple[int, int], tuple[tuple[int, int], ...]] = {}
    for record, value in records.items():
        if conservative_operand_scan:
            operands = [
                struct.unpack("<I", match.group(1))[0]
                for gap in BASE_AUDIT.literal_gaps(value)
                for pattern in (CALL_RE, JUMP_RE)
                for match in pattern.finditer(gap)
            ]
            targets = [
                (operand // 10_000, operand % 10_000)
                for operand in operands
                if operand
            ]
        else:
            targets = [
                tuple(component["target"])
                for component in BASE_AUDIT.decode_record(value)
                if component["kind"] in {"call", "jump"}
            ]
        require(
            all(target in records for target in targets),
            f"call/jump target outside resource: {record}",
        )
        edges[record] = tuple(targets)
    return edges


def reverse_ancestors(
    *,
    edges: Mapping[tuple[int, int], Sequence[tuple[int, int]]],
    targets: Sequence[tuple[int, int]],
) -> set[tuple[int, int]]:
    reverse: defaultdict[
        tuple[int, int],
        set[tuple[int, int]],
    ] = defaultdict(set)
    for source, descendants in edges.items():
        for target in descendants:
            reverse[target].add(source)
    affected = set(targets)
    queue = deque(targets)
    while queue:
        target = queue.popleft()
        for source in reverse.get(target, set()):
            if source not in affected:
                affected.add(source)
                queue.append(source)
    return affected


def reachable_targets(
    root: tuple[int, int],
    *,
    edges: Mapping[tuple[int, int], Sequence[tuple[int, int]]],
    target_records: set[tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    seen: set[tuple[int, int]] = set()
    queue = [root]
    while queue:
        record = queue.pop()
        if record in seen:
            continue
        seen.add(record)
        queue.extend(edges.get(record, ()))
    targets = tuple(sorted(seen & target_records))
    require(targets, f"affected root has no repaired descendant: {root}")
    return targets


def component_signatures(record: Any) -> list[dict[str, Any]]:
    return [
        FULL_AUDIT.pk_component_signature(component)
        for component in BASE_AUDIT.decode_record(record)
    ]


def target_delta_manifest(
    *,
    resource: str,
    target_records: Sequence[tuple[int, int]],
    source_records: Mapping[tuple[int, int], Any],
    current_records: Mapping[tuple[int, int], Any],
    predecessor_records: Mapping[tuple[int, int], Any],
    candidate_records: Mapping[tuple[int, int], Any],
) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for record in sorted(target_records):
        source = source_records[record]
        current = current_records[record]
        predecessor = predecessor_records[record]
        candidate = candidate_records[record]
        source_signatures = component_signatures(source)
        current_signatures = component_signatures(current)
        predecessor_signatures = component_signatures(predecessor)
        candidate_signatures = component_signatures(candidate)
        require(
            source_signatures
            == current_signatures
            == predecessor_signatures
            == candidate_signatures,
            f"{resource} repaired target control signature drifted: {record}",
        )
        current_literals = BASE_AUDIT.parse_record_literals(current)
        predecessor_literals = BASE_AUDIT.parse_record_literals(predecessor)
        candidate_literals = BASE_AUDIT.parse_record_literals(candidate)
        require(
            len(current_literals)
            == len(predecessor_literals)
            == len(candidate_literals)
            == 1,
            f"{resource} repaired target literal arity drifted: {record}",
        )
        current_text = current_literals[0].text
        predecessor_text = predecessor_literals[0].text
        candidate_text = candidate_literals[0].text
        current_widths = CROSS.RESIDUAL_AUDIT.raw_line_widths(current_text)
        predecessor_widths = CROSS.RESIDUAL_AUDIT.raw_line_widths(
            predecessor_text
        )
        candidate_widths = CROSS.RESIDUAL_AUDIT.raw_line_widths(candidate_text)
        require(
            predecessor_text == candidate_text.strip()
            and candidate_text == f" {predecessor_text}"
            and len(current_widths)
            == len(predecessor_widths)
            == len(candidate_widths)
            == 1
            and predecessor_widths == (48,)
            and candidate_widths == (72,)
            and current_widths == (96,)
            and candidate_widths[0] <= current_widths[0]
            and ENGINE.protected_signature(candidate_text[1:])
            == ENGINE.protected_signature(predecessor_text),
            f"{resource} repaired target spacing/width proof drifted: {record}",
        )
        manifest.append(
            {
                "record": list(record),
                "source_record_sha256": sha256_bytes(source.data),
                "current_record_sha256": sha256_bytes(current.data),
                "predecessor_record_sha256": sha256_bytes(predecessor.data),
                "candidate_record_sha256": sha256_bytes(candidate.data),
                "component_sha256": canonical_sha256(candidate_signatures),
                "current_literal_utf16le_sha256": ENGINE.sha256_text(
                    current_text
                ),
                "predecessor_literal_utf16le_sha256": ENGINE.sha256_text(
                    predecessor_text
                ),
                "candidate_literal_utf16le_sha256": ENGINE.sha256_text(
                    candidate_text
                ),
                "current_raw_g1n_widths": list(current_widths),
                "predecessor_raw_g1n_widths": list(predecessor_widths),
                "candidate_raw_g1n_widths": list(candidate_widths),
                "candidate_current_relative_nonexpanding": True,
                "literal_owned_ascii_leading_space_count": 1,
            }
        )
    return manifest


def changed_record_guard(
    *,
    predecessor_records: Mapping[tuple[int, int], Any],
    candidate_records: Mapping[tuple[int, int], Any],
    expected_changed: set[tuple[int, int]],
) -> dict[str, Any]:
    require(
        set(predecessor_records) == set(candidate_records),
        "candidate record universe drifted",
    )
    changed = {
        record
        for record in predecessor_records
        if predecessor_records[record].data != candidate_records[record].data
    }
    require(
        changed == expected_changed,
        f"candidate changed record universe drifted: {changed}",
    )
    return {
        "changed_records": [list(record) for record in sorted(changed)],
        "changed_record_universe_sha256": record_digest(changed),
        "unchanged_record_count": len(candidate_records) - len(changed),
    }


def repaired_pk_decisions(
    checkpoint_rows: Mapping[tuple[str, str], Mapping[str, Any]],
) -> tuple[
    dict[tuple[int, int], list[dict[str, Any]]],
    dict[str, dict[str, Any]],
]:
    by_record: defaultdict[
        tuple[int, int],
        list[dict[str, Any]],
    ] = defaultdict(list)
    by_coordinate: dict[str, dict[str, Any]] = {}
    for (resource, coordinate), predecessor in checkpoint_rows.items():
        if resource != "pk_msggame":
            continue
        row = copy.deepcopy(dict(predecessor))
        if coordinate in PK_TRANSLATION_OVERRIDES:
            row["translation"] = PK_TRANSLATION_OVERRIDES[coordinate]
            evidence = copy.deepcopy(row.get("honorific_spacing_evidence"))
            require(
                isinstance(evidence, dict)
                and evidence.get("automatic_space_inserted") is False
                and evidence.get("caller_rewrite_required") is True,
                f"PK honorific predecessor evidence drifted: {coordinate}",
            )
            evidence.update(
                {
                    "semantic_candidate": PK_TRANSLATION_OVERRIDES[coordinate],
                    "caller_rewrite_required": False,
                    "boundary_space_literal_owned": True,
                    "all_speaker_branches_grammatical": True,
                    "review": (
                        "dynamic name-title boundary repaired by one "
                        "literal-owned ASCII space"
                    ),
                }
            )
            row["honorific_spacing_evidence"] = evidence
        parsed = BASE_AUDIT.parse_literal_coordinate(coordinate)
        by_record[parsed[:2]].append(row)
        by_coordinate[coordinate] = row
    return dict(by_record), by_coordinate


def root_delta_proofs(
    *,
    resource: str,
    affected_records: set[tuple[int, int]],
    edges: Mapping[tuple[int, int], Sequence[tuple[int, int]]],
    target_records: set[tuple[int, int]],
    predecessor_records: Mapping[tuple[int, int], Any],
    candidate_records: Mapping[tuple[int, int], Any],
    target_delta_sha256: str,
) -> dict[tuple[int, int], dict[str, Any]]:
    proofs: dict[tuple[int, int], dict[str, Any]] = {}
    for root in sorted(affected_records):
        targets = reachable_targets(
            root,
            edges=edges,
            target_records=target_records,
        )
        payload = {
            "resource": resource,
            "root": list(root),
            "reachable_repaired_targets": [
                list(target) for target in targets
            ],
            "predecessor_root_record_sha256": sha256_bytes(
                predecessor_records[root].data
            ),
            "candidate_root_record_sha256": sha256_bytes(
                candidate_records[root].data
            ),
            "root_record_changed": root in target_records,
            "target_delta_manifest_sha256": target_delta_sha256,
        }
        proofs[root] = {
            **payload,
            "proof_sha256": canonical_sha256(payload),
        }
    return proofs


def build_analysis(
    *,
    checkpoint_rows: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    context = CROSS.PK_ONLY.input_context()
    baseline_inputs = context["inputs"]
    base_blob, base_candidate_records, base_replacement_manifest = (
        build_candidate(
            resource="base_msggame",
            checkpoint_rows=checkpoint_rows,
        )
    )
    pk_blob, pk_candidate_records, pk_replacement_manifest = build_candidate(
        resource="pk_msggame",
        checkpoint_rows=checkpoint_rows,
    )
    require(
        sha256_bytes(base_blob) == EXPECTED_BASE_CANDIDATE_SHA256,
        f"repaired Base candidate drifted: {sha256_bytes(base_blob)}",
    )
    require(
        sha256_bytes(pk_blob) == EXPECTED_PK_CANDIDATE_SHA256,
        f"repaired PK candidate drifted: {sha256_bytes(pk_blob)}",
    )
    base_current_records = BASE_AUDIT.records_from_blob(
        BASE_AUDIT.DEFAULT_BASE_CURRENT.read_bytes()
    )
    pk_current_records = BASE_AUDIT.records_from_blob(
        BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes()
    )
    updated_inputs = dataclasses.replace(
        baseline_inputs,
        base_candidate_records=base_candidate_records,
        pk_candidate_records=pk_candidate_records,
    )
    base_targets = {
        BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        for coordinate in BASE_TRANSLATION_OVERRIDES
    }
    pk_targets = {
        BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        for coordinate in PK_TRANSLATION_OVERRIDES
    }
    base_changed = changed_record_guard(
        predecessor_records=baseline_inputs.base_candidate_records,
        candidate_records=base_candidate_records,
        expected_changed=base_targets,
    )
    pk_changed = changed_record_guard(
        predecessor_records=baseline_inputs.pk_candidate_records,
        candidate_records=pk_candidate_records,
        expected_changed=pk_targets,
    )
    base_target_delta = target_delta_manifest(
        resource="base_msggame",
        target_records=tuple(base_targets),
        source_records=baseline_inputs.base_source_records,
        current_records=base_current_records,
        predecessor_records=baseline_inputs.base_candidate_records,
        candidate_records=base_candidate_records,
    )
    pk_target_delta = target_delta_manifest(
        resource="pk_msggame",
        target_records=tuple(pk_targets),
        source_records=baseline_inputs.pk_source_records,
        current_records=pk_current_records,
        predecessor_records=baseline_inputs.pk_candidate_records,
        candidate_records=pk_candidate_records,
    )
    base_target_delta_sha256 = canonical_sha256(base_target_delta)
    pk_target_delta_sha256 = canonical_sha256(pk_target_delta)
    base_edges = graph_edges(
        base_candidate_records,
        conservative_operand_scan=True,
    )
    pk_profiles, pk_edges = CROSS.RESIDUAL_AUDIT.build_record_profiles(
        inputs=updated_inputs
    )
    for record in pk_targets:
        profile = dict(pk_profiles[record])
        reasons = set(profile["reason_codes"])
        require(
            reasons == {"protected_signature_mismatch"},
            f"PK repaired target profile drifted: {record}/{reasons}",
        )
        profile["reason_codes"] = []
        pk_profiles[record] = profile
    base_affected = reverse_ancestors(
        edges=base_edges,
        targets=tuple(base_targets),
    )
    pk_affected = reverse_ancestors(
        edges=pk_edges,
        targets=tuple(pk_targets),
    )
    base_root_proofs = root_delta_proofs(
        resource="base_msggame",
        affected_records=base_affected,
        edges=base_edges,
        target_records=base_targets,
        predecessor_records=baseline_inputs.base_candidate_records,
        candidate_records=base_candidate_records,
        target_delta_sha256=base_target_delta_sha256,
    )
    pk_root_proofs = root_delta_proofs(
        resource="pk_msggame",
        affected_records=pk_affected,
        edges=pk_edges,
        target_records=pk_targets,
        predecessor_records=baseline_inputs.pk_candidate_records,
        candidate_records=pk_candidate_records,
        target_delta_sha256=pk_target_delta_sha256,
    )

    pk_decisions_by_record, repaired_pk_by_coordinate = repaired_pk_decisions(
        checkpoint_rows
    )
    pending_by_root: defaultdict[
        tuple[int, int],
        list[str],
    ] = defaultdict(list)
    for (resource, coordinate), row in checkpoint_rows.items():
        if (
            resource == "pk_msggame"
            and row.get("runtime_review") == "pending"
        ):
            pending_by_root[
                BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
            ].append(coordinate)
    for coordinates in pending_by_root.values():
        coordinates.sort(key=BASE_AUDIT.parse_literal_coordinate)
    affected_pending_roots = sorted(set(pending_by_root) & pk_affected)
    affected_pending_coordinates = [
        coordinate
        for root in affected_pending_roots
        for coordinate in pending_by_root[root]
    ]
    require(
        len(affected_pending_roots) == EXPECTED_AFFECTED_PENDING_ROOTS
        and len(affected_pending_coordinates) == EXPECTED_AFFECTED_PENDING_ROWS,
        "affected pending honorific universe drifted",
    )

    eligible: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for root in affected_pending_roots:
        guard = CROSS.PK_ONLY.closure_guard(
            root,
            inputs=updated_inputs,
            decisions_by_record=pk_decisions_by_record,
        )
        layout = CROSS.relative_layout_closure_guard(
            root,
            profiles=pk_profiles,
            edges=pk_edges,
        )
        entry = {
            "root": list(root),
            "member_coordinates": pending_by_root[root],
            "member_coordinate_sha256": coordinate_digest(
                pending_by_root[root]
            ),
            "reachable_repaired_targets": [
                list(target)
                for target in reachable_targets(
                    root,
                    edges=pk_edges,
                    target_records=pk_targets,
                )
            ],
            "closure_guard": guard,
            "relative_layout_guard": layout,
            "root_delta_proof_sha256": pk_root_proofs[root][
                "proof_sha256"
            ],
        }
        if (
            CROSS.target_guard_passes(guard)
            and layout.get("status") == "verified"
        ):
            eligible.append(entry)
        else:
            rejected.append(entry)
    eligible_coordinates = [
        coordinate
        for entry in eligible
        for coordinate in entry["member_coordinates"]
    ]
    rejected_coordinates = [
        coordinate
        for entry in rejected
        for coordinate in entry["member_coordinates"]
    ]
    require(
        len(eligible) == EXPECTED_ELIGIBLE_ROOTS
        and len(eligible_coordinates) == EXPECTED_ELIGIBLE_ROWS
        and coordinate_digest(eligible_coordinates)
        == EXPECTED_ELIGIBLE_COORDINATE_SHA256
        and record_digest(tuple(entry["root"]) for entry in eligible)
        == EXPECTED_ELIGIBLE_ROOT_SHA256,
        "eligible honorific closure universe drifted",
    )
    require(
        len(rejected) == EXPECTED_REJECTED_ROOTS
        and len(rejected_coordinates) == EXPECTED_REJECTED_ROWS,
        "rejected honorific closure universe drifted",
    )

    base_renewal_coordinates = [
        coordinate
        for (resource, coordinate), row in checkpoint_rows.items()
        if resource == "base_msggame"
        and row.get("runtime_review") == "verified"
        and BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        in base_affected
    ]
    pk_renewal_coordinates = [
        coordinate
        for (resource, coordinate), row in checkpoint_rows.items()
        if resource == "pk_msggame"
        and row.get("runtime_review") == "verified"
        and BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        in pk_affected
    ]
    base_renewal_coordinates.sort(key=BASE_AUDIT.parse_literal_coordinate)
    pk_renewal_coordinates.sort(key=BASE_AUDIT.parse_literal_coordinate)
    require(
        set(BASE_TRANSLATION_OVERRIDES) <= set(base_renewal_coordinates)
        and set(PK_TRANSLATION_OVERRIDES) <= set(pk_renewal_coordinates),
        "repaired selector rows are absent from renewal universe",
    )
    require(
        len(base_renewal_coordinates) == EXPECTED_BASE_RENEWAL_ROWS
        and len(pk_renewal_coordinates) == EXPECTED_PK_RENEWAL_ROWS
        and coordinate_digest(base_renewal_coordinates)
        == EXPECTED_BASE_RENEWAL_COORDINATE_SHA256
        and coordinate_digest(pk_renewal_coordinates)
        == EXPECTED_PK_RENEWAL_COORDINATE_SHA256,
        "honorific evidence-renewal universe drifted",
    )
    rejection_reason_rows: Counter[str] = Counter()
    rejection_reason_roots: Counter[str] = Counter()
    for entry in rejected:
        reasons = set(entry["closure_guard"]["failure_codes"])
        reasons.update(entry["relative_layout_guard"]["reason_codes"])
        for reason in reasons:
            rejection_reason_roots[reason] += 1
            rejection_reason_rows[reason] += len(entry["member_coordinates"])

    return {
        "context": context,
        "updated_inputs": updated_inputs,
        "checkpoint_rows": checkpoint_rows,
        "repaired_pk_by_coordinate": repaired_pk_by_coordinate,
        "base_candidate_blob": base_blob,
        "pk_candidate_blob": pk_blob,
        "base_candidate_records": base_candidate_records,
        "pk_candidate_records": pk_candidate_records,
        "base_replacement_manifest_sha256": canonical_sha256(
            base_replacement_manifest
        ),
        "pk_replacement_manifest_sha256": canonical_sha256(
            pk_replacement_manifest
        ),
        "base_changed": base_changed,
        "pk_changed": pk_changed,
        "base_targets": base_targets,
        "pk_targets": pk_targets,
        "base_target_delta": base_target_delta,
        "pk_target_delta": pk_target_delta,
        "base_target_delta_sha256": base_target_delta_sha256,
        "pk_target_delta_sha256": pk_target_delta_sha256,
        "base_edges": base_edges,
        "pk_edges": pk_edges,
        "base_affected": base_affected,
        "pk_affected": pk_affected,
        "base_root_proofs": base_root_proofs,
        "pk_root_proofs": pk_root_proofs,
        "base_renewal_coordinates": base_renewal_coordinates,
        "pk_renewal_coordinates": pk_renewal_coordinates,
        "affected_pending_coordinates": affected_pending_coordinates,
        "eligible": eligible,
        "eligible_coordinates": eligible_coordinates,
        "rejected": rejected,
        "rejected_coordinates": rejected_coordinates,
        "rejection_reason_rows": dict(sorted(rejection_reason_rows.items())),
        "rejection_reason_roots": dict(
            sorted(rejection_reason_roots.items())
        ),
    }


def build_audit(
    *,
    analysis: Mapping[str, Any],
    checkpoint_metadata: Mapping[str, Any],
    contract_metadata: Mapping[str, Any],
) -> dict[str, Any]:
    eligible_manifest = [
        {
            "root": entry["root"],
            "member_coordinate_sha256": entry["member_coordinate_sha256"],
            "closure_guard_sha256": entry["closure_guard"]["proof_sha256"],
            "relative_layout_guard_sha256": entry[
                "relative_layout_guard"
            ]["proof_sha256"],
            "root_delta_proof_sha256": entry[
                "root_delta_proof_sha256"
            ],
        }
        for entry in analysis["eligible"]
    ]
    rejected_manifest = [
        {
            "root": entry["root"],
            "member_coordinate_sha256": entry["member_coordinate_sha256"],
            "failure_codes": entry["closure_guard"]["failure_codes"],
            "grammar_risk_keys": entry["closure_guard"][
                "grammar_risk_keys"
            ],
            "layout_reason_codes": entry["relative_layout_guard"][
                "reason_codes"
            ],
            "closure_guard_sha256": entry["closure_guard"]["proof_sha256"],
            "relative_layout_guard_sha256": entry[
                "relative_layout_guard"
            ]["proof_sha256"],
        }
        for entry in analysis["rejected"]
    ]
    report = {
        "schema": AUDIT_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resources": [
            "MSG/JP/msggame.bin",
            "MSG_PK/JP/msggame.bin",
        ],
        "scope": {
            "predecessor_rows": EXPECTED_PREDECESSOR_ROWS,
            "predecessor_pending_rows": EXPECTED_PREDECESSOR_PENDING,
            "translation_override_rows": len(TRANSLATION_OVERRIDES),
            "base_affected_records": len(analysis["base_affected"]),
            "base_verified_renewal_rows": len(
                analysis["base_renewal_coordinates"]
            ),
            "pk_affected_records": len(analysis["pk_affected"]),
            "pk_verified_renewal_rows": len(
                analysis["pk_renewal_coordinates"]
            ),
            "pk_affected_pending_rows": len(
                analysis["affected_pending_coordinates"]
            ),
            "pk_affected_pending_roots":
            EXPECTED_AFFECTED_PENDING_ROOTS,
            "pk_promotion_eligible_rows": EXPECTED_ELIGIBLE_ROWS,
            "pk_promotion_eligible_roots": EXPECTED_ELIGIBLE_ROOTS,
            "pk_rejected_rows": EXPECTED_REJECTED_ROWS,
            "pk_rejected_roots": EXPECTED_REJECTED_ROOTS,
            "post_layer_pending_rows": EXPECTED_PENDING_AFTER,
        },
        "adjudication": {
            "literal_owned_ascii_leading_space": True,
            "automatic_space_inserted": False,
            "historical_honorific_semantics_preserved": True,
            "base_pk_semantic_pairs_kept_equal": True,
            "control_bytes_unchanged": True,
            "current_raw_g1n_width_px": 96,
            "predecessor_raw_g1n_width_px": 48,
            "candidate_raw_g1n_width_px": 72,
            "candidate_current_relative_nonexpanding": True,
            "one_absolute_widget_gate_assumed": False,
            "promotion_requires_full_closure_current_relative_nonexpansion":
            True,
            "pre_layout_theoretical_rows_not_promoted": (
                EXPECTED_AFFECTED_PENDING_ROWS - EXPECTED_ELIGIBLE_ROWS
            ),
        },
        "rejections": {
            "reason_row_counts": analysis["rejection_reason_rows"],
            "reason_root_counts": analysis["rejection_reason_roots"],
            "rejected_manifest_sha256": canonical_sha256(
                rejected_manifest
            ),
        },
        "guards": {
            "checkpoint_private_sha256": checkpoint_metadata[
                "private_sha256"
            ],
            "checkpoint_report_file_sha256": checkpoint_metadata[
                "report_file_sha256"
            ],
            "checkpoint_report_payload_sha256": checkpoint_metadata[
                "report_payload_sha256"
            ],
            "checkpoint_builder_sha256": checkpoint_metadata[
                "builder_sha256"
            ],
            "ghidra_vm_contract_file_sha256": contract_metadata[
                "vm_file_sha256"
            ],
            "ghidra_layout_contract_file_sha256": contract_metadata[
                "layout_file_sha256"
            ],
            "base_candidate_packed_sha256": sha256_bytes(
                analysis["base_candidate_blob"]
            ),
            "pk_candidate_packed_sha256": sha256_bytes(
                analysis["pk_candidate_blob"]
            ),
            "base_replacement_manifest_sha256": analysis[
                "base_replacement_manifest_sha256"
            ],
            "pk_replacement_manifest_sha256": analysis[
                "pk_replacement_manifest_sha256"
            ],
            "translation_override_coordinate_sha256": sha256_bytes(
                "".join(
                    f"{resource}:{coordinate}\n"
                    for resource, coordinate in sorted(
                        TRANSLATION_OVERRIDES,
                        key=coordinate_sort_key,
                    )
                ).encode("ascii")
            ),
            "base_changed_record_sha256": analysis["base_changed"][
                "changed_record_universe_sha256"
            ],
            "pk_changed_record_sha256": analysis["pk_changed"][
                "changed_record_universe_sha256"
            ],
            "base_target_delta_manifest_sha256": analysis[
                "base_target_delta_sha256"
            ],
            "pk_target_delta_manifest_sha256": analysis[
                "pk_target_delta_sha256"
            ],
            "base_affected_record_sha256": record_digest(
                analysis["base_affected"]
            ),
            "pk_affected_record_sha256": record_digest(
                analysis["pk_affected"]
            ),
            "base_renewal_coordinate_sha256": coordinate_digest(
                analysis["base_renewal_coordinates"]
            ),
            "pk_renewal_coordinate_sha256": coordinate_digest(
                analysis["pk_renewal_coordinates"]
            ),
            "eligible_coordinate_sha256": coordinate_digest(
                analysis["eligible_coordinates"]
            ),
            "eligible_root_sha256": record_digest(
                tuple(entry["root"]) for entry in analysis["eligible"]
            ),
            "eligible_proof_manifest_sha256": canonical_sha256(
                eligible_manifest
            ),
            "base_root_delta_proof_sha256": canonical_sha256(
                {
                    f"{root[0]}:{root[1]}": proof
                    for root, proof in sorted(
                        analysis["base_root_proofs"].items()
                    )
                }
            ),
            "pk_root_delta_proof_sha256": canonical_sha256(
                {
                    f"{root[0]}:{root[1]}": proof
                    for root, proof in sorted(
                        analysis["pk_root_proofs"].items()
                    )
                }
            ),
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "private_decisions_stay_below_tmp": True,
            "private_overlays_contain_translation_bodies": False,
        },
        "steam_write_performed": False,
    }
    return seal_report(report)


def evidence_row(
    *,
    resource: str,
    coordinate: str,
    action: str,
    predecessor: Mapping[str, Any],
    updated_translation: str,
    updated_layout: str,
    root_proof: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    root_entry: Mapping[str, Any] | None,
) -> dict[str, Any]:
    method = BASE_METHOD if resource == "base_msggame" else PK_METHOD
    schema = (
        BASE_OVERLAY_ROW_SCHEMA
        if resource == "base_msggame"
        else PK_OVERLAY_ROW_SCHEMA
    )
    evidence: dict[str, Any] = {
        "schema": schema,
        "resource": resource,
        "coordinate": coordinate,
        "status": "verified",
        "method": method,
        "action": action,
        "scope_transition": {
            "from": predecessor["scope_classification"],
            "to": (
                "retranslated"
                if action == "runtime_promotion"
                else predecessor["scope_classification"]
            ),
        },
        "layout_transition": {
            "from": predecessor["layout_review"],
            "to": updated_layout,
        },
        "translation_utf16le_sha256": ENGINE.sha256_text(
            updated_translation
        ),
        "predecessor_integrated_binding": {
            "row_sha256": canonical_sha256(predecessor),
            "private_integrated_decision_sha256": audit["guards"][
                "checkpoint_private_sha256"
            ],
            "source_free_report_file_sha256": audit["guards"][
                "checkpoint_report_file_sha256"
            ],
            "integrated_builder_sha256": audit["guards"][
                "checkpoint_builder_sha256"
            ],
            "previous_runtime_vm_verification_sha256": (
                canonical_sha256(predecessor["runtime_vm_verification"])
                if isinstance(
                    predecessor.get("runtime_vm_verification"),
                    dict,
                )
                else None
            ),
        },
        "honorific_spacing_delta_binding": {
            "root": root_proof["root"],
            "reachable_repaired_targets": root_proof[
                "reachable_repaired_targets"
            ],
            "root_delta_proof_sha256": root_proof["proof_sha256"],
            "target_delta_manifest_sha256": (
                audit["guards"]["base_target_delta_manifest_sha256"]
                if resource == "base_msggame"
                else audit["guards"]["pk_target_delta_manifest_sha256"]
            ),
            "candidate_packed_sha256": (
                audit["guards"]["base_candidate_packed_sha256"]
                if resource == "base_msggame"
                else audit["guards"]["pk_candidate_packed_sha256"]
            ),
            "ghidra_vm_contract_file_sha256": audit["guards"][
                "ghidra_vm_contract_file_sha256"
            ],
            "ghidra_layout_contract_file_sha256": audit["guards"][
                "ghidra_layout_contract_file_sha256"
            ],
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256": audit["guards"][
                "report_payload_sha256"
            ],
        },
        "per_row_game_playback_required": False,
    }
    if root_entry is not None:
        evidence["pk_promoted_root_binding"] = {
            "root_member_pending_coordinate_sha256": root_entry[
                "member_coordinate_sha256"
            ],
            "closure_guard_sha256": root_entry["closure_guard"][
                "proof_sha256"
            ],
            "source_current_control_equal": root_entry["closure_guard"][
                "source_current_control_equal"
            ],
            "source_final_control_equal": root_entry["closure_guard"][
                "source_final_control_equal"
            ],
            "current_final_control_equal": root_entry["closure_guard"][
                "current_final_control_equal"
            ],
            "hard_grammar_risk_absent": root_entry["closure_guard"][
                "hard_grammar_risk_absent"
            ],
            "relative_layout_guard_sha256": root_entry[
                "relative_layout_guard"
            ]["proof_sha256"],
            "relative_full_closure_line_envelope_nonexpanding": root_entry[
                "relative_layout_guard"
            ]["relative_full_closure_line_envelope_nonexpanding"],
        }
    return evidence


def build_updated_rows(
    *,
    analysis: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    checkpoint_rows = analysis["checkpoint_rows"]
    eligible_by_key = {
        ("pk_msggame", coordinate): entry
        for entry in analysis["eligible"]
        for coordinate in entry["member_coordinates"]
    }
    base_coordinates = set(analysis["base_renewal_coordinates"])
    pk_coordinates = set(analysis["pk_renewal_coordinates"]) | set(
        analysis["eligible_coordinates"]
    )
    updated_rows: list[dict[str, Any]] = []
    base_evidence_rows: list[dict[str, Any]] = []
    pk_evidence_rows: list[dict[str, Any]] = []
    for resource, coordinates in (
        ("base_msggame", base_coordinates),
        ("pk_msggame", pk_coordinates),
    ):
        root_proofs = (
            analysis["base_root_proofs"]
            if resource == "base_msggame"
            else analysis["pk_root_proofs"]
        )
        for coordinate in sorted(
            coordinates,
            key=BASE_AUDIT.parse_literal_coordinate,
        ):
            key = (resource, coordinate)
            predecessor = checkpoint_rows[key]
            root = BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
            translation_override = TRANSLATION_OVERRIDES.get(key)
            if translation_override is not None:
                action = "translation_override"
                translation = translation_override
            elif key in eligible_by_key:
                action = "runtime_promotion"
                translation = str(predecessor["translation"])
            else:
                action = "verification_renewal"
                translation = str(predecessor["translation"])
            updated = copy.deepcopy(dict(predecessor))
            updated["translation"] = translation
            if action == "runtime_promotion":
                require(
                    predecessor.get("runtime_review") == "pending"
                    and predecessor.get("scope_classification")
                    == "runtime_fragment_pending",
                    f"promotion predecessor drifted: {key}",
                )
                updated["scope_classification"] = "retranslated"
                updated["runtime_review"] = "verified"
                updated["layout_review"] = "runtime_verified"
            else:
                require(
                    predecessor.get("runtime_review") == "verified",
                    f"renewal predecessor is not verified: {key}",
                )
            if translation_override is not None:
                predecessor_spacing = predecessor.get(
                    "honorific_spacing_evidence"
                )
                require(
                    isinstance(predecessor_spacing, dict)
                    and predecessor_spacing.get("automatic_space_inserted")
                    is False,
                    f"honorific spacing evidence drifted: {key}",
                )
                updated_spacing = copy.deepcopy(predecessor_spacing)
                updated_spacing.update(
                    {
                        "semantic_candidate": translation,
                        "caller_rewrite_required": False,
                        "boundary_space_literal_owned": True,
                        "all_speaker_branches_grammatical": True,
                        "review": (
                            "dynamic name-title boundary repaired by one "
                            "literal-owned ASCII space"
                        ),
                    }
                )
                updated["honorific_spacing_evidence"] = updated_spacing
                updated["runtime_boundary_leading_space_inserted"] = True
            root_entry = eligible_by_key.get(key)
            evidence = evidence_row(
                resource=resource,
                coordinate=coordinate,
                action=action,
                predecessor=predecessor,
                updated_translation=translation,
                updated_layout=str(updated["layout_review"]),
                root_proof=root_proofs[root],
                audit=audit,
                audit_file_sha256=audit_file_sha256,
                root_entry=root_entry,
            )
            updated["runtime_vm_verification"] = evidence
            updated_rows.append(updated)
            if resource == "base_msggame":
                base_evidence_rows.append(evidence)
            else:
                pk_evidence_rows.append(evidence)
    updated_rows.sort(key=row_sort_key)
    base_evidence_rows.sort(
        key=lambda row: BASE_AUDIT.parse_literal_coordinate(
            row["coordinate"]
        )
    )
    pk_evidence_rows.sort(
        key=lambda row: BASE_AUDIT.parse_literal_coordinate(
            row["coordinate"]
        )
    )
    return updated_rows, base_evidence_rows, pk_evidence_rows


def build_overlay_report(
    *,
    schema: str,
    resource: str,
    method: str,
    evidence_rows: Sequence[Mapping[str, Any]],
    private_content: str,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    promotion_rows: int,
) -> dict[str, Any]:
    action_counts = Counter(str(row["action"]) for row in evidence_rows)
    report = {
        "schema": schema,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": resource,
        "method": method,
        "result": {
            "private_overlay_rows": len(evidence_rows),
            "private_overlay_sha256": sha256_bytes(
                private_content.encode("utf-8")
            ),
            "translation_override_rows": action_counts[
                "translation_override"
            ],
            "verification_renewal_rows": action_counts[
                "verification_renewal"
            ],
            "runtime_promotion_rows": action_counts["runtime_promotion"],
            "pending_rows_after": EXPECTED_PENDING_AFTER,
            "translation_body_copied_to_overlay": False,
        },
        "evidence": {
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256": audit["guards"][
                "report_payload_sha256"
            ],
            "checkpoint_private_sha256": audit["guards"][
                "checkpoint_private_sha256"
            ],
            "promotion_rows": promotion_rows,
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "private_overlay_contains_translation_bodies": False,
            "private_overlay_stays_below_tmp": True,
        },
        "steam_write_performed": False,
        "guards": {},
    }
    return seal_report(report)


def build_outputs() -> tuple[
    str,
    str,
    str,
    str,
    str,
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    steam_before = {
        "base": live_hash(LIVE_STEAM_BASE),
        "pk": live_hash(LIVE_STEAM_PK),
    }
    contract_metadata = verify_contracts()
    checkpoint_rows, checkpoint_metadata = load_checkpoint()
    analysis = build_analysis(checkpoint_rows=checkpoint_rows)
    audit = build_audit(
        analysis=analysis,
        checkpoint_metadata=checkpoint_metadata,
        contract_metadata=contract_metadata,
    )
    validate_seal(audit)
    audit_content = canonical_json(audit)
    audit_file_sha256 = sha256_bytes(audit_content.encode("utf-8"))
    (
        updated_rows,
        base_evidence_rows,
        pk_evidence_rows,
    ) = build_updated_rows(
        analysis=analysis,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
    )
    decision_content = canonical_jsonl(updated_rows)
    base_overlay_content = canonical_jsonl(base_evidence_rows)
    pk_overlay_content = canonical_jsonl(pk_evidence_rows)
    base_report = build_overlay_report(
        schema=BASE_REPORT_SCHEMA,
        resource="base_msggame",
        method=BASE_METHOD,
        evidence_rows=base_evidence_rows,
        private_content=base_overlay_content,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        promotion_rows=0,
    )
    pk_report = build_overlay_report(
        schema=PK_REPORT_SCHEMA,
        resource="pk_msggame",
        method=PK_METHOD,
        evidence_rows=pk_evidence_rows,
        private_content=pk_overlay_content,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        promotion_rows=EXPECTED_ELIGIBLE_ROWS,
    )
    validate_seal(base_report)
    validate_seal(pk_report)
    base_report_content = canonical_json(base_report)
    pk_report_content = canonical_json(pk_report)
    steam_after = {
        "base": live_hash(LIVE_STEAM_BASE),
        "pk": live_hash(LIVE_STEAM_PK),
    }
    require(
        steam_before == steam_after,
        "live Steam msggame changed during honorific analysis",
    )
    return (
        decision_content,
        base_overlay_content,
        pk_overlay_content,
        audit_content,
        base_report_content,
        pk_report_content,
        audit,
        {
            "updated_rows": updated_rows,
            "base_evidence_rows": base_evidence_rows,
            "pk_evidence_rows": pk_evidence_rows,
            "base_report": base_report,
            "pk_report": pk_report,
            "analysis": analysis,
        },
    )


def validate_outputs(
    *,
    decision_content: str,
    base_overlay_content: str,
    pk_overlay_content: str,
    audit_content: str,
    base_report_content: str,
    pk_report_content: str,
    audit: Mapping[str, Any],
    bundle: Mapping[str, Any],
) -> None:
    require(
        audit_content == canonical_json(audit),
        "audit serialization drifted",
    )
    validate_seal(audit)
    updated_rows = bundle["updated_rows"]
    base_evidence_rows = bundle["base_evidence_rows"]
    pk_evidence_rows = bundle["pk_evidence_rows"]
    require(
        decision_content == canonical_jsonl(updated_rows)
        and base_overlay_content == canonical_jsonl(base_evidence_rows)
        and pk_overlay_content == canonical_jsonl(pk_evidence_rows),
        "private honorific output serialization drifted",
    )
    require(
        base_report_content == canonical_json(bundle["base_report"])
        and pk_report_content == canonical_json(bundle["pk_report"]),
        "honorific promotion report serialization drifted",
    )
    validate_seal(bundle["base_report"])
    validate_seal(bundle["pk_report"])
    updated_by_key = {
        (str(row["resource"]), str(row["coordinate"])): row
        for row in updated_rows
    }
    require(
        len(updated_by_key) == len(updated_rows),
        "duplicate updated honorific decision",
    )
    promotion_count = sum(
        row["runtime_vm_verification"]["action"] == "runtime_promotion"
        for row in updated_rows
    )
    override_keys = {
        key
        for key, row in updated_by_key.items()
        if row.get("runtime_boundary_leading_space_inserted") is True
    }
    require(
        promotion_count == EXPECTED_ELIGIBLE_ROWS
        and override_keys == set(TRANSLATION_OVERRIDES)
        and audit["scope"]["post_layer_pending_rows"]
        == EXPECTED_PENDING_AFTER
        and audit.get("steam_write_performed") is False,
        "honorific result count/override contract drifted",
    )
    for row in base_evidence_rows + pk_evidence_rows:
        require(
            "translation" not in row
            and row.get("per_row_game_playback_required") is False,
            "private evidence overlay copied a translation body",
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=DEFAULT_AUDIT_OUTPUT,
    )
    parser.add_argument(
        "--base-report-output",
        type=Path,
        default=DEFAULT_BASE_REPORT_OUTPUT,
    )
    parser.add_argument(
        "--pk-report-output",
        type=Path,
        default=DEFAULT_PK_REPORT_OUTPUT,
    )
    parser.add_argument(
        "--decision-output",
        type=Path,
        default=DEFAULT_DECISION_OUTPUT,
    )
    parser.add_argument(
        "--base-overlay-output",
        type=Path,
        default=DEFAULT_BASE_OVERLAY_OUTPUT,
    )
    parser.add_argument(
        "--pk-overlay-output",
        type=Path,
        default=DEFAULT_PK_OVERLAY_OUTPUT,
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser


def validate_output_paths(args: argparse.Namespace) -> None:
    private_root = DIALOGUE_TMP.resolve(strict=False)
    public_root = (WORKSTREAM / "public").resolve(strict=False)
    private_paths = (
        args.decision_output,
        args.base_overlay_output,
        args.pk_overlay_output,
    )
    public_paths = (
        args.audit_output,
        args.base_report_output,
        args.pk_report_output,
    )
    resolved_paths: list[Path] = []
    for path in private_paths:
        resolved = path.resolve(strict=False)
        require(
            resolved != private_root and private_root in resolved.parents,
            f"private output must remain below {private_root}: {path}",
        )
        resolved_paths.append(resolved)
    for path in public_paths:
        resolved = path.resolve(strict=False)
        require(
            resolved != public_root and public_root in resolved.parents,
            f"public output must remain below {public_root}: {path}",
        )
        resolved_paths.append(resolved)
    require(
        len(set(resolved_paths)) == len(resolved_paths),
        "honorific output paths must be distinct",
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")
    validate_output_paths(args)
    (
        decision_content,
        base_overlay_content,
        pk_overlay_content,
        audit_content,
        base_report_content,
        pk_report_content,
        audit,
        bundle,
    ) = build_outputs()
    validate_outputs(
        decision_content=decision_content,
        base_overlay_content=base_overlay_content,
        pk_overlay_content=pk_overlay_content,
        audit_content=audit_content,
        base_report_content=base_report_content,
        pk_report_content=pk_report_content,
        audit=audit,
        bundle=bundle,
    )
    outputs = {
        args.decision_output: decision_content,
        args.base_overlay_output: base_overlay_content,
        args.pk_overlay_output: pk_overlay_content,
        args.audit_output: audit_content,
        args.base_report_output: base_report_content,
        args.pk_report_output: pk_report_content,
    }
    if args.write:
        for path, content in outputs.items():
            ENGINE.atomic_write(path, content)
    if args.check:
        for path, content in outputs.items():
            require(
                path.is_file()
                and path.read_text(encoding="utf-8") == content,
                f"generated honorific output drifted: {path}",
            )
    print(
        "PASS "
        f"overrides={len(TRANSLATION_OVERRIDES)} "
        f"promoted={EXPECTED_ELIGIBLE_ROWS} "
        f"pending={EXPECTED_PENDING_AFTER} "
        f"base_renewed={len(bundle['base_evidence_rows'])} "
        f"pk_renewed={len(bundle['pk_evidence_rows'])} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        ValueError,
        HonorificSpacingError,
        CROSS.CrossResourceClosureError,
        CROSS.PK_ONLY.PkOnlyClosureError,
        CROSS.FULL_AUDIT.FullCandidateAuditError,
        CROSS.BASE_AUDIT.AuditError,
        ENGINE.RetranslationError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
