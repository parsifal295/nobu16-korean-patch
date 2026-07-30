#!/usr/bin/env python3
"""Repair two PK bound-ending families on the frozen honorific checkpoint.

The fourteen terminal literals are data-driven VM endings.  Their predecessor
translations incorrectly own a lexical Korean predicate even though callers
already supply the predicate stem.  This independent layer removes that
predicate, renews every previously verified PK evidence row whose closure
reaches either terminal family, and promotes only four conservatively reviewed
pending rows.

Tracked reports contain hashes, coordinates, counts, and predicates only.
Decision bodies and evidence overlays stay below ``tmp``.  Steam is read only.
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
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
HONORIFIC_BUILDER_PATH = (
    WORKSTREAM / "build_dynamic_honorific_spacing_closure_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_dynamic_honorific_checkpoint.private.v1.jsonl"
)
CHECKPOINT_REPORT_PATH = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration.post_dynamic_honorific_checkpoint.source_free.v1.json"
)
CHECKPOINT_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM
    / "build_runtime_vm_post_dynamic_honorific_checkpoint_v1.py"
)
GHIDRA_VM_CONTRACT_PATH = WORKSTREAM / "ghidra_pk_vm_contract.v1.json"
GHIDRA_LAYOUT_CONTRACT_PATH = (
    WORKSTREAM / "ghidra_pk_msggame_layout_contract.v1.json"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_family_exact_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_family_exact_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    OVERRIDE_DIR
    / "pk_bound_terminal_family_exact_integrated_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    OVERLAY_DIR
    / "pk_bound_terminal_family_exact_closure_evidence.private.v1.jsonl"
)

LIVE_STEAM_BASE = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin"
)
LIVE_STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

AUDIT_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-family-exact-closure-coverage.v1"
)
PROMOTION_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-family-exact-closure-promotion.v1"
)
EVIDENCE_ROW_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-family-exact-closure-evidence-row.v1"
)
METHOD = "reversed_vm_pk_bound_terminal_family_exact_closure_analysis"

EXPECTED_HONORIFIC_BUILDER_SHA256 = (
    "0B48E3A5B418637240E0A2BDC472FB8144E7981B926DEE902351790906D65C4A"
)
EXPECTED_CHECKPOINT_PRIVATE_SHA256 = (
    "D8BF282386F081F5B4B26674653DD3A085A8FF490E3043B6B4AF1BAB3F3A1CC2"
)
EXPECTED_CHECKPOINT_REPORT_SHA256 = (
    "1F38F0B45DA6D7FBFDCC47F2F2C1E5353F89DBA862A86799D1F20C6C69B09F5D"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256 = (
    "23DDA0392ED1DE56B9438FDE010074BA5F5AF6AB30AB416852C527BC4A827DF0"
)
EXPECTED_GHIDRA_VM_CONTRACT_SHA256 = (
    "21DAF83330F278484BFB2462188804947A6C457F4B072DA80D7ADFBD3D13F461"
)
EXPECTED_GHIDRA_LAYOUT_CONTRACT_SHA256 = (
    "EE28501EE41586025518325DE5CEE9722B99E1063FBE7B8E9049DFA6E310F9AC"
)
EXPECTED_BASE_PRISTINE_SHA256 = (
    "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4"
)
EXPECTED_BASE_CURRENT_SHA256 = (
    "3886D081E26AC2DEE75D8799CF839FEF2EFC6D27433FCD04C5FD43B4D23FD23A"
)
EXPECTED_PK_PRISTINE_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PK_CURRENT_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING_ROWS = 8_645
EXPECTED_PREDECESSOR_PENDING_ROOTS = 5_151
EXPECTED_BASE_PREDECESSOR_CANDIDATE_SHA256 = (
    "44828B27368FB74EF906DC167DCAF1BA54129A4313F7EDA3C0668777BB86E276"
)
EXPECTED_PK_PREDECESSOR_CANDIDATE_SHA256 = (
    "18F9E09F7D0FE71317733208B25B22EE47A45B5D927C2B583F6AA44B8019D41E"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "902CD3A1372BC19ABCA846C6A9F43195085C0782994ECFCE8A8353B2F9E0A628"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "FEBEB0D830C5820B55B4E9C8CF6B99D8734FA09A5CF3BEF2504D968E45C5AF15"
)
EXPECTED_OVERRIDE_MANIFEST_SHA256 = (
    "8D8FA45A379098A0E6FDF311DB5879E632B3C5AC9DD51DF03EA1A911B27031A0"
)
EXPECTED_TARGET_DELTA_MANIFEST_SHA256 = (
    "88500664C52652650D388A7C51EC60C3FC83BB9EFF2AF501021E40AA2B33CF47"
)
EXPECTED_ROOT_DELTA_PROOF_MANIFEST_SHA256 = (
    "3D61DF1B87F28AAD703B28D6FFE9D1A4BF53993F7B58F6AAE89C9D6766F238DD"
)
EXPECTED_AFFECTED_RECORDS = 731
EXPECTED_AFFECTED_RECORD_SHA256 = (
    "383AF83EBD0DC3B10DB1480FB431E569061800AF17084511547C2269FA75DC89"
)
EXPECTED_VERIFIED_RENEWAL_ROWS = 685
EXPECTED_VERIFIED_RENEWAL_ROOTS = 382
EXPECTED_VERIFIED_RENEWAL_COORDINATE_SHA256 = (
    "5EE0736B1EF15AC4C6FD52BB87EB99CE80719A8F725597A1D009B2027C2A49BF"
)
EXPECTED_VERIFIED_RENEWAL_ROOT_SHA256 = (
    "6D5A4769255C6A0B311DBFFF5F8ADA1138D4452DED09912761819FD19F387F22"
)
EXPECTED_AFFECTED_PENDING_ROWS = 920
EXPECTED_AFFECTED_PENDING_ROOTS = 430
EXPECTED_AFFECTED_PENDING_COORDINATE_SHA256 = (
    "C39E49A41CA826BE3E72965979462B5766FF585D3F5ABA98929A37CA6631496B"
)
EXPECTED_AFFECTED_PENDING_ROOT_SHA256 = (
    "61FD27A732C750E415A0F1FB188A49C7EB5147A500BC6FDCF9E43E598CF1480C"
)
EXPECTED_MACHINE_ELIGIBLE_ROWS = 22
EXPECTED_MACHINE_ELIGIBLE_ROOTS = 12
EXPECTED_MACHINE_ELIGIBLE_COORDINATE_SHA256 = (
    "A06442F6F5886DBE58EDF4F361F2B8621399F40F719DDDB278D1A6F4FB6E7A41"
)
EXPECTED_MACHINE_ELIGIBLE_ROOT_SHA256 = (
    "38F1BAF2D3AF7F78487F50EEC040D61DA6747F3101EDA062667C167964863EA1"
)
EXPECTED_ELIGIBLE_ROWS = 4
EXPECTED_ELIGIBLE_ROOTS = 4
EXPECTED_ELIGIBLE_COORDINATE_SHA256 = (
    "4DF163871B35C27A3A241492B9131F496C5A0EDC8EC4AA6055F17C358EA507F9"
)
EXPECTED_ELIGIBLE_ROOT_SHA256 = (
    "47E9F29977B5F25A8717A1FDF1A51D22CB0F61A7EDD692CBEE71A9ACD7A693EC"
)
EXPECTED_REJECTED_ROWS = 916
EXPECTED_REJECTED_ROOTS = 426
EXPECTED_REJECTED_COORDINATE_SHA256 = (
    "ECE23521BA93F5822F07CC3A8C969E30924947DDE46F7E72032F9F5A335B874C"
)
EXPECTED_REJECTED_ROOT_SHA256 = (
    "C11B5D1208D21973E3961980F29E540C3584E2C43C2F2CEA0336FA307B026565"
)
EXPECTED_PENDING_AFTER = 8_641
EXPECTED_DECISION_DELTA_ROWS = 695
EXPECTED_EVIDENCE_ROWS = 695
EXPECTED_AUDIT_PAYLOAD_SHA256 = (
    "4955A1F11075E895BBCC9A915AF62787121B601DDDBF026D65E2B315F9FBBCA6"
)
EXPECTED_AUDIT_FILE_SHA256 = (
    "132B857E1108BA42F1FBB9F410B1096576E52598D121111DFD4B67585F22CD3A"
)
EXPECTED_PROMOTION_FILE_SHA256 = (
    "50A60FD3B2F7E16DAFED4B1B67F5C925E6E09A57FEFEBD3125AD56433735A37D"
)
EXPECTED_DECISION_DELTA_FILE_SHA256 = (
    "74235120686C819652A4ADE6F0892C7F46D5155D6DB3837C0B9364858185EC1C"
)
EXPECTED_EVIDENCE_FILE_SHA256 = (
    "91C1E97FCC6FB65DFB769C8CD58B262CABC1A1827E58F0CAC6D34F31830F6DE7"
)

FAMILY_RECORDS = {
    "past_1916_1922": {(0, record_id) for record_id in range(1916, 1923)},
    "intent_2546_2552": {
        (0, record_id) for record_id in range(2546, 2553)
    },
}
TRANSLATION_OVERRIDES = {
    "0:1916:0": "\uc2b5\ub2c8\ub2e4",
    "0:1917:0": "\ub2e4",
    "0:1918:0": "\uc2b5\ub2c8\ub2e4",
    "0:1919:0": "\uc2b5\ub2c8\ub2e4",
    "0:1920:0": "\uc2b5\ub2c8\ub2e4",
    "0:1921:0": "\uc2b5\ub2c8\ub2e4",
    "0:1922:0": "\ub2e4",
    "0:2546:0": "\uaca0\uc2b5\ub2c8\ub2e4",
    "0:2547:0": "\uaca0\ub2e4",
    "0:2548:0": "\uaca0\uc0ac\uc635\ub2c8\ub2e4",
    "0:2549:0": "\uaca0\uc0ac\uc635\ub2c8\ub2e4",
    "0:2550:0": "\uaca0\uc2b5\ub2c8\ub2e4",
    "0:2551:0": "\uaca0\uc18c",
    "0:2552:0": "\uaca0\ub2e4",
}
PREDECESSOR_TRANSLATIONS = {
    "0:1916:0": "\ud588\uc2b5\ub2c8\ub2e4",
    "0:1917:0": "\ud588\ub2e4",
    "0:1918:0": "\ud588\uc2b5\ub2c8\ub2e4",
    "0:1919:0": "\ud588\uc2b5\ub2c8\ub2e4",
    "0:1920:0": "\ud588\uc2b5\ub2c8\ub2e4",
    "0:1921:0": "\ud588\uc2b5\ub2c8\ub2e4",
    "0:1922:0": "\ud588\ub2e4",
    "0:2546:0": "\ud558\uaca0\uc2b5\ub2c8\ub2e4",
    "0:2547:0": "\ud558\uaca0\ub2e4",
    "0:2548:0": "\ud558\uaca0\uc0ac\uc635\ub2c8\ub2e4",
    "0:2549:0": "\ud558\uaca0\uc0ac\uc635\ub2c8\ub2e4",
    "0:2550:0": "\ud558\uaca0\uc2b5\ub2c8\ub2e4",
    "0:2551:0": "\ud558\uaca0\uc18c",
    "0:2552:0": "\ud558\uaca0\ub2e4",
}
EXPECTED_CURRENT_CANDIDATE_WIDTHS = {
    "0:1916:0": (192, 144),
    "0:1917:0": (48, 48),
    "0:1918:0": (192, 144),
    "0:1919:0": (192, 144),
    "0:1920:0": (192, 144),
    "0:1921:0": (192, 144),
    "0:1922:0": (48, 48),
    "0:2546:0": (144, 192),
    "0:2547:0": (48, 96),
    "0:2548:0": (144, 240),
    "0:2549:0": (144, 240),
    "0:2550:0": (144, 192),
    "0:2551:0": (144, 96),
    "0:2552:0": (48, 96),
}
ACTUAL_ELIGIBLE_ROOTS = {
    (0, 1917),
    (0, 1922),
    (0, 2551),
    (8, 1241),
}
MANUAL_REJECT_REASONS = {
    (6, 3856): "source_tense_semantics_not_preserved",
    (6, 4350): "nominal_caller_requires_predicate_stem",
    (6, 4921): "nominal_caller_requires_predicate_stem",
    (9, 3509): "conjugation_boundary_incompatible",
    (9, 3513): "nominal_caller_requires_predicate_stem",
    (9, 3514): "nominal_caller_requires_predicate_stem",
    (9, 3515): "nominal_caller_requires_predicate_stem",
    (15, 1237): "conjugation_boundary_incompatible",
}


class TerminalFamilyError(ValueError):
    """Raised when the bound-ending family proof drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TerminalFamilyError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


