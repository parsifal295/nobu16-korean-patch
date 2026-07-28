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
    OUTPUT_ROOT
    / "runtime_vm_integrated."
    "post_selector568_1096_1174_consolidated_checkpoint.private.v1.jsonl"
)
RUNTIME_VM_INTEGRATION_REPORT = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector568_1096_1174_consolidated_checkpoint.source_free.v1.json"
)
SELECTOR538_PREDECESSOR_DECISIONS = (
    OUTPUT_ROOT
    / "runtime_vm_integrated."
    "post_selector538_family_checkpoint.private.v1.jsonl"
)
SELECTOR538_PREDECESSOR_REPORT = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector538_family_checkpoint.source_free.v1.json"
)
HISTORICAL_RUNTIME_VM_INTEGRATED_DECISIONS = (
    OUTPUT_ROOT
    / "runtime_vm_integrated."
    "post_bound_terminal_2546_checkpoint.private.v1.jsonl"
)
HISTORICAL_RUNTIME_VM_INTEGRATION_REPORT = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_bound_terminal_2546_checkpoint.source_free.v1.json"
)
D5_DECISION_PATH = (
    OUTPUT_ROOT
    / "semantic_overrides"
    / "pk_bound_terminal_2546_category_b_deferred_full_vm_"
    "closure_integrated_decisions.private.v1.jsonl"
)
D5_EVIDENCE_PATH = (
    OUTPUT_ROOT
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_bound_terminal_2546_category_b_deferred_full_vm_"
    "closure_evidence.private.v1.jsonl"
)
SELECTOR538_FAMILY_DECISION_PATH = (
    OUTPUT_ROOT
    / "semantic_overrides"
    / "pk_selector538_family_consolidated_closure_decisions.private.v1.jsonl"
)
SELECTOR538_FAMILY_EVIDENCE_PATH = (
    OUTPUT_ROOT
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector538_family_consolidated_closure_evidence.private.v1.jsonl"
)
SELECTOR568_1096_1174_CONSOLIDATED_DECISION_PATH = (
    OUTPUT_ROOT
    / "semantic_overrides"
    / "pk_selector568_1096_1174_consolidated_closure_"
    "decisions.private.v1.jsonl"
)
SELECTOR568_1096_1174_CONSOLIDATED_EVIDENCE_PATH = (
    OUTPUT_ROOT
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector568_1096_1174_consolidated_closure_"
    "evidence.private.v1.jsonl"
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
EXPECTED_RUNTIME_VM_INTEGRATED_PRIVATE_SHA256 = (
    "FC157A9907686D0EA6DC6C61C7785E81AC7F750100F2E1CDDE02DBF4F09F2DCA"
)
EXPECTED_RUNTIME_VM_INTEGRATION_REPORT_SHA256 = (
    "1FCF033F1F75FC43473152CFB7115D170657519952C19D563C36C3F9BAB4CBD1"
)
EXPECTED_SELECTOR538_PREDECESSOR_PRIVATE_SHA256 = (
    "81B4E22C3C20AA5F7FF8B8251A2829AEEB0C6E0A0D9FA2B93748B6249F23F6CB"
)
EXPECTED_SELECTOR538_PREDECESSOR_REPORT_SHA256 = (
    "46270F70A019484EFB1F99851D436467C8FD2DE32EB222BDC048DA1B5BC080FA"
)
EXPECTED_HISTORICAL_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_HISTORICAL_REPORT_SHA256 = (
    "838D162126925ECF706577688D35570853CDA68226AF3C8FFB7FE14C3943D072"
)
EXPECTED_D5_DECISION_SHA256 = (
    "54343C398C7D8E22A957AE47CA9B8AA5C11DD7F64C6BEF4EFF50DFA4EF466095"
)
EXPECTED_D5_EVIDENCE_SHA256 = (
    "C328430233A81E4457BD253844D65622B7305AEB20FACB30E011C2EEF7B58BD0"
)
EXPECTED_SELECTOR538_FAMILY_DECISION_SHA256 = (
    "5640EB7FB7E4EA9B32309B7FA280637DA9F26F96CA500BCD4FA9847D997456C0"
)
EXPECTED_SELECTOR538_FAMILY_EVIDENCE_SHA256 = (
    "910C0A59823C2B6B083F58257D6203053738EFEFC2E49E6271D553FF44CAB940"
)
EXPECTED_SELECTOR568_1096_1174_CONSOLIDATED_DECISION_SHA256 = (
    "3260FCF12561EE116228907E1619FDB368DBDF9D0BA8565C03CD014440669B38"
)
EXPECTED_SELECTOR568_1096_1174_CONSOLIDATED_EVIDENCE_SHA256 = (
    "3AA3CB05106CA921F22B96D26B8FA74A4F7C7D15A4D3AE122738F92E10A34C25"
)
EXPECTED_SELECTOR568_1096_1174_CONSOLIDATED_AUDIT_SHA256 = (
    "1C70A12C107DB79B1402F5879364F5AAEA31F34B3933F4C53524C89B570F9990"
)
EXPECTED_SELECTOR568_1096_1174_CONSOLIDATED_PROMOTION_SHA256 = (
    "E16B597EF856822350D3FD0E0FAB7A9737E3D40D6FE156ED39EA778E5DE85AA0"
)
EXPECTED_SELECTOR538_PK_CANDIDATE_SHA256 = (
    "DCB19B0D85422F7C0EA5888F9A0C47667D75A88D100BABAE11DDAF4A8DD2000E"
)
EXPECTED_FINAL_PK_CANDIDATE_SHA256 = (
    "07E65E6338D32C1FD13F17408F82A4133E55541C722874632948C7B36C909805"
)
EXPECTED_SELECTOR538_CONSOLIDATED_OVERLAP_COUNT = 72
BOUND_TERMINAL_2546_OVERRIDE_COORDINATE_SHA256 = (
    "212DEF7EE8B508CEA406FF223BADE5E2DC0DC7D7B1EE5255AD828764B6A866B5"
)
BOUND_TERMINAL_2546_PROMOTION_COORDINATE_SHA256 = (
    "667E25717B1F8CB5E8AD4C26DC4615CD2D52B38D69529BCB9E62AB562FD23320"
)
BOUND_TERMINAL_2546_RENEWAL_COORDINATE_SHA256 = (
    "203B38F2EFD645D710467F7663ECE6B65EDAB32D1BF376B17C092BCFE898FA5F"
)
BOUND_TERMINAL_2546_DECISION_COORDINATE_SHA256 = (
    "F176E7D99EC74F07AE6041B29EC5CCB3DB36A356B7600CF291B2B61B51ABC349"
)
BOUND_TERMINAL_2546_EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 279,
    "translation_override_and_runtime_promotion": 85,
    "translation_override_and_verification_renewal": 131,
    "verification_renewal": 161,
}
BOUND_TERMINAL_2546_SUPERSEDED_TERMINAL_OVERRIDES = frozenset(
    {
        ("pk_msggame", f"0:{record_id}:0")
        for record_id in range(2546, 2553)
    }
)
BOUND_TERMINAL_2546_SUPERSEDED_THOUGHT_OVERRIDES = frozenset(
    {
        ("pk_msggame", "6:3551:1"),
        ("pk_msggame", "6:4398:0"),
        ("pk_msggame", "6:4437:0"),
    }
)
BOUND_TERMINAL_2546_SUPERSEDED_CALLER_OVERRIDES = frozenset(
    {
        ("pk_msggame", "6:3863:0"),
        ("pk_msggame", "6:3863:1"),
        ("pk_msggame", "6:4713:0"),
        ("pk_msggame", "6:4713:1"),
        ("pk_msggame", "6:4757:0"),
        ("pk_msggame", "6:4757:1"),
        ("pk_msggame", "6:4758:0"),
        ("pk_msggame", "6:4758:1"),
        ("pk_msggame", "6:4896:1"),
        ("pk_msggame", "6:4896:2"),
        ("pk_msggame", "15:277:1"),
        ("pk_msggame", "15:277:2"),
        ("pk_msggame", "15:278:1"),
        ("pk_msggame", "15:278:2"),
    }
)
BOUND_TERMINAL_2546_NEW_CALLER_OVERRIDE_OVERLAP = frozenset(
    {
        ("pk_msggame", "6:4713:1"),
        ("pk_msggame", "6:4758:1"),
        ("pk_msggame", "6:4896:2"),
        ("pk_msggame", "15:277:1"),
        ("pk_msggame", "15:278:1"),
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


def canonical_ascii_row_sha256(row: dict[str, Any]) -> str:
    encoded = json.dumps(
        row,
        ensure_ascii=True,
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
            "bound_terminal_caller_runtime_evidence",
            "bound_terminal_caller_update_action",
            "bound_terminal_caller_override_evidence",
            "bound_terminal_2546_full_caller_update_action",
            "bound_terminal_2546_exact_override_evidence",
            "bound_terminal_2546_simple_caller_update_action",
            "bound_terminal_2546_category_b_immediate_update_action",
            "bound_terminal_2546_category_b_deferred_full_vm_update_action",
            "bound_terminal_2546_category_b_deferred_full_vm_exact_override_evidence",
            "selector538_chunk0_update_action",
            "selector538_family_update_action",
            "selector568_family_update_action",
            "selector568_family_exact_override_evidence",
            "selector1096_family_update_action",
            "selector1096_family_exact_override_evidence",
            "selector568_1096_cross_family_update_action",
            "selector568_1096_cross_family_exact_override_evidence",
            "selector568_1096_1174_consolidated_update_action",
            "selector568_1096_1174_exact_override_evidence",
        }
    }


def load_historical_runtime_vm_integration(
    prepared: Any,
) -> tuple[dict[tuple[str, str], dict[str, Any]], dict[str, Any]]:
    if not HISTORICAL_RUNTIME_VM_INTEGRATION_REPORT.is_file():
        raise RuntimeError(
            "historical source-free runtime VM integration report is absent: "
            f"{HISTORICAL_RUNTIME_VM_INTEGRATION_REPORT}"
        )
    if not HISTORICAL_RUNTIME_VM_INTEGRATED_DECISIONS.is_file():
        raise RuntimeError(
            "historical private runtime VM integrated decisions are absent: "
            f"{HISTORICAL_RUNTIME_VM_INTEGRATED_DECISIONS}"
        )
    report_bytes = HISTORICAL_RUNTIME_VM_INTEGRATION_REPORT.read_bytes()
    report = json.loads(report_bytes.decode("utf-8"))
    if (
        sha256_bytes(report_bytes)
        != EXPECTED_HISTORICAL_REPORT_SHA256
        or
        not isinstance(report, dict)
        or report.get("schema") != RUNTIME_VM_INTEGRATION_SCHEMA
        or report.get("status") != "PASS"
        or report.get("release_target") != "0.15.0"
        or report.get("steam_write_performed") is not False
    ):
        raise RuntimeError("runtime VM integration report metadata drifted")
    private_sha256 = sha256_bytes(
        HISTORICAL_RUNTIME_VM_INTEGRATED_DECISIONS.read_bytes()
    )
    result = report.get("result")
    if (
        private_sha256 != EXPECTED_HISTORICAL_PRIVATE_SHA256
        or
        not isinstance(result, dict)
        or result.get("private_integrated_decision_sha256") != private_sha256
        or result.get("semantic_review_approved")
        != len(prepared.visible_targets)
    ):
        raise RuntimeError("runtime VM integrated decision guard drifted")
    ENGINE.validate_decisions(
        prepared,
        HISTORICAL_RUNTIME_VM_INTEGRATED_DECISIONS,
        require_complete=False,
    )
    rows = load_jsonl(HISTORICAL_RUNTIME_VM_INTEGRATED_DECISIONS)
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
        or pending != 8_213
        or result.get("fully_candidate_eligible") != 44_590
    ):
        raise RuntimeError("runtime VM integration result counts drifted")
    pk_promotions = report.get("promotions", {}).get("pk_msggame", {})
    bound_terminal_2546 = pk_promotions.get(
        "bound_terminal_2546_full_caller"
    )
    if (
        pk_promotions.get(
            "bound_terminal_2546_full_caller_layer_included"
        )
        is not True
        or not isinstance(bound_terminal_2546, dict)
        or bound_terminal_2546.get("translation_override_count") != 216
        or bound_terminal_2546.get("override_coordinate_sha256")
        != BOUND_TERMINAL_2546_OVERRIDE_COORDINATE_SHA256
        or bound_terminal_2546.get("promotion_count") != 364
        or bound_terminal_2546.get("promotion_coordinate_sha256")
        != BOUND_TERMINAL_2546_PROMOTION_COORDINATE_SHA256
        or bound_terminal_2546.get("verification_renewal_count") != 292
        or bound_terminal_2546.get("renewal_coordinate_sha256")
        != BOUND_TERMINAL_2546_RENEWAL_COORDINATE_SHA256
        or bound_terminal_2546.get("updated_row_count") != 656
        or bound_terminal_2546.get("decision_coordinate_sha256")
        != BOUND_TERMINAL_2546_DECISION_COORDINATE_SHA256
        or bound_terminal_2546.get("action_counts")
        != BOUND_TERMINAL_2546_EXPECTED_ACTION_COUNTS
        or bound_terminal_2546.get("steam_write_performed") is not False
        or report.get("validation", {}).get(
            "bound_terminal_2546_full_caller_layer_included"
        )
        is not True
        or report.get("validation", {}).get(
            "exact_216_translation_overrides_rechecked"
        )
        is not True
        or report.get("validation", {}).get(
            "actual_364_pending_promotions_rechecked"
        )
        is not True
        or report.get("validation", {}).get(
            "affected_292_verified_pk_runtime_evidence_renewed"
        )
        is not True
    ):
        raise RuntimeError(
            "bound-terminal 2546 integration metadata drifted"
        )
    metadata = {
        "historical_path":
            HISTORICAL_RUNTIME_VM_INTEGRATION_REPORT
            .relative_to(REPO)
            .as_posix(),
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
        "bound_terminal_caller_layer_included": report["promotions"][
            "pk_msggame"
        ].get("bound_terminal_caller_layer_included")
        is True,
        "bound_terminal_caller": report["promotions"]["pk_msggame"].get(
            "bound_terminal_caller"
        ),
        "bound_terminal_2546_full_caller_layer_included": True,
        "bound_terminal_2546_full_caller": bound_terminal_2546,
        "steam_write_performed": False,
    }
    return by_coordinate, metadata


