#!/usr/bin/env python3
"""Apply post-selector292 dialogue wave 4 as a targeted ledger delta."""

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
    / "build_runtime_vm_post_selector292_wave3_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector292_wave3_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector292_wave3_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT
    / "build_pk_dialogue_wave_post_selector292_wave4_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_dialogue_wave_post_selector292_wave4_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP
    / "pk_dialogue_wave_post_selector292_wave4_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT
    / "public"
    / "pk_dialogue_wave_post_selector292_wave4_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT
    / "public"
    / "pk_dialogue_wave_post_selector292_wave4_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_wave4_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector292_wave4_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "359D6F8FEF6F91A50041E1437EF941867CB2401A672C7F0535218F01E242D998"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "3AEE8906C75A77C5808A28D3BAD62509BA2A32FF69C80AA68FAEA3C99CA72FDE"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "6B8E2A8701A0FE248909DE9FB0C6F9F448B4C37F98CBA47370A9F04259D30359"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "4B2A09C787802B073109DE00B280FFC7FAB69FCF91C8D800EADCA3F072BE3C20"
)

# Frozen only after the wave-4 closure lands.
EXPECTED_CLOSURE_BUILDER_SHA256: str | None = (
    "72A658503FF172195921FC42A1EEEC0981F210C61480A780DF1D7588CC25469C"
)
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "BF56EAC530AB4D6AD5D510663575E18FDEE76F73751CFF755196D073E0D1EAC3"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256: str | None = (
    "FFECCCF055079FD81F002453C353237847F018CE7CC39FF2DBE613C1401E2AFF"
)
EXPECTED_CLOSURE_COVERAGE_SHA256: str | None = (
    "93EA8E767469DD9122D12C6A76AF09F045CC4C83153C6A0EB80991BC3BC54B19"
)
EXPECTED_CLOSURE_PROMOTION_SHA256: str | None = (
    "04689FCCB2D848400AA54E225BB6EE6CB5758F66B84738731CDAFD083AFA232F"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "6D60AEEDBD22843B9AEC1DC4B1DDC3509106D6C8FC8F74FE79E4C1E3CE037836"
)
EXPECTED_DECISION_COORDINATE_SHA256: str | None = (
    "61FE5268346CC75CB3F2BD42C5C06D5DF9D22750545358BFABD254FD1B9BE8F0"
)
EXPECTED_PROMOTION_COORDINATE_SHA256: str | None = (
    "61FE5268346CC75CB3F2BD42C5C06D5DF9D22750545358BFABD254FD1B9BE8F0"
)
EXPECTED_RENEWAL_COORDINATE_SHA256: str | None = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256: str | None = (
    "A46ABB48AC83DBE04CAB4ACF78FAE6F75D42A5AF939B3766FDDE44F3EB54EFBF"
)
EXPECTED_REVIEWED_SITE_SHA256: str | None = (
    "5C219F1B900224752C9AD74F5777A91528EFB67F01A28989BACE98538E6A3C06"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256: str | None = (
    "712759ED5902F1BA7CBC458E1C4DF82F66291AE7F7E47F97D1AFCCD9C6D92119"
)
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "BDE252E097BB1D7531F2269E0C4C105972EAEC484961E7EEEA44C0D1414C1DAE"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "FA294DE6C6B4D26F5BE6BF352D7631AB210224D6C1B95962871275011C07CAEB"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS: int | None = 29
EXPECTED_UNAFFECTED_ROWS: int | None = 52_774
EXPECTED_OWNER_ROWS: int | None = 29
EXPECTED_PROMOTIONS: int | None = 29
EXPECTED_RENEWALS: int | None = 0
EXPECTED_OVERRIDES: int | None = 27
EXPECTED_ACTION_COUNTS: dict[str, int] | None = {
    "runtime_promotion": 2,
    "translation_override_and_runtime_promotion": 27,
}
EXPECTED_OWNER_CHUNK_COUNTS: dict[int, int] | None = {0: 15, 1: 14}
EXPECTED_PREDECESSOR_PENDING = 5_999
EXPECTED_FINAL_PENDING: int | None = 5_970
EXPECTED_PREDECESSOR_ELIGIBLE = 46_804
EXPECTED_FINAL_ELIGIBLE: int | None = 46_833
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_684
EXPECTED_FINAL_PK_PROMOTIONS: int | None = 14_713
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_335
EXPECTED_FINAL_PROMOTED_TOTAL: int | None = 30_364
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES: int | None = 53
EXPECTED_SOURCE_ONLY_SITES: int | None = 1
UPDATE_ACTION_FIELD = "post_selector292_wave4_update_action"

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
        "nobu16.kr.pc-dialogue-runtime-vm-post-selector292-wave4-"
        "delta-checkpoint.source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-"
        "closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector292_dialogue_wave4_single_coordinate_union_"
        "targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = (
        "post_selector292_wave4_exact_override_evidence"
    )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-wave4-consolidated-"
        "row-verification.v1"
    )
    verification["method"] = (
        "reversed_vm_pk_dialogue_wave_post_selector292_wave4_consolidated_closure"
    )
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    report = ORIGINAL_BUILD_PUBLIC_REPORT(private_sha256, stream_result)
    report["dialogue_wave_post_selector292_wave4_consolidated"] = report.pop(
        "dialogue_wave_post_selector292_wave3_consolidated"
    )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        not blocking_pins(),
        "post-selector292 wave4 targeted checkpoint input pins unresolved: "
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
