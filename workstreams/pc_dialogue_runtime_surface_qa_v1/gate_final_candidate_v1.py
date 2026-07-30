#!/usr/bin/env python3
"""Gate Base/PK final candidates on user-visible runtime surface defects.

This wrapper intentionally emits a source-free release artifact.  It binds the
surface audit result to both candidate binaries and exposes
``runtime_completion = PASS`` only when the combined issue count is zero.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
sys.path.insert(0, str(WORKSTREAM))

import audit_runtime_surface_v1 as AUDIT  # noqa: E402
import audit_candidate_relative_width_v1 as STAGE_WIDTH  # noqa: E402
import audit_empirical_block_width_policy_v1 as WIDTH  # noqa: E402
import audit_candidate_structure_v1 as STRUCTURE  # noqa: E402
import terminal_boundary_detector_v1 as TERMINAL  # noqa: E402
import audit_call_assembly_boundaries_v1 as CALL_ASSEMBLY  # noqa: E402


SCHEMA = "nobu16.kr.pc-dialogue-runtime-surface-final-candidate-gate.v1"
SELECTOR_DOMAIN_CONTRACT = (
    WORKSTREAM / "ghidra_selector_domain_contract.v1.json"
)
RESOURCE_PATHS = {
    "base_msggame": "MSG/JP/msggame.bin",
    "pk_msggame": "MSG_PK/JP/msggame.bin",
}
BASE_CALL_REMEDIATION_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_runtime_surface_remediation_v1"
    / "base_call_assembly_remediation_v1.py"
)
BASE_PRE_CALL = WIDTH.DEFAULT_PRE_CALL
BASE_CALL_CANDIDATE = WIDTH.DEFAULT_CALL


class FinalCandidateGateError(ValueError):
    """Raised when the two-resource release gate cannot be evaluated."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FinalCandidateGateError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def load_selector_domain_contract() -> dict[str, Any]:
    require(
        SELECTOR_DOMAIN_CONTRACT.is_file(),
        "Ghidra selector-domain contract is absent",
    )
    document = json.loads(
        SELECTOR_DOMAIN_CONTRACT.read_text(encoding="utf-8")
    )
    require(
        document.get("schema")
        == "nobu16.kr.pc-dialogue-ghidra-selector-domain-contract.v1",
        "Ghidra selector-domain contract schema drifted",
    )
    adjudication = document.get("adjudication", {})
    expected = {
        "fixed_particle_is_allowed_only_for_property_32": True,
        "all_other_selector_particle_boundaries_remain_blocked": True,
        "automatic_particle_resolution_is_absent": True,
        "automatic_space_insertion_is_absent": True,
        "literal_and_selector_utf16_units_are_copied_verbatim": True,
        "opcode_0143_calls_another_record": True,
    }
    require(
        all(adjudication.get(key) is value for key, value in expected.items()),
        "Ghidra runtime-assembly adjudication drifted",
    )
    live_session = document.get("live_session", {})
    require(
        live_session.get("transport") == "GhidraMCP HTTP bridge"
        and live_session.get("open_program_verified") is True
        and live_session.get("program_is_current") is True
        and live_session.get("forced_decompile_refreshed") is True,
        "Ghidra live-session verification drifted",
    )
    fresh_checks = document.get("fresh_decompile_checks", {})
    assembler = fresh_checks.get("runtime_assembler_0x140A013B0", {})
    castle = fresh_checks.get("castle_slot_handler_0x1409FDA70", {})
    require(
        assembler.get("opcode_0x02_copies_resolved_utf16_units") is True
        and assembler.get("opcode_0x1B_copies_selector_utf16_units") is True
        and assembler.get("injected_separator_or_particle_branch_observed")
        is False
        and assembler.get(
            "selector_only_terminal_leaf_assumed_zero_output"
        ) is False
        and castle.get("property_0x32_calls_0x1405F3C20") is True,
        "Ghidra fresh decompile verification drifted",
    )
    selector_leaf_model = document.get("selector_leaf_model", {})
    require(
        selector_leaf_model.get("jump_condition_selectors_emit_text")
        is False
        and selector_leaf_model.get(
            "output_selectors_are_rendered_as_nonempty_sentinels"
        ) is True
        and selector_leaf_model.get(
            "literal_or_decompiled_function_body_included"
        ) is False,
        "Ghidra selector-leaf model drifted",
    )
    return document


