#!/usr/bin/env python3
"""Apply selector-364 as a targeted immutable ledger delta."""

from __future__ import annotations

import importlib.util
import json
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
    WORKSTREAM / "build_runtime_vm_post_selector1162_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1162_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector1162_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector364_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector364_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector364_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector364_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector364_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector364_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector364_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "8D3BD60AA4F593057BF76FBD033E17C238843C1A499CA8A8DBA232AA876E6678"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "A3A5433CCDD5F085AF61BEDB0409B5A02C7CAD162AD4ADE5938B356C988065B4"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "E063AF9F3681DA84315A4596F43EE6ED8F5FC368D4D712A96DD2B1BFEA1031D7"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "94FE58C283D696DA36E0F6ADB8339713A0211163EDCD6FD0A92EB5110AE613D2"
)
EXPECTED_CLOSURE_BUILDER_SHA256 = (
    "024A7A1946808584EB9C52F28A80F6804CDF727D2A50636C6541485A4AD64596"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "19FB86E3D7B129344B42F391F9F8B72CC6ED0D3AFE61A86031A8BFD6EC9E5106"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    "CDA509B7225014678292D1765D0A2DFAFEB73137468E50E585AF4A44DC497689"
)
EXPECTED_CLOSURE_COVERAGE_SHA256 = (
    "94F76C8D8BA158A9F50608BAE9254945B27AF7520A5C43FAED0E9DAC002A0B0D"
)
EXPECTED_CLOSURE_PROMOTION_SHA256 = (
    "700C3DC088B607319E79510CBE103E7366D2DE7B8FE6183E2D6724776AE405EE"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 5
EXPECTED_UNAFFECTED_ROWS = 52_798
EXPECTED_OWNER_ROWS = 5
EXPECTED_PROMOTIONS = 5
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 2
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 3,
    "translation_override_and_runtime_promotion": 2,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 5}
EXPECTED_PREDECESSOR_PENDING = 6_307
EXPECTED_FINAL_PENDING = 6_302
EXPECTED_PREDECESSOR_ELIGIBLE = 46_496
EXPECTED_FINAL_ELIGIBLE = 46_501
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_376
EXPECTED_FINAL_PK_PROMOTIONS = 14_381
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_027
EXPECTED_FINAL_PROMOTED_TOTAL = 30_032
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES = 38
EXPECTED_SOURCE_ONLY_SITES = 4
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "A0B197328C57E3882B759B9023E95764809DCFF6CD5CB8BCB38ABD5B58CE52CB"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "A0B197328C57E3882B759B9023E95764809DCFF6CD5CB8BCB38ABD5B58CE52CB"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "127F5B99D4ACB221140A599CF2C8B7DB9161502CA0E0A725EC4B23ABF4C6E100"
)
EXPECTED_REVIEWED_SITE_SHA256 = (
    "79029DA92407A84927E7F696B37C325A4F42E4C866513957B73C565C6D2C9537"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "D217E9475CBA2CC9055EC61AC94DF8463E3EF64B820C4A30884A045CEA43C0AF"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "6F3880DF9105F47402378E89E9C1ADE9599C052CAEC6EE3D7CC795333C04C7DE"
)
UPDATE_ACTION_FIELD = "selector364_consolidated_update_action"
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "B776FEF076BC8A466D02F7A8C3624A2BC1EF52012306715A7FF083CF1F53FBD5"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "6FBC581903028C5DE82B53368310D730F47CF408F59685BAA6310F6E62663680"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR = load_module(PREDECESSOR_BUILDER_PATH, "selector364_checkpoint_base")
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
        "nobu16.kr.pc-dialogue-runtime-vm-selector364-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector364-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector1162_selector364_single_coordinate_union_targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = (
        "selector364_consolidated_exact_override_evidence"
    )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector364-consolidated-row-verification.v1"
    )
    verification["method"] = "reversed_vm_pk_selector364_consolidated_closure"
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    report = PREDECESSOR.build_public_report(private_sha256, stream_result)
    report["selector364_consolidated"] = report.pop("selector1162_consolidated")
    return report


def validate_confirmed_non_display(
    decisions: Mapping[str, Mapping[str, Any]],
) -> None:
    count = 0
    touched = 0
    with PREDECESSOR_PRIVATE_PATH.open("r", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("scope_classification") == "confirmed_non_display":
                count += 1
                if (
                    row.get("resource") == "pk_msggame"
                    and str(row.get("coordinate")) in decisions
                ):
                    touched += 1
    BASE.require(
        count == EXPECTED_CONFIRMED_NON_DISPLAY and touched == 0,
        "confirmed-non-display predecessor invariant drifted",
    )


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        BASE.sha256_file(PREDECESSOR_BUILDER_PATH)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "selector1162 targeted checkpoint base drifted",
    )
    configure_base()
    BASE.validate_closure_reports = UPSTREAM.validate_closure_reports
    BASE.patch_predecessor_row = patch_predecessor_row
    BASE.build_public_report = build_public_report
    decisions = BASE.load_closure_decisions()
    validate_confirmed_non_display(decisions)
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