def keyed_rows(
    path: Path,
) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for row in load_jsonl(path):
        key = (str(row["resource"]), str(row["coordinate"]))
        if key in result:
            raise RuntimeError(f"duplicate exact layer row: {path}/{key}")
        result[key] = row
    return result


def validate_final_exact_layers(
    *,
    historical_rows: dict[tuple[str, str], dict[str, Any]],
    selector538_predecessor_rows: dict[
        tuple[str, str],
        dict[str, Any],
    ],
    final_rows: dict[tuple[str, str], dict[str, Any]],
    report: dict[str, Any],
) -> dict[str, Any]:
    pk = report.get("promotions", {}).get("pk_msggame", {})
    d5 = pk.get("bound_terminal_2546_category_b_deferred")
    selector538 = pk.get("selector538_family")
    consolidated = pk.get("selector568_1096_1174_consolidated")
    validation = report.get("validation", {})
    if (
        pk.get(
            "bound_terminal_2546_category_b_deferred_layer_included"
        )
        is not True
        or pk.get("selector538_family_layer_included") is not True
        or pk.get(
            "selector568_1096_1174_consolidated_layer_included"
        )
        is not True
        or not isinstance(d5, dict)
        or not isinstance(selector538, dict)
        or not isinstance(consolidated, dict)
        or d5.get("private_source_update_sha256")
        != EXPECTED_D5_DECISION_SHA256
        or d5.get("private_source_evidence_sha256")
        != EXPECTED_D5_EVIDENCE_SHA256
        or d5.get("audit_report_sha256")
        != "6DF07C5897901C6807AF02FAFFDF45B2433423162D2FBE5CD1D0BEF0B3593C17"
        or d5.get("promotion_report_sha256")
        != "7488765148CF320B66D28F5820DD3321629A7962F54A3AF5D528CB79CF48757F"
        or d5.get("combined_candidate_packed_sha256")
        != "7A2FFBC5A175BDE9B78169EE6D6212BCEC73A949652A92863C35F93EC9B8A04F"
        or d5.get("source_candidate_packed_sha256")
        != "1E57A600BE7EC64F2D923816121D16E2444B460527291347322ADCEE48110053"
        or d5.get("promotion_count") != 5
        or d5.get("verification_renewal_count") != 2
        or d5.get("translation_override_count") != 6
        or d5.get("updated_row_count") != 7
        or d5.get("action_counts")
        != {
            "runtime_promotion": 1,
            "translation_override_and_runtime_promotion": 4,
            "translation_override_and_verification_renewal": 2,
        }
        or d5.get("steam_write_performed") is not False
        or selector538.get("private_source_update_sha256")
        != EXPECTED_SELECTOR538_FAMILY_DECISION_SHA256
        or selector538.get("private_source_evidence_sha256")
        != EXPECTED_SELECTOR538_FAMILY_EVIDENCE_SHA256
        or selector538.get("audit_report_sha256")
        != "39E287858CDF49ABDA329A6C3E8EB1E9497E415CDE25F4348C3E12113A1C07A8"
        or selector538.get("promotion_report_sha256")
        != "6F7DDA159299CC9B1923C14A55B5341CFBDB9E9DB3CADA5D7CB77453EAEF3E85"
        or selector538.get("source_candidate_sha256")
        != "24E0E9CCAAD469C0EEFB41EDB032A17F0DAE9BF3EEB471688D452C2FC2A37C56"
        or selector538.get("combined_candidate_packed_sha256")
        != EXPECTED_SELECTOR538_PK_CANDIDATE_SHA256
        or selector538.get("promotion_count") != 212
        or selector538.get("total_family_promotion_count") != 277
        or selector538.get("verification_renewal_count") != 420
        or selector538.get("translation_override_count") != 142
        or selector538.get("updated_row_count") != 697
        or selector538.get("decision_union_coordinate_sha256")
        != "CE46C3E9524D6FB61DA1B24B58F3EB6EC863BC3860727A4B7BCB2F9D2D23AABF"
        or selector538.get("promotion_union_coordinate_sha256")
        != "B6D1D61B1681F9CA92AD6DCD2C43F4913D83916C0DC5BFE05A4C0BFEC3BED5C1"
        or selector538.get("renewal_common_coordinate_sha256")
        != "36058C249C73F5B42C0DC7426FA68879F4BDC515F40F9C50B6CFEC07C7FD4D59"
        or selector538.get("override_union_coordinate_sha256")
        != "8DA1C9C2491E145FD1EBAD2C326F48FDD344E91766758B68644EDDD53131C1A5"
        or selector538.get("action_counts")
        != {
            "runtime_promotion": 220,
            "translation_override_and_runtime_promotion": 57,
            "translation_override_and_verification_renewal": 85,
            "verification_renewal": 335,
        }
        or selector538.get("steam_write_performed") is not False
        or consolidated.get("private_source_update_sha256")
        != EXPECTED_SELECTOR568_1096_1174_CONSOLIDATED_DECISION_SHA256
        or consolidated.get("private_source_evidence_sha256")
        != EXPECTED_SELECTOR568_1096_1174_CONSOLIDATED_EVIDENCE_SHA256
        or consolidated.get("audit_report_sha256")
        != EXPECTED_SELECTOR568_1096_1174_CONSOLIDATED_AUDIT_SHA256
        or consolidated.get("promotion_report_sha256")
        != EXPECTED_SELECTOR568_1096_1174_CONSOLIDATED_PROMOTION_SHA256
        or consolidated.get("official_predecessor_private_sha256")
        != EXPECTED_SELECTOR538_PREDECESSOR_PRIVATE_SHA256
        or consolidated.get("source_candidate_packed_sha256")
        != EXPECTED_FINAL_PK_CANDIDATE_SHA256
        or consolidated.get("combined_candidate_packed_sha256")
        != EXPECTED_FINAL_PK_CANDIDATE_SHA256
        or consolidated.get("promotion_count") != 628
        or consolidated.get("verification_renewal_count") != 545
        or consolidated.get("semantic_override_count") != 440
        or consolidated.get("updated_row_count") != 1_173
        or consolidated.get("action_counts")
        != {
            "runtime_promotion": 413,
            "translation_override_and_runtime_promotion": 215,
            "translation_override_and_verification_renewal": 225,
            "verification_renewal": 320,
        }
        or consolidated.get("steam_write_performed") is not False
        or validation.get("d5_selector538_family_disjointness_rechecked")
        is not True
        or validation.get("all_1057_register_assemblies_rechecked")
        is not True
        or validation.get(
            "unique_renewal_override_owner_union_preserved"
        )
        is not True
        or validation.get(
            "selector568_1096_1174_consolidated_layer_included"
        )
        is not True
        or validation.get("single_combined_coordinate_union_used")
        is not True
        or validation.get("sequential_cross_and_selector1174_overlays_used")
        is not False
        or validation.get("actual_628_pending_promotions_rechecked")
        is not True
        or validation.get(
            "affected_545_verified_pk_runtime_evidence_renewed"
        )
        is not True
        or validation.get("exact_440_semantic_overrides_rechecked")
        is not True
    ):
        raise RuntimeError(
            "final D5/selector-538/consolidated report binding drifted"
        )

    expected_files = {
        D5_DECISION_PATH: EXPECTED_D5_DECISION_SHA256,
        D5_EVIDENCE_PATH: EXPECTED_D5_EVIDENCE_SHA256,
        SELECTOR538_FAMILY_DECISION_PATH:
            EXPECTED_SELECTOR538_FAMILY_DECISION_SHA256,
        SELECTOR538_FAMILY_EVIDENCE_PATH:
            EXPECTED_SELECTOR538_FAMILY_EVIDENCE_SHA256,
        SELECTOR568_1096_1174_CONSOLIDATED_DECISION_PATH:
            EXPECTED_SELECTOR568_1096_1174_CONSOLIDATED_DECISION_SHA256,
        SELECTOR568_1096_1174_CONSOLIDATED_EVIDENCE_PATH:
            EXPECTED_SELECTOR568_1096_1174_CONSOLIDATED_EVIDENCE_SHA256,
    }
    for path, expected in expected_files.items():
        if sha256_bytes(path.read_bytes()) != expected:
            raise RuntimeError(f"final exact layer file drifted: {path}")

    d5_decisions = keyed_rows(D5_DECISION_PATH)
    d5_evidence = keyed_rows(D5_EVIDENCE_PATH)
    family_decisions = keyed_rows(SELECTOR538_FAMILY_DECISION_PATH)
    family_evidence = keyed_rows(SELECTOR538_FAMILY_EVIDENCE_PATH)
    consolidated_decisions = keyed_rows(
        SELECTOR568_1096_1174_CONSOLIDATED_DECISION_PATH
    )
    consolidated_evidence = keyed_rows(
        SELECTOR568_1096_1174_CONSOLIDATED_EVIDENCE_PATH
    )
    selector538_overlap = set(family_decisions) & set(
        consolidated_decisions
    )
    if (
        len(d5_decisions) != 7
        or set(d5_decisions) != set(d5_evidence)
        or len(family_decisions) != 697
        or set(family_decisions) != set(family_evidence)
        or set(d5_decisions) & set(family_decisions)
        or len(consolidated_decisions) != 1_173
        or set(consolidated_decisions) != set(consolidated_evidence)
        or set(d5_decisions) & set(consolidated_decisions)
        or len(selector538_overlap)
        != EXPECTED_SELECTOR538_CONSOLIDATED_OVERLAP_COUNT
    ):
        raise RuntimeError("final exact layer coordinate universe drifted")

    def validate_rows(
        decisions: dict[tuple[str, str], dict[str, Any]],
        evidence_rows: dict[tuple[str, str], dict[str, Any]],
        *,
        target_rows: dict[tuple[str, str], dict[str, Any]],
        action_field: str,
        method: str,
        historical_hash_field: str,
        historical_ascii: bool,
    ) -> None:
        for key, decision in decisions.items():
            evidence = evidence_rows[key]
            final = target_rows.get(key)
            historical = historical_rows.get(key)
            if (
                final != decision
                or not isinstance(historical, dict)
                or final.get("runtime_vm_verification") != evidence
                or final.get(action_field) != evidence.get("action")
                or evidence.get("method") != method
                or evidence.get("status") != "verified"
                or evidence.get("translation_utf16le_sha256")
                != ENGINE.sha256_text(str(final.get("translation")))
                or evidence.get("predecessor_binding", {}).get(
                    historical_hash_field
                )
                != (
                    canonical_ascii_row_sha256(historical)
                    if historical_ascii
                    else canonical_row_sha256(historical)
                )
            ):
                raise RuntimeError(
                    f"final exact layer row binding drifted: {key}"
                )

    validate_rows(
        d5_decisions,
        d5_evidence,
        target_rows=selector538_predecessor_rows,
        action_field=(
            "bound_terminal_2546_category_b_deferred_full_vm_"
            "update_action"
        ),
        method=(
            "reversed_vm_pk_bound_terminal_2546_category_b_deferred_"
            "dependency_inclusive_full_closure"
        ),
        historical_hash_field="row_sha256",
        historical_ascii=False,
    )
    validate_rows(
        family_decisions,
        family_evidence,
        target_rows=selector538_predecessor_rows,
        action_field="selector538_family_update_action",
        method=(
            "reversed_vm_pk_selector538_chunks_0_3_consolidated_closure"
        ),
        historical_hash_field="baseline_row_sha256",
        historical_ascii=True,
    )

    if (
        set(selector538_predecessor_rows) != set(final_rows)
        or any(
            final_rows[key] != predecessor
            for key, predecessor in selector538_predecessor_rows.items()
            if key not in consolidated_decisions
        )
    ):
        raise RuntimeError(
            "consolidated final changed rows outside its exact union"
        )

    consolidated_action_counts: Counter[str] = Counter()
    promotion_count = 0
    renewal_count = 0
    override_count = 0
    for key, decision in consolidated_decisions.items():
        final = final_rows.get(key)
        predecessor = selector538_predecessor_rows.get(key)
        evidence = consolidated_evidence[key]
        action = str(
            decision.get(
                ENGINE
                .PK_SELECTOR568_1096_1174_CONSOLIDATED_UPDATE_ACTION_FIELD
            )
        )
        if (
            final != decision
            or not isinstance(predecessor, dict)
            or decision.get("runtime_vm_verification") != evidence
        ):
            raise RuntimeError(
                f"consolidated final row binding drifted: {key}"
            )
        ENGINE.validate_selector568_1096_1174_consolidated_decision_row(
            decision,
            label=f"progress consolidated row {key}",
        )
        consolidated_action_counts[action] += 1
        if action in {
            "runtime_promotion",
            "translation_override_and_runtime_promotion",
        }:
            promotion_count += 1
        else:
            renewal_count += 1
        if action.startswith("translation_override"):
            override_count += 1
    if (
        dict(consolidated_action_counts)
        != consolidated["action_counts"]
        or promotion_count != 628
        or renewal_count != 545
        or override_count != 440
    ):
        raise RuntimeError(
            "consolidated action/promotion/renewal universe drifted"
        )

    return {
        "d5_action_counts": d5["action_counts"],
        "d5_decision_rows": len(d5_decisions),
        "d5_decision_sha256": EXPECTED_D5_DECISION_SHA256,
        "d5_evidence_sha256": EXPECTED_D5_EVIDENCE_SHA256,
        "d5_selector538_disjoint": True,
        "d5_consolidated_disjoint": True,
        "final_pk_candidate_sha256": EXPECTED_FINAL_PK_CANDIDATE_SHA256,
        "selector538_action_counts": selector538["action_counts"],
        "selector538_decision_rows": len(family_decisions),
        "selector538_decision_sha256":
            EXPECTED_SELECTOR538_FAMILY_DECISION_SHA256,
        "selector538_evidence_sha256":
            EXPECTED_SELECTOR538_FAMILY_EVIDENCE_SHA256,
        "selector538_consolidated_overlap_count": len(
            selector538_overlap
        ),
        "selector568_1096_1174_action_counts": dict(
            consolidated_action_counts
        ),
        "selector568_1096_1174_decision_rows": len(
            consolidated_decisions
        ),
        "selector568_1096_1174_decision_sha256":
            EXPECTED_SELECTOR568_1096_1174_CONSOLIDATED_DECISION_SHA256,
        "selector568_1096_1174_evidence_sha256":
            EXPECTED_SELECTOR568_1096_1174_CONSOLIDATED_EVIDENCE_SHA256,
        "selector568_1096_1174_promotion_count": promotion_count,
        "selector568_1096_1174_renewal_count": renewal_count,
        "selector568_1096_1174_override_count": override_count,
    }