HONORIFIC = load_module(
    "pk_bound_terminal_family_honorific_dependency",
    HONORIFIC_BUILDER_PATH,
)
CROSS = HONORIFIC.CROSS
BASE_AUDIT = HONORIFIC.BASE_AUDIT
ENGINE = HONORIFIC.ENGINE


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    require(path.is_file(), f"required file is absent: {path}")
    return sha256_bytes(path.read_bytes())


def canonical_sha256(value: Any) -> str:
    return HONORIFIC.canonical_sha256(value)


def canonical_json(value: Mapping[str, Any]) -> str:
    return HONORIFIC.canonical_json(value)


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return HONORIFIC.canonical_jsonl(rows)


def coordinate_digest(values: Iterable[str]) -> str:
    return HONORIFIC.coordinate_digest(values)


def record_digest(values: Iterable[tuple[int, int]]) -> str:
    return HONORIFIC.record_digest(values)


def row_sort_key(row: Mapping[str, Any]) -> tuple[int, int, int, int]:
    return HONORIFIC.row_sort_key(row)


def file_bindings() -> dict[str, str]:
    bindings = {
        "honorific_builder_sha256": sha256_file(HONORIFIC_BUILDER_PATH),
        "checkpoint_private_sha256": sha256_file(CHECKPOINT_PRIVATE_PATH),
        "checkpoint_report_file_sha256": sha256_file(
            CHECKPOINT_REPORT_PATH
        ),
        "checkpoint_builder_sha256": sha256_file(CHECKPOINT_BUILDER_PATH),
        "ghidra_vm_contract_file_sha256": sha256_file(
            GHIDRA_VM_CONTRACT_PATH
        ),
        "ghidra_layout_contract_file_sha256": sha256_file(
            GHIDRA_LAYOUT_CONTRACT_PATH
        ),
        "base_pristine_sha256": sha256_file(
            BASE_AUDIT.DEFAULT_BASE_PRISTINE
        ),
        "base_current_sha256": sha256_file(BASE_AUDIT.DEFAULT_BASE_CURRENT),
        "pk_pristine_sha256": sha256_file(BASE_AUDIT.DEFAULT_PK_PRISTINE),
        "pk_current_sha256": sha256_file(BASE_AUDIT.DEFAULT_PK_CURRENT),
    }
    expected = {
        "honorific_builder_sha256":
        EXPECTED_HONORIFIC_BUILDER_SHA256,
        "checkpoint_private_sha256":
        EXPECTED_CHECKPOINT_PRIVATE_SHA256,
        "checkpoint_report_file_sha256":
        EXPECTED_CHECKPOINT_REPORT_SHA256,
        "checkpoint_builder_sha256":
        EXPECTED_CHECKPOINT_BUILDER_SHA256,
        "ghidra_vm_contract_file_sha256":
        EXPECTED_GHIDRA_VM_CONTRACT_SHA256,
        "ghidra_layout_contract_file_sha256":
        EXPECTED_GHIDRA_LAYOUT_CONTRACT_SHA256,
        "base_pristine_sha256": EXPECTED_BASE_PRISTINE_SHA256,
        "base_current_sha256": EXPECTED_BASE_CURRENT_SHA256,
        "pk_pristine_sha256": EXPECTED_PK_PRISTINE_SHA256,
        "pk_current_sha256": EXPECTED_PK_CURRENT_SHA256,
    }
    require(bindings == expected, f"bound input file drifted: {bindings}")
    contract = HONORIFIC.verify_contracts()
    require(
        contract["vm_file_sha256"]
        == EXPECTED_GHIDRA_VM_CONTRACT_SHA256
        and contract["layout_file_sha256"]
        == EXPECTED_GHIDRA_LAYOUT_CONTRACT_SHA256
        and contract["automatic_space_inserted"] is False
        and contract["current_relative_nonexpansion_widget_independent"]
        is True,
        "Ghidra VM/layout contract drifted",
    )
    bindings["ghidra_program_sha256"] = contract["program_sha256"]
    return bindings


