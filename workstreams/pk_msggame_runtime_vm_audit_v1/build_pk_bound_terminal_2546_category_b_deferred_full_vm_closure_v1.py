#!/usr/bin/env python3
"""Close the deferred PK 2546 category-B roots with full VM evidence.

The builder composes the immutable BF7B checkpoint, the independently closed
category-B immediate layer, and the frozen dependency-inclusive private map.
It proves source/candidate incoming and outgoing VM closure equality, renews
only the exact verified dependencies whose translations change, and promotes
the remaining pending rows. Translation-bearing decisions stay below ``tmp``;
tracked coverage and promotion reports are source-free. No shared integration,
progress, engine, or Steam write path exists here.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"

IMMEDIATE_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_bound_terminal_2546_category_b_immediate_closure_v1.py"
)
GHIDRA_VM_CONTRACT_PATH = WORKSTREAM / "ghidra_pk_vm_contract.v1.json"
IMMEDIATE_AUDIT_PATH = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_2546_category_b_immediate_closure_coverage.v1.json"
)
IMMEDIATE_PROMOTION_PATH = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_2546_category_b_immediate_closure_promotion.v1.json"
)
IMMEDIATE_DECISION_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / (
        "pk_bound_terminal_2546_category_b_immediate_closure_"
        "integrated_decisions.private.v1.jsonl"
    )
)
IMMEDIATE_EVIDENCE_PATH = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / (
        "pk_bound_terminal_2546_category_b_immediate_closure_"
        "evidence.private.v1.jsonl"
    )
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / (
        "pk_bound_terminal_2546_category_b_deferred_"
        "full_vm_closure_coverage.v1.json"
    )
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / (
        "pk_bound_terminal_2546_category_b_deferred_"
        "full_vm_closure_promotion.v1.json"
    )
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / (
        "pk_bound_terminal_2546_category_b_deferred_full_vm_closure_"
        "integrated_decisions.private.v1.jsonl"
    )
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / (
        "pk_bound_terminal_2546_category_b_deferred_full_vm_closure_"
        "evidence.private.v1.jsonl"
    )
)

AUDIT_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-category-b-"
    "deferred-full-vm-closure-coverage.v1"
)
PROMOTION_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-category-b-"
    "deferred-full-vm-closure-promotion.v1"
)
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-category-b-"
    "deferred-full-vm-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-category-b-"
    "deferred-full-vm-exact-override.v1"
)
METHOD = (
    "reversed_vm_pk_bound_terminal_2546_"
    "category_b_deferred_dependency_inclusive_full_closure"
)
UPDATE_ACTION_FIELD = (
    "bound_terminal_2546_category_b_deferred_full_vm_update_action"
)
OVERRIDE_FIELD = (
    "bound_terminal_2546_category_b_deferred_full_vm_"
    "exact_override_evidence"
)

EXPECTED_GHIDRA_VM_CONTRACT_SHA256 = (
    "21DAF83330F278484BFB2462188804947A6C457F4B072DA80D7ADFBD3D13F461"
)
EXPECTED_GHIDRA_CONTRACT_SUBSET_SHA256 = (
    "8283DD8C86121CCF16D6DC5A9131BA769F579BCB14E724C39FA38135275EE5FF"
)
EXPECTED_IMMEDIATE_AUDIT_SHA256 = (
    "19E869B8D1DF6B0896F39E79ECC0397F8C8B2B7CF3D28BB2547AC7587D72AAAD"
)
EXPECTED_IMMEDIATE_PROMOTION_SHA256 = (
    "92CEF30654AF571D21F56DDA3A3796E728578A64EEDFF2426572E8060E750610"
)
EXPECTED_IMMEDIATE_DECISION_SHA256 = (
    "8A44196B7EB20267FAC4ADD6953350257FCB9C5DA92406241B23F0B70133FABA"
)
EXPECTED_IMMEDIATE_EVIDENCE_SHA256 = (
    "9741F68BB504CEFF3750F56A4AD4D296E249B3656AFD6EB9F5D131F53A32509B"
)
EXPECTED_IMMEDIATE_CANDIDATE_SHA256 = (
    "2AE326439AC0A503104A245774FA4D2CA3B833E05AAE7E8E40F5CFCF7F5B31E2"
)
EXPECTED_FULL_CANDIDATE_SHA256 = (
    "1E57A600BE7EC64F2D923816121D16E2444B460527291347322ADCEE48110053"
)

EXPECTED_ROWS = 52_803
EXPECTED_PENDING_BEFORE = 8_201
EXPECTED_PENDING_AFTER = 8_196
EXPECTED_ROOTS = 2
EXPECTED_PROMOTION_ROWS = 5
EXPECTED_RENEWAL_ROWS = 2
EXPECTED_DECISION_ROWS = 7
EXPECTED_OVERRIDE_ROWS = 6
EXPECTED_KEEP_ROWS = 1
EXPECTED_ASSEMBLIES = 14
EXPECTED_ROOT_SHA256 = (
    "0C6D9BC26056B32ED99DBADEA8CB5637FE67C8BD3C0A94C2B90846F1F744D5C4"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "A17010484F8BEFD7CD337CC678E585B43BC0305766C566D1544197B503CB5A28"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "A7E739AEF436B94F5DE6A2BE2FE2BC2C434B9DEB7EA807B33C4D9D3D69A8A15B"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "FC939D8F82428C9455C5FB2609F8C047FEADB3C893812BAE7590A3BDD4B2997B"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "B8FBAE25CF0AE1872ADC7F72AD4B9E86907832884BA76CC3EB3FAF18CDD4CBCA"
)
EXPECTED_KEEP_COORDINATE_SHA256 = (
    "9A38C5F3AE7EEDE6EA265F9A6BF1073065D43BE8B02C2E721116BDB6F5FAD611"
)
EXPECTED_OVERRIDE_MAP_SHA256 = (
    "7F341F8267CF38DDA282227A1A2A8838E0C63674BA67B8F45352C5F5D2BD7D6E"
)
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 1,
    "translation_override_and_runtime_promotion": 4,
    "translation_override_and_verification_renewal": 2,
}
EXPECTED_ACTION_COORDINATE_SHA256 = {
    "runtime_promotion": EXPECTED_KEEP_COORDINATE_SHA256,
    "translation_override_and_runtime_promotion":
    "237B9D051F481F3EF909BE2C5FABEC565304837E26B382E6B1E8454F02F567B8",
    "translation_override_and_verification_renewal":
    EXPECTED_RENEWAL_COORDINATE_SHA256,
}
EXPECTED_ASSEMBLY_MANIFEST_SHA256 = (
    "CE69192BC0E9B6CDA44DCC2EB7C3359AB87F4630563723A1CFD62E54D90C5A48"
)
EXPECTED_COMPONENT_MANIFEST_SHA256 = (
    "62CD1D2B15FF6BD88C76DCB50EF9DA70E9FF7BEC28D92D54246CB98A46692B55"
)
EXPECTED_PROPOSAL_DECISION_MANIFEST_SHA256 = (
    "ABC05EC1888F98A770F3FB8BE6BB8C604887A86C2132994863C7521AD7FC36F4"
)
EXPECTED_PREDECESSOR_MANIFEST_SHA256 = (
    "BA7996C84732493B8262ED872D8AAEF0DD22F84100E185947EE9040ADF00B123"
)
EXPECTED_PREDECESSOR_RENEWAL_EVIDENCE_SHA256 = (
    "AF943B1A4C1DFB3FD769021E97650415D8B4D6705600932C8A0392F3D806885F"
)
EXPECTED_UNCHANGED_PREVERIFIED_MANIFEST_SHA256 = (
    "3C4EFB9352B2B150CF831E821B4BCC8B2B96AC24133F23776604BB77BA844A48"
)
EXPECTED_TERMINAL_COORDINATE_SHA256 = (
    "DD975EDD56BA114A8BB46274BF5B141E18A3A28C0153A769F586059E6C9F810A"
)
EXPECTED_CALL_SITE_SHA256 = (
    "45388803EED78CEC4A505F77C44B04F8544B3CCC5E9EE642E5F761288D7FA13E"
)
EXPECTED_INCOMING_RECORDS = 3
EXPECTED_INCOMING_RECORD_SHA256 = (
    "9BE16CF36D9AFC3490AB7D8AA46AF6E7AD07C030E1E20EECFC4B73CE18399AFB"
)
EXPECTED_INCOMING_EDGE_MANIFEST_SHA256 = (
    "6A051F984B9E32216835365D36266D6C482B86ABCBFFF4762D9A87600B036E1F"
)
EXPECTED_OUTGOING_RECORDS = 28
EXPECTED_OUTGOING_RECORD_SHA256 = (
    "F7934704534DFDFEFD90906B5670EF01F02D982C421CB3F7958C24E8738073B7"
)
EXPECTED_OUTGOING_EDGE_MANIFEST_SHA256 = (
    "864502319EACAF85738131985EEDEF371695D1F85EC452D8C0363DAB59DAE064"
)
EXPECTED_SOURCE_EDGE_COUNT = 20_060
EXPECTED_INTERMEDIATE_EDGE_COUNT = 19_552
EXPECTED_CANDIDATE_EDGE_COUNT = 19_552

# Frozen after the first independent --write reproduction.
EXPECTED_AUDIT_OUTPUT_SHA256: str | None = (
    "6DF07C5897901C6807AF02FAFFDF45B2433423162D2FBE5CD1D0BEF0B3593C17"
)
EXPECTED_PROMOTION_OUTPUT_SHA256: str | None = (
    "7488765148CF320B66D28F5820DD3321629A7962F54A3AF5D528CB79CF48757F"
)
EXPECTED_DECISION_OUTPUT_SHA256 = (
    "54343C398C7D8E22A957AE47CA9B8AA5C11DD7F64C6BEF4EFF50DFA4EF466095"
)
EXPECTED_EVIDENCE_OUTPUT_SHA256 = (
    "C328430233A81E4457BD253844D65622B7305AEB20FACB30E011C2EEF7B58BD0"
)


class ClosureError(ValueError):
    """Raised when the deferred full-VM closure contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ClosureError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(
        spec is not None and spec.loader is not None,
        f"cannot import {path}",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


IMMEDIATE = load_module(
    IMMEDIATE_BUILDER_PATH,
    "pk_bound_terminal_2546_category_b_deferred_immediate_helpers_v1",
)
PROPOSAL = IMMEDIATE.PROPOSAL
BASE_AUDIT = IMMEDIATE.BASE_AUDIT
CALLER = IMMEDIATE.FAMILY.CALLER
CROSS = IMMEDIATE.FAMILY.CROSS
ENGINE = IMMEDIATE.ENGINE
HONORIFIC = IMMEDIATE.HONORIFIC
LIVE_STEAM_BASE = IMMEDIATE.LIVE_STEAM_BASE
LIVE_STEAM_PK = IMMEDIATE.LIVE_STEAM_PK


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    )


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(canonical_json(row) for row in rows)


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def parse_coordinate(value: str) -> tuple[int, int, int]:
    return IMMEDIATE.parse_coordinate(value)