def source_free_issue(value: AUDIT.Issue) -> dict[str, Any]:
    payload = asdict(value)
    payload.pop("text", None)
    return payload


def load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    require(
        specification is not None
        and specification.loader is not None,
        f"cannot import {path}",
    )
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def build_stage_width_report(base_final: Path) -> dict[str, Any]:
    stages = {
        "surface_remediation": STAGE_WIDTH.audit_pair(
            "base_msggame",
            STAGE_WIDTH.DEFAULT_BASE_SOURCE,
            BASE_PRE_CALL,
        ),
        "post_call_selector_spacing": STAGE_WIDTH.audit_pair(
            "base_msggame",
            BASE_CALL_CANDIDATE,
            base_final,
        ),
    }
    issue_count = sum(
        int(stage["issue_count"]) for stage in stages.values()
    )
    return {
        "schema": "nobu16.kr.base-remediation-stage-relative-width.v1",
        "status": "PASS" if issue_count == 0 else "FAIL",
        "issue_count": issue_count,
        "stages": stages,
        "call_semantic_rebuild_excluded_from_plus_24_gate": True,
        "steam_write_performed": False,
    }


def build_call_semantic_contract() -> dict[str, Any]:
    module = load_module(
        "final_gate_base_call_assembly_remediation_v1",
        BASE_CALL_REMEDIATION_PATH,
    )
    candidate, report = module.build(BASE_PRE_CALL.read_bytes())
    materialized_sha256 = sha256_bytes(
        BASE_CALL_CANDIDATE.read_bytes()
    )
    require(
        sha256_bytes(candidate) == materialized_sha256,
        "materialized Base call-semantic candidate drifted",
    )
    return report