def load_checkpoint() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[str, Any],
]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for line in CHECKPOINT_PRIVATE_PATH.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = json.loads(line)
        require(isinstance(row, dict), "checkpoint row is not an object")
        key = (str(row["resource"]), str(row["coordinate"]))
        require(key not in rows, f"duplicate checkpoint row: {key}")
        rows[key] = row
    pending = [
        coordinate
        for (resource, coordinate), row in rows.items()
        if row.get("runtime_review") == "pending"
    ]
    pending_roots = {
        (resource, *BASE_AUDIT.parse_literal_coordinate(coordinate)[:2])
        for (resource, coordinate), row in rows.items()
        if row.get("runtime_review") == "pending"
    }
    require(
        len(rows) == EXPECTED_PREDECESSOR_ROWS
        and len(pending) == EXPECTED_PREDECESSOR_PENDING_ROWS
        and len(pending_roots) == EXPECTED_PREDECESSOR_PENDING_ROOTS,
        "frozen post-honorific checkpoint universe drifted",
    )
    for coordinate, expected in PREDECESSOR_TRANSLATIONS.items():
        row = rows.get(("pk_msggame", coordinate))
        require(
            row is not None and row.get("translation") == expected,
            f"terminal predecessor translation drifted: {coordinate}",
        )
    return rows, {
        "rows": len(rows),
        "pending_rows": len(pending),
        "pending_roots": len(pending_roots),
    }


def checkpoint_candidate(
    *,
    resource: str,
    checkpoint_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    apply_overrides: bool,
) -> tuple[bytes, dict[tuple[int, int], Any], list[dict[str, Any]]]:
    current_path = (
        BASE_AUDIT.DEFAULT_BASE_CURRENT
        if resource == "base_msggame"
        else BASE_AUDIT.DEFAULT_PK_CURRENT
    )
    replacements: dict[tuple[int, int, int], str] = {}
    manifest: list[dict[str, Any]] = []
    for (row_resource, coordinate), row in checkpoint_rows.items():
        if row_resource != resource or not isinstance(
            row.get("translation"), str
        ):
            continue
        text = str(row["translation"])
        if apply_overrides and resource == "pk_msggame":
            text = TRANSLATION_OVERRIDES.get(coordinate, text)
        replacements[BASE_AUDIT.parse_literal_coordinate(coordinate)] = text
        manifest.append(
            {
                "coordinate": coordinate,
                "translation_utf16le_sha256": ENGINE.sha256_text(text),
            }
        )
    manifest.sort(
        key=lambda row: BASE_AUDIT.parse_literal_coordinate(
            str(row["coordinate"])
        )
    )
    blob = BASE_AUDIT.rebuild_packed_with_literals(
        current_path.read_bytes(),
        replacements,
    )
    return blob, BASE_AUDIT.records_from_blob(blob), manifest


def repair_hard_risks(value: Any) -> int:
    changed = 0
    if isinstance(value, dict):
        for key, child in value.items():
            if (
                key in CROSS.PK_ONLY.HARD_TRUE_GRAMMAR_RISK_FIELDS
                and child is True
            ):
                value[key] = False
                changed += 1
            elif (
                key in CROSS.PK_ONLY.HARD_FALSE_GRAMMAR_RISK_FIELDS
                and child is False
            ):
                value[key] = True
                changed += 1
            else:
                changed += repair_hard_risks(child)
    elif isinstance(value, list):
        changed += sum(repair_hard_risks(child) for child in value)
    return changed


def repaired_pk_decisions(
    checkpoint_rows: Mapping[tuple[str, str], Mapping[str, Any]],
) -> tuple[
    dict[tuple[int, int], list[dict[str, Any]]],
    dict[str, dict[str, Any]],
    int,
]:
    by_record: defaultdict[tuple[int, int], list[dict[str, Any]]] = (
        defaultdict(list)
    )
    by_coordinate: dict[str, dict[str, Any]] = {}
    repaired_risks = 0
    for (resource, coordinate), predecessor in checkpoint_rows.items():
        if resource != "pk_msggame":
            continue
        row = copy.deepcopy(dict(predecessor))
        if coordinate in TRANSLATION_OVERRIDES:
            row["translation"] = TRANSLATION_OVERRIDES[coordinate]
            repaired_risks += repair_hard_risks(row)
            row["terminal_family_exact_override_evidence"] = {
                "schema":
                "nobu16.kr.pk-bound-terminal-family-exact-override.v1",
                "bound_ending_only": True,
                "lexical_predicate_removed": True,
                "caller_predicate_stem_required": True,
                "automatic_space_inserted": False,
                "all_register_branches_preserved": True,
                "translation_utf16le_sha256": ENGINE.sha256_text(
                    str(row["translation"])
                ),
            }
        root = BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        by_record[root].append(row)
        by_coordinate[coordinate] = row
    require(repaired_risks == 7, "terminal hard-risk repair count drifted")
    return dict(by_record), by_coordinate, repaired_risks