def coordinate_digest(values: Iterable[str]) -> str:
    return IMMEDIATE.coordinate_digest(values)


def record_digest(values: Iterable[tuple[int, int]]) -> str:
    return IMMEDIATE.record_digest(values)


def row_sort_key(row: Mapping[str, Any]) -> tuple[int, int, int, int]:
    return IMMEDIATE.row_sort_key(row)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def root_string(root: tuple[int, int]) -> str:
    return f"{root[0]}:{root[1]}"


def site_root(site: str) -> tuple[int, int]:
    parts = site.split(":")
    require(len(parts) == 4, f"invalid call site: {site}")
    return int(parts[0]), int(parts[1])


def exact_map_sha256(values: Mapping[str, str]) -> str:
    return sha256_bytes(
        json.dumps(
            values,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def load_ghidra_contract() -> tuple[dict[str, Any], dict[str, Any]]:
    require(
        sha256_file(GHIDRA_VM_CONTRACT_PATH)
        == EXPECTED_GHIDRA_VM_CONTRACT_SHA256,
        "Ghidra VM contract file drifted",
    )
    contract = json.loads(
        GHIDRA_VM_CONTRACT_PATH.read_text(encoding="utf-8")
    )
    functions = contract["functions"]
    selected_names = (
        "execute_record_vm",
        "dispatch_opcode",
        "select_record",
        "resolve_expression",
        "resolve_selector",
        "handle_return_or_block",
        "pop_record_return",
    )
    subset = {
        "program": contract["program"],
        "functions": {name: functions[name] for name in selected_names},
        "select_record_contract": contract["select_record_contract"],
        "literal_contract": contract["literal_contract"],
        "opcode_contract": {
            key: contract["opcode_contract"][key]
            for key in ("0143", "014A", "02", "05_block_tokens")
        },
    }
    require(
        canonical_sha256(subset)
        == EXPECTED_GHIDRA_CONTRACT_SUBSET_SHA256
        and subset["opcode_contract"]["0143"]["semantics"]
        == "push_return_address_then_call_record"
        and subset["opcode_contract"]["014A"]["semantics"]
        == "jump_to_record"
        and subset["opcode_contract"]["02"]["automatic_space_inserted"]
        is False
        and subset["opcode_contract"]["02"][
            "automatic_punctuation_inserted"
        ]
        is False
        and subset["select_record_contract"]["packed_coordinate_formula"]
        == "block_id = operand // 10000; record_id = operand % 10000",
        "Ghidra VM behavioral subset drifted",
    )
    observation = {
        "program_sha256": contract["program"]["unpacked_exe_sha256"],
        "contract_file_sha256": EXPECTED_GHIDRA_VM_CONTRACT_SHA256,
        "contract_subset_sha256": EXPECTED_GHIDRA_CONTRACT_SUBSET_SHA256,
        "function_count": len(selected_names),
        "live_mcp_redecompile_completed": True,
        "call_pushes_return_offset_and_current_block": True,
        "return_pops_block_then_instruction_offset": True,
        "packed_record_selection_verified": True,
        "dynamic_output_is_verbatim": True,
        "automatic_spacing_or_punctuation": False,
        "structured_block_token_decoder_required": True,
    }
    return contract, observation


def load_inputs() -> dict[str, Any]:
    expected_files = {
        IMMEDIATE_AUDIT_PATH: EXPECTED_IMMEDIATE_AUDIT_SHA256,
        IMMEDIATE_PROMOTION_PATH: EXPECTED_IMMEDIATE_PROMOTION_SHA256,
        IMMEDIATE_DECISION_PATH: EXPECTED_IMMEDIATE_DECISION_SHA256,
        IMMEDIATE_EVIDENCE_PATH: EXPECTED_IMMEDIATE_EVIDENCE_SHA256,
    }
    require(
        all(sha256_file(path) == expected for path, expected in expected_files.items()),
        "immediate closure artifact digest drifted",
    )
    (
        immediate_decision_content,
        immediate_evidence_content,
        immediate_audit_content,
        immediate_promotion_content,
        immediate_audit,
        immediate_bundle,
    ) = IMMEDIATE.build_outputs()
    IMMEDIATE.validate_outputs(
        decision_content=immediate_decision_content,
        evidence_content=immediate_evidence_content,
        audit_content=immediate_audit_content,
        promotion_content=immediate_promotion_content,
        audit=immediate_audit,
        bundle=immediate_bundle,
    )
    require(
        immediate_audit_content
        == IMMEDIATE_AUDIT_PATH.read_text(encoding="ascii")
        and immediate_promotion_content
        == IMMEDIATE_PROMOTION_PATH.read_text(encoding="ascii")
        and immediate_decision_content
        == IMMEDIATE_DECISION_PATH.read_text(encoding="utf-8")
        and immediate_evidence_content
        == IMMEDIATE_EVIDENCE_PATH.read_text(encoding="utf-8"),
        "immediate closure deterministic rebuild drifted",
    )
    predecessor_rows = immediate_bundle["predecessor_rows"]
    proposal_handoff = immediate_bundle["proposal_handoff"]
    proposal_bundle = immediate_bundle["proposal_bundle"]
    immediate_rows = load_jsonl(IMMEDIATE_DECISION_PATH)
    intermediate_rows = {
        key: copy.deepcopy(dict(row))
        for key, row in predecessor_rows.items()
    }
    for row in immediate_rows:
        key = (str(row["resource"]), str(row["coordinate"]))
        require(key in intermediate_rows, f"unknown immediate row: {key}")
        intermediate_rows[key] = row
    require(
        len(intermediate_rows) == EXPECTED_ROWS
        and sum(
            row.get("runtime_review") == "pending"
            for row in intermediate_rows.values()
        )
        == EXPECTED_PENDING_BEFORE
        and IMMEDIATE.rebuild_merged_candidate(intermediate_rows)
        == EXPECTED_IMMEDIATE_CANDIDATE_SHA256,
        "logical immediate predecessor reconstruction drifted",
    )
    return {
        "predecessor_rows": predecessor_rows,
        "intermediate_rows": intermediate_rows,
        "proposal_handoff": proposal_handoff,
        "proposal_bundle": proposal_bundle,
        "immediate_audit": immediate_audit,
    }


def build_partition(inputs: Mapping[str, Any]) -> dict[str, Any]:
    handoff = inputs["proposal_handoff"]
    bundle = inputs["proposal_bundle"]
    promotion = set(handoff["deferred_pending"])
    renewal = set(handoff["dependencies"])
    roots = set(handoff["deferred_roots"])
    pending_override = set(handoff["deferred_override"])
    overrides = {
        coordinate: handoff["exact_map"][coordinate]
        for coordinate in pending_override | renewal
    }
    keep = set(handoff["deferred_keep"])
    decisions = promotion | renewal
    actions = {
        "runtime_promotion": keep,
        "translation_override_and_runtime_promotion": pending_override,
        "translation_override_and_verification_renewal": renewal,
    }
    require(
        len(roots) == EXPECTED_ROOTS
        and record_digest(roots) == EXPECTED_ROOT_SHA256
        and len(promotion) == EXPECTED_PROMOTION_ROWS
        and coordinate_digest(promotion)
        == EXPECTED_PROMOTION_COORDINATE_SHA256
        and len(renewal) == EXPECTED_RENEWAL_ROWS
        and coordinate_digest(renewal)
        == EXPECTED_RENEWAL_COORDINATE_SHA256
        and len(decisions) == EXPECTED_DECISION_ROWS
        and coordinate_digest(decisions)
        == EXPECTED_DECISION_COORDINATE_SHA256
        and len(overrides) == EXPECTED_OVERRIDE_ROWS
        and coordinate_digest(overrides)
        == EXPECTED_OVERRIDE_COORDINATE_SHA256
        and exact_map_sha256(overrides) == EXPECTED_OVERRIDE_MAP_SHA256
        and len(keep) == EXPECTED_KEEP_ROWS
        and coordinate_digest(keep) == EXPECTED_KEEP_COORDINATE_SHA256
        and pending_override | keep == promotion
        and not (pending_override & keep)
        and not (promotion & renewal),
        "deferred promotion/renewal partition drifted",
    )
    require(
        {name: len(values) for name, values in actions.items()}
        == EXPECTED_ACTION_COUNTS
        and all(
            coordinate_digest(values)
            == EXPECTED_ACTION_COORDINATE_SHA256[name]
            for name, values in actions.items()
        ),
        "deferred action partition drifted",
    )
    component_manifest = [
        row
        for row in bundle["component_manifest"]
        if PROPOSAL.parse_root(str(row["root"])) in roots
    ]
    decision_manifest = [
        row
        for row in bundle["decision_manifest"]
        if str(row["coordinate"]) in decisions
    ]
    assemblies = bundle["deferred_full_manifest"]
    deltas = [
        delta
        for row in assemblies
        for delta in row["width_delta_px"]
    ]
    require(
        len(assemblies) == EXPECTED_ASSEMBLIES
        and all(row["nonexpanding"] for row in assemblies)
        and all(row["line_topology_equal"] for row in assemblies)
        and canonical_sha256(assemblies)
        == EXPECTED_ASSEMBLY_MANIFEST_SHA256
        and canonical_sha256(component_manifest)
        == EXPECTED_COMPONENT_MANIFEST_SHA256
        and canonical_sha256(decision_manifest)
        == EXPECTED_PROPOSAL_DECISION_MANIFEST_SHA256
        and min(deltas) == -264
        and max(deltas) == -72,
        "dependency-inclusive assembly/control proof drifted",
    )
    return {
        "promotion": promotion,
        "renewal": renewal,
        "roots": roots,
        "pending_override": pending_override,
        "overrides": overrides,
        "keep": keep,
        "decisions": decisions,
        "actions": actions,
        "component_manifest": component_manifest,
        "decision_manifest": decision_manifest,
        "assemblies": assemblies,
        "width_deltas": deltas,
    }


def predecessor_manifests(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    partition: Mapping[str, Any],
    proposal_bundle: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    manifest: list[dict[str, Any]] = []
    renewal_manifest: list[dict[str, Any]] = []
    for coordinate in sorted(
        partition["decisions"],
        key=parse_coordinate,
    ):
        row = predecessor_rows[("pk_msggame", coordinate)]
        expected_status = (
            "pending"
            if coordinate in partition["promotion"]
            else "verified"
        )
        require(
            row.get("runtime_review") == expected_status,
            f"predecessor status drifted: {coordinate}",
        )
        manifest.append(
            {
                "coordinate": coordinate,
                "status": expected_status,
                "row_sha256": canonical_sha256(row),
                "translation_utf16le_sha256": ENGINE.sha256_text(
                    str(row["translation"])
                ),
            }
        )
        if coordinate in partition["renewal"]:
            prior = row.get("runtime_vm_verification")
            require(
                isinstance(prior, Mapping)
                and prior.get("status") == "verified"
                and prior.get("action") == "verification_renewal",
                f"verified dependency evidence drifted: {coordinate}",
            )
            renewal_manifest.append(
                {
                    "coordinate": coordinate,
                    "row_sha256": canonical_sha256(row),
                    "runtime_vm_verification_sha256":
                    canonical_sha256(prior),
                    "predecessor_action": prior["action"],
                    "predecessor_status": row["runtime_review"],
                    "predecessor_translation_utf16le_sha256":
                    ENGINE.sha256_text(str(row["translation"])),
                }
            )
    unchanged_preverified = (
        set(proposal_bundle["preverified"]) - partition["renewal"]
    )
    require(
        len(unchanged_preverified) == 1,
        "unchanged preverified universe drifted",
    )
    unchanged_manifest: list[dict[str, Any]] = []
    for coordinate in sorted(unchanged_preverified, key=parse_coordinate):
        row = predecessor_rows[("pk_msggame", coordinate)]
        unchanged_manifest.append(
            {
                "coordinate": coordinate,
                "row_sha256": canonical_sha256(row),
                "runtime_vm_verification_sha256": canonical_sha256(
                    row["runtime_vm_verification"]
                ),
                "translation_utf16le_sha256": ENGINE.sha256_text(
                    str(row["translation"])
                ),
            }
        )
    require(
        canonical_sha256(manifest)
        == EXPECTED_PREDECESSOR_MANIFEST_SHA256
        and canonical_sha256(renewal_manifest)
        == EXPECTED_PREDECESSOR_RENEWAL_EVIDENCE_SHA256
        and canonical_sha256(unchanged_manifest)
        == EXPECTED_UNCHANGED_PREVERIFIED_MANIFEST_SHA256,
        "predecessor evidence manifest drifted",
    )
    return manifest, renewal_manifest, unchanged_manifest


def descendants(
    edges: Mapping[tuple[int, int], Sequence[tuple[int, int]]],
    roots: Iterable[tuple[int, int]],
) -> set[tuple[int, int]]:
    result = set(roots)
    queue = list(result)
    while queue:
        root = queue.pop()
        for target in edges.get(root, ()):
            if target not in result:
                result.add(target)
                queue.append(target)
    return result


def edge_manifest(
    edges: Mapping[tuple[int, int], Sequence[tuple[int, int]]],
    nodes: Iterable[tuple[int, int]],
    *,
    restrict_targets: bool,
) -> list[list[Any]]:
    node_set = set(nodes)
    return [
        [
            root_string(root),
            [
                root_string(target)
                for target in edges.get(root, ())
                if not restrict_targets or target in node_set
            ],
        ]
        for root in sorted(node_set)
    ]


def build_graph_proof(
    *,
    partition: Mapping[str, Any],
    proposal_bundle: Mapping[str, Any],
) -> dict[str, Any]:
    candidates = proposal_bundle["candidates"]
    source_records = BASE_AUDIT.archive_records(
        BASE_AUDIT.DEFAULT_PK_PRISTINE
    )[0]
    intermediate_records = candidates["immediate_records"]
    candidate_records = candidates["full_records"]
    graphs = {
        "source": HONORIFIC.graph_edges(
            source_records,
            conservative_operand_scan=True,
        ),
        "intermediate": HONORIFIC.graph_edges(
            intermediate_records,
            conservative_operand_scan=True,
        ),
        "candidate": HONORIFIC.graph_edges(
            candidate_records,
            conservative_operand_scan=True,
        ),
    }
    expected_edge_counts = {
        "source": EXPECTED_SOURCE_EDGE_COUNT,
        "intermediate": EXPECTED_INTERMEDIATE_EDGE_COUNT,
        "candidate": EXPECTED_CANDIDATE_EDGE_COUNT,
    }
    incoming_sets: dict[str, set[tuple[int, int]]] = {}
    outgoing_sets: dict[str, set[tuple[int, int]]] = {}
    incoming_manifests: dict[str, list[list[Any]]] = {}
    outgoing_manifests: dict[str, list[list[Any]]] = {}
    for name, edges in graphs.items():
        require(
            sum(len(targets) for targets in edges.values())
            == expected_edge_counts[name],
            f"{name} graph edge count drifted",
        )
        incoming = HONORIFIC.reverse_ancestors(
            edges=edges,
            targets=tuple(partition["roots"]),
        )
        outgoing = descendants(edges, partition["roots"])
        incoming_sets[name] = incoming
        outgoing_sets[name] = outgoing
        incoming_manifests[name] = edge_manifest(
            edges,
            incoming,
            restrict_targets=True,
        )
        outgoing_manifests[name] = edge_manifest(
            edges,
            outgoing,
            restrict_targets=False,
        )
        require(
            len(incoming) == EXPECTED_INCOMING_RECORDS
            and record_digest(incoming)
            == EXPECTED_INCOMING_RECORD_SHA256
            and canonical_sha256(incoming_manifests[name])
            == EXPECTED_INCOMING_EDGE_MANIFEST_SHA256
            and len(outgoing) == EXPECTED_OUTGOING_RECORDS
            and record_digest(outgoing)
            == EXPECTED_OUTGOING_RECORD_SHA256
            and canonical_sha256(outgoing_manifests[name])
            == EXPECTED_OUTGOING_EDGE_MANIFEST_SHA256,
            f"{name} incoming/outgoing closure drifted",
        )
    require(
        incoming_sets["source"]
        == incoming_sets["intermediate"]
        == incoming_sets["candidate"]
        and outgoing_sets["source"]
        == outgoing_sets["intermediate"]
        == outgoing_sets["candidate"],
        "source/intermediate/candidate closure universe differs",
    )
    sites = {
        name: {
            site
            for site in CALLER.call_sites(records, PROPOSAL.SELECTOR)
            if site_root(site) in partition["roots"]
        }
        for name, records in {
            "source": source_records,
            "intermediate": intermediate_records,
            "candidate": candidate_records,
        }.items()
    }
    require(
        sites["source"] == sites["intermediate"] == sites["candidate"]
        and len(sites["candidate"]) == EXPECTED_ROOTS
        and canonical_sha256(sorted(sites["candidate"]))
        == EXPECTED_CALL_SITE_SHA256,
        "selector caller-site topology drifted",
    )
    terminals = {
        (0, record_id) for record_id in PROPOSAL.TERMINAL_RECORD_IDS
    }
    require(
        terminals <= outgoing_sets["candidate"]
        and coordinate_digest(
            f"{block}:{record}:0" for block, record in terminals
        )
        == EXPECTED_TERMINAL_COORDINATE_SHA256,
        "selector terminal closure drifted",
    )
    return {
        "source_edge_count": expected_edge_counts["source"],
        "intermediate_edge_count": expected_edge_counts["intermediate"],
        "candidate_edge_count": expected_edge_counts["candidate"],
        "incoming_records": EXPECTED_INCOMING_RECORDS,
        "incoming_record_sha256": EXPECTED_INCOMING_RECORD_SHA256,
        "incoming_edge_manifest_sha256":
        EXPECTED_INCOMING_EDGE_MANIFEST_SHA256,
        "outgoing_records": EXPECTED_OUTGOING_RECORDS,
        "outgoing_record_sha256": EXPECTED_OUTGOING_RECORD_SHA256,
        "outgoing_edge_manifest_sha256":
        EXPECTED_OUTGOING_EDGE_MANIFEST_SHA256,
        "selector_call_sites": EXPECTED_ROOTS,
        "selector_call_site_sha256": EXPECTED_CALL_SITE_SHA256,
        "terminal_records": len(terminals),
        "terminal_coordinate_sha256":
        EXPECTED_TERMINAL_COORDINATE_SHA256,
        "source_intermediate_candidate_incoming_equal": True,
        "source_intermediate_candidate_outgoing_equal": True,
    }


def build_audit(
    *,
    inputs: Mapping[str, Any],
    partition: Mapping[str, Any],
    graph_proof: Mapping[str, Any],
    ghidra_observation: Mapping[str, Any],
    predecessor_manifest: Sequence[Mapping[str, Any]],
    renewal_manifest: Sequence[Mapping[str, Any]],
    unchanged_manifest: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    audit = {
        "schema": AUDIT_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "method": METHOD,
        "scope": {
            "selector": PROPOSAL.SELECTOR,
            "terminal_records": len(PROPOSAL.TERMINAL_RECORD_IDS),
            "root_count": EXPECTED_ROOTS,
            "predecessor_rows": EXPECTED_ROWS,
            "predecessor_pending_rows": EXPECTED_PENDING_BEFORE,
            "runtime_promotion_rows": EXPECTED_PROMOTION_ROWS,
            "verification_renewal_rows": EXPECTED_RENEWAL_ROWS,
            "exact_override_rows": EXPECTED_OVERRIDE_ROWS,
            "translation_keep_rows": EXPECTED_KEEP_ROWS,
            "decision_delta_rows": EXPECTED_DECISION_ROWS,
            "post_layer_pending_rows": EXPECTED_PENDING_AFTER,
        },
        "action_counts": dict(sorted(EXPECTED_ACTION_COUNTS.items())),
        "proof": {
            "dependency_inclusive_candidate_rebuilt": True,
            "register_assemblies_recomputed": EXPECTED_ASSEMBLIES,
            "register_assembly_pass": EXPECTED_ASSEMBLIES,
            "register_assembly_fail": 0,
            "minimum_width_delta_px": min(partition["width_deltas"]),
            "maximum_width_delta_px": max(partition["width_deltas"]),
            "all_register_assemblies_current_relative_raw_g1n_"
            "nonexpanding": True,
            "source_candidate_reverse_ancestor_closure_equal": True,
            "source_candidate_outgoing_closure_equal": True,
            "verified_dependency_rows_rewritten_and_renewed":
            EXPECTED_RENEWAL_ROWS,
            "unchanged_preverified_rows_not_renewed":
            len(unchanged_manifest),
            "control_components_preserved": True,
            "record_gap_bytes_preserved": True,
            "protected_token_signatures_preserved": True,
            "newline_topology_preserved": True,
            "per_row_game_playback_required": False,
            "absolute_msggame_widget_width_assumed": False,
            "pk_msgev_912px_rule_applied": False,
        },
        "vm_graph": dict(graph_proof),
        "ghidra_vm_recheck": dict(ghidra_observation),
        "guards": {
            "immutable_checkpoint_private_sha256":
            IMMEDIATE.EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            "immutable_checkpoint_public_sha256":
            IMMEDIATE.EXPECTED_PREDECESSOR_PUBLIC_SHA256,
            "immediate_audit_sha256": EXPECTED_IMMEDIATE_AUDIT_SHA256,
            "immediate_promotion_sha256":
            EXPECTED_IMMEDIATE_PROMOTION_SHA256,
            "immediate_decision_sha256":
            EXPECTED_IMMEDIATE_DECISION_SHA256,
            "immediate_evidence_sha256":
            EXPECTED_IMMEDIATE_EVIDENCE_SHA256,
            "proposal_private_sha256":
            IMMEDIATE.EXPECTED_PROPOSAL_PRIVATE_SHA256,
            "proposal_public_sha256":
            IMMEDIATE.EXPECTED_PROPOSAL_PUBLIC_SHA256,
            "intermediate_candidate_sha256":
            EXPECTED_IMMEDIATE_CANDIDATE_SHA256,
            "candidate_sha256": EXPECTED_FULL_CANDIDATE_SHA256,
            "root_sha256": EXPECTED_ROOT_SHA256,
            "promotion_coordinate_sha256":
            EXPECTED_PROMOTION_COORDINATE_SHA256,
            "renewal_coordinate_sha256":
            EXPECTED_RENEWAL_COORDINATE_SHA256,
            "decision_coordinate_sha256":
            EXPECTED_DECISION_COORDINATE_SHA256,
            "override_coordinate_sha256":
            EXPECTED_OVERRIDE_COORDINATE_SHA256,
            "override_map_canonical_sha256":
            EXPECTED_OVERRIDE_MAP_SHA256,
            "keep_coordinate_sha256": EXPECTED_KEEP_COORDINATE_SHA256,
            "action_coordinate_sha256": dict(
                sorted(EXPECTED_ACTION_COORDINATE_SHA256.items())
            ),
            "assembly_manifest_sha256":
            EXPECTED_ASSEMBLY_MANIFEST_SHA256,
            "component_manifest_sha256":
            EXPECTED_COMPONENT_MANIFEST_SHA256,
            "proposal_decision_manifest_sha256":
            EXPECTED_PROPOSAL_DECISION_MANIFEST_SHA256,
            "predecessor_manifest_sha256":
            canonical_sha256(predecessor_manifest),
            "predecessor_renewal_evidence_sha256":
            canonical_sha256(renewal_manifest),
            "unchanged_preverified_manifest_sha256":
            canonical_sha256(unchanged_manifest),
            "ghidra_vm_contract_sha256":
            EXPECTED_GHIDRA_VM_CONTRACT_SHA256,
            "ghidra_contract_subset_sha256":
            EXPECTED_GHIDRA_CONTRACT_SUBSET_SHA256,
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translation_map_keys": False,
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_contains_dialogue_bodies": False,
        },
        "integration_boundary": {
            "shared_engine_modified": False,
            "shared_runtime_vm_integration_modified": False,
            "shared_progress_modified": False,
            "dedicated_layer_only": True,
        },
        "steam_write_performed": False,
    }
    return HONORIFIC.seal_report(audit)


def action_for(
    coordinate: str,
    *,
    partition: Mapping[str, Any],
) -> str:
    for action, values in partition["actions"].items():
        if coordinate in values:
            return action
    raise ClosureError(f"coordinate has no action: {coordinate}")


def build_updated_rows(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    partition: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    manifest_by_coordinate = {
        str(row["coordinate"]): row
        for row in partition["decision_manifest"]
    }
    updated_rows: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    for coordinate in sorted(
        partition["decisions"],
        key=parse_coordinate,
    ):
        predecessor = predecessor_rows[("pk_msggame", coordinate)]
        action = action_for(coordinate, partition=partition)
        is_renewal = coordinate in partition["renewal"]
        is_override = coordinate in partition["overrides"]
        require(
            predecessor.get("runtime_review")
            == ("verified" if is_renewal else "pending"),
            f"decision predecessor status drifted: {coordinate}",
        )
        proposal_decision = manifest_by_coordinate[coordinate]
        require(
            proposal_decision.get("decision")
            == ("rewrite" if is_override else "keep"),
            f"proposal decision drifted: {coordinate}",
        )
        updated = copy.deepcopy(dict(predecessor))
        previous_evidence = updated.get("runtime_vm_verification")
        if is_override:
            updated["translation"] = partition["overrides"][coordinate]
            IMMEDIATE.FAMILY.CALLER.PREDECESSOR.repair_hard_risks(updated)
            require(
                ENGINE.sha256_text(str(updated["translation"]))
                == proposal_decision[
                    "proposal_translation_utf16le_sha256"
                ],
                f"override translation hash drifted: {coordinate}",
            )
            updated[OVERRIDE_FIELD] = {
                "schema": OVERRIDE_SCHEMA,
                "private_proposal_sha256":
                IMMEDIATE.EXPECTED_PROPOSAL_PRIVATE_SHA256,
                "proposal_public_sha256":
                IMMEDIATE.EXPECTED_PROPOSAL_PUBLIC_SHA256,
                "exact_override_coordinate_sha256":
                EXPECTED_OVERRIDE_COORDINATE_SHA256,
                "exact_override_map_sha256":
                EXPECTED_OVERRIDE_MAP_SHA256,
                "translation_utf16le_sha256":
                ENGINE.sha256_text(str(updated["translation"])),
                "control_components_preserved": True,
                "record_gap_bytes_preserved": True,
                "protected_token_signatures_preserved": True,
                "full_incoming_outgoing_vm_closure_recomputed": True,
                "all_register_assemblies_recomputed": True,
            }
        updated["runtime_review"] = "verified"
        updated["scope_classification"] = "retranslated"
        updated["layout_review"] = "runtime_verified"
        evidence = {
            "schema": EVIDENCE_SCHEMA,
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "status": "verified",
            "method": METHOD,
            "action": action,
            "translation_utf16le_sha256":
            ENGINE.sha256_text(str(updated["translation"])),
            "predecessor_binding": {
                "row_sha256": canonical_sha256(predecessor),
                "immutable_checkpoint_sha256":
                IMMEDIATE.EXPECTED_PREDECESSOR_PRIVATE_SHA256,
                "logical_intermediate_candidate_sha256":
                EXPECTED_IMMEDIATE_CANDIDATE_SHA256,
                "prior_runtime_vm_verification_sha256": (
                    canonical_sha256(previous_evidence)
                    if is_renewal
                    else None
                ),
            },
            "closure_binding": {
                "selector": PROPOSAL.SELECTOR,
                "candidate_sha256": EXPECTED_FULL_CANDIDATE_SHA256,
                "decision_coordinate_sha256":
                EXPECTED_DECISION_COORDINATE_SHA256,
                "audit_report_file_sha256": audit_file_sha256,
                "audit_report_payload_sha256":
                audit["guards"]["report_payload_sha256"],
                "proposal_private_sha256":
                IMMEDIATE.EXPECTED_PROPOSAL_PRIVATE_SHA256,
                "proposal_public_sha256":
                IMMEDIATE.EXPECTED_PROPOSAL_PUBLIC_SHA256,
                "assembly_manifest_sha256":
                EXPECTED_ASSEMBLY_MANIFEST_SHA256,
                "incoming_edge_manifest_sha256":
                EXPECTED_INCOMING_EDGE_MANIFEST_SHA256,
                "outgoing_edge_manifest_sha256":
                EXPECTED_OUTGOING_EDGE_MANIFEST_SHA256,
                "ghidra_contract_subset_sha256":
                EXPECTED_GHIDRA_CONTRACT_SUBSET_SHA256,
            },
            "proof": {
                "grammar_pass_for_all_register_assemblies": True,
                "raw_g1n_nonexpanding_for_all_register_assemblies": True,
                "source_candidate_reverse_ancestor_closure_equal": True,
                "source_candidate_outgoing_closure_equal": True,
                "control_components_preserved": True,
                "record_gap_bytes_preserved": True,
                "protected_token_signatures_preserved": True,
                "newline_topology_preserved": True,
            },
            "preexisting_verified_evidence_renewed": is_renewal,
            "per_row_game_playback_required": False,
        }
        updated[UPDATE_ACTION_FIELD] = action
        updated["runtime_vm_verification"] = evidence
        updated_rows.append(updated)
        evidence_rows.append(evidence)
    updated_rows.sort(key=row_sort_key)
    evidence_rows.sort(key=lambda row: parse_coordinate(str(row["coordinate"])))
    require(
        Counter(row["action"] for row in evidence_rows)
        == Counter(EXPECTED_ACTION_COUNTS)
        and sum(
            row["preexisting_verified_evidence_renewed"]
            for row in evidence_rows
        )
        == EXPECTED_RENEWAL_ROWS,
        "private decision/evidence action counts drifted",
    )
    return updated_rows, evidence_rows


def rebuild_merged_candidate(
    rows: Mapping[tuple[str, str], Mapping[str, Any]],
) -> str:
    replacements = {
        parse_coordinate(coordinate): str(row["translation"])
        for (resource, coordinate), row in rows.items()
        if resource == "pk_msggame"
        and isinstance(row.get("translation"), str)
    }
    blob = BASE_AUDIT.rebuild_packed_with_literals(
        BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        replacements,
    )
    return sha256_bytes(blob)


def build_promotion(
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    decision_content: str,
    evidence_content: str,
) -> dict[str, Any]:
    promotion = {
        "schema": PROMOTION_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "method": METHOD,
        "result": {
            "runtime_promotion_rows": EXPECTED_PROMOTION_ROWS,
            "runtime_promotion_roots": EXPECTED_ROOTS,
            "verification_renewal_rows": EXPECTED_RENEWAL_ROWS,
            "pending_rows_before": EXPECTED_PENDING_BEFORE,
            "pending_rows_after": EXPECTED_PENDING_AFTER,
            "exact_override_rows": EXPECTED_OVERRIDE_ROWS,
            "translation_keep_rows": EXPECTED_KEEP_ROWS,
            "decision_delta_rows": EXPECTED_DECISION_ROWS,
            "private_evidence_rows": EXPECTED_DECISION_ROWS,
            "private_decision_delta_sha256": sha256_bytes(
                decision_content.encode("utf-8")
            ),
            "private_evidence_sha256": sha256_bytes(
                evidence_content.encode("utf-8")
            ),
        },
        "action_counts": dict(sorted(EXPECTED_ACTION_COUNTS.items())),
        "evidence": {
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256":
            audit["guards"]["report_payload_sha256"],
            "immutable_checkpoint_sha256":
            IMMEDIATE.EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            "logical_intermediate_candidate_sha256":
            EXPECTED_IMMEDIATE_CANDIDATE_SHA256,
            "candidate_sha256": EXPECTED_FULL_CANDIDATE_SHA256,
            "decision_coordinate_sha256":
            EXPECTED_DECISION_COORDINATE_SHA256,
            "assembly_manifest_sha256":
            EXPECTED_ASSEMBLY_MANIFEST_SHA256,
            "incoming_edge_manifest_sha256":
            EXPECTED_INCOMING_EDGE_MANIFEST_SHA256,
            "outgoing_edge_manifest_sha256":
            EXPECTED_OUTGOING_EDGE_MANIFEST_SHA256,
            "ghidra_contract_subset_sha256":
            EXPECTED_GHIDRA_CONTRACT_SUBSET_SHA256,
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translation_map_keys": False,
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_contains_dialogue_bodies": False,
        },
        "integration_boundary": {
            "shared_engine_modified": False,
            "shared_runtime_vm_integration_modified": False,
            "shared_progress_modified": False,
            "dedicated_layer_only": True,
        },
        "steam_write_performed": False,
    }
    return HONORIFIC.seal_report(promotion)


SOURCE_TEXT_RE = re.compile(
    r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7a3]"
)
EXACT_COORDINATE_RE = re.compile(r"\b\d+:\d+(?::\d+)?\b")
SENSITIVE_BODY_KEYS = {
    "translation",
    "translations",
    "source_text",
    "current_text",
    "candidate_text",
    "assembly",
    "assemblies",
    "exact_map",
    "exact_reflow_map",
    "records",
    "sites",
    "coordinates",
}


def body_key_count(value: Any) -> int:
    if isinstance(value, Mapping):
        return sum(
            int(key in SENSITIVE_BODY_KEYS) + body_key_count(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return sum(body_key_count(child) for child in value)
    return 0


def assert_source_free_report(value: Any) -> None:
    require(body_key_count(value) == 0, "tracked report contains a body key")
    if isinstance(value, Mapping):
        for child in value.values():
            assert_source_free_report(child)
    elif isinstance(value, list):
        for child in value:
            assert_source_free_report(child)
    elif isinstance(value, str):
        require(
            SOURCE_TEXT_RE.search(value) is None,
            "tracked report contains Hangul/CJK text",
        )
        require(
            EXACT_COORDINATE_RE.search(value) is None,
            "tracked report contains an exact coordinate",
        )


def build_outputs() -> tuple[
    str,
    str,
    str,
    str,
    dict[str, Any],
    dict[str, Any],
]:
    steam_before = {
        "base": HONORIFIC.live_hash(LIVE_STEAM_BASE),
        "pk": HONORIFIC.live_hash(LIVE_STEAM_PK),
    }
    _, ghidra_observation = load_ghidra_contract()
    inputs = load_inputs()
    partition = build_partition(inputs)
    (
        predecessor_manifest,
        renewal_manifest,
        unchanged_manifest,
    ) = predecessor_manifests(
        predecessor_rows=inputs["predecessor_rows"],
        partition=partition,
        proposal_bundle=inputs["proposal_bundle"],
    )
    graph_proof = build_graph_proof(
        partition=partition,
        proposal_bundle=inputs["proposal_bundle"],
    )
    audit = build_audit(
        inputs=inputs,
        partition=partition,
        graph_proof=graph_proof,
        ghidra_observation=ghidra_observation,
        predecessor_manifest=predecessor_manifest,
        renewal_manifest=renewal_manifest,
        unchanged_manifest=unchanged_manifest,
    )
    HONORIFIC.validate_seal(audit)
    assert_source_free_report(audit)
    audit_content = canonical_json(audit)
    audit_file_sha256 = sha256_bytes(audit_content.encode("utf-8"))
    updated_rows, evidence_rows = build_updated_rows(
        predecessor_rows=inputs["predecessor_rows"],
        partition=partition,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
    )
    decision_content = canonical_jsonl(updated_rows)
    evidence_content = canonical_jsonl(evidence_rows)
    merged = {
        key: copy.deepcopy(dict(row))
        for key, row in inputs["intermediate_rows"].items()
    }
    for row in updated_rows:
        merged[(str(row["resource"]), str(row["coordinate"]))] = row
    require(
        len(merged) == EXPECTED_ROWS
        and sum(
            row.get("runtime_review") == "pending"
            for row in merged.values()
        )
        == EXPECTED_PENDING_AFTER
        and rebuild_merged_candidate(merged)
        == EXPECTED_FULL_CANDIDATE_SHA256,
        "merged dependency-inclusive candidate drifted",
    )
    promotion = build_promotion(
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        decision_content=decision_content,
        evidence_content=evidence_content,
    )
    HONORIFIC.validate_seal(promotion)
    assert_source_free_report(promotion)
    promotion_content = canonical_json(promotion)
    steam_after = {
        "base": HONORIFIC.live_hash(LIVE_STEAM_BASE),
        "pk": HONORIFIC.live_hash(LIVE_STEAM_PK),
    }
    require(
        steam_before == steam_after,
        "live Steam msggame changed during deferred closure build",
    )
    return (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        {
            "inputs": inputs,
            "partition": partition,
            "predecessor_manifest": predecessor_manifest,
            "renewal_manifest": renewal_manifest,
            "unchanged_manifest": unchanged_manifest,
            "graph_proof": graph_proof,
            "ghidra_observation": ghidra_observation,
            "updated_rows": updated_rows,
            "evidence_rows": evidence_rows,
            "merged": merged,
            "promotion": promotion,
            "steam_before": steam_before,
            "steam_after": steam_after,
        },
    )


def validate_outputs(
    *,
    decision_content: str,
    evidence_content: str,
    audit_content: str,
    promotion_content: str,
    audit: Mapping[str, Any],
    bundle: Mapping[str, Any],
    require_frozen_hashes: bool = True,
) -> None:
    promotion = bundle["promotion"]
    require(
        len(bundle["updated_rows"]) == EXPECTED_DECISION_ROWS
        and len(bundle["evidence_rows"]) == EXPECTED_DECISION_ROWS
        and audit["scope"]["runtime_promotion_rows"]
        == EXPECTED_PROMOTION_ROWS
        and audit["scope"]["verification_renewal_rows"]
        == EXPECTED_RENEWAL_ROWS
        and audit["scope"]["exact_override_rows"]
        == EXPECTED_OVERRIDE_ROWS
        and audit["scope"]["post_layer_pending_rows"]
        == EXPECTED_PENDING_AFTER
        and audit["proof"]["register_assembly_pass"]
        == EXPECTED_ASSEMBLIES
        and audit["proof"]["register_assembly_fail"] == 0
        and audit["action_counts"] == EXPECTED_ACTION_COUNTS
        and promotion["result"]["pending_rows_after"]
        == EXPECTED_PENDING_AFTER
        and promotion["result"]["verification_renewal_rows"]
        == EXPECTED_RENEWAL_ROWS
        and promotion["action_counts"] == EXPECTED_ACTION_COUNTS,
        "closure output summary drifted",
    )
    require(
        sum(
            row["preexisting_verified_evidence_renewed"]
            for row in bundle["evidence_rows"]
        )
        == EXPECTED_RENEWAL_ROWS
        and rebuild_merged_candidate(bundle["merged"])
        == EXPECTED_FULL_CANDIDATE_SHA256
        and bundle["steam_before"] == bundle["steam_after"],
        "private closure evidence/candidate drifted",
    )
    HONORIFIC.validate_seal(audit)
    HONORIFIC.validate_seal(promotion)
    assert_source_free_report(audit)
    assert_source_free_report(promotion)
    require(
        audit_content == canonical_json(audit)
        and promotion_content == canonical_json(promotion)
        and decision_content == canonical_jsonl(bundle["updated_rows"])
        and evidence_content == canonical_jsonl(bundle["evidence_rows"]),
        "serialized output is not canonical",
    )
    if require_frozen_hashes:
        if EXPECTED_AUDIT_OUTPUT_SHA256 is not None:
            require(
                sha256_bytes(audit_content.encode("utf-8"))
                == EXPECTED_AUDIT_OUTPUT_SHA256,
                "audit output hash drifted",
            )
        if EXPECTED_PROMOTION_OUTPUT_SHA256 is not None:
            require(
                sha256_bytes(promotion_content.encode("utf-8"))
                == EXPECTED_PROMOTION_OUTPUT_SHA256,
                "promotion output hash drifted",
            )
        require(
            sha256_bytes(decision_content.encode("utf-8"))
            == EXPECTED_DECISION_OUTPUT_SHA256
            and sha256_bytes(evidence_content.encode("utf-8"))
            == EXPECTED_EVIDENCE_OUTPUT_SHA256,
            "private decision/evidence output hash drifted",
        )


def validate_output_paths(args: argparse.Namespace) -> None:
    require(
        args.audit_output.resolve() == DEFAULT_AUDIT_OUTPUT.resolve()
        and args.promotion_output.resolve()
        == DEFAULT_PROMOTION_OUTPUT.resolve()
        and args.decision_output.resolve()
        == DEFAULT_DECISION_OUTPUT.resolve()
        and args.evidence_output.resolve()
        == DEFAULT_EVIDENCE_OUTPUT.resolve(),
        "custom output paths are not allowed",
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=DEFAULT_AUDIT_OUTPUT,
    )
    parser.add_argument(
        "--promotion-output",
        type=Path,
        default=DEFAULT_PROMOTION_OUTPUT,
    )
    parser.add_argument(
        "--decision-output",
        type=Path,
        default=DEFAULT_DECISION_OUTPUT,
    )
    parser.add_argument(
        "--evidence-output",
        type=Path,
        default=DEFAULT_EVIDENCE_OUTPUT,
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    validate_output_paths(args)
    (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        bundle,
    ) = build_outputs()
    validate_outputs(
        decision_content=decision_content,
        evidence_content=evidence_content,
        audit_content=audit_content,
        promotion_content=promotion_content,
        audit=audit,
        bundle=bundle,
    )
    if args.write:
        for path, content in (
            (args.decision_output, decision_content),
            (args.evidence_output, evidence_content),
            (args.audit_output, audit_content),
            (args.promotion_output, promotion_content),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                content,
                encoding="ascii" if path.suffix == ".json" else "utf-8",
                newline="\n",
            )
    print(
        "status=PASS "
        f"promotion={EXPECTED_PROMOTION_ROWS} "
        f"renewal={EXPECTED_RENEWAL_ROWS} "
        f"override={EXPECTED_OVERRIDE_ROWS} "
        f"assemblies={EXPECTED_ASSEMBLIES} "
        f"pending={EXPECTED_PENDING_AFTER} "
        f"candidate={EXPECTED_FULL_CANDIDATE_SHA256}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