def build_gate_from_audits(
    audits: Sequence[AUDIT.ResourceAudit],
    terminal_resources: Sequence[TERMINAL.TerminalBoundaryResource],
    call_assembly_resources: Sequence[
        CALL_ASSEMBLY.CallAssemblyResource
    ],
    *,
    sizes: Mapping[str, int],
    structure_report: Mapping[str, Any],
    relative_width_report: Mapping[str, Any],
    stage_width_report: Mapping[str, Any],
    call_semantic_report: Mapping[str, Any],
) -> dict[str, Any]:
    by_resource = {audit.resource: audit for audit in audits}
    terminal_by_resource = {
        resource.resource: resource for resource in terminal_resources
    }
    call_assembly_by_resource = {
        resource.resource: resource
        for resource in call_assembly_resources
    }
    require(
        set(by_resource) == set(RESOURCE_PATHS),
        "gate requires exactly Base and PK msggame audits",
    )
    require(
        set(sizes) == set(RESOURCE_PATHS),
        "gate requires exact Base and PK candidate sizes",
    )
    require(
        set(terminal_by_resource) == set(RESOURCE_PATHS),
        "gate requires exact Base and PK terminal-boundary audits",
    )
    require(
        set(call_assembly_by_resource) == set(RESOURCE_PATHS),
        "gate requires exact Base and PK call-assembly audits",
    )
    for resource in RESOURCE_PATHS:
        require(
            by_resource[resource].sha256
            == terminal_by_resource[resource].sha256,
            f"surface/terminal candidate hash mismatch: {resource}",
        )
        require(
            by_resource[resource].sha256
            == call_assembly_by_resource[resource].sha256,
            f"surface/call-assembly candidate hash mismatch: {resource}",
        )
    require(
        structure_report.get("schema") == STRUCTURE.SCHEMA,
        "candidate structure schema mismatch",
    )
    require(
        relative_width_report.get("schema") == WIDTH.SCHEMA,
        "candidate empirical block-width schema mismatch",
    )
    require(
        stage_width_report.get("schema")
        == "nobu16.kr.base-remediation-stage-relative-width.v1",
        "Base remediation stage-width schema mismatch",
    )
    require(
        call_semantic_report.get("schema")
        == "nobu16.kr.base-call-assembly-remediation.v1",
        "Base call-semantic contract schema mismatch",
    )
    structure_resources = structure_report.get("resources", {})
    width_resources = relative_width_report.get("resources", {})
    pk_retarget_contract = structure_report.get(
        "pk_reviewed_retarget_contract",
        {},
    )
    require(
        set(structure_resources) == set(RESOURCE_PATHS.values()),
        "candidate structure report requires exact Base/PK resources",
    )
    require(
        set(width_resources) == set(RESOURCE_PATHS.values()),
        "candidate relative-width report requires exact Base/PK resources",
    )
    for resource, relative_path in RESOURCE_PATHS.items():
        expected_sha256 = by_resource[resource].sha256
        require(
            structure_resources[relative_path]["candidate"]["sha256"]
            == expected_sha256,
            f"surface/structure candidate hash mismatch: {resource}",
        )
        require(
            width_resources[relative_path]["candidate"]["sha256"]
            == expected_sha256,
            f"surface/empirical-width candidate hash mismatch: {resource}",
        )
    require(
        int(
            structure_resources["MSG/JP/msggame.bin"].get(
                "allowed_mutation_count",
                -1,
            )
        )
        == STRUCTURE.EXPECTED_BASE_CALL_ALLOWLIST_COUNT,
        "Base reviewed structure mutation count drifted",
    )
    require(
        int(
            structure_resources["MSG_PK/JP/msggame.bin"].get(
                "allowed_mutation_count",
                -1,
            )
        )
        == STRUCTURE.EXPECTED_PK_REVIEWED_MUTATION_COUNT,
        "PK reviewed structure mutation count drifted",
    )
    require(
        pk_retarget_contract.get("source_sha256")
        == STRUCTURE.EXPECTED_PK_SOURCE_SHA256
        and pk_retarget_contract.get("candidate_sha256")
        == by_resource["pk_msggame"].sha256
        and int(pk_retarget_contract.get("operation_count", -1))
        == STRUCTURE.EXPECTED_PK_REVIEWED_OPERATION_COUNT
        and pk_retarget_contract.get("operation_sha256")
        == STRUCTURE.EXPECTED_PK_REVIEWED_OPERATION_SHA256
        and int(
            pk_retarget_contract.get("component_mutation_count", -1)
        )
        == STRUCTURE.EXPECTED_PK_REVIEWED_MUTATION_COUNT
        and pk_retarget_contract.get("component_contract_sha256")
        == STRUCTURE.EXPECTED_PK_REVIEWED_COMPONENT_SHA256
        and pk_retarget_contract.get(
            "exact_coordinate_component_before_after_hash_bound"
        )
        is True
        and pk_retarget_contract.get("literal_bodies_omitted") is True,
        "PK reviewed control-retarget contract drifted",
    )
    literal_hash_contract = call_semantic_report.get(
        "literal_before_after_hash_contract",
        {},
    )
    require(
        call_semantic_report.get("status") == "PASS"
        and int(call_semantic_report.get("final_issue_count", -1)) == 0,
        "Base call-semantic rebuild is not PASS",
    )
    require(
        int(literal_hash_contract.get("entry_count", -1))
        == int(call_semantic_report.get("literal_replacement_count", -2))
        and len(literal_hash_contract.get("entries", []))
        == int(literal_hash_contract.get("entry_count", -1))
        and literal_hash_contract.get(
            "source_or_translation_bodies_omitted"
        ) is True,
        "Base call-semantic before/after hash contract is incomplete",
    )
    require(
        stage_width_report.get(
            "call_semantic_rebuild_excluded_from_plus_24_gate"
        ) is True,
        "Base stage-width report does not isolate semantic call rebuild",
    )

    category_counts = Counter(
        issue.category
        for audit in audits
        for issue in audit.issues
    )
    category_counts.update(
        issue.category
        for resource in terminal_resources
        for issue in resource.issues
    )
    category_counts.update(
        issue.category
        for resource in call_assembly_resources
        for issue in resource.issues
    )
    for issue in structure_report.get("resources", {}).values():
        category_counts.update(
            {
                f"structure:{category}": count
                for category, count
                in issue.get("category_counts", {}).items()
            }
        )
    for issue in relative_width_report.get("resources", {}).values():
        category_counts.update(
            {
                f"empirical_width:{category}": count
                for category, count
                in issue.get("category_counts", {}).items()
            }
        )
    for stage in stage_width_report.get("stages", {}).values():
        category_counts.update(
            {
                f"stage_width:{category}": count
                for category, count
                in stage.get("category_counts", {}).items()
            }
        )
    issue_count = sum(category_counts.values())
    passed = (
        issue_count == 0
        and structure_report.get("status") == "PASS"
        and int(structure_report.get("issue_count", -1)) == 0
        and relative_width_report.get("status") == "PASS"
        and int(relative_width_report.get("issue_count", -1)) == 0
        and stage_width_report.get("status") == "PASS"
        and int(stage_width_report.get("issue_count", -1)) == 0
        and call_semantic_report.get("status") == "PASS"
    )
    resources: dict[str, Any] = {}
    for resource, relative_path in RESOURCE_PATHS.items():
        audit = by_resource[resource]
        terminal_resource = terminal_by_resource[resource]
        call_assembly_resource = call_assembly_by_resource[resource]
        structure_resource = structure_resources[relative_path]
        width_resource = width_resources[relative_path]
        resource_categories = Counter(
            issue.category for issue in audit.issues
        )
        resource_categories.update(
            issue.category for issue in terminal_resource.issues
        )
        resource_categories.update(
            issue.category for issue in call_assembly_resource.issues
        )
        resource_categories.update(
            {
                f"structure:{category}": count
                for category, count
                in structure_resource.get("category_counts", {}).items()
            }
        )
        resource_categories.update(
            {
                f"empirical_width:{category}": count
                for category, count
                in width_resource.get("category_counts", {}).items()
            }
        )
        resources[relative_path] = {
            "resource": resource,
            "size": int(sizes[resource]),
            "sha256": audit.sha256,
            "record_count": audit.record_count,
            "literal_count": audit.literal_count,
            "decoded_record_count": audit.decoded_record_count,
            "issue_count": (
                len(audit.issues)
                + len(terminal_resource.issues)
                + len(call_assembly_resource.issues)
                + int(structure_resource["issue_count"])
                + int(width_resource["issue_count"])
            ),
            "surface_issue_count": len(audit.issues),
            "terminal_boundary_issue_count": len(
                terminal_resource.issues
            ),
            "call_assembly_issue_count": len(
                call_assembly_resource.issues
            ),
            "call_assembly_call_site_count":
                call_assembly_resource.call_site_count,
            "call_assembly_cartesian_variant_count":
                call_assembly_resource.assembled_record_variant_count,
            "structure_issue_count":
                int(structure_resource["issue_count"]),
            "empirical_width_issue_count":
                int(width_resource["issue_count"]),
            "literal_changed_count":
                int(structure_resource["literal_changed_count"]),
            "allowed_structure_mutation_count":
                int(structure_resource["allowed_mutation_count"]),
            "empirical_width_issue_coordinate_count":
                int(width_resource["issue_coordinate_count"]),
            "terminal_call_site_count": (
                terminal_resource.call_site_count
            ),
            "terminal_suffix_variant_count": (
                terminal_resource.terminal_suffix_variant_count
            ),
            "category_counts": dict(sorted(resource_categories.items())),
        }

    return {
        "schema": SCHEMA,
        "status": "PASS" if passed else "FAIL",
        "release_target": "0.15.0",
        "runtime_completion": "PASS" if passed else "FAIL",
        "runtime_completion_allowed": passed,
        "issue_count": issue_count,
        "category_counts": dict(sorted(category_counts.items())),
        "resources": resources,
        "issues": [
            source_free_issue(issue)
            for audit in audits
            for issue in audit.issues
        ] + [
            TERMINAL.source_free_issue(issue)
            for resource in terminal_resources
            for issue in resource.issues
        ] + [
            CALL_ASSEMBLY.source_free_issue(issue)
            for resource in call_assembly_resources
            for issue in resource.issues
        ] + [
            {
                "resource": relative_path,
                **issue,
            }
            for relative_path, resource
            in structure_resources.items()
            for issue in resource.get("issues", [])
        ] + [
            {
                "resource": relative_path,
                **issue,
            }
            for relative_path, resource
            in width_resources.items()
            for issue in resource.get("issues", [])
        ] + [
            {
                "resource": "MSG/JP/msggame.bin",
                "stage": stage_name,
                **issue,
            }
            for stage_name, stage
            in stage_width_report.get("stages", {}).items()
            for issue in stage.get("issues", [])
        ],
        "audit_contract": {
            "schema": AUDIT.SCHEMA,
            "engine_sha256": sha256_bytes(
                (WORKSTREAM / "audit_runtime_surface_v1.py").read_bytes()
            ),
            "selector_domain_contract": {
                "schema": (
                    "nobu16.kr.pc-dialogue-ghidra-selector-domain-contract.v1"
                ),
                "sha256": sha256_bytes(
                    SELECTOR_DOMAIN_CONTRACT.read_bytes()
                ),
            },
            "terminal_boundary_detector": {
                "schema": TERMINAL.SCHEMA,
                "engine_sha256": sha256_bytes(
                    (
                        WORKSTREAM
                        / "terminal_boundary_detector_v1.py"
                    ).read_bytes()
                ),
                "completed_prefix_before_terminal_suffix_forbidden": True,
            },
            "call_assembly_audit": {
                "schema": CALL_ASSEMBLY.SCHEMA,
                "engine_sha256": sha256_bytes(
                    (
                        WORKSTREAM
                        / "audit_call_assembly_boundaries_v1.py"
                    ).read_bytes()
                ),
                "report_status": (
                    "PASS"
                    if all(
                        not resource.issues
                        for resource in call_assembly_resources
                    )
                    else "FAIL"
                ),
                "report_issue_count": sum(
                    len(resource.issues)
                    for resource in call_assembly_resources
                ),
                "all_call_sites_enumerated": True,
                "all_call_bearing_records_cartesian_rendered": True,
                "output_selectors_use_nonempty_sentinel": True,
            },
            "candidate_structure": {
                "schema": STRUCTURE.SCHEMA,
                "engine_sha256": sha256_bytes(
                    (
                        WORKSTREAM
                        / "audit_candidate_structure_v1.py"
                    ).read_bytes()
                ),
                "report_status":
                    str(structure_report.get("status")),
                "report_issue_count":
                    int(structure_report.get("issue_count", -1)),
                "only_reviewed_pk_call_retargets_allowed": True,
                "base_reviewed_component_mutation_count":
                    STRUCTURE.EXPECTED_BASE_CALL_ALLOWLIST_COUNT,
                "pk_reviewed_operation_count":
                    int(pk_retarget_contract["operation_count"]),
                "pk_reviewed_operation_sha256":
                    str(pk_retarget_contract["operation_sha256"]),
                "pk_reviewed_component_mutation_count":
                    int(pk_retarget_contract["component_mutation_count"]),
                "pk_reviewed_component_contract_sha256":
                    str(
                        pk_retarget_contract[
                            "component_contract_sha256"
                        ]
                    ),
                "pk_exact_coordinate_component_before_after_hash_bound":
                    True,
            },
            "candidate_empirical_block_width": {
                "schema": WIDTH.SCHEMA,
                "engine_sha256": sha256_bytes(
                    (
                        WORKSTREAM
                        / "audit_empirical_block_width_policy_v1.py"
                    ).read_bytes()
                ),
                "report_status":
                    str(relative_width_report.get("status")),
                "report_issue_count":
                    int(relative_width_report.get("issue_count", -1)),
                "event_dialogue_912px_gate_applied": False,
                "final_global_plus_24px_gate_applied": False,
                "candidate_line_must_fit_predecessor_same_block_max":
                    True,
                "candidate_line_count_must_fit_predecessor_same_block_max":
                    True,
                "base_and_pk_required": True,
            },
            "base_stage_relative_width": {
                "schema":
                    "nobu16.kr.base-remediation-stage-relative-width.v1",
                "engine_sha256": sha256_bytes(
                    (
                        WORKSTREAM
                        / "audit_candidate_relative_width_v1.py"
                    ).read_bytes()
                ),
                "report_status": str(stage_width_report.get("status")),
                "report_issue_count":
                    int(stage_width_report.get("issue_count", -1)),
                "surface_and_post_call_maximum_line_growth_px":
                    STAGE_WIDTH.MAX_LINE_DELTA_PX,
                "call_semantic_rebuild_excluded_from_plus_24_gate":
                    True,
            },
            "base_call_semantic_rebuild": {
                "schema":
                    "nobu16.kr.base-call-assembly-remediation.v1",
                "engine_sha256": sha256_bytes(
                    BASE_CALL_REMEDIATION_PATH.read_bytes()
                ),
                "report_status":
                    str(call_semantic_report.get("status")),
                "report_issue_count":
                    int(call_semantic_report.get("final_issue_count", -1)),
                "source_sha256":
                    str(call_semantic_report.get("source_sha256")),
                "candidate_sha256":
                    str(call_semantic_report.get("candidate_sha256")),
                "literal_replacement_count": int(
                    call_semantic_report.get(
                        "literal_replacement_count",
                        -1,
                    )
                ),
                "literal_before_after_hash_contract": {
                    "entry_count":
                        int(literal_hash_contract["entry_count"]),
                    "entry_sha256":
                        str(literal_hash_contract["entry_sha256"]),
                    "source_or_translation_bodies_omitted": True,
                },
            },
            "base_and_pk_required": True,
            "issue_count_must_be_zero": True,
            "binary_hash_binding_required": True,
            "ghidra_contract": {
                "literal_and_dynamic_output_are_verbatim": True,
                "automatic_space_inserted": False,
                "automatic_punctuation_inserted": False,
                "opcode_0143_calls_record": True,
            },
        },
        "source_or_translation_bodies_omitted": True,
        "steam_write_performed": False,
    }


