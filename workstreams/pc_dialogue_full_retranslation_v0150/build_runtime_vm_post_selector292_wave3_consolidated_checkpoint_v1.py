#!/usr/bin/env python3
"""Apply post-selector292 dialogue wave 3 as a targeted ledger delta."""

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
    / "build_runtime_vm_post_selector292_wave2_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector292_wave2_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector292_wave2_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT
    / "build_pk_dialogue_wave_post_selector292_wave3_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_dialogue_wave_post_selector292_wave3_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP
    / "pk_dialogue_wave_post_selector292_wave3_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT
    / "public"
    / "pk_dialogue_wave_post_selector292_wave3_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT
    / "public"
    / "pk_dialogue_wave_post_selector292_wave3_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_wave3_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector292_wave3_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "32812D569C2F5CDF431871AB8FD0E1610776ADE8846E04A3203432AF86414F6D"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "477C57FE380B20F45F5D952ED3954DE3D1F267CA2E0EA4BC5FA6E96B36877843"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "24EC33757EB877A0025F23908305D002306359DAC277D36ED85EC45EF076E21A"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "DF91852936FFBCF0F7C9A17D4D05166A66E041F7A837E50BE600923DB8A2CA9A"
)

# Frozen only after the wave-2 closure lands.
EXPECTED_CLOSURE_BUILDER_SHA256: str | None = (
    "293634B76696D3E2DEADFB82F94381C33F0E59EA373CE50BAC904E0A8B465722"
)
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "4B6CF7DD899DD928D518959ABC9E3D570996983533225B03A2E4241BDFE951CE"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256: str | None = (
    "26A064CE588B968644F920508C382BAAECBD2E4FC178BA8BDD531C55F718ABE2"
)
EXPECTED_CLOSURE_COVERAGE_SHA256: str | None = (
    "786E04A50D4E6DE44F7B09B9AB14A237FD24A8AFC796D2B608BE8A2508BC49F4"
)
EXPECTED_CLOSURE_PROMOTION_SHA256: str | None = (
    "86847F29A38D9AC9888F70DB9E02671C819ADBF134B9EE97DA89A8FDD0139D69"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "4B2A09C787802B073109DE00B280FFC7FAB69FCF91C8D800EADCA3F072BE3C20"
)
EXPECTED_DECISION_COORDINATE_SHA256: str | None = (
    "DDD190A9E4C13EB250B9F6A78C303938A73936D08708202A768352B373EE85C9"
)
EXPECTED_PROMOTION_COORDINATE_SHA256: str | None = (
    "DDD190A9E4C13EB250B9F6A78C303938A73936D08708202A768352B373EE85C9"
)
EXPECTED_RENEWAL_COORDINATE_SHA256: str | None = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256: str | None = (
    "58E5DBE4E4D805C5113D3CAC7D875E272863B3588E5C032C0B52D10B2127F14E"
)
EXPECTED_REVIEWED_SITE_SHA256: str | None = (
    "72DD83C17082C0BA2BA3A3DDB2B844D5EAFA69AFDDF2BEFD4D15DA6E0C7580E3"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256: str | None = (
    "9076DE97D9C5B80F2C7F30F63EAB729AAA693A24259545650C0F9DF699244779"
)
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "3AEE8906C75A77C5808A28D3BAD62509BA2A32FF69C80AA68FAEA3C99CA72FDE"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "6B8E2A8701A0FE248909DE9FB0C6F9F448B4C37F98CBA47370A9F04259D30359"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS: int | None = 23
EXPECTED_UNAFFECTED_ROWS: int | None = 52_780
EXPECTED_OWNER_ROWS: int | None = 23
EXPECTED_PROMOTIONS: int | None = 23
EXPECTED_RENEWALS: int | None = 0
EXPECTED_OVERRIDES: int | None = 9
EXPECTED_ACTION_COUNTS: dict[str, int] | None = {
    "runtime_promotion": 14,
    "translation_override_and_runtime_promotion": 9,
}
EXPECTED_OWNER_CHUNK_COUNTS: dict[int, int] | None = {0: 19, 1: 1, 2: 3}
EXPECTED_PREDECESSOR_PENDING = 6_022
EXPECTED_FINAL_PENDING: int | None = 5_999
EXPECTED_PREDECESSOR_ELIGIBLE = 46_781
EXPECTED_FINAL_ELIGIBLE: int | None = 46_804
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_661
EXPECTED_FINAL_PK_PROMOTIONS: int | None = 14_684
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_312
EXPECTED_FINAL_PROMOTED_TOTAL: int | None = 30_335
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES: int | None = 46
EXPECTED_SOURCE_ONLY_SITES: int | None = 3
UPDATE_ACTION_FIELD = "post_selector292_wave3_update_action"

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
        "nobu16.kr.pc-dialogue-runtime-vm-post-selector292-wave3-"
        "delta-checkpoint.source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-"
        "closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector292_dialogue_wave3_single_coordinate_union_"
        "targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = (
        "post_selector292_wave3_exact_override_evidence"
    )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-wave3-consolidated-"
        "row-verification.v1"
    )
    verification["method"] = (
        "reversed_vm_pk_dialogue_wave_post_selector292_wave3_consolidated_closure"
    )
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    report = ORIGINAL_BUILD_PUBLIC_REPORT(private_sha256, stream_result)
    report["dialogue_wave_post_selector292_wave3_consolidated"] = report.pop(
        "dialogue_wave_post_selector292_wave2_consolidated"
    )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        not blocking_pins(),
        "post-selector292 wave3 targeted checkpoint input pins unresolved: "
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