def target_delta_manifest(
    *,
    source_records: Mapping[tuple[int, int], Any],
    current_records: Mapping[tuple[int, int], Any],
    predecessor_records: Mapping[tuple[int, int], Any],
    candidate_records: Mapping[tuple[int, int], Any],
) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for coordinate in sorted(
        TRANSLATION_OVERRIDES,
        key=BASE_AUDIT.parse_literal_coordinate,
    ):
        root = BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        source = source_records[root]
        current = current_records[root]
        predecessor = predecessor_records[root]
        candidate = candidate_records[root]
        signatures = [
            HONORIFIC.component_signatures(record)
            for record in (source, current, predecessor, candidate)
        ]
        require(
            signatures.count(signatures[0]) == len(signatures),
            f"terminal control signature drifted: {coordinate}",
        )
        current_literals = BASE_AUDIT.parse_record_literals(current)
        predecessor_literals = BASE_AUDIT.parse_record_literals(predecessor)
        candidate_literals = BASE_AUDIT.parse_record_literals(candidate)
        require(
            len(current_literals)
            == len(predecessor_literals)
            == len(candidate_literals)
            == 1,
            f"terminal literal arity drifted: {coordinate}",
        )
        current_width = CROSS.RESIDUAL_AUDIT.raw_line_widths(
            current_literals[0].text
        )
        candidate_width = CROSS.RESIDUAL_AUDIT.raw_line_widths(
            candidate_literals[0].text
        )
        require(
            current_width == (EXPECTED_CURRENT_CANDIDATE_WIDTHS[coordinate][0],)
            and candidate_width
            == (EXPECTED_CURRENT_CANDIDATE_WIDTHS[coordinate][1],)
            and predecessor_literals[0].text
            == PREDECESSOR_TRANSLATIONS[coordinate]
            and candidate_literals[0].text
            == TRANSLATION_OVERRIDES[coordinate]
            and ENGINE.record_gap_bytes(source)
            == ENGINE.record_gap_bytes(current)
            == ENGINE.record_gap_bytes(predecessor)
            == ENGINE.record_gap_bytes(candidate),
            f"terminal literal/gap/width drifted: {coordinate}",
        )
        manifest.append(
            {
                "coordinate": coordinate,
                "record": list(root),
                "source_record_sha256": sha256_bytes(source.data),
                "current_record_sha256": sha256_bytes(current.data),
                "predecessor_record_sha256": sha256_bytes(predecessor.data),
                "candidate_record_sha256": sha256_bytes(candidate.data),
                "component_sha256": canonical_sha256(signatures[0]),
                "current_literal_utf16le_sha256": ENGINE.sha256_text(
                    current_literals[0].text
                ),
                "predecessor_literal_utf16le_sha256": ENGINE.sha256_text(
                    predecessor_literals[0].text
                ),
                "candidate_literal_utf16le_sha256": ENGINE.sha256_text(
                    candidate_literals[0].text
                ),
                "current_raw_g1n_widths": list(current_width),
                "candidate_raw_g1n_widths": list(candidate_width),
                "current_relative_nonexpanding":
                candidate_width[0] <= current_width[0],
                "bound_ending_only": True,
                "lexical_predicate_removed": True,
            }
        )
    return manifest


def member_coordinates(
    roots: Iterable[tuple[int, int]],
    by_root: Mapping[tuple[int, int], Sequence[str]],
) -> list[str]:
    return [
        coordinate
        for root in sorted(roots)
        for coordinate in by_root[root]
    ]


def digest_summary(
    roots: set[tuple[int, int]],
    by_root: Mapping[tuple[int, int], Sequence[str]],
) -> dict[str, Any]:
    coordinates = member_coordinates(roots, by_root)
    return {
        "rows": len(coordinates),
        "roots": len(roots),
        "coordinate_sha256": coordinate_digest(coordinates),
        "record_sha256": record_digest(roots),
    }


