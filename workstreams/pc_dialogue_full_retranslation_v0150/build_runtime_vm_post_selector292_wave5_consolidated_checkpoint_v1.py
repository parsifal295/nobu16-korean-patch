#!/usr/bin/env python3
"""Apply post-selector292 dialogue wave 5 as a targeted ledger delta."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PK_AUDIT = REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"
DIALOGUE_TMP = REPO / "tmp" / WORKSTREAM.name

PREDECESSOR_BUILDER_PATH = (
    WORKSTREAM
    / "build_runtime_vm_post_selector292_wave4_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector292_wave4_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector292_wave4_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT
    / "build_pk_dialogue_wave_post_selector292_wave5_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_dialogue_wave_post_selector292_wave5_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP
    / "pk_dialogue_wave_post_selector292_wave5_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT
    / "public"
    / "pk_dialogue_wave_post_selector292_wave5_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT
    / "public"
    / "pk_dialogue_wave_post_selector292_wave5_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_wave5_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector292_wave5_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "C6BEB85B9E7CFB8B5BE395EFC9837631A806D40572151924ADBB06F62AA072F5"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "BDE252E097BB1D7531F2269E0C4C105972EAEC484961E7EEEA44C0D1414C1DAE"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "FA294DE6C6B4D26F5BE6BF352D7631AB210224D6C1B95962871275011C07CAEB"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "6D60AEEDBD22843B9AEC1DC4B1DDC3509106D6C8FC8F74FE79E4C1E3CE037836"
)

# Frozen only after the wave-5 closure lands.
EXPECTED_CLOSURE_BUILDER_SHA256: str | None = (
    "D0DD4BCDF2AD641F1334149F46748B0F7D3966E2FEBBD8FFD78DAD6AE1065FFD"
)
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "DC3519DDEF49D4C98512BDC1CF656E4F7E77704DED06AADB182F3280A4B05B9E"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256: str | None = (
    "39E8749BE2A4991C944562C99B98DDE228305B7F19D906A6B505ED8EFBD46231"
)
EXPECTED_CLOSURE_COVERAGE_SHA256: str | None = (
    "8C21B4218759B5AB7F428EE621A5565C3844320A13B2D5D260D64B8CB2D61DF6"
)
EXPECTED_CLOSURE_PROMOTION_SHA256: str | None = (
    "4B2CC357762CB5AE498D600FED1EBAB9776889E796C73B1C31D9C34ED82A64C0"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "41CBC25028A3251C954597B2EA6797E503D8F8D6887D79C99BB7191FEBD5617F"
)
EXPECTED_DECISION_COORDINATE_SHA256: str | None = (
    "DA95F132DFF9687B7566207B4D3BAF8E4DB687934649FAB41F31DAA1B3AEE777"
)
EXPECTED_PROMOTION_COORDINATE_SHA256: str | None = (
    "DA95F132DFF9687B7566207B4D3BAF8E4DB687934649FAB41F31DAA1B3AEE777"
)
EXPECTED_RENEWAL_COORDINATE_SHA256: str | None = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256: str | None = (
    "DA95F132DFF9687B7566207B4D3BAF8E4DB687934649FAB41F31DAA1B3AEE777"
)
EXPECTED_REVIEWED_SITE_SHA256: str | None = (
    "099380489835D059B785D47A3D3386ED3ED1914451D44F826418F0A197AC6359"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256: str | None = (
    "3AC61A5DF1EA1151FA1F031793B848C21E1EBF9D86666EB9ABE91D520775521F"
)
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "ABC78C74996A5C9467DB92C1EBB55A940A2A39099E9A12A5D565954D4AB68F12"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "D2928654B9CD246366567E5FF996EB0A58F9044962EADBB79F3921BA2ABC680A"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS: int | None = 14
EXPECTED_UNAFFECTED_ROWS: int | None = 52_789
EXPECTED_OWNER_ROWS: int | None = 14
EXPECTED_PROMOTIONS: int | None = 14
EXPECTED_RENEWALS: int | None = 0
EXPECTED_OVERRIDES: int | None = 14
EXPECTED_ACTION_COUNTS: dict[str, int] | None = {
    "translation_override_and_runtime_promotion": 14,
}
EXPECTED_OWNER_CHUNK_COUNTS: dict[int, int] | None = {0: 11, 1: 1, 2: 2}
EXPECTED_PREDECESSOR_PENDING = 5_970
EXPECTED_FINAL_PENDING: int | None = 5_956
EXPECTED_PREDECESSOR_ELIGIBLE = 46_833
EXPECTED_FINAL_ELIGIBLE: int | None = 46_847
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_713
EXPECTED_FINAL_PK_PROMOTIONS: int | None = 14_727
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_364
EXPECTED_FINAL_PROMOTED_TOTAL: int | None = 30_378
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES: int | None = 130
EXPECTED_SOURCE_ONLY_SITES: int | None = 14
UPDATE_ACTION_FIELD = "post_selector292_wave5_update_action"

PIN_NAMES = (
    "EXPECTED_CLOSURE_BUILDER_SHA256",
    "EXPECTED_CLOSURE_DECISIONS_SHA256",
    "EXPECTED_CLOSURE_EVIDENCE_SHA256",
    "EXPECTED_CLOSURE_COVERAGE_SHA256",
    "EXPECTED_CLOSURE_PROMOTION_SHA256",
    "EXPECTED_FINAL_CANDIDATE_SHA256",
    "EXPECTED_DECISION_COORDINATE_SHA256",
    "EXPECTED_PROMOTION_COORDINATE_SHA256",
    "EXPECTED_RENEWAL_COORDINATE_SHA256",
    "EXPECTED_OVERRIDE_COORDINATE_SHA256",
    "EXPECTED_REVIEWED_SITE_SHA256",
    "EXPECTED_SOURCE_ONLY_SITE_SHA256",
    "EXPECTED_PRIVATE_OUTPUT_SHA256",
    "EXPECTED_PUBLIC_OUTPUT_SHA256",
    "EXPECTED_DECISIONS",
    "EXPECTED_UNAFFECTED_ROWS",
    "EXPECTED_OWNER_ROWS",
    "EXPECTED_PROMOTIONS",
    "EXPECTED_RENEWALS",
    "EXPECTED_OVERRIDES",
    "EXPECTED_ACTION_COUNTS",
    "EXPECTED_OWNER_CHUNK_COUNTS",
    "EXPECTED_FINAL_PENDING",
    "EXPECTED_FINAL_ELIGIBLE",
    "EXPECTED_FINAL_PK_PROMOTIONS",
    "EXPECTED_FINAL_PROMOTED_TOTAL",
    "EXPECTED_REVIEWED_SITES",
    "EXPECTED_SOURCE_ONLY_SITES",
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR = load_module(
    PREDECESSOR_BUILDER_PATH, "post292_wave1_checkpoint_predecessor"
)
BASE = PREDECESSOR.BASE
ORIGINAL_CONFIGURE_BASE = PREDECESSOR.configure_predecessor
ORIGINAL_PATCH_PREDECESSOR_ROW = PREDECESSOR.patch_predecessor_row
ORIGINAL_BUILD_PUBLIC_REPORT = PREDECESSOR.build_public_report


def unresolved_pins() -> list[str]:
    return [name for name in PIN_NAMES if globals()[name] is None]


def blocking_pins() -> list[str]:
    return [
        name
        for name in unresolved_pins()
        if name
        not in {
            "EXPECTED_PRIVATE_OUTPUT_SHA256",
            "EXPECTED_PUBLIC_OUTPUT_SHA256",
        }
    ]


def is_frozen() -> bool:
    return not unresolved_pins()


def configure_predecessor() -> None:
    names = (
        "PREDECESSOR_BUILDER_PATH",
        "PREDECESSOR_PRIVATE_PATH",
        "PREDECESSOR_PUBLIC_PATH",
        "CLOSURE_BUILDER_PATH",
        "CLOSURE_DECISIONS_PATH",
        "CLOSURE_EVIDENCE_PATH",
        "CLOSURE_COVERAGE_PATH",
        "CLOSURE_PROMOTION_PATH",
        "DEFAULT_PRIVATE_OUTPUT",
        "DEFAULT_PUBLIC_OUTPUT",
        "EXPECTED_ROWS",
        "EXPECTED_DECISIONS",
        "EXPECTED_UNAFFECTED_ROWS",
        "EXPECTED_OWNER_ROWS",
        "EXPECTED_PROMOTIONS",
        "EXPECTED_RENEWALS",
        "EXPECTED_OVERRIDES",
        "EXPECTED_ACTION_COUNTS",
        "EXPECTED_OWNER_CHUNK_COUNTS",
        "EXPECTED_PREDECESSOR_PENDING",
        "EXPECTED_FINAL_PENDING",
        "EXPECTED_PREDECESSOR_ELIGIBLE",
        "EXPECTED_FINAL_ELIGIBLE",
        "EXPECTED_PREDECESSOR_PK_PROMOTIONS",
        "EXPECTED_FINAL_PK_PROMOTIONS",
        "EXPECTED_PREDECESSOR_PROMOTED_TOTAL",
        "EXPECTED_FINAL_PROMOTED_TOTAL",
        "EXPECTED_CONFIRMED_NON_DISPLAY",
        "EXPECTED_REVIEWED_SITES",
        "EXPECTED_SOURCE_ONLY_SITES",
        "EXPECTED_PREDECESSOR_BUILDER_SHA256",
        "EXPECTED_PREDECESSOR_PRIVATE_SHA256",
        "EXPECTED_PREDECESSOR_PUBLIC_SHA256",
        "EXPECTED_PREDECESSOR_CANDIDATE_SHA256",
        "EXPECTED_CLOSURE_BUILDER_SHA256",
        "EXPECTED_CLOSURE_DECISIONS_SHA256",
        "EXPECTED_CLOSURE_EVIDENCE_SHA256",
        "EXPECTED_CLOSURE_COVERAGE_SHA256",
        "EXPECTED_CLOSURE_PROMOTION_SHA256",
        "EXPECTED_DECISION_COORDINATE_SHA256",
        "EXPECTED_PROMOTION_COORDINATE_SHA256",
        "EXPECTED_RENEWAL_COORDINATE_SHA256",
        "EXPECTED_OVERRIDE_COORDINATE_SHA256",
        "EXPECTED_REVIEWED_SITE_SHA256",
        "EXPECTED_SOURCE_ONLY_SITE_SHA256",
        "EXPECTED_FINAL_CANDIDATE_SHA256",
        "EXPECTED_PRIVATE_OUTPUT_SHA256",
        "EXPECTED_PUBLIC_OUTPUT_SHA256",
        "UPDATE_ACTION_FIELD",
    )
    for name in names:
        setattr(PREDECESSOR, name, globals()[name])
    ORIGINAL_CONFIGURE_BASE()
    BASE.SCHEMA = (
        "nobu16.kr.pc-dialogue-runtime-vm-post-selector292-wave5-"
        "delta-checkpoint.source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-"
        "closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector292_dialogue_wave5_single_coordinate_union_"
        "targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = (
        "post_selector292_wave5_exact_override_evidence"
    )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-wave5-consolidated-"
        "row-verification.v1"
    )
    verification["method"] = (
        "reversed_vm_pk_dialogue_wave_post_selector292_wave5_consolidated_closure"
    )
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    report = ORIGINAL_BUILD_PUBLIC_REPORT(private_sha256, stream_result)
    report["dialogue_wave_post_selector292_wave5_consolidated"] = report.pop(
        "dialogue_wave_post_selector292_wave4_consolidated"
    )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        not blocking_pins(),
        "post-selector292 wave5 targeted checkpoint input pins unresolved: "
        + ",".join(blocking_pins()),
    )
    BASE.require(
        BASE.sha256_file(PREDECESSOR_BUILDER_PATH)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "post-selector292 targeted checkpoint predecessor drifted",
    )
    configure_predecessor()
    PREDECESSOR.configure_predecessor = configure_predecessor
    PREDECESSOR.patch_predecessor_row = patch_predecessor_row
    PREDECESSOR.build_public_report = build_public_report
    return PREDECESSOR.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