def load_runtime_vm_integration(
    prepared: Any,
) -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[tuple[str, str], dict[str, Any]],
    dict[str, Any],
]:
    historical_rows, metadata = (
        load_historical_runtime_vm_integration(prepared)
    )
    if (
        not RUNTIME_VM_INTEGRATION_REPORT.is_file()
        or not RUNTIME_VM_INTEGRATED_DECISIONS.is_file()
        or not SELECTOR538_PREDECESSOR_REPORT.is_file()
        or not SELECTOR538_PREDECESSOR_DECISIONS.is_file()
    ):
        raise RuntimeError("final runtime VM integration artifacts are absent")
    report_bytes = RUNTIME_VM_INTEGRATION_REPORT.read_bytes()
    private_bytes = RUNTIME_VM_INTEGRATED_DECISIONS.read_bytes()
    predecessor_report_bytes = SELECTOR538_PREDECESSOR_REPORT.read_bytes()
    predecessor_private_bytes = (
        SELECTOR538_PREDECESSOR_DECISIONS.read_bytes()
    )
    report = json.loads(report_bytes.decode("utf-8"))
    predecessor_report = json.loads(
        predecessor_report_bytes.decode("utf-8")
    )
    private_sha256 = sha256_bytes(private_bytes)
    predecessor_private_sha256 = sha256_bytes(
        predecessor_private_bytes
    )
    result = report.get("result", {})
    predecessor_result = predecessor_report.get("result", {})
    pk = report.get("promotions", {}).get("pk_msggame", {})
    if (
        sha256_bytes(report_bytes)
        != EXPECTED_RUNTIME_VM_INTEGRATION_REPORT_SHA256
        or private_sha256
        != EXPECTED_RUNTIME_VM_INTEGRATED_PRIVATE_SHA256
        or report.get("schema") != RUNTIME_VM_INTEGRATION_SCHEMA
        or report.get("status") != "PASS"
        or report.get("release_target") != "0.15.0"
        or report.get("steam_write_performed") is not False
        or result.get("private_integrated_decision_sha256")
        != private_sha256
        or result.get("semantic_review_approved") != 52_803
        or result.get("runtime_review_pending") != 7_268
        or result.get("fully_candidate_eligible") != 45_535
        or report.get("promotions", {}).get("promoted_total") != 29_066
        or pk.get("promotion_count") != 13_415
        or sha256_bytes(predecessor_report_bytes)
        != EXPECTED_SELECTOR538_PREDECESSOR_REPORT_SHA256
        or predecessor_private_sha256
        != EXPECTED_SELECTOR538_PREDECESSOR_PRIVATE_SHA256
        or predecessor_report.get("schema")
        != RUNTIME_VM_INTEGRATION_SCHEMA
        or predecessor_report.get("status") != "PASS"
        or predecessor_report.get("steam_write_performed") is not False
        or predecessor_result.get("private_integrated_decision_sha256")
        != predecessor_private_sha256
        or predecessor_result.get("semantic_review_approved") != 52_803
        or predecessor_result.get("runtime_review_pending") != 7_896
        or predecessor_result.get("fully_candidate_eligible") != 44_907
    ):
        raise RuntimeError("final runtime VM integration guard drifted")
    ENGINE.validate_decisions(
        prepared,
        SELECTOR538_PREDECESSOR_DECISIONS,
        require_complete=False,
    )
    ENGINE.validate_decisions(
        prepared,
        RUNTIME_VM_INTEGRATED_DECISIONS,
        require_complete=False,
    )
    selector538_predecessor_rows = keyed_rows(
        SELECTOR538_PREDECESSOR_DECISIONS
    )
    final_rows = keyed_rows(RUNTIME_VM_INTEGRATED_DECISIONS)
    pending = sum(
        row.get("runtime_review") == "pending"
        for row in final_rows.values()
    )
    if (
        len(final_rows) != 52_803
        or pending != 7_268
        or set(final_rows) != set(historical_rows)
        or set(selector538_predecessor_rows) != set(historical_rows)
    ):
        raise RuntimeError("final runtime VM row/status universe drifted")
    exact = validate_final_exact_layers(
        historical_rows=historical_rows,
        selector538_predecessor_rows=selector538_predecessor_rows,
        final_rows=final_rows,
        report=report,
    )
    metadata.update(
        {
            "path":
                RUNTIME_VM_INTEGRATION_REPORT.relative_to(REPO).as_posix(),
            "sha256": EXPECTED_RUNTIME_VM_INTEGRATION_REPORT_SHA256,
            "private_integrated_decision_sha256": private_sha256,
            "promoted_total": 29_066,
            "runtime_review_pending_after": pending,
            "historical_checkpoint_private_sha256":
                EXPECTED_HISTORICAL_PRIVATE_SHA256,
            "historical_checkpoint_report_sha256":
                EXPECTED_HISTORICAL_REPORT_SHA256,
            "historical_layers_revalidated_from_immutable_checkpoint":
                True,
            "selector538_predecessor_path":
                SELECTOR538_PREDECESSOR_REPORT
                .relative_to(REPO)
                .as_posix(),
            "selector538_predecessor_private_sha256":
                predecessor_private_sha256,
            "selector538_predecessor_report_sha256":
                EXPECTED_SELECTOR538_PREDECESSOR_REPORT_SHA256,
            "final_exact_layers": exact,
            "bound_terminal_2546_category_b_deferred_layer_included":
                True,
            "bound_terminal_2546_category_b_deferred":
                pk["bound_terminal_2546_category_b_deferred"],
            "selector538_family_layer_included": True,
            "selector538_family": pk["selector538_family"],
            "selector568_1096_1174_consolidated_layer_included": True,
            "selector568_1096_1174_consolidated":
                pk["selector568_1096_1174_consolidated"],
            "steam_write_performed": False,
        }
    )
    return historical_rows, final_rows, metadata


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
    (
        runtime_vm_integrated,
        runtime_vm_final,
        runtime_vm_integration_metadata,
    ) = load_runtime_vm_integration(prepared)
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
    caller_metadata = runtime_vm_integration_metadata.get(
        "bound_terminal_caller"
    )
    if (
        runtime_vm_integration_metadata.get(
            "bound_terminal_caller_layer_included"
        )
        is not True
        or not isinstance(caller_metadata, dict)
    ):
        raise RuntimeError(
            "bound-terminal caller integration metadata is absent"
        )
    caller_override_coordinates = {
        key
        for key, integrated_row in runtime_vm_integrated.items()
        if str(
            integrated_row.get("bound_terminal_caller_update_action", "")
        ).startswith("translation_override")
    }
    if (
        len(caller_override_coordinates)
        != caller_metadata.get("ledger_backed_override_count")
        or any(
            resource != "pk_msggame"
            for resource, _coordinate in caller_override_coordinates
        )
        or coordinate_digest(
            [
                coordinate
                for _resource, coordinate in caller_override_coordinates
            ]
        )
        != caller_metadata.get("ledger_override_coordinate_sha256")
    ):
        raise RuntimeError(
            "bound-terminal caller semantic override universe drifted"
        )
    bound_terminal_2546_metadata = runtime_vm_integration_metadata.get(
        "bound_terminal_2546_full_caller"
    )
    if (
        runtime_vm_integration_metadata.get(
            "bound_terminal_2546_full_caller_layer_included"
        )
        is not True
        or not isinstance(bound_terminal_2546_metadata, dict)
    ):
        raise RuntimeError(
            "bound-terminal 2546 integration metadata is absent"
        )
    bound_terminal_2546_updated_coordinates = {
        key
        for key, integrated_row in runtime_vm_integrated.items()
        if integrated_row.get(
            ENGINE.PK_BOUND_TERMINAL_2546_UPDATE_ACTION_FIELD
        )
        is not None
    }
    bound_terminal_2546_override_coordinates = {
        key
        for key in bound_terminal_2546_updated_coordinates
        if str(
            runtime_vm_integrated[key].get(
                ENGINE.PK_BOUND_TERMINAL_2546_UPDATE_ACTION_FIELD,
                "",
            )
        ).startswith("translation_override")
    }
    bound_terminal_2546_action_counts = Counter(
        str(
            runtime_vm_integrated[key][
                ENGINE.PK_BOUND_TERMINAL_2546_UPDATE_ACTION_FIELD
            ]
        )
        for key in bound_terminal_2546_updated_coordinates
    )
    if (
        len(bound_terminal_2546_updated_coordinates) != 656
        or coordinate_digest(
            [
                coordinate
                for _resource, coordinate
                in bound_terminal_2546_updated_coordinates
            ]
        )
        != BOUND_TERMINAL_2546_DECISION_COORDINATE_SHA256
        or len(bound_terminal_2546_override_coordinates) != 216
        or coordinate_digest(
            [
                coordinate
                for _resource, coordinate
                in bound_terminal_2546_override_coordinates
            ]
        )
        != BOUND_TERMINAL_2546_OVERRIDE_COORDINATE_SHA256
        or dict(bound_terminal_2546_action_counts)
        != BOUND_TERMINAL_2546_EXPECTED_ACTION_COUNTS
        or sum(
            bound_terminal_2546_action_counts[action]
            for action in (
                "runtime_promotion",
                "translation_override_and_runtime_promotion",
            )
        )
        != 364
        or sum(
            bound_terminal_2546_action_counts[action]
            for action in (
                "verification_renewal",
                "translation_override_and_verification_renewal",
            )
        )
        != 292
        or any(
            resource != "pk_msggame"
            for resource, _coordinate
            in bound_terminal_2546_updated_coordinates
        )
    ):
        raise RuntimeError(
            "bound-terminal 2546 update/override universe drifted"
        )
    bound_terminal_2546_predecessor_rows = (
        ENGINE.load_bound_terminal_2546_predecessor_rows()
    )
    consumed_runtime_vm_integrated: set[tuple[str, str]] = set()
    consumed_dynamic_honorific_overrides: set[
        tuple[str, str]
    ] = set()
    consumed_bound_terminal_overrides: set[tuple[str, str]] = set()
    consumed_thought_predicate_overrides: set[tuple[str, str]] = set()
    consumed_caller_overrides: set[tuple[str, str]] = set()
    consumed_bound_terminal_2546_overrides: set[
        tuple[str, str]
    ] = set()
    consumed_bound_terminal_2546_superseded_terminal: set[
        tuple[str, str]
    ] = set()
    consumed_bound_terminal_2546_superseded_thought: set[
        tuple[str, str]
    ] = set()
    consumed_bound_terminal_2546_superseded_caller: set[
        tuple[str, str]
    ] = set()

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
            bound_terminal_2546_evidence = (
                integrated_row.get("runtime_vm_verification")
                if key in bound_terminal_2546_updated_coordinates
                else None
            )
            bound_terminal_2546_predecessor = (
                bound_terminal_2546_predecessor_rows.get(key)
                if key in bound_terminal_2546_updated_coordinates
                else None
            )
            if key in bound_terminal_2546_updated_coordinates:
                if (
                    not isinstance(bound_terminal_2546_evidence, dict)
                    or not isinstance(
                        bound_terminal_2546_predecessor,
                        dict,
                    )
                    or bound_terminal_2546_evidence.get("method")
                    != (
                        ENGINE
                        .PK_BOUND_TERMINAL_2546_RUNTIME_VM_VERIFICATION_METHOD
                    )
                    or bound_terminal_2546_evidence.get("action")
                    != integrated_row.get(
                        ENGINE.PK_BOUND_TERMINAL_2546_UPDATE_ACTION_FIELD
                    )
                    or bound_terminal_2546_evidence.get(
                        "translation_utf16le_sha256"
                    )
                    != ENGINE.sha256_text(
                        str(integrated_row.get("translation"))
                    )
                    or bound_terminal_2546_evidence.get(
                        "predecessor_binding",
                        {},
                    ).get("checkpoint_sha256")
                    != (
                        ENGINE
                        .PK_BOUND_TERMINAL_2546_PREDECESSOR_CHECKPOINT_SHA256
                    )
                    or bound_terminal_2546_evidence.get(
                        "predecessor_binding",
                        {},
                    ).get("row_sha256")
                    != ENGINE.canonical_sha256(
                        bound_terminal_2546_predecessor
                    )
                    or bound_terminal_2546_evidence.get(
                        "closure_binding",
                        {},
                    ).get("candidate_sha256")
                    != ENGINE.PK_BOUND_TERMINAL_2546_CANDIDATE_SHA256
                    or bound_terminal_2546_evidence.get(
                        "closure_binding",
                        {},
                    ).get("decision_coordinate_sha256")
                    != BOUND_TERMINAL_2546_DECISION_COORDINATE_SHA256
                ):
                    raise RuntimeError(
                        "bound-terminal 2546 integrated row binding drifted: "
                        f"{key}"
                    )
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
                terminal_superseded_by_2546 = (
                    key
                    in BOUND_TERMINAL_2546_SUPERSEDED_TERMINAL_OVERRIDES
                    and isinstance(bound_terminal_2546_evidence, dict)
                )
                if terminal_superseded_by_2546:
                    assert isinstance(
                        bound_terminal_2546_predecessor,
                        dict,
                    )
                    predecessor_terminal_evidence = (
                        bound_terminal_2546_predecessor.get(
                            "runtime_vm_verification"
                        )
                        if bound_terminal_2546_predecessor.get(
                            "runtime_review"
                        )
                        == "verified"
                        else bound_terminal_2546_predecessor.get(
                            "terminal_family_runtime_evidence"
                        )
                    )
                    if (
                        integrated_row.get(
                            "terminal_family_update_action"
                        )
                        != bound_terminal_2546_predecessor.get(
                            "terminal_family_update_action"
                        )
                        or terminal_override_evidence
                        != bound_terminal_2546_predecessor.get(
                            "terminal_family_exact_override_evidence"
                        )
                        or integrated_row.get(
                            "terminal_family_runtime_evidence"
                        )
                        != bound_terminal_2546_predecessor.get(
                            "terminal_family_runtime_evidence"
                        )
                    ):
                        raise RuntimeError(
                            "superseded terminal metadata was not preserved: "
                            f"{key}"
                        )
                    terminal_runtime_evidence = (
                        predecessor_terminal_evidence
                    )
                    terminal_translation = str(
                        bound_terminal_2546_predecessor.get("translation")
                    )
                    consumed_bound_terminal_2546_superseded_terminal.add(
                        key
                    )
                else:
                    terminal_runtime_evidence = (
                        integrated_row.get("runtime_vm_verification")
                        if integrated_row.get("runtime_review") == "verified"
                        else integrated_row.get(
                            "terminal_family_runtime_evidence"
                        )
                    )
                    terminal_translation = str(
                        integrated_row.get("translation")
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
                        terminal_translation
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
                thought_superseded_by_2546 = (
                    key
                    in BOUND_TERMINAL_2546_SUPERSEDED_THOUGHT_OVERRIDES
                    and isinstance(bound_terminal_2546_evidence, dict)
                )
                if thought_superseded_by_2546:
                    assert isinstance(
                        bound_terminal_2546_predecessor,
                        dict,
                    )
                    thought_evidence = (
                        bound_terminal_2546_predecessor.get(
                            "runtime_vm_verification"
                        )
                    )
                    if (
                        thought_predicate_action
                        != bound_terminal_2546_predecessor.get(
                            "thought_predicate_family_update_action"
                        )
                    ):
                        raise RuntimeError(
                            "superseded thought metadata was not preserved: "
                            f"{key}"
                        )
                    thought_translation = str(
                        bound_terminal_2546_predecessor.get("translation")
                    )
                    consumed_bound_terminal_2546_superseded_thought.add(
                        key
                    )
                else:
                    thought_evidence = integrated_row.get(
                        "runtime_vm_verification"
                    )
                    thought_translation = str(
                        integrated_row.get("translation")
                    )
                thought_evidence_preserved_by_caller = (
                    key
                    == ENGINE.CALLER_SUPERSEDED_THOUGHT_ACTION_COORDINATE
                    and isinstance(thought_evidence, dict)
                    and thought_evidence.get("method")
                    == ENGINE.PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD
                    and thought_evidence.get("action")
                    == "verification_renewal"
                    and thought_evidence.get(
                        "translation_utf16le_sha256"
                    )
                    == ENGINE.sha256_text(
                        str(integrated_row.get("translation"))
                    )
                    and thought_evidence.get(
                        "combined_final_binding", {}
                    ).get("thought_translation_preserved")
                    is True
                )
                if (
                    key not in thought_predicate_override_coordinates
                    or not isinstance(thought_evidence, dict)
                    or (
                        not thought_evidence_preserved_by_caller
                        and (
                            thought_evidence.get("method")
                            != ENGINE.PK_THOUGHT_PREDICATE_FAMILY_RUNTIME_VM_VERIFICATION_METHOD
                            or thought_evidence.get("action")
                            != thought_predicate_action
                            or thought_evidence.get(
                                "updated_translation_utf16le_sha256"
                            )
                            != ENGINE.sha256_text(
                                thought_translation
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
                        )
                    )
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
            caller_action = integrated_row.get(
                "bound_terminal_caller_update_action"
            )
            if str(caller_action).startswith("translation_override"):
                caller_superseded_by_2546 = (
                    key
                    in BOUND_TERMINAL_2546_SUPERSEDED_CALLER_OVERRIDES
                    and isinstance(bound_terminal_2546_evidence, dict)
                )
                if caller_superseded_by_2546:
                    assert isinstance(
                        bound_terminal_2546_predecessor,
                        dict,
                    )
                    caller_evidence = (
                        bound_terminal_2546_predecessor.get(
                            "runtime_vm_verification"
                        )
                        if bound_terminal_2546_predecessor.get(
                            "runtime_review"
                        )
                        == "verified"
                        else bound_terminal_2546_predecessor.get(
                            "bound_terminal_caller_runtime_evidence"
                        )
                    )
                    if (
                        caller_action
                        != bound_terminal_2546_predecessor.get(
                            "bound_terminal_caller_update_action"
                        )
                        or integrated_row.get(
                            "bound_terminal_caller_runtime_evidence"
                        )
                        != bound_terminal_2546_predecessor.get(
                            "bound_terminal_caller_runtime_evidence"
                        )
                        or integrated_row.get(
                            "bound_terminal_caller_override_evidence"
                        )
                        != bound_terminal_2546_predecessor.get(
                            "bound_terminal_caller_override_evidence"
                        )
                    ):
                        raise RuntimeError(
                            "superseded caller metadata was not preserved: "
                            f"{key}"
                        )
                    caller_translation = str(
                        bound_terminal_2546_predecessor.get("translation")
                    )
                    consumed_bound_terminal_2546_superseded_caller.add(
                        key
                    )
                else:
                    caller_evidence = (
                        integrated_row.get("runtime_vm_verification")
                        if integrated_row.get("runtime_review") == "verified"
                        else integrated_row.get(
                            "bound_terminal_caller_runtime_evidence"
                        )
                    )
                    caller_translation = str(
                        integrated_row.get("translation")
                    )
                if (
                    key not in caller_override_coordinates
                    or not isinstance(caller_evidence, dict)
                    or caller_evidence.get("method")
                    != ENGINE.PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD
                    or caller_evidence.get("action") != caller_action
                    or caller_evidence.get("translation_utf16le_sha256")
                    != ENGINE.sha256_text(
                        caller_translation
                    )
                ):
                    raise RuntimeError(
                        f"bound-terminal caller semantic override drifted: {key}"
                    )
                immutable_integrated_row = dict(immutable_integrated_row)
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
                consumed_caller_overrides.add(key)
            bound_terminal_2546_action = integrated_row.get(
                ENGINE.PK_BOUND_TERMINAL_2546_UPDATE_ACTION_FIELD
            )
            if str(bound_terminal_2546_action).startswith(
                "translation_override"
            ):
                override_evidence = integrated_row.get(
                    "bound_terminal_2546_exact_override_evidence"
                )
                if (
                    key not in bound_terminal_2546_override_coordinates
                    or key in consumed_bound_terminal_2546_overrides
                    or not isinstance(bound_terminal_2546_evidence, dict)
                    or bound_terminal_2546_evidence.get("action")
                    != bound_terminal_2546_action
                    or bound_terminal_2546_evidence.get(
                        "translation_utf16le_sha256"
                    )
                    != ENGINE.sha256_text(
                        str(integrated_row.get("translation"))
                    )
                    or not isinstance(override_evidence, dict)
                    or override_evidence.get("schema")
                    != (
                        "nobu16.kr.pk-bound-terminal-2546-"
                        "exact-override.v1"
                    )
                    or override_evidence.get(
                        "private_handoff_hash_bound"
                    )
                    is not True
                    or override_evidence.get("control_bytes_preserved")
                    is not True
                    or override_evidence.get("automatic_space_inserted")
                    is not False
                    or override_evidence.get(
                        "translation_utf16le_sha256"
                    )
                    != ENGINE.sha256_text(
                        str(integrated_row.get("translation"))
                    )
                ):
                    raise RuntimeError(
                        "bound-terminal 2546 semantic override drifted: "
                        f"{key}"
                    )
                immutable_integrated_row = dict(immutable_integrated_row)
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
                if key in consumed_bound_terminal_2546_overrides:
                    raise RuntimeError(
                        "bound-terminal 2546 override was consumed twice: "
                        f"{key}"
                    )
                consumed_bound_terminal_2546_overrides.add(key)
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
                caller_predecessor_binding = evidence.get(
                    "predecessor_binding"
                )
                caller_predecessor_renewal = (
                    evidence.get("method")
                    == ENGINE.PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD
                    and evidence.get("action")
                    in {
                        "verification_renewal",
                        "translation_override_and_verification_renewal",
                    }
                    and evidence.get(
                        "preexisting_verified_evidence_renewed"
                    )
                    is True
                    and isinstance(caller_predecessor_binding, dict)
                    and isinstance(
                        caller_predecessor_binding.get(
                            "previous_runtime_vm_verification_sha256"
                        ),
                        str,
                    )
                )
                bound_terminal_2546_action = evidence.get("action")
                bound_terminal_2546_predecessor_state_matches = (
                    isinstance(bound_terminal_2546_predecessor, dict)
                    and evidence.get("method")
                    == (
                        ENGINE
                        .PK_BOUND_TERMINAL_2546_RUNTIME_VM_VERIFICATION_METHOD
                    )
                    and (
                        (
                            bound_terminal_2546_action
                            in {
                                "runtime_promotion",
                                (
                                    "translation_override_and_"
                                    "runtime_promotion"
                                ),
                            }
                            and bound_terminal_2546_predecessor.get(
                                "runtime_review"
                            )
                            == "pending"
                            and evidence.get(
                                "preexisting_verified_evidence_renewed"
                            )
                            is False
                        )
                        or (
                            bound_terminal_2546_action
                            in {
                                "verification_renewal",
                                (
                                    "translation_override_and_"
                                    "verification_renewal"
                                ),
                            }
                            and bound_terminal_2546_predecessor.get(
                                "runtime_review"
                            )
                            == "verified"
                            and evidence.get(
                                "preexisting_verified_evidence_renewed"
                            )
                            is True
                        )
                    )
                )
                bound_terminal_2546_transition = (
                    evidence.get("method")
                    == (
                        ENGINE
                        .PK_BOUND_TERMINAL_2546_RUNTIME_VM_VERIFICATION_METHOD
                    )
                    and bound_terminal_2546_predecessor_state_matches
                    and isinstance(
                        evidence.get("predecessor_binding"),
                        dict,
                    )
                    and evidence["predecessor_binding"].get(
                        "row_sha256"
                    )
                    == ENGINE.canonical_sha256(
                        bound_terminal_2546_predecessor
                    )
                    and evidence.get("closure_binding", {}).get(
                        "decision_coordinate_sha256"
                    )
                    == BOUND_TERMINAL_2546_DECISION_COORDINATE_SHA256
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
                    in {
                        "verification_renewal",
                        "translation_override_and_verification_renewal",
                    }
                    and evidence.get("method")
                    == ENGINE.PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD
                    and not caller_predecessor_renewal
                ):
                    raise RuntimeError(
                        "caller runtime evidence did not bind its verified "
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
                    evidence.get("method")
                    == (
                        ENGINE
                        .PK_BOUND_TERMINAL_2546_RUNTIME_VM_VERIFICATION_METHOD
                    )
                    and not bound_terminal_2546_transition
                ):
                    raise RuntimeError(
                        "bound-terminal 2546 transition did not bind its "
                        f"expected predecessor state: {key}"
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
                            (
                                "reversed_vm_pk_bound_terminal_caller_"
                                "full_closure_analysis"
                            ),
                            (
                                "reversed_vm_pk_bound_terminal_2546_"
                                "full_caller_closure"
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
                            or (
                                evidence.get("method")
                                == (
                                    "reversed_vm_pk_bound_terminal_caller_"
                                    "full_closure_analysis"
                                )
                                and evidence.get(
                                    "actual_promotion_binding",
                                    {},
                                ).get("manual_full_assembly_verified")
                                is True
                            )
                            or bound_terminal_2546_transition
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
                            caller_predecessor_renewal
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
            final_integrated_row = runtime_vm_final.get(key)
            if final_integrated_row is None:
                raise RuntimeError(
                    f"final runtime VM integrated decision is absent: {key}"
                )
            effective_row = final_integrated_row
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
    if consumed_caller_overrides != caller_override_coordinates:
        missing = sorted(
            caller_override_coordinates - consumed_caller_overrides
        )
        extra = sorted(
            consumed_caller_overrides - caller_override_coordinates
        )
        raise RuntimeError(
            "bound-terminal caller overrides were not exactly consumed: "
            f"missing={missing} extra={extra}"
        )
    runtime_vm_integration_metadata[
        "bound_terminal_caller_override_count"
    ] = len(consumed_caller_overrides)
    if (
        consumed_bound_terminal_2546_overrides
        != bound_terminal_2546_override_coordinates
    ):
        missing = sorted(
            bound_terminal_2546_override_coordinates
            - consumed_bound_terminal_2546_overrides
        )
        extra = sorted(
            consumed_bound_terminal_2546_overrides
            - bound_terminal_2546_override_coordinates
        )
        raise RuntimeError(
            "bound-terminal 2546 overrides were not exactly consumed: "
            f"missing={missing[:8]} extra={extra[:8]}"
        )
    if (
        consumed_bound_terminal_2546_superseded_terminal
        != BOUND_TERMINAL_2546_SUPERSEDED_TERMINAL_OVERRIDES
        or consumed_bound_terminal_2546_superseded_thought
        != BOUND_TERMINAL_2546_SUPERSEDED_THOUGHT_OVERRIDES
        or consumed_bound_terminal_2546_superseded_caller
        != BOUND_TERMINAL_2546_SUPERSEDED_CALLER_OVERRIDES
    ):
        raise RuntimeError(
            "bound-terminal 2546 superseded predecessor override sets "
            "were not exactly preserved"
        )
    if (
        bound_terminal_2546_override_coordinates
        & BOUND_TERMINAL_OVERRIDE_COORDINATES
        or bound_terminal_2546_override_coordinates
        & thought_predicate_override_coordinates
        or (
            bound_terminal_2546_override_coordinates
            & caller_override_coordinates
        )
        != BOUND_TERMINAL_2546_NEW_CALLER_OVERRIDE_OVERLAP
    ):
        raise RuntimeError(
            "bound-terminal 2546 override overlap universe drifted"
        )
    runtime_vm_integration_metadata.update(
        {
            "bound_terminal_2546_full_caller_override_count": len(
                consumed_bound_terminal_2546_overrides
            ),
            "bound_terminal_2546_superseded_terminal_override_count": len(
                consumed_bound_terminal_2546_superseded_terminal
            ),
            "bound_terminal_2546_superseded_thought_override_count": len(
                consumed_bound_terminal_2546_superseded_thought
            ),
            "bound_terminal_2546_superseded_caller_override_count": len(
                consumed_bound_terminal_2546_superseded_caller
            ),
            "bound_terminal_2546_prior_caller_override_overlap_count": len(
                BOUND_TERMINAL_2546_NEW_CALLER_OVERRIDE_OVERLAP
            ),
        }
    )

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
    expected_scope_counts = Counter(
        {
            "confirmed_non_display": 345,
            "retranslated": 45_190,
            "runtime_fragment_pending": 7_268,
        }
    )
    if (
        total_targets != 52_803
        or approved != 52_803
        or pending != 7_268
        or eligible != 45_535
        or scope_classification_counts != expected_scope_counts
    ):
        raise RuntimeError(
            "post-selector568/1096/1174 progress totals drifted: "
            f"targets={total_targets} approved={approved} "
            f"pending={pending} eligible={eligible} "
            f"scope={dict(scope_classification_counts)}"
        )
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
