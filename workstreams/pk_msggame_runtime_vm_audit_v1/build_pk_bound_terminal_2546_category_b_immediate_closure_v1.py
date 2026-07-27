#!/usr/bin/env python3
"""Integrate only the frozen PK 2546 category-B immediate proposal.

The immutable BF7B predecessor and the hash-bound category-B proposal are
rebuilt before twelve pending rows are promoted.  Translation-bearing
decisions and source-free evidence stay below ``tmp``; only source-free
coverage and promotion reports are tracked.  The two deferred roots, their
five pending rows, and two verified dependencies remain untouched.  This
builder has no shared-integration, progress, engine, or Steam write path.
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
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
PROPOSAL_BUILDER_PATH = (
    WORKSTREAM
    / (
        "build_pk_bound_terminal_2546_category_b_"
        "relative_width_reflow_proposal_v1.py"
    )
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_bound_terminal_2546_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration."
    "post_bound_terminal_2546_checkpoint.source_free.v1.json"
)
PROPOSAL_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "family2546_category_b_relative_width_reflow.private.v1.json"
)
PROPOSAL_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_2546_category_b_relative_width_reflow_proposal.v1.json"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_2546_category_b_immediate_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_2546_category_b_immediate_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / (
        "pk_bound_terminal_2546_category_b_immediate_closure_"
        "integrated_decisions.private.v1.jsonl"
    )
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / (
        "pk_bound_terminal_2546_category_b_immediate_closure_"
        "evidence.private.v1.jsonl"
    )
)

AUDIT_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-category-b-"
    "immediate-closure-coverage.v1"
)
PROMOTION_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-category-b-"
    "immediate-closure-promotion.v1"
)
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-category-b-"
    "immediate-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-category-b-"
    "immediate-exact-override.v1"
)
METHOD = (
    "reversed_vm_pk_bound_terminal_2546_"
    "category_b_immediate_relative_width_closure"
)
UPDATE_ACTION_FIELD = (
    "bound_terminal_2546_category_b_immediate_update_action"
)
OVERRIDE_FIELD = (
    "bound_terminal_2546_category_b_immediate_exact_override_evidence"
)

EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "838D162126925ECF706577688D35570853CDA68226AF3C8FFB7FE14C3943D072"
)
EXPECTED_PROPOSAL_PRIVATE_SHA256 = (
    "686E1D80457C3CF62AEAEDA7BAD619A998B66982980DBAE29AC88C94C0CB3102"
)
EXPECTED_PROPOSAL_PUBLIC_SHA256 = (
    "9D39B97FDC11037A1B46EFD5F1F743939CAF4F5AD176B0F5299F89DDBEEC1E9A"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "2AE326439AC0A503104A245774FA4D2CA3B833E05AAE7E8E40F5CFCF7F5B31E2"
)
EXPECTED_ROWS = 52_803
EXPECTED_PENDING_BEFORE = 8_213
EXPECTED_PENDING_AFTER = 8_201
EXPECTED_OVERRIDE_ROWS = 7
EXPECTED_KEEP_ROWS = 5
EXPECTED_PROMOTION_ROWS = 12
EXPECTED_PROMOTION_ROOTS = 4
EXPECTED_RENEWAL_ROWS = 0
EXPECTED_DECISION_ROWS = 12
EXPECTED_ASSEMBLIES = 28
EXPECTED_ROOT_SHA256 = (
    "4B31FB1F28AD390A8C953EC762B51FEF6FFAF2F914DD0AE40EF9264B727041CC"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "D3AF7F5D0111F7FD630BD4DD3782828F6B7140C5B036567BDD3E542605CCB00F"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "F88B5E9A65BAF53723BB7CD4CEFF830D6E47F33D8DCED4324F568FB869BBF271"
)
EXPECTED_KEEP_COORDINATE_SHA256 = (
    "DD29C9619AF48DF4E7CB5ED98AA44C5F1133586AC879FADE6D098DB7B95EABDA"
)
EXPECTED_OVERRIDE_MAP_SHA256 = (
    "8B709CE05A5A0EA674990F54BE4F095DF9BE8D7BE8F8426500808D06F285E883"
)
EXPECTED_TERMINAL_COORDINATE_SHA256 = (
    "DD975EDD56BA114A8BB46274BF5B141E18A3A28C0153A769F586059E6C9F810A"
)
EXPECTED_ASSEMBLY_MANIFEST_SHA256 = (
    "C4AFCB6065A5057AF7DBCE649C28BA14ADFC167FAC23CEAB3137DD6D9A757214"
)
EXPECTED_COMPONENT_MANIFEST_SHA256 = (
    "BD86DB85D1C34A9D608151526949F82A53B95F8DA869AD3CFDA1993D966CDA4E"
)
EXPECTED_PROPOSAL_DECISION_MANIFEST_SHA256 = (
    "AA8A7DC7DABCFBB24052CCBC439888295549AFCF703264A0006406637354EBF1"
)
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 5,
    "translation_override_and_runtime_promotion": 7,
}
EXPECTED_ACTION_COORDINATE_SHA256 = {
    "runtime_promotion": EXPECTED_KEEP_COORDINATE_SHA256,
    "translation_override_and_runtime_promotion":
    EXPECTED_OVERRIDE_COORDINATE_SHA256,
}

EXPECTED_DEFERRED_ROOTS = 2
EXPECTED_DEFERRED_PENDING_ROWS = 5
EXPECTED_DEFERRED_DEPENDENCY_ROWS = 2
EXPECTED_DEFERRED_ROOT_SHA256 = (
    "0C6D9BC26056B32ED99DBADEA8CB5637FE67C8BD3C0A94C2B90846F1F744D5C4"
)
EXPECTED_DEFERRED_PENDING_COORDINATE_SHA256 = (
    "A17010484F8BEFD7CD337CC678E585B43BC0305766C566D1544197B503CB5A28"
)
EXPECTED_DEFERRED_DEPENDENCY_COORDINATE_SHA256 = (
    "A7E739AEF436B94F5DE6A2BE2FE2BC2C434B9DEB7EA807B33C4D9D3D69A8A15B"
)
EXPECTED_DEFERRED_BLOCKER_MANIFEST_SHA256 = (
    "BA7996C84732493B8262ED872D8AAEF0DD22F84100E185947EE9040ADF00B123"
)
EXPECTED_DEFERRED_PENDING_ONLY_ASSEMBLY_SHA256 = (
    "E64E863D3F6600A70075475EAC18120EA1523A8D2DAEF4AA28D1083767A08B38"
)
EXPECTED_DEFERRED_PENDING_ONLY_FAILURE_SHA256 = (
    "6FADD0E16CA0B41F6845C2F26631D7799CBA3C7FAB4805A7AE0577986B128818"
)

# Frozen after the first deterministic write.
EXPECTED_AUDIT_FILE_SHA256: str | None = (
    "19E869B8D1DF6B0896F39E79ECC0397F8C8B2B7CF3D28BB2547AC7587D72AAAD"
)
EXPECTED_PROMOTION_FILE_SHA256: str | None = (
    "92CEF30654AF571D21F56DDA3A3796E728578A64EEDFF2426572E8060E750610"
)
EXPECTED_DECISION_FILE_SHA256: str | None = (
    "8A44196B7EB20267FAC4ADD6953350257FCB9C5DA92406241B23F0B70133FABA"
)
EXPECTED_EVIDENCE_FILE_SHA256: str | None = (
    "9741F68BB504CEFF3750F56A4AD4D296E249B3656AFD6EB9F5D131F53A32509B"
)


class ClosureError(ValueError):
    """Raised when the category-B immediate closure drifts."""


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


PROPOSAL = load_module(
    PROPOSAL_BUILDER_PATH,
    "pk_bound_terminal_2546_category_b_immediate_proposal_helpers_v1",
)
FAMILY = PROPOSAL.FAMILY
BASE_AUDIT = PROPOSAL.BASE_AUDIT
ENGINE = PROPOSAL.ENGINE
HONORIFIC = PROPOSAL.HONORIFIC
LIVE_STEAM_BASE = PROPOSAL.LIVE_STEAM_BASE
LIVE_STEAM_PK = PROPOSAL.LIVE_STEAM_PK


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
    return PROPOSAL.parse_coordinate(value)


def coordinate_digest(values: Iterable[str]) -> str:
    return PROPOSAL.coordinate_digest(values)


def record_digest(values: Iterable[tuple[int, int]]) -> str:
    return PROPOSAL.record_digest(values)


def row_sort_key(row: Mapping[str, Any]) -> tuple[int, int, int, int]:
    resource_order = {"base_msggame": 0, "pk_msggame": 1}
    return (
        resource_order.get(str(row.get("resource")), 9),
        *parse_coordinate(str(row["coordinate"])),
    )


def load_predecessor() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[str, Any],
]:
    require(
        sha256_file(PREDECESSOR_PRIVATE_PATH)
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and sha256_file(PREDECESSOR_PUBLIC_PATH)
        == EXPECTED_PREDECESSOR_PUBLIC_SHA256,
        "immutable BF7B/838D predecessor digest drifted",
    )
    rows = PROPOSAL.load_checkpoint()
    report = PROPOSAL.validate_checkpoint_source_free()
    require(
        len(rows) == EXPECTED_ROWS
        and sum(
            row.get("runtime_review") == "pending"
            for row in rows.values()
        )
        == EXPECTED_PENDING_BEFORE,
        "immutable predecessor universe drifted",
    )
    return rows, report


def load_and_rebuild_proposal() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    require(
        sha256_file(PROPOSAL_PRIVATE_PATH)
        == EXPECTED_PROPOSAL_PRIVATE_SHA256
        and sha256_file(PROPOSAL_PUBLIC_PATH)
        == EXPECTED_PROPOSAL_PUBLIC_SHA256,
        "frozen private/public category-B proposal digest drifted",
    )
    content, report, bundle = PROPOSAL.build_outputs()
    PROPOSAL.validate_outputs(
        content=content,
        report=report,
        bundle=bundle,
    )
    require(
        content == PROPOSAL_PUBLIC_PATH.read_text(encoding="ascii")
        and report.get("status") == "PASS"
        and report.get("steam_write_performed") is False
        and report["bindings"]["checkpoint_candidate_sha256"]
        == EXPECTED_PREDECESSOR_CANDIDATE_SHA256
        and report["proposal"]["immediate"]["candidate_sha256"]
        == EXPECTED_CANDIDATE_SHA256,
        "deterministic category-B proposal rebuild drifted",
    )
    return dict(report), bundle["handoff"], dict(bundle)


def build_partition(
    proposal_handoff: Mapping[str, Any],
    proposal_bundle: Mapping[str, Any],
) -> dict[str, Any]:
    promotion = set(proposal_handoff["immediate_pending"])
    roots = set(proposal_handoff["immediate_roots"])
    overrides = dict(proposal_handoff["immediate_map"])
    keep = set(proposal_handoff["immediate_keep"])
    deferred_roots = set(proposal_handoff["deferred_roots"])
    deferred_pending = set(proposal_handoff["deferred_pending"])
    deferred_dependencies = set(proposal_handoff["dependencies"])
    compact_map = json.dumps(
        overrides,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    require(
        len(promotion) == EXPECTED_PROMOTION_ROWS
        and coordinate_digest(promotion)
        == EXPECTED_PROMOTION_COORDINATE_SHA256
        and len(roots) == EXPECTED_PROMOTION_ROOTS
        and record_digest(roots) == EXPECTED_ROOT_SHA256
        and len(overrides) == EXPECTED_OVERRIDE_ROWS
        and coordinate_digest(overrides)
        == EXPECTED_OVERRIDE_COORDINATE_SHA256
        and sha256_bytes(compact_map) == EXPECTED_OVERRIDE_MAP_SHA256
        and len(keep) == EXPECTED_KEEP_ROWS
        and coordinate_digest(keep) == EXPECTED_KEEP_COORDINATE_SHA256
        and set(overrides) | keep == promotion
        and not (set(overrides) & keep)
        and len(deferred_roots) == EXPECTED_DEFERRED_ROOTS
        and record_digest(deferred_roots)
        == EXPECTED_DEFERRED_ROOT_SHA256
        and len(deferred_pending) == EXPECTED_DEFERRED_PENDING_ROWS
        and coordinate_digest(deferred_pending)
        == EXPECTED_DEFERRED_PENDING_COORDINATE_SHA256
        and len(deferred_dependencies)
        == EXPECTED_DEFERRED_DEPENDENCY_ROWS
        and coordinate_digest(deferred_dependencies)
        == EXPECTED_DEFERRED_DEPENDENCY_COORDINATE_SHA256,
        "category-B immediate/deferred partition drifted",
    )
    actions = {
        "runtime_promotion": keep,
        "translation_override_and_runtime_promotion": set(overrides),
    }
    require(
        {name: len(values) for name, values in actions.items()}
        == EXPECTED_ACTION_COUNTS
        and all(
            coordinate_digest(values)
            == EXPECTED_ACTION_COORDINATE_SHA256[name]
            for name, values in actions.items()
        ),
        "category-B immediate action partition drifted",
    )

    component_manifest = [
        row
        for row in proposal_bundle["component_manifest"]
        if PROPOSAL.parse_root(str(row["root"])) in roots
    ]
    decision_manifest = [
        row
        for row in proposal_bundle["decision_manifest"]
        if str(row["coordinate"]) in promotion
    ]
    require(
        len(proposal_bundle["immediate_manifest"]) == EXPECTED_ASSEMBLIES
        and not any(
            not row["nonexpanding"]
            for row in proposal_bundle["immediate_manifest"]
        )
        and canonical_sha256(proposal_bundle["immediate_manifest"])
        == EXPECTED_ASSEMBLY_MANIFEST_SHA256
        and canonical_sha256(component_manifest)
        == EXPECTED_COMPONENT_MANIFEST_SHA256
        and canonical_sha256(decision_manifest)
        == EXPECTED_PROPOSAL_DECISION_MANIFEST_SHA256
        and len(proposal_bundle["pending_failures"]) == 13
        and canonical_sha256(proposal_bundle["pending_manifest"])
        == EXPECTED_DEFERRED_PENDING_ONLY_ASSEMBLY_SHA256
        and canonical_sha256(proposal_bundle["pending_failures"])
        == EXPECTED_DEFERRED_PENDING_ONLY_FAILURE_SHA256,
        "category-B assembly/control proposal proof drifted",
    )
    return {
        "promotion": promotion,
        "roots": roots,
        "overrides": overrides,
        "keep": keep,
        "actions": actions,
        "component_manifest": component_manifest,
        "decision_manifest": decision_manifest,
        "deferred_roots": deferred_roots,
        "deferred_pending": deferred_pending,
        "deferred_dependencies": deferred_dependencies,
    }


def build_deferred_blocker_manifest(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    partition: Mapping[str, Any],
) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for coordinate in sorted(
        partition["deferred_pending"] | partition["deferred_dependencies"],
        key=parse_coordinate,
    ):
        row = predecessor_rows[("pk_msggame", coordinate)]
        expected_status = (
            "pending"
            if coordinate in partition["deferred_pending"]
            else "verified"
        )
        require(
            row.get("runtime_review") == expected_status,
            f"deferred predecessor status drifted: {coordinate}",
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
    require(
        len(manifest)
        == EXPECTED_DEFERRED_PENDING_ROWS
        + EXPECTED_DEFERRED_DEPENDENCY_ROWS
        and canonical_sha256(manifest)
        == EXPECTED_DEFERRED_BLOCKER_MANIFEST_SHA256,
        "deferred blocker predecessor manifest drifted",
    )
    return manifest


def build_audit(
    *,
    predecessor_report: Mapping[str, Any],
    proposal_public: Mapping[str, Any],
    partition: Mapping[str, Any],
    blocker_manifest: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    proof = proposal_public["proof"]
    report = {
        "schema": AUDIT_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "method": METHOD,
        "scope": {
            "selector": 1066,
            "terminal_records": 7,
            "predecessor_rows": EXPECTED_ROWS,
            "predecessor_pending_rows": EXPECTED_PENDING_BEFORE,
            "exact_override_rows": EXPECTED_OVERRIDE_ROWS,
            "runtime_promotion_rows": EXPECTED_PROMOTION_ROWS,
            "runtime_promotion_roots": EXPECTED_PROMOTION_ROOTS,
            "verification_renewal_rows": EXPECTED_RENEWAL_ROWS,
            "decision_delta_rows": EXPECTED_DECISION_ROWS,
            "post_layer_pending_rows": EXPECTED_PENDING_AFTER,
        },
        "action_counts": dict(sorted(EXPECTED_ACTION_COUNTS.items())),
        "deferred_blockers": {
            "root_count": EXPECTED_DEFERRED_ROOTS,
            "pending_rows": EXPECTED_DEFERRED_PENDING_ROWS,
            "preexisting_verified_dependency_rows":
            EXPECTED_DEFERRED_DEPENDENCY_ROWS,
            "root_sha256": EXPECTED_DEFERRED_ROOT_SHA256,
            "pending_coordinate_sha256":
            EXPECTED_DEFERRED_PENDING_COORDINATE_SHA256,
            "dependency_coordinate_sha256":
            EXPECTED_DEFERRED_DEPENDENCY_COORDINATE_SHA256,
            "predecessor_manifest_sha256":
            canonical_sha256(blocker_manifest),
            "pending_only_register_assembly_failures": 13,
            "pending_only_failure_manifest_sha256":
            EXPECTED_DEFERRED_PENDING_ONLY_FAILURE_SHA256,
            "reason_code": (
                "verified_left_dependency_rewrite_and_"
                "full_vm_renewal_still_required"
            ),
            "runtime_promotion_authorized": False,
        },
        "proof": {
            "register_assemblies_recomputed": EXPECTED_ASSEMBLIES,
            "register_assembly_pass": EXPECTED_ASSEMBLIES,
            "register_assembly_fail": 0,
            "minimum_width_delta_px":
            proof["minimum_immediate_width_delta_px"],
            "maximum_width_delta_px":
            proof["maximum_immediate_width_delta_px"],
            "all_7_register_assemblies_current_relative_raw_g1n_"
            "nonexpanding": True,
            "control_components_preserved": True,
            "record_gap_bytes_preserved": True,
            "protected_token_signatures_preserved": True,
            "newline_topology_preserved": True,
            "verification_renewal_rows_zero": True,
            "per_row_game_playback_required": False,
            "absolute_msggame_widget_width_assumed": False,
            "pk_msgev_912px_rule_applied": False,
        },
        "guards": {
            "predecessor_private_sha256":
            EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            "predecessor_public_sha256":
            EXPECTED_PREDECESSOR_PUBLIC_SHA256,
            "predecessor_result_canonical_sha256": canonical_sha256(
                predecessor_report["result"]
            ),
            "proposal_private_sha256": EXPECTED_PROPOSAL_PRIVATE_SHA256,
            "proposal_public_sha256": EXPECTED_PROPOSAL_PUBLIC_SHA256,
            "predecessor_candidate_sha256":
            EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
            "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "root_sha256": EXPECTED_ROOT_SHA256,
            "promotion_coordinate_sha256":
            EXPECTED_PROMOTION_COORDINATE_SHA256,
            "override_coordinate_sha256":
            EXPECTED_OVERRIDE_COORDINATE_SHA256,
            "keep_coordinate_sha256": EXPECTED_KEEP_COORDINATE_SHA256,
            "override_map_canonical_sha256":
            EXPECTED_OVERRIDE_MAP_SHA256,
            "terminal_coordinate_sha256":
            EXPECTED_TERMINAL_COORDINATE_SHA256,
            "assembly_manifest_sha256":
            EXPECTED_ASSEMBLY_MANIFEST_SHA256,
            "component_manifest_sha256":
            EXPECTED_COMPONENT_MANIFEST_SHA256,
            "proposal_decision_manifest_sha256":
            EXPECTED_PROPOSAL_DECISION_MANIFEST_SHA256,
            "action_coordinate_sha256": dict(
                sorted(EXPECTED_ACTION_COORDINATE_SHA256.items())
            ),
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translation_map_keys": False,
            "private_proposal_stays_below_tmp": True,
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
    return HONORIFIC.seal_report(report)


def action_for(
    coordinate: str,
    *,
    overrides: Mapping[str, str],
) -> str:
    return (
        "translation_override_and_runtime_promotion"
        if coordinate in overrides
        else "runtime_promotion"
    )


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
    for coordinate in sorted(partition["promotion"], key=parse_coordinate):
        predecessor = predecessor_rows[("pk_msggame", coordinate)]
        require(
            predecessor.get("runtime_review") == "pending",
            f"promotion predecessor status drifted: {coordinate}",
        )
        updated = copy.deepcopy(dict(predecessor))
        is_override = coordinate in partition["overrides"]
        manifest = manifest_by_coordinate[coordinate]
        require(
            manifest.get("checkpoint_status") == "pending"
            and manifest.get("decision")
            == ("rewrite" if is_override else "keep"),
            f"proposal decision binding drifted: {coordinate}",
        )
        if is_override:
            updated["translation"] = partition["overrides"][coordinate]
            FAMILY.CALLER.PREDECESSOR.repair_hard_risks(updated)
            require(
                ENGINE.sha256_text(str(updated["translation"]))
                == manifest["proposal_translation_utf16le_sha256"],
                f"override translation hash drifted: {coordinate}",
            )
            updated[OVERRIDE_FIELD] = {
                "schema": OVERRIDE_SCHEMA,
                "private_proposal_sha256":
                EXPECTED_PROPOSAL_PRIVATE_SHA256,
                "proposal_public_sha256":
                EXPECTED_PROPOSAL_PUBLIC_SHA256,
                "exact_override_coordinate_sha256":
                EXPECTED_OVERRIDE_COORDINATE_SHA256,
                "exact_override_map_sha256":
                EXPECTED_OVERRIDE_MAP_SHA256,
                "translation_utf16le_sha256":
                ENGINE.sha256_text(str(updated["translation"])),
                "control_components_preserved": True,
                "record_gap_bytes_preserved": True,
                "protected_token_signatures_preserved": True,
                "all_7_register_assemblies_recomputed": True,
            }
        updated["runtime_review"] = "verified"
        updated["scope_classification"] = "retranslated"
        updated["layout_review"] = "runtime_verified"
        action = action_for(
            coordinate,
            overrides=partition["overrides"],
        )
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
                "checkpoint_sha256":
                EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            },
            "closure_binding": {
                "selector": 1066,
                "terminal_coordinate_sha256":
                EXPECTED_TERMINAL_COORDINATE_SHA256,
                "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
                "decision_coordinate_sha256":
                EXPECTED_PROMOTION_COORDINATE_SHA256,
                "audit_report_file_sha256": audit_file_sha256,
                "audit_report_payload_sha256":
                audit["guards"]["report_payload_sha256"],
                "proposal_private_sha256":
                EXPECTED_PROPOSAL_PRIVATE_SHA256,
                "proposal_public_sha256":
                EXPECTED_PROPOSAL_PUBLIC_SHA256,
                "assembly_manifest_sha256":
                EXPECTED_ASSEMBLY_MANIFEST_SHA256,
                "component_manifest_sha256":
                EXPECTED_COMPONENT_MANIFEST_SHA256,
                "deferred_pending_coordinate_sha256":
                EXPECTED_DEFERRED_PENDING_COORDINATE_SHA256,
                "deferred_dependency_coordinate_sha256":
                EXPECTED_DEFERRED_DEPENDENCY_COORDINATE_SHA256,
            },
            "proof": {
                "grammar_pass_for_all_7_register_assemblies": True,
                "raw_g1n_nonexpanding_for_all_7_register_assemblies": True,
                "control_components_preserved": True,
                "record_gap_bytes_preserved": True,
                "protected_token_signatures_preserved": True,
                "newline_topology_preserved": True,
            },
            "preexisting_verified_evidence_renewed": False,
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
        == Counter(EXPECTED_ACTION_COUNTS),
        "private output action counts drifted",
    )
    return updated_rows, evidence_rows


def build_promotion(
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    decision_content: str,
    evidence_content: str,
) -> dict[str, Any]:
    report = {
        "schema": PROMOTION_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "method": METHOD,
        "result": {
            "runtime_promotion_rows": EXPECTED_PROMOTION_ROWS,
            "runtime_promotion_roots": EXPECTED_PROMOTION_ROOTS,
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
        "deferred_blockers": {
            "root_count": EXPECTED_DEFERRED_ROOTS,
            "pending_rows": EXPECTED_DEFERRED_PENDING_ROWS,
            "preexisting_verified_dependency_rows":
            EXPECTED_DEFERRED_DEPENDENCY_ROWS,
            "pending_coordinate_sha256":
            EXPECTED_DEFERRED_PENDING_COORDINATE_SHA256,
            "dependency_coordinate_sha256":
            EXPECTED_DEFERRED_DEPENDENCY_COORDINATE_SHA256,
            "runtime_promotion_authorized": False,
        },
        "evidence": {
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256":
            audit["guards"]["report_payload_sha256"],
            "predecessor_checkpoint_sha256":
            EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            "proposal_private_sha256": EXPECTED_PROPOSAL_PRIVATE_SHA256,
            "proposal_public_sha256": EXPECTED_PROPOSAL_PUBLIC_SHA256,
            "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "decision_coordinate_sha256":
            EXPECTED_PROMOTION_COORDINATE_SHA256,
            "assembly_manifest_sha256":
            EXPECTED_ASSEMBLY_MANIFEST_SHA256,
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translation_map_keys": False,
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_contains_dialogue_bodies": False,
        },
        "steam_write_performed": False,
    }
    return HONORIFIC.seal_report(report)


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


def rebuild_merged_candidate(
    merged: Mapping[tuple[str, str], Mapping[str, Any]],
) -> str:
    replacements = {
        parse_coordinate(coordinate): str(row["translation"])
        for (resource, coordinate), row in merged.items()
        if resource == "pk_msggame"
        and isinstance(row.get("translation"), str)
    }
    blob = BASE_AUDIT.rebuild_packed_with_literals(
        BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        replacements,
    )
    return sha256_bytes(blob)


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
    predecessor_rows, predecessor_report = load_predecessor()
    proposal_public, proposal_handoff, proposal_bundle = (
        load_and_rebuild_proposal()
    )
    partition = build_partition(proposal_handoff, proposal_bundle)
    blocker_manifest = build_deferred_blocker_manifest(
        predecessor_rows=predecessor_rows,
        partition=partition,
    )
    audit = build_audit(
        predecessor_report=predecessor_report,
        proposal_public=proposal_public,
        partition=partition,
        blocker_manifest=blocker_manifest,
    )
    HONORIFIC.validate_seal(audit)
    audit_content = canonical_json(audit)
    audit_file_sha256 = sha256_bytes(audit_content.encode("utf-8"))
    updated_rows, evidence_rows = build_updated_rows(
        predecessor_rows=predecessor_rows,
        partition=partition,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
    )
    decision_content = canonical_jsonl(updated_rows)
    evidence_content = canonical_jsonl(evidence_rows)
    promotion = build_promotion(
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        decision_content=decision_content,
        evidence_content=evidence_content,
    )
    HONORIFIC.validate_seal(promotion)
    promotion_content = canonical_json(promotion)
    steam_after = {
        "base": HONORIFIC.live_hash(LIVE_STEAM_BASE),
        "pk": HONORIFIC.live_hash(LIVE_STEAM_PK),
    }
    require(
        steam_before == steam_after,
        "live Steam msggame changed during closure build",
    )
    return (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        {
            "predecessor_rows": predecessor_rows,
            "proposal_public": proposal_public,
            "proposal_handoff": proposal_handoff,
            "proposal_bundle": proposal_bundle,
            "partition": partition,
            "blocker_manifest": blocker_manifest,
            "updated_rows": updated_rows,
            "evidence_rows": evidence_rows,
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
        decision_content == canonical_jsonl(bundle["updated_rows"])
        and evidence_content == canonical_jsonl(bundle["evidence_rows"])
        and audit_content == canonical_json(audit)
        and promotion_content == canonical_json(promotion),
        "serialized output drifted",
    )
    frozen = (
        EXPECTED_AUDIT_FILE_SHA256,
        EXPECTED_PROMOTION_FILE_SHA256,
        EXPECTED_DECISION_FILE_SHA256,
        EXPECTED_EVIDENCE_FILE_SHA256,
    )
    actual = (
        sha256_bytes(audit_content.encode("utf-8")),
        sha256_bytes(promotion_content.encode("utf-8")),
        sha256_bytes(decision_content.encode("utf-8")),
        sha256_bytes(evidence_content.encode("utf-8")),
    )
    if require_frozen_hashes:
        require(all(frozen), "output hashes have not been frozen")
        require(actual == frozen, f"frozen output file hash drifted: {actual}")
    HONORIFIC.validate_seal(audit)
    HONORIFIC.validate_seal(promotion)
    assert_source_free_report(audit)
    assert_source_free_report(promotion)
    require(
        body_key_count(bundle["evidence_rows"]) == 0,
        "private evidence contains a dialogue body/map key",
    )
    updated_by_key = {
        ("pk_msggame", str(row["coordinate"])): row
        for row in bundle["updated_rows"]
    }
    require(
        len(updated_by_key) == EXPECTED_DECISION_ROWS
        and len(bundle["evidence_rows"]) == EXPECTED_DECISION_ROWS,
        "private output row count drifted",
    )
    merged = {
        key: copy.deepcopy(dict(row))
        for key, row in bundle["predecessor_rows"].items()
    }
    merged.update(updated_by_key)
    pending_after = sum(
        row.get("runtime_review") == "pending" for row in merged.values()
    )
    actions = Counter(
        str(row[UPDATE_ACTION_FIELD]) for row in bundle["updated_rows"]
    )
    partition = bundle["partition"]
    untouched_blockers = (
        partition["deferred_pending"] | partition["deferred_dependencies"]
    )
    require(
        all(
            merged[("pk_msggame", coordinate)]
            == bundle["predecessor_rows"][("pk_msggame", coordinate)]
            for coordinate in untouched_blockers
        ),
        "deferred blocker row was modified",
    )
    require(
        pending_after == EXPECTED_PENDING_AFTER
        and dict(actions) == EXPECTED_ACTION_COUNTS
        and rebuild_merged_candidate(merged) == EXPECTED_CANDIDATE_SHA256
        and audit["scope"]["post_layer_pending_rows"]
        == EXPECTED_PENDING_AFTER
        and promotion["result"]["pending_rows_after"]
        == EXPECTED_PENDING_AFTER
        and audit["scope"]["verification_renewal_rows"] == 0
        and promotion["result"]["verification_renewal_rows"] == 0
        and audit["deferred_blockers"]["runtime_promotion_authorized"]
        is False
        and promotion["deferred_blockers"][
            "runtime_promotion_authorized"
        ]
        is False
        and audit.get("steam_write_performed") is False
        and promotion.get("steam_write_performed") is False
        and bundle["steam_before"] == bundle["steam_after"],
        "final category-B immediate closure result drifted",
    )
    for coordinate, text in partition["overrides"].items():
        require(
            merged[("pk_msggame", coordinate)].get("translation") == text,
            f"merged private override drifted: {coordinate}",
        )


def validate_output_paths(args: argparse.Namespace) -> None:
    private_root = DIALOGUE_TMP.resolve(strict=False)
    steam_paths = {
        LIVE_STEAM_BASE.resolve(strict=False),
        LIVE_STEAM_PK.resolve(strict=False),
    }
    for path in (args.decision_output, args.evidence_output):
        resolved = path.resolve(strict=False)
        require(
            resolved not in steam_paths,
            "private output may not target live Steam",
        )
        require(
            private_root in resolved.parents,
            f"private output must remain below {private_root}",
        )
    require(
        args.audit_output.resolve(strict=False)
        == DEFAULT_AUDIT_OUTPUT.resolve(strict=False)
        and args.promotion_output.resolve(strict=False)
        == DEFAULT_PROMOTION_OUTPUT.resolve(strict=False),
        "public reports must use their fixed tracked source-free paths",
    )
    output_paths = {
        args.audit_output.resolve(strict=False),
        args.promotion_output.resolve(strict=False),
        args.decision_output.resolve(strict=False),
        args.evidence_output.resolve(strict=False),
    }
    require(len(output_paths) == 4, "closure output paths must be distinct")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-output", type=Path, default=DEFAULT_AUDIT_OUTPUT)
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
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")
    validate_output_paths(args)
    (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        bundle,
    ) = build_outputs()
    frozen_ready = all(
        (
            EXPECTED_AUDIT_FILE_SHA256,
            EXPECTED_PROMOTION_FILE_SHA256,
            EXPECTED_DECISION_FILE_SHA256,
            EXPECTED_EVIDENCE_FILE_SHA256,
        )
    )
    validate_outputs(
        decision_content=decision_content,
        evidence_content=evidence_content,
        audit_content=audit_content,
        promotion_content=promotion_content,
        audit=audit,
        bundle=bundle,
        require_frozen_hashes=frozen_ready,
    )
    outputs = {
        args.audit_output: audit_content,
        args.promotion_output: promotion_content,
        args.decision_output: decision_content,
        args.evidence_output: evidence_content,
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    if args.check:
        require(frozen_ready, "output hashes have not been frozen")
        for path, expected_content in outputs.items():
            require(path.is_file(), f"output missing: {path}")
            require(
                path.read_text(encoding="utf-8") == expected_content,
                f"output drifted: {path}",
            )
    print(
        "PASS "
        f"overrides={EXPECTED_OVERRIDE_ROWS} "
        f"renewed={EXPECTED_RENEWAL_ROWS} "
        f"promoted={EXPECTED_PROMOTION_ROWS} "
        f"pending={EXPECTED_PENDING_AFTER} "
        f"assemblies={EXPECTED_ASSEMBLIES} "
        f"deferred={EXPECTED_DEFERRED_PENDING_ROWS} "
        "shared_integration_write=false "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
