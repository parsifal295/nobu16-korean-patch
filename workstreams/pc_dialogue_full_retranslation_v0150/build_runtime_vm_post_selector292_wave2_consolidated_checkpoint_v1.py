#!/usr/bin/env python3
"""Apply post-selector292 dialogue wave 2 as a targeted ledger delta."""

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
    / "build_runtime_vm_post_selector292_wave1_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector292_wave1_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector292_wave1_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT
    / "build_pk_dialogue_wave_post_selector292_wave2_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_dialogue_wave_post_selector292_wave2_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP
    / "pk_dialogue_wave_post_selector292_wave2_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT
    / "public"
    / "pk_dialogue_wave_post_selector292_wave2_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT
    / "public"
    / "pk_dialogue_wave_post_selector292_wave2_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_wave2_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector292_wave2_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "A74174C263654B8314E72C854B512B08D9CCE3BBF32696378A078B445C40A5C2"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "3A49375034F28AE3AB088D7A22DDCEE6252CA4C45F67B3B57F32FC449DF2BEFF"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "71930E0261038636E8B20D0E03C577A98B4E09E160C10429E68D88B2F88A4331"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "C47390C28DE697CAD3F57A72A079F4D8CEA897F6E343CFCE704851BCC3507060"
)

# Frozen only after the wave-2 closure lands.
EXPECTED_CLOSURE_BUILDER_SHA256: str | None = (
    "9BCC703A0C5D92CB8FF6EAC7E3886AC955B11AC7D0E05263E271FF7E670DFFF3"
)
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "8126679196ACC7E85A1C3B9C760884650BD01BF7219C30CDFF2E005732460E49"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256: str | None = (
    "88379AC4C8C06CAFAEFD481CBF5E1EE67BE5CC89848D15A810780BEEE0AD9598"
)
EXPECTED_CLOSURE_COVERAGE_SHA256: str | None = (
    "443BA5DFE3F997E01F99DD55C39E0C2B8CA2A778D36D3D3904B6883D11DD39AB"
)
EXPECTED_CLOSURE_PROMOTION_SHA256: str | None = (
    "331AB234848248CAAD54550ECD286C97F64F5E3C3D60422CBFB77709E8583446"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "DF91852936FFBCF0F7C9A17D4D05166A66E041F7A837E50BE600923DB8A2CA9A"
)
EXPECTED_DECISION_COORDINATE_SHA256: str | None = (
    "14E9001048DAD9D7F051BA4A011286F5077AFD6D3C324DD999B78FC11981BBA5"
)
EXPECTED_PROMOTION_COORDINATE_SHA256: str | None = (
    "14E9001048DAD9D7F051BA4A011286F5077AFD6D3C324DD999B78FC11981BBA5"
)
EXPECTED_RENEWAL_COORDINATE_SHA256: str | None = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256: str | None = (
    "D696F583C4CBC6B9DC55E8C03DB62E0A9D2C260F87283A2155C46671322B1FF9"
)
EXPECTED_REVIEWED_SITE_SHA256: str | None = (
    "D8D06AD97D036F239C8C9812139A9EC972DE2E852D3C5C8D7F06A54311D358AB"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256: str | None = (
    "FFCE60822C0C80B86BDDEFA08A70C490CAF16048CB2396FDBDC22594659AB6D4"
)
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "477C57FE380B20F45F5D952ED3954DE3D1F267CA2E0EA4BC5FA6E96B36877843"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "24EC33757EB877A0025F23908305D002306359DAC277D36ED85EC45EF076E21A"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS: int | None = 62
EXPECTED_UNAFFECTED_ROWS: int | None = 52_741
EXPECTED_OWNER_ROWS: int | None = 62
EXPECTED_PROMOTIONS: int | None = 62
EXPECTED_RENEWALS: int | None = 0
EXPECTED_OVERRIDES: int | None = 50
EXPECTED_ACTION_COUNTS: dict[str, int] | None = {
    "runtime_promotion": 12,
    "translation_override_and_runtime_promotion": 50,
}
EXPECTED_OWNER_CHUNK_COUNTS: dict[int, int] | None = {0: 23, 1: 20, 2: 19}
EXPECTED_PREDECESSOR_PENDING = 6_084
EXPECTED_FINAL_PENDING: int | None = 6_022
EXPECTED_PREDECESSOR_ELIGIBLE = 46_719
EXPECTED_FINAL_ELIGIBLE: int | None = 46_781
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_599
EXPECTED_FINAL_PK_PROMOTIONS: int | None = 14_661
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_250
EXPECTED_FINAL_PROMOTED_TOTAL: int | None = 30_312
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES: int | None = 100
EXPECTED_SOURCE_ONLY_SITES: int | None = 9
UPDATE_ACTION_FIELD = "post_selector292_wave2_update_action"

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
        "nobu16.kr.pc-dialogue-runtime-vm-post-selector292-wave2-"
        "delta-checkpoint.source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-"
        "closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector292_dialogue_wave2_single_coordinate_union_"
        "targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = (
        "post_selector292_wave2_exact_override_evidence"
    )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-wave2-consolidated-"
        "row-verification.v1"
    )
    verification["method"] = (
        "reversed_vm_pk_dialogue_wave_post_selector292_wave2_consolidated_closure"
    )
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    report = ORIGINAL_BUILD_PUBLIC_REPORT(private_sha256, stream_result)
    report["dialogue_wave_post_selector292_wave2_consolidated"] = report.pop(
        "dialogue_wave_post_selector292_consolidated"
    )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        not blocking_pins(),
        "post-selector292 wave2 targeted checkpoint input pins unresolved: "
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