def build_analysis(
    checkpoint_rows: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    (
        base_predecessor_blob,
        base_predecessor_records,
        base_predecessor_manifest,
    ) = checkpoint_candidate(
        resource="base_msggame",
        checkpoint_rows=checkpoint_rows,
        apply_overrides=False,
    )
    (
        pk_predecessor_blob,
        pk_predecessor_records,
        pk_predecessor_manifest,
    ) = checkpoint_candidate(
        resource="pk_msggame",
        checkpoint_rows=checkpoint_rows,
        apply_overrides=False,
    )
    pk_candidate_blob, pk_candidate_records, pk_candidate_manifest = (
        checkpoint_candidate(
            resource="pk_msggame",
            checkpoint_rows=checkpoint_rows,
            apply_overrides=True,
        )
    )
    require(
        sha256_bytes(base_predecessor_blob)
        == EXPECTED_BASE_PREDECESSOR_CANDIDATE_SHA256
        and sha256_bytes(pk_predecessor_blob)
        == EXPECTED_PK_PREDECESSOR_CANDIDATE_SHA256
        and sha256_bytes(pk_candidate_blob) == EXPECTED_PK_CANDIDATE_SHA256,
        "full packed candidate hash drifted",
    )
    require(
        base_predecessor_manifest
        == checkpoint_candidate(
            resource="base_msggame",
            checkpoint_rows=checkpoint_rows,
            apply_overrides=True,
        )[2],
        "PK-only override changed the Base replacement manifest",
    )
    override_manifest = [
        {
            "coordinate": coordinate,
            "translation_utf16le_sha256": ENGINE.sha256_text(
                TRANSLATION_OVERRIDES[coordinate]
            ),
        }
        for coordinate in sorted(
            TRANSLATION_OVERRIDES,
            key=BASE_AUDIT.parse_literal_coordinate,
        )
    ]
    require(
        coordinate_digest(TRANSLATION_OVERRIDES)
        == EXPECTED_OVERRIDE_COORDINATE_SHA256
        and canonical_sha256(override_manifest)
        == EXPECTED_OVERRIDE_MANIFEST_SHA256,
        "terminal override universe drifted",
    )
    changed = HONORIFIC.changed_record_guard(
        predecessor_records=pk_predecessor_records,
        candidate_records=pk_candidate_records,
        expected_changed=set().union(*FAMILY_RECORDS.values()),
    )
    source_records = BASE_AUDIT.archive_records(
        BASE_AUDIT.DEFAULT_PK_PRISTINE
    )[0]
    current_records = BASE_AUDIT.archive_records(
        BASE_AUDIT.DEFAULT_PK_CURRENT
    )[0]
    target_delta = target_delta_manifest(
        source_records=source_records,
        current_records=current_records,
        predecessor_records=pk_predecessor_records,
        candidate_records=pk_candidate_records,
    )
    target_delta_sha256 = canonical_sha256(target_delta)
    require(
        target_delta_sha256 == EXPECTED_TARGET_DELTA_MANIFEST_SHA256,
        "terminal target delta manifest drifted",
    )
    decisions_by_record, repaired_by_coordinate, repaired_risks = (
        repaired_pk_decisions(checkpoint_rows)
    )
    candidate_inputs = dataclasses.make_dataclass(
        "TerminalCandidateInputs",
        [
            ("pk_source_records", object),
            ("pk_current_records", object),
            ("pk_candidate_records", object),
        ],
    )(
        source_records,
        current_records,
        pk_candidate_records,
    )
    profiles, edges = CROSS.RESIDUAL_AUDIT.build_record_profiles(
        inputs=candidate_inputs
    )
    targets = set().union(*FAMILY_RECORDS.values())
    affected = HONORIFIC.reverse_ancestors(
        edges=edges,
        targets=tuple(targets),
    )
    require(
        len(affected) == EXPECTED_AFFECTED_RECORDS
        and record_digest(affected) == EXPECTED_AFFECTED_RECORD_SHA256,
        "affected terminal closure record universe drifted",
    )
    root_proofs = HONORIFIC.root_delta_proofs(
        resource="pk_msggame",
        affected_records=affected,
        edges=edges,
        target_records=targets,
        predecessor_records=pk_predecessor_records,
        candidate_records=pk_candidate_records,
        target_delta_sha256=target_delta_sha256,
    )
    root_proof_manifest_sha256 = canonical_sha256(
        {
            f"{root[0]}:{root[1]}": proof
            for root, proof in sorted(root_proofs.items())
        }
    )
    require(
        root_proof_manifest_sha256
        == EXPECTED_ROOT_DELTA_PROOF_MANIFEST_SHA256,
        "terminal root delta proof manifest drifted",
    )
    pending_by_root: defaultdict[tuple[int, int], list[str]] = defaultdict(list)
    verified_by_root: defaultdict[tuple[int, int], list[str]] = (
        defaultdict(list)
    )
    for (resource, coordinate), row in checkpoint_rows.items():
        if resource != "pk_msggame":
            continue
        root = BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        if row.get("runtime_review") == "pending":
            pending_by_root[root].append(coordinate)
        elif row.get("runtime_review") == "verified":
            verified_by_root[root].append(coordinate)
    for mapping in (pending_by_root, verified_by_root):
        for coordinates in mapping.values():
            coordinates.sort(key=BASE_AUDIT.parse_literal_coordinate)
    affected_pending_roots = set(pending_by_root) & affected
    affected_verified_roots = set(verified_by_root) & affected
    pending_summary = digest_summary(affected_pending_roots, pending_by_root)
    verified_summary = digest_summary(
        affected_verified_roots,
        verified_by_root,
    )
    require(
        pending_summary
        == {
            "rows": EXPECTED_AFFECTED_PENDING_ROWS,
            "roots": EXPECTED_AFFECTED_PENDING_ROOTS,
            "coordinate_sha256":
            EXPECTED_AFFECTED_PENDING_COORDINATE_SHA256,
            "record_sha256": EXPECTED_AFFECTED_PENDING_ROOT_SHA256,
        }
        and verified_summary
        == {
            "rows": EXPECTED_VERIFIED_RENEWAL_ROWS,
            "roots": EXPECTED_VERIFIED_RENEWAL_ROOTS,
            "coordinate_sha256":
            EXPECTED_VERIFIED_RENEWAL_COORDINATE_SHA256,
            "record_sha256": EXPECTED_VERIFIED_RENEWAL_ROOT_SHA256,
        },
        "affected pending/verified row universe drifted",
    )
    machine_entries: dict[tuple[int, int], dict[str, Any]] = {}
    for root in sorted(affected_pending_roots):
        guard = CROSS.PK_ONLY.closure_guard(
            root,
            inputs=candidate_inputs,
            decisions_by_record=decisions_by_record,
        )
        layout = CROSS.relative_layout_closure_guard(
            root,
            profiles=profiles,
            edges=edges,
        )
        machine_entries[root] = {
            "root": list(root),
            "member_coordinates": pending_by_root[root],
            "member_coordinate_sha256": coordinate_digest(
                pending_by_root[root]
            ),
            "closure_guard": guard,
            "relative_layout_guard": layout,
            "root_delta_proof_sha256": root_proofs[root]["proof_sha256"],
        }
    machine_roots = {
        root
        for root, entry in machine_entries.items()
        if CROSS.target_guard_passes(entry["closure_guard"])
        and entry["relative_layout_guard"]["status"] == "verified"
    }
    machine_summary = digest_summary(machine_roots, pending_by_root)
    require(
        machine_summary
        == {
            "rows": EXPECTED_MACHINE_ELIGIBLE_ROWS,
            "roots": EXPECTED_MACHINE_ELIGIBLE_ROOTS,
            "coordinate_sha256":
            EXPECTED_MACHINE_ELIGIBLE_COORDINATE_SHA256,
            "record_sha256": EXPECTED_MACHINE_ELIGIBLE_ROOT_SHA256,
        }
        and ACTUAL_ELIGIBLE_ROOTS <= machine_roots
        and machine_roots - ACTUAL_ELIGIBLE_ROOTS
        == set(MANUAL_REJECT_REASONS),
        "machine/manual terminal adjudication drifted",
    )
    rejected_roots = affected_pending_roots - ACTUAL_ELIGIBLE_ROOTS
    eligible_summary = digest_summary(ACTUAL_ELIGIBLE_ROOTS, pending_by_root)
    rejected_summary = digest_summary(rejected_roots, pending_by_root)
    require(
        eligible_summary
        == {
            "rows": EXPECTED_ELIGIBLE_ROWS,
            "roots": EXPECTED_ELIGIBLE_ROOTS,
            "coordinate_sha256": EXPECTED_ELIGIBLE_COORDINATE_SHA256,
            "record_sha256": EXPECTED_ELIGIBLE_ROOT_SHA256,
        }
        and rejected_summary
        == {
            "rows": EXPECTED_REJECTED_ROWS,
            "roots": EXPECTED_REJECTED_ROOTS,
            "coordinate_sha256": EXPECTED_REJECTED_COORDINATE_SHA256,
            "record_sha256": EXPECTED_REJECTED_ROOT_SHA256,
        },
        "actual terminal adjudication digest drifted",
    )
    family_summaries: dict[str, dict[str, Any]] = {}
    for family, family_targets in FAMILY_RECORDS.items():
        family_affected = HONORIFIC.reverse_ancestors(
            edges=edges,
            targets=tuple(family_targets),
        )
        roots = affected_pending_roots & family_affected
        eligible = roots & ACTUAL_ELIGIBLE_ROOTS
        family_summaries[family] = {
            "affected": digest_summary(roots, pending_by_root),
            "eligible": digest_summary(eligible, pending_by_root),
            "rejected": digest_summary(roots - eligible, pending_by_root),
        }
    rejection_reason_rows: Counter[str] = Counter()
    rejection_reason_roots: Counter[str] = Counter()
    for root in sorted(rejected_roots):
        entry = machine_entries[root]
        reasons = set(entry["closure_guard"]["failure_codes"])
        reasons.update(entry["relative_layout_guard"]["reason_codes"])
        if root in MANUAL_REJECT_REASONS:
            reasons.add(MANUAL_REJECT_REASONS[root])
        for reason in reasons:
            rejection_reason_roots[reason] += 1
            rejection_reason_rows[reason] += len(pending_by_root[root])
    return {
        "base_predecessor_blob": base_predecessor_blob,
        "base_predecessor_records": base_predecessor_records,
        "base_predecessor_manifest": base_predecessor_manifest,
        "pk_predecessor_blob": pk_predecessor_blob,
        "pk_predecessor_records": pk_predecessor_records,
        "pk_predecessor_manifest": pk_predecessor_manifest,
        "pk_candidate_blob": pk_candidate_blob,
        "pk_candidate_records": pk_candidate_records,
        "pk_candidate_manifest": pk_candidate_manifest,
        "override_manifest": override_manifest,
        "changed": changed,
        "target_delta": target_delta,
        "target_delta_sha256": target_delta_sha256,
        "repaired_by_coordinate": repaired_by_coordinate,
        "repaired_risks": repaired_risks,
        "candidate_inputs": candidate_inputs,
        "profiles": profiles,
        "edges": edges,
        "targets": targets,
        "affected": affected,
        "root_proofs": root_proofs,
        "root_proof_manifest_sha256": root_proof_manifest_sha256,
        "pending_by_root": dict(pending_by_root),
        "verified_by_root": dict(verified_by_root),
        "affected_pending_roots": affected_pending_roots,
        "affected_verified_roots": affected_verified_roots,
        "pending_summary": pending_summary,
        "verified_summary": verified_summary,
        "machine_entries": machine_entries,
        "machine_roots": machine_roots,
        "machine_summary": machine_summary,
        "eligible_roots": ACTUAL_ELIGIBLE_ROOTS,
        "eligible_summary": eligible_summary,
        "rejected_roots": rejected_roots,
        "rejected_summary": rejected_summary,
        "family_summaries": family_summaries,
        "rejection_reason_rows": dict(sorted(rejection_reason_rows.items())),
        "rejection_reason_roots": dict(
            sorted(rejection_reason_roots.items())
        ),
    }


def public_machine_manifest(
    analysis: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    eligible: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for root in sorted(analysis["affected_pending_roots"]):
        entry = analysis["machine_entries"][root]
        base = {
            "root": list(root),
            "member_coordinate_sha256": entry[
                "member_coordinate_sha256"
            ],
            "closure_guard_sha256": entry["closure_guard"]["proof_sha256"],
            "relative_layout_guard_sha256": entry[
                "relative_layout_guard"
            ]["proof_sha256"],
            "root_delta_proof_sha256": entry[
                "root_delta_proof_sha256"
            ],
        }
        if root in analysis["eligible_roots"]:
            eligible.append(base)
            continue
        reasons = set(entry["closure_guard"]["failure_codes"])
        reasons.update(entry["relative_layout_guard"]["reason_codes"])
        manual_reason = MANUAL_REJECT_REASONS.get(root)
        if manual_reason is not None:
            reasons.add(manual_reason)
        rejected.append(
            {
                **base,
                "reason_codes": sorted(reasons),
                "manual_full_assembly_rejected":
                manual_reason is not None,
            }
        )
    return eligible, rejected


def build_audit(
    *,
    analysis: Mapping[str, Any],
    checkpoint_metadata: Mapping[str, Any],
    bindings: Mapping[str, str],
) -> dict[str, Any]:
    eligible_manifest, rejected_manifest = public_machine_manifest(analysis)
    report = {
        "schema": AUDIT_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "scope": {
            "predecessor_rows": checkpoint_metadata["rows"],
            "predecessor_pending_rows": checkpoint_metadata["pending_rows"],
            "translation_override_rows": len(TRANSLATION_OVERRIDES),
            "changed_pk_records": len(analysis["targets"]),
            "affected_pk_records": len(analysis["affected"]),
            "affected_existing_verified_pk_rows":
            EXPECTED_VERIFIED_RENEWAL_ROWS,
            "affected_existing_verified_pk_roots":
            EXPECTED_VERIFIED_RENEWAL_ROOTS,
            "affected_existing_verified_base_rows": 0,
            "affected_pending_pk_rows": EXPECTED_AFFECTED_PENDING_ROWS,
            "affected_pending_pk_roots": EXPECTED_AFFECTED_PENDING_ROOTS,
            "machine_eligible_rows": EXPECTED_MACHINE_ELIGIBLE_ROWS,
            "machine_eligible_roots": EXPECTED_MACHINE_ELIGIBLE_ROOTS,
            "actual_eligible_rows": EXPECTED_ELIGIBLE_ROWS,
            "actual_eligible_roots": EXPECTED_ELIGIBLE_ROOTS,
            "actual_rejected_rows": EXPECTED_REJECTED_ROWS,
            "actual_rejected_roots": EXPECTED_REJECTED_ROOTS,
            "post_layer_pending_rows": EXPECTED_PENDING_AFTER,
        },
        "adjudication": {
            "terminal_literals_are_bound_endings": True,
            "lexical_predicate_removed_from_terminal_family": True,
            "caller_predicate_stem_required": True,
            "automatic_space_inserted": False,
            "register_branch_matrix_preserved": True,
            "control_bytes_preserved": True,
            "current_relative_raw_g1n_full_closure_gate": True,
            "manual_full_assembly_review_after_machine_gate": True,
            "uncertain_roots_remain_rejected": True,
            "preexisting_verified_state_renewed_not_repromoted": True,
            "base_resource_changed": False,
        },
        "families": analysis["family_summaries"],
        "eligible_coordinates": member_coordinates(
            analysis["eligible_roots"],
            analysis["pending_by_root"],
        ),
        "manual_rejected_roots": [
            {
                "root": list(root),
                "reason_code": MANUAL_REJECT_REASONS[root],
            }
            for root in sorted(MANUAL_REJECT_REASONS)
        ],
        "rejection_reason_rows": analysis["rejection_reason_rows"],
        "rejection_reason_roots": analysis["rejection_reason_roots"],
        "eligible_manifest_sha256": canonical_sha256(eligible_manifest),
        "rejected_manifest_sha256": canonical_sha256(rejected_manifest),
        "guards": {
            **dict(bindings),
            "checkpoint_git_commit":
            "bde654aaea2fae23da486232f44a5c3132a667de",
            "base_predecessor_candidate_packed_sha256":
            sha256_bytes(analysis["base_predecessor_blob"]),
            "pk_predecessor_candidate_packed_sha256":
            sha256_bytes(analysis["pk_predecessor_blob"]),
            "pk_candidate_packed_sha256":
            sha256_bytes(analysis["pk_candidate_blob"]),
            "override_coordinate_sha256":
            EXPECTED_OVERRIDE_COORDINATE_SHA256,
            "override_manifest_sha256":
            EXPECTED_OVERRIDE_MANIFEST_SHA256,
            "target_delta_manifest_sha256":
            analysis["target_delta_sha256"],
            "affected_record_sha256":
            EXPECTED_AFFECTED_RECORD_SHA256,
            "verified_renewal_coordinate_sha256":
            EXPECTED_VERIFIED_RENEWAL_COORDINATE_SHA256,
            "verified_renewal_root_sha256":
            EXPECTED_VERIFIED_RENEWAL_ROOT_SHA256,
            "affected_pending_coordinate_sha256":
            EXPECTED_AFFECTED_PENDING_COORDINATE_SHA256,
            "affected_pending_root_sha256":
            EXPECTED_AFFECTED_PENDING_ROOT_SHA256,
            "machine_eligible_coordinate_sha256":
            EXPECTED_MACHINE_ELIGIBLE_COORDINATE_SHA256,
            "machine_eligible_root_sha256":
            EXPECTED_MACHINE_ELIGIBLE_ROOT_SHA256,
            "actual_eligible_coordinate_sha256":
            EXPECTED_ELIGIBLE_COORDINATE_SHA256,
            "actual_eligible_root_sha256":
            EXPECTED_ELIGIBLE_ROOT_SHA256,
            "actual_rejected_coordinate_sha256":
            EXPECTED_REJECTED_COORDINATE_SHA256,
            "actual_rejected_root_sha256":
            EXPECTED_REJECTED_ROOT_SHA256,
            "root_delta_proof_manifest_sha256": canonical_sha256(
                {
                    f"{root[0]}:{root[1]}": proof
                    for root, proof in sorted(
                        analysis["root_proofs"].items()
                    )
                }
            ),
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_overlay_contains_translation_bodies": False,
        },
        "steam_write_performed": False,
    }
    return HONORIFIC.seal_report(report)


def evidence_row(
    *,
    coordinate: str,
    predecessor: Mapping[str, Any],
    action: str,
    status: str,
    root_proof: Mapping[str, Any],
    root_entry: Mapping[str, Any] | None,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    updated_translation: str,
) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "schema": EVIDENCE_ROW_SCHEMA,
        "resource": "pk_msggame",
        "coordinate": coordinate,
        "status": status,
        "method": METHOD,
        "action": action,
        "translation_utf16le_sha256": ENGINE.sha256_text(
            updated_translation
        ),
        "predecessor_integrated_binding": {
            "row_sha256": canonical_sha256(predecessor),
            "checkpoint_private_sha256": audit["guards"][
                "checkpoint_private_sha256"
            ],
            "checkpoint_report_file_sha256": audit["guards"][
                "checkpoint_report_file_sha256"
            ],
            "checkpoint_builder_sha256": audit["guards"][
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
        "terminal_family_delta_binding": {
            "root": root_proof["root"],
            "reachable_repaired_targets": root_proof[
                "reachable_repaired_targets"
            ],
            "root_delta_proof_sha256": root_proof["proof_sha256"],
            "target_delta_manifest_sha256": audit["guards"][
                "target_delta_manifest_sha256"
            ],
            "pk_candidate_packed_sha256": audit["guards"][
                "pk_candidate_packed_sha256"
            ],
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
        "preexisting_verified_evidence_renewed": (
            predecessor.get("runtime_review") == "verified"
        ),
        "per_row_game_playback_required": False,
    }
    if root_entry is not None:
        evidence["actual_promotion_binding"] = {
            "member_coordinate_sha256": root_entry[
                "member_coordinate_sha256"
            ],
            "closure_guard_sha256": root_entry["closure_guard"][
                "proof_sha256"
            ],
            "relative_layout_guard_sha256": root_entry[
                "relative_layout_guard"
            ]["proof_sha256"],
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
            "relative_full_closure_line_envelope_nonexpanding":
            root_entry["relative_layout_guard"][
                "relative_full_closure_line_envelope_nonexpanding"
            ],
            "manual_full_assembly_verified": True,
        }
    return evidence


def build_updated_rows(
    *,
    checkpoint_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    analysis: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    verified_coordinates = set(
        member_coordinates(
            analysis["affected_verified_roots"],
            analysis["verified_by_root"],
        )
    )
    eligible_coordinates = set(
        member_coordinates(
            analysis["eligible_roots"],
            analysis["pending_by_root"],
        )
    )
    pending_override_coordinates = {
        coordinate
        for coordinate in TRANSLATION_OVERRIDES
        if checkpoint_rows[("pk_msggame", coordinate)].get(
            "runtime_review"
        )
        == "pending"
    } - eligible_coordinates
    update_coordinates = (
        verified_coordinates
        | eligible_coordinates
        | pending_override_coordinates
    )
    require(
        len(update_coordinates) == EXPECTED_DECISION_DELTA_ROWS,
        "decision delta coordinate count drifted",
    )
    updated_rows: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    for coordinate in sorted(
        update_coordinates,
        key=BASE_AUDIT.parse_literal_coordinate,
    ):
        key = ("pk_msggame", coordinate)
        predecessor = checkpoint_rows[key]
        updated = copy.deepcopy(
            analysis["repaired_by_coordinate"][coordinate]
        )
        root = BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        is_override = coordinate in TRANSLATION_OVERRIDES
        is_promotion = coordinate in eligible_coordinates
        if is_override and is_promotion:
            action = "translation_override_and_runtime_promotion"
        elif is_override and predecessor.get("runtime_review") == "pending":
            action = "translation_override_pending"
        elif is_override:
            action = "translation_override"
        elif is_promotion:
            action = "runtime_promotion"
        else:
            action = "verification_renewal"
        if is_promotion:
            require(
                predecessor.get("runtime_review") == "pending"
                and predecessor.get("scope_classification")
                == "runtime_fragment_pending",
                f"promotion predecessor drifted: {coordinate}",
            )
            updated["runtime_review"] = "verified"
            updated["scope_classification"] = "retranslated"
            updated["layout_review"] = "runtime_verified"
        elif predecessor.get("runtime_review") == "verified":
            require(
                updated.get("runtime_review") == "verified",
                f"verified renewal state drifted: {coordinate}",
            )
        else:
            require(
                action == "translation_override_pending",
                f"unexpected pending delta action: {coordinate}",
            )
        status = (
            "verified"
            if updated.get("runtime_review") == "verified"
            else "pending"
        )
        root_entry = (
            analysis["machine_entries"][root] if is_promotion else None
        )
        evidence = evidence_row(
            coordinate=coordinate,
            predecessor=predecessor,
            action=action,
            status=status,
            root_proof=analysis["root_proofs"][root],
            root_entry=root_entry,
            audit=audit,
            audit_file_sha256=audit_file_sha256,
            updated_translation=str(updated["translation"]),
        )
        updated["terminal_family_update_action"] = action
        if status == "verified":
            updated["runtime_vm_verification"] = evidence
        else:
            updated["terminal_family_runtime_evidence"] = evidence
        updated_rows.append(updated)
        evidence_rows.append(evidence)
    updated_rows.sort(key=row_sort_key)
    evidence_rows.sort(
        key=lambda row: BASE_AUDIT.parse_literal_coordinate(
            str(row["coordinate"])
        )
    )
    return updated_rows, evidence_rows


def build_promotion_report(
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    decision_content: str,
    evidence_content: str,
    evidence_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    actions = Counter(str(row["action"]) for row in evidence_rows)
    report = {
        "schema": PROMOTION_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "method": METHOD,
        "result": {
            "translation_override_rows": 14,
            "existing_verified_pk_evidence_renewal_rows":
            EXPECTED_VERIFIED_RENEWAL_ROWS,
            "existing_verified_base_evidence_renewal_rows": 0,
            "runtime_promotion_rows": EXPECTED_ELIGIBLE_ROWS,
            "runtime_promotion_roots": EXPECTED_ELIGIBLE_ROOTS,
            "rejected_pending_rows": EXPECTED_REJECTED_ROWS,
            "pending_rows_after": EXPECTED_PENDING_AFTER,
            "decision_delta_rows": EXPECTED_DECISION_DELTA_ROWS,
            "private_evidence_rows": EXPECTED_EVIDENCE_ROWS,
            "private_decision_delta_sha256": sha256_bytes(
                decision_content.encode("utf-8")
            ),
            "private_evidence_sha256": sha256_bytes(
                evidence_content.encode("utf-8")
            ),
            "translation_body_copied_to_evidence_overlay": False,
        },
        "action_counts": dict(sorted(actions.items())),
        "evidence": {
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256": audit["guards"][
                "report_payload_sha256"
            ],
            "checkpoint_private_sha256": audit["guards"][
                "checkpoint_private_sha256"
            ],
            "pk_candidate_packed_sha256": audit["guards"][
                "pk_candidate_packed_sha256"
            ],
            "actual_eligible_coordinate_sha256":
            EXPECTED_ELIGIBLE_COORDINATE_SHA256,
            "actual_eligible_root_sha256": EXPECTED_ELIGIBLE_ROOT_SHA256,
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_overlay_contains_translation_bodies": False,
        },
        "steam_write_performed": False,
    }
    return HONORIFIC.seal_report(report)


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
    bindings = file_bindings()
    checkpoint_rows, checkpoint_metadata = load_checkpoint()
    analysis = build_analysis(checkpoint_rows)
    audit = build_audit(
        analysis=analysis,
        checkpoint_metadata=checkpoint_metadata,
        bindings=bindings,
    )
    HONORIFIC.validate_seal(audit)
    audit_content = canonical_json(audit)
    audit_file_sha256 = sha256_bytes(audit_content.encode("utf-8"))
    updated_rows, evidence_rows = build_updated_rows(
        checkpoint_rows=checkpoint_rows,
        analysis=analysis,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
    )
    decision_content = canonical_jsonl(updated_rows)
    evidence_content = canonical_jsonl(evidence_rows)
    promotion = build_promotion_report(
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        decision_content=decision_content,
        evidence_content=evidence_content,
        evidence_rows=evidence_rows,
    )
    HONORIFIC.validate_seal(promotion)
    promotion_content = canonical_json(promotion)
    steam_after = {
        "base": HONORIFIC.live_hash(LIVE_STEAM_BASE),
        "pk": HONORIFIC.live_hash(LIVE_STEAM_PK),
    }
    require(
        steam_before == steam_after,
        "live Steam msggame changed during terminal analysis",
    )
    return (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        {
            "checkpoint_rows": checkpoint_rows,
            "updated_rows": updated_rows,
            "evidence_rows": evidence_rows,
            "analysis": analysis,
            "promotion": promotion,
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
) -> None:
    require(
        decision_content == canonical_jsonl(bundle["updated_rows"])
        and evidence_content == canonical_jsonl(bundle["evidence_rows"])
        and audit_content == canonical_json(audit)
        and promotion_content == canonical_json(bundle["promotion"]),
        "terminal output serialization drifted",
    )
    require(
        audit["guards"]["report_payload_sha256"]
        == EXPECTED_AUDIT_PAYLOAD_SHA256
        and audit["guards"]["root_delta_proof_manifest_sha256"]
        == EXPECTED_ROOT_DELTA_PROOF_MANIFEST_SHA256
        and audit["guards"]["target_delta_manifest_sha256"]
        == EXPECTED_TARGET_DELTA_MANIFEST_SHA256
        and sha256_bytes(audit_content.encode("utf-8"))
        == EXPECTED_AUDIT_FILE_SHA256
        and sha256_bytes(promotion_content.encode("utf-8"))
        == EXPECTED_PROMOTION_FILE_SHA256
        and sha256_bytes(decision_content.encode("utf-8"))
        == EXPECTED_DECISION_DELTA_FILE_SHA256
        and sha256_bytes(evidence_content.encode("utf-8"))
        == EXPECTED_EVIDENCE_FILE_SHA256,
        "terminal full output digest drifted",
    )
    HONORIFIC.validate_seal(audit)
    HONORIFIC.validate_seal(bundle["promotion"])
    updated_by_key = {
        (str(row["resource"]), str(row["coordinate"])): row
        for row in bundle["updated_rows"]
    }
    require(
        len(updated_by_key) == EXPECTED_DECISION_DELTA_ROWS
        and len(bundle["evidence_rows"]) == EXPECTED_EVIDENCE_ROWS,
        "terminal decision/evidence row count drifted",
    )
    merged = {
        key: copy.deepcopy(dict(row))
        for key, row in bundle["checkpoint_rows"].items()
    }
    require(
        set(updated_by_key) <= set(merged),
        "terminal decision delta contains a foreign coordinate",
    )
    merged.update(updated_by_key)
    merged_pending = [
        key
        for key, row in merged.items()
        if row.get("runtime_review") == "pending"
    ]
    require(
        len(merged) == EXPECTED_PREDECESSOR_ROWS
        and len(merged_pending) == EXPECTED_PENDING_AFTER
        and all(
            row.get("resource") == "pk_msggame"
            for row in bundle["updated_rows"]
        ),
        "terminal decision delta does not merge cleanly over the checkpoint",
    )
    promoted = [
        row
        for row in bundle["updated_rows"]
        if row["terminal_family_update_action"]
        in {
            "runtime_promotion",
            "translation_override_and_runtime_promotion",
        }
    ]
    promoted_coordinates = [str(row["coordinate"]) for row in promoted]
    require(
        len(promoted) == EXPECTED_ELIGIBLE_ROWS
        and coordinate_digest(promoted_coordinates)
        == EXPECTED_ELIGIBLE_COORDINATE_SHA256
        and audit["scope"]["post_layer_pending_rows"]
        == EXPECTED_PENDING_AFTER
        and audit.get("steam_write_performed") is False
        and bundle["promotion"].get("steam_write_performed") is False,
        "terminal promotion result drifted",
    )
    override_rows = [
        row
        for row in bundle["updated_rows"]
        if str(row["coordinate"]) in TRANSLATION_OVERRIDES
    ]
    require(
        len(override_rows) == len(TRANSLATION_OVERRIDES)
        and all(
            row["translation"]
            == TRANSLATION_OVERRIDES[str(row["coordinate"])]
            for row in override_rows
        ),
        "terminal override body drifted",
    )
    for evidence in bundle["evidence_rows"]:
        require(
            "translation" not in evidence
            and evidence.get("per_row_game_playback_required") is False,
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
    return parser


def validate_output_paths(args: argparse.Namespace) -> None:
    private_root = DIALOGUE_TMP.resolve(strict=False)
    public_root = (WORKSTREAM / "public").resolve(strict=False)
    private_paths = (args.decision_output, args.evidence_output)
    public_paths = (args.audit_output, args.promotion_output)
    resolved: list[Path] = []
    for path in private_paths:
        value = path.resolve(strict=False)
        require(
            value != private_root and private_root in value.parents,
            f"private output must remain below {private_root}: {path}",
        )
        resolved.append(value)
    for path in public_paths:
        value = path.resolve(strict=False)
        require(
            value != public_root and public_root in value.parents,
            f"public output must remain below {public_root}: {path}",
        )
        resolved.append(value)
    live_paths = {
        LIVE_STEAM_BASE.resolve(strict=False),
        LIVE_STEAM_PK.resolve(strict=False),
    }
    require(
        len(set(resolved)) == len(resolved)
        and not (set(resolved) & live_paths),
        "terminal output paths overlap or target live Steam",
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
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
    validate_outputs(
        decision_content=decision_content,
        evidence_content=evidence_content,
        audit_content=audit_content,
        promotion_content=promotion_content,
        audit=audit,
        bundle=bundle,
    )
    outputs = {
        args.decision_output: decision_content,
        args.evidence_output: evidence_content,
        args.audit_output: audit_content,
        args.promotion_output: promotion_content,
    }
    if args.write:
        for path, content in outputs.items():
            ENGINE.atomic_write(path, content)
    if args.check:
        for path, content in outputs.items():
            require(
                path.is_file()
                and path.read_text(encoding="utf-8") == content,
                f"generated terminal output drifted: {path}",
            )
    print(
        "PASS "
        f"overrides={len(TRANSLATION_OVERRIDES)} "
        f"verified_renewed={EXPECTED_VERIFIED_RENEWAL_ROWS} "
        f"promoted={EXPECTED_ELIGIBLE_ROWS} "
        f"pending={EXPECTED_PENDING_AFTER} "
        "base_renewed=0 steam_write=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        ValueError,
        TerminalFamilyError,
        HONORIFIC.HonorificSpacingError,
        CROSS.CrossResourceClosureError,
        CROSS.PK_ONLY.PkOnlyClosureError,
        CROSS.BASE_AUDIT.AuditError,
        ENGINE.RetranslationError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
