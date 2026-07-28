#!/usr/bin/env python3
"""Apply selector-1162 as a targeted immutable ledger delta."""

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
    WORKSTREAM / "build_runtime_vm_post_selector322_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector322_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector322_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector1162_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1162_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1162_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector1162_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector1162_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1162_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector1162_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "8FE37F41B9ECBCF7D5E5F3CCF6F1FAFF6A3C31E519081783A994C3E7E380D510"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "9A7E135544FA2F2A02A0D2B4941159CB92A3E4A495AF72B6CB335DE371351343"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "3C245CE82733F50F08E61B05A165B1038C4D5BBA5D3DAD38D46933B392101642"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "D0739EBB2E00B9034071165D00CA0D5E08D5F30A6400C8FF38CDA2867BA0203E"
)
EXPECTED_CLOSURE_BUILDER_SHA256 = (
    "AE341A593D7DC3200924558E38FEA88C9D624F4C578F39101D92639CB812DAE4"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "61E3E983D040461169FC989BB9F54BA67E4031CCF0CF49A411B0FB41CFC8BD37"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    "1A63F4BF4E3B6FCF2B37CCC309FBF8BEA80E33B3501F44888FA3F0859C7F7487"
)
EXPECTED_CLOSURE_COVERAGE_SHA256 = (
    "7F0D18ED4F11295A20F506DA05B0B9A0624D5BB70CC7D6D9BDE795C4ECA75B64"
)
EXPECTED_CLOSURE_PROMOTION_SHA256 = (
    "1F5A2BD0319F04588E7A883252DDAF2D7F18CE347BACC6A3953498AAA39F682A"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 3
EXPECTED_UNAFFECTED_ROWS = 52_800
EXPECTED_OWNER_ROWS = 3
EXPECTED_PROMOTIONS = 3
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 1
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 2,
    "translation_override_and_runtime_promotion": 1,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 3}
EXPECTED_PREDECESSOR_PENDING = 6_310
EXPECTED_FINAL_PENDING = 6_307
EXPECTED_PREDECESSOR_ELIGIBLE = 46_493
EXPECTED_FINAL_ELIGIBLE = 46_496
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_373
EXPECTED_FINAL_PK_PROMOTIONS = 14_376
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_024
EXPECTED_FINAL_PROMOTED_TOTAL = 30_027
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES = 61
EXPECTED_SOURCE_ONLY_SITES = 5
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "07BFB1EED9C2B0CCA64B47493BD2E99F310F50649787F259082E11BFB27BF9BE"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "07BFB1EED9C2B0CCA64B47493BD2E99F310F50649787F259082E11BFB27BF9BE"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "46B92144EE1666B7C23D51D338298932C73E438A91D4F1560B9B9A0BF3C80AF0"
)
EXPECTED_REVIEWED_SITE_SHA256 = (
    "05170F0F5AD5A05EED6D030E51F78D3D13BB9E234729D012C70D7DADB348300D"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "605715A7C0C0512A87DF52B89302A859EC002E3C64644276B2F1E112854D949B"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "94FE58C283D696DA36E0F6ADB8339713A0211163EDCD6FD0A92EB5110AE613D2"
)
UPDATE_ACTION_FIELD = "selector1162_consolidated_update_action"
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "A3A5433CCDD5F085AF61BEDB0409B5A02C7CAD162AD4ADE5938B356C988065B4"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "E063AF9F3681DA84315A4596F43EE6ED8F5FC368D4D712A96DD2B1BFEA1031D7"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR = load_module(PREDECESSOR_BUILDER_PATH, "selector1162_checkpoint_base")
UPSTREAM = PREDECESSOR.UPSTREAM
BASE = PREDECESSOR.BASE
ORIGINAL_PATCH_PREDECESSOR_ROW = PREDECESSOR.ORIGINAL_PATCH_PREDECESSOR_ROW


def configure_base() -> None:
    names = (
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
    PREDECESSOR.configure_base()
    BASE.SCHEMA = (
        "nobu16.kr.pc-dialogue-runtime-vm-selector1162-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector1162-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector322_selector1162_single_coordinate_union_targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = (
        "selector1162_consolidated_exact_override_evidence"
    )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector1162-consolidated-row-verification.v1"
    )
    verification["method"] = "reversed_vm_pk_selector1162_consolidated_closure"
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    report = PREDECESSOR.build_public_report(private_sha256, stream_result)
    report["selector1162_consolidated"] = report.pop("selector322_consolidated")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        BASE.sha256_file(PREDECESSOR_BUILDER_PATH)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "selector322 targeted checkpoint base drifted",
    )
    configure_base()
    BASE.validate_closure_reports = UPSTREAM.validate_closure_reports
    BASE.patch_predecessor_row = patch_predecessor_row
    BASE.build_public_report = build_public_report
    decisions = BASE.load_closure_decisions()
    PREDECESSOR.PREDECESSOR.validate_confirmed_non_display(decisions)
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
