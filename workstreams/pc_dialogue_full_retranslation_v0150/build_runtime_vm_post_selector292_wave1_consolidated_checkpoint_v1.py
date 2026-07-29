#!/usr/bin/env python3
"""Apply post-selector292 dialogue wave 1 as a targeted ledger delta."""

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
    WORKSTREAM / "build_runtime_vm_post_selector292_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector292_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector292_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT
    / "build_pk_dialogue_wave_post_selector292_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_dialogue_wave_post_selector292_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP
    / "pk_dialogue_wave_post_selector292_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT
    / "public"
    / "pk_dialogue_wave_post_selector292_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT
    / "public"
    / "pk_dialogue_wave_post_selector292_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_wave1_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector292_wave1_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "CCF550E94624B4A8C0E8A343DAC700568F1FA91798948C25E63E96F3B18EF50E"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "90644EA8E6F2EF99CA2020993930E551536F00E9BF4DFD244ED46640123E8725"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "E76C849DFB6589B7C48B830D227C368ACA98B80F18FBBC2DD8CF146D455F9652"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "723589D4CC42165F93FF60F0711E96DAB6E84737C75954FA36819F780CD57A2C"
)

# Frozen after the post-selector292 wave closure landed.
EXPECTED_CLOSURE_BUILDER_SHA256: str | None = (
    "5E1E0D9FAFC2BC99ADA1577D07FB2A66FE2F9004F489D98FB1DD91CB5D5BCA7D"
)
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "9F16DD6B5AEA794FAF2E1B56CB331D9AC1126D3C272B79FD635AA5AA36CCC96C"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256: str | None = (
    "9107F6A543AB92B8E7B757DEBC5BBF192035B9F3398B88B098DD0856FAB8C92A"
)
EXPECTED_CLOSURE_COVERAGE_SHA256: str | None = (
    "52B908B14C78754B7D4E8900D55F6F3912938FA3D5178C8AC22560E6B740BDF4"
)
EXPECTED_CLOSURE_PROMOTION_SHA256: str | None = (
    "1DBBFDFC7B1CF7D189B04176698BDDDED5C2C09CD7B7B6CAB532D8DA66A0B887"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "C47390C28DE697CAD3F57A72A079F4D8CEA897F6E343CFCE704851BCC3507060"
)
EXPECTED_DECISION_COORDINATE_SHA256: str | None = (
    "0103863F553F53594BB037949E32F0C0FD327004473FC5834518CA03D6C3705B"
)
EXPECTED_PROMOTION_COORDINATE_SHA256: str | None = (
    "0103863F553F53594BB037949E32F0C0FD327004473FC5834518CA03D6C3705B"
)
EXPECTED_RENEWAL_COORDINATE_SHA256: str | None = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256: str | None = (
    "12C4DB7F7452C9E2C9628B40CA22A6F0C486FDB3A46A82B5C6A7F4C7702EBF67"
)
EXPECTED_REVIEWED_SITE_SHA256: str | None = (
    "7A373EE18382323EA013055FE97E01D9712F3D611C03B4CEE754A525175505E1"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256: str | None = (
    "01BEB60B6268233BDE87421EE2BCF96597E337108B80112F8D0ED1C47C256DF1"
)
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "3A49375034F28AE3AB088D7A22DDCEE6252CA4C45F67B3B57F32FC449DF2BEFF"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "71930E0261038636E8B20D0E03C577A98B4E09E160C10429E68D88B2F88A4331"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS: int | None = 46
EXPECTED_UNAFFECTED_ROWS: int | None = 52_757
EXPECTED_OWNER_ROWS: int | None = 46
EXPECTED_PROMOTIONS: int | None = 46
EXPECTED_RENEWALS: int | None = 0
EXPECTED_OVERRIDES: int | None = 29
EXPECTED_ACTION_COUNTS: dict[str, int] | None = {
    "runtime_promotion": 17,
    "translation_override_and_runtime_promotion": 29,
}
EXPECTED_OWNER_CHUNK_COUNTS: dict[int, int] | None = {0: 21, 1: 16, 2: 9}
EXPECTED_PREDECESSOR_PENDING = 6_130
EXPECTED_FINAL_PENDING: int | None = 6_084
EXPECTED_PREDECESSOR_ELIGIBLE = 46_673
EXPECTED_FINAL_ELIGIBLE: int | None = 46_719
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_553
EXPECTED_FINAL_PK_PROMOTIONS: int | None = 14_599
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_204
EXPECTED_FINAL_PROMOTED_TOTAL: int | None = 30_250
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES: int | None = 96
EXPECTED_SOURCE_ONLY_SITES: int | None = 15
UPDATE_ACTION_FIELD = "post_selector292_wave1_update_action"

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
        "nobu16.kr.pc-dialogue-runtime-vm-post-selector292-wave1-"
        "delta-checkpoint.source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-"
        "closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector292_dialogue_wave1_single_coordinate_union_"
        "targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = (
        "post_selector292_wave1_exact_override_evidence"
    )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-consolidated-"
        "row-verification.v1"
    )
    verification["method"] = (
        "reversed_vm_pk_dialogue_wave_post_selector292_consolidated_closure"
    )
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    report = ORIGINAL_BUILD_PUBLIC_REPORT(private_sha256, stream_result)
    report["dialogue_wave_post_selector292_consolidated"] = report.pop(
        "selector292_consolidated"
    )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        not blocking_pins(),
        "post-selector292 wave1 targeted checkpoint input pins unresolved: "
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