def build_gate(
    base_path: Path,
    pk_path: Path,
) -> dict[str, Any]:
    load_selector_domain_contract()
    audits = (
        AUDIT.audit_resource("base_msggame", base_path),
        AUDIT.audit_resource("pk_msggame", pk_path),
    )
    terminal_resources = (
        TERMINAL.detect_resource("base_msggame", base_path),
        TERMINAL.detect_resource("pk_msggame", pk_path),
    )
    call_assembly_resources = (
        CALL_ASSEMBLY.audit_resource("base_msggame", base_path),
        CALL_ASSEMBLY.audit_resource("pk_msggame", pk_path),
    )
    structure_report = STRUCTURE.build_report(
        STRUCTURE.DEFAULT_BASE_SOURCE,
        base_path,
        STRUCTURE.DEFAULT_PK_SOURCE,
        pk_path,
    )
    relative_width_report = WIDTH.build_final_report(
        WIDTH.DEFAULT_SOURCE,
        base_path,
        WIDTH.DEFAULT_PK_SOURCE,
        pk_path,
    )
    stage_width_report = build_stage_width_report(base_path)
    call_semantic_report = build_call_semantic_contract()
    return build_gate_from_audits(
        audits,
        terminal_resources,
        call_assembly_resources,
        sizes={
            "base_msggame": base_path.stat().st_size,
            "pk_msggame": pk_path.stat().st_size,
        },
        structure_report=structure_report,
        relative_width_report=relative_width_report,
        stage_width_report=stage_width_report,
        call_semantic_report=call_semantic_report,
    )


def canonical_json(value: Any) -> str:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=AUDIT.DEFAULT_BASE)
    parser.add_argument("--pk", type=Path, default=AUDIT.DEFAULT_PK)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_gate(args.base, args.pk)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(canonical_json(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "schema": payload["schema"],
                "status": payload["status"],
                "runtime_completion": payload["runtime_completion"],
                "issue_count": payload["issue_count"],
                "resources": {
                    relative_path: {
                        "size": resource["size"],
                        "sha256": resource["sha256"],
                        "issue_count": resource["issue_count"],
                    }
                    for relative_path, resource
                    in payload["resources"].items()
                },
                "output": (
                    str(args.output.resolve())
                    if args.output is not None
                    else None
                ),
            },
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    return 0 if payload["runtime_completion_allowed"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, AUDIT.SurfaceAuditError, FinalCandidateGateError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
