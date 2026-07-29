#!/usr/bin/env python3
"""Apply root-sharded post-selector292 dialogue wave 7 as a targeted ledger delta."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TRACKED_DIALOGUE = REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
PK_AUDIT = REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"
DIALOGUE_TMP = REPO / "tmp" / WORKSTREAM.name

PREDECESSOR_BUILDER_PATH = (
    TRACKED_DIALOGUE
    / "build_runtime_vm_post_selector292_wave6_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector292_wave6_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    TRACKED_DIALOGUE
    / "runtime_vm_integration.post_selector292_wave6_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT
    / "build_pk_dialogue_wave7_root_sharded_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_dialogue_wave_post_selector292_wave7_root_sharded_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP
    / "pk_dialogue_wave_post_selector292_wave7_root_sharded_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT
    / "public"
    / "pk_dialogue_wave_post_selector292_wave7_root_sharded_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT
    / "public"
    / "pk_dialogue_wave_post_selector292_wave7_root_sharded_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_wave7_root_sharded_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    TRACKED_DIALOGUE
    / "runtime_vm_integration."
    "post_selector292_wave7_root_sharded_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "E595CB9AF6F48F494BBF8351774BDC2A04BE12EB0086B831A580057433E87B40"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "7016A0AB5EFD5B0FD223818F860B5757A914188A8EE58C2AD3BE6D14BC393F61"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "987E9644DD5DC235C74E52858546C9196BA15203871A7FE9DDEBF121697435F3"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "DC8F4F47EA9DDD81BA6DD788ECE55FD303FA5C228925E6E947E4E7F5C1007804"
)

# Frozen after the wave-6 closure landed.
EXPECTED_CLOSURE_BUILDER_SHA256: str | None = (
    "C568CBBBAB9ED21FF26ED3DE942396316D90A3B1A727701836BD44D10C272387"
)
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "554F0365B15976A7F0457D277AB7FFECFCCD86CBF0B6507E68D5737B072D7AE4"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256: str | None = (
    "BD7F78DC393CDC9C6B41273304F9FAD2810324B4354E82D720AB790F5473E971"
)
EXPECTED_CLOSURE_COVERAGE_SHA256: str | None = (
    "D4B75C47480F155FC0C1EF091E1205C135EE6C160045013C2D687B09A5CAF1D7"
)
EXPECTED_CLOSURE_PROMOTION_SHA256: str | None = (
    "32DC1CA24BDFD72E88E5896CB1BEE191B0D743C7E9EBBCF84EF475049F99BB68"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "DAB40F2AA8095E67550B69213A53CC777B96B17071FFF5B860CFAEE1A868D7E0"
)
EXPECTED_DECISION_COORDINATE_SHA256: str | None = (
    "DE8BA114858A9A5D8B0D01A3989D43C5FFCDAB889E72B93A65AF500456843693"
)
EXPECTED_PROMOTION_COORDINATE_SHA256: str | None = (
    "DE8BA114858A9A5D8B0D01A3989D43C5FFCDAB889E72B93A65AF500456843693"
)
EXPECTED_RENEWAL_COORDINATE_SHA256: str | None = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256: str | None = (
    "36E25FF18A6763E01AA4B98457272F075C192AF2466F06999EB0E9A38B310142"
)
EXPECTED_REVIEWED_SITE_SHA256: str | None = (
    "D16CBA93E7EAB8AC2DA9B801BCAF99B8FCDC3EEDAF010D6FD466E639F9F4CB9A"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256: str | None = (
    "1E584D0B12B469CEF69E489D50DFFAB67E5DFFDF4E16A0E6AD5BB8DF6AA10437"
)
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "B1CF7F4523DE9411BA5172E7C9DEA946C7646085C83A1480C51807E2DD0C90E7"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "96E03D3EA32FAB5E6701DB75060038A5E967F9617EB0E22E5C91352944626930"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS: int | None = 21
EXPECTED_UNAFFECTED_ROWS: int | None = 52_782
EXPECTED_OWNER_ROWS: int | None = 21
EXPECTED_PROMOTIONS: int | None = 21
EXPECTED_RENEWALS: int | None = 0
EXPECTED_OVERRIDES: int | None = 13
EXPECTED_ACTION_COUNTS: dict[str, int] | None = {
    "runtime_promotion": 8,
    "translation_override_and_runtime_promotion": 13,
}
EXPECTED_OWNER_CHUNK_COUNTS: dict[int, int] | None = {
    2: 3,
    4: 1,
    12: 2,
    18: 1,
    19: 4,
    21: 2,
    27: 2,
    30: 2,
    34: 2,
    43: 1,
    47: 1,
}
EXPECTED_PREDECESSOR_PENDING = 5_922
EXPECTED_FINAL_PENDING: int | None = 5_901
EXPECTED_PREDECESSOR_ELIGIBLE = 46_881
EXPECTED_FINAL_ELIGIBLE: int | None = 46_902
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_761
EXPECTED_FINAL_PK_PROMOTIONS: int | None = 14_782
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_412
EXPECTED_FINAL_PROMOTED_TOTAL: int | None = 30_433
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES: int | None = 738
EXPECTED_SOURCE_ONLY_SITES: int | None = 103
UPDATE_ACTION_FIELD = "post_selector292_wave7_root_sharded_update_action"

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
    PREDECESSOR_BUILDER_PATH, "post292_wave7_checkpoint_predecessor"
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
        "nobu16.kr.pc-dialogue-runtime-vm-post-selector292-wave7-root-sharded-"
        "delta-checkpoint.source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-"
        "closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector292_dialogue_wave7_root_sharded_single_coordinate_union_"
        "targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = (
        "post_selector292_wave7_root_sharded_exact_override_evidence"
    )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-wave7-root-sharded-"
        "consolidated-"
        "row-verification.v1"
    )
    verification["method"] = (
        "reversed_vm_pk_dialogue_wave_post_selector292_wave7_"
        "root_sharded_consolidated_closure"
    )
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    report = ORIGINAL_BUILD_PUBLIC_REPORT(private_sha256, stream_result)
    report[
        "dialogue_wave_post_selector292_wave7_root_sharded_consolidated"
    ] = report.pop(
        "dialogue_wave_post_selector292_wave6_consolidated"
    )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        not blocking_pins(),
        "post-selector292 wave7 root-sharded targeted checkpoint input pins unresolved: "
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
