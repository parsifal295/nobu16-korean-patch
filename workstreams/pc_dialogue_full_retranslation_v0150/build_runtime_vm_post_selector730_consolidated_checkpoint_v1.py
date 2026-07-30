#!/usr/bin/env python3
"""Scaffold selector-730 as a targeted immutable ledger delta."""

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
    WORKSTREAM / "build_runtime_vm_post_selector562_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector562_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector562_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector730_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP / "semantic_overrides"
    / "pk_selector730_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector730_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector730_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector730_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector730_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector730_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "F748FE30B4940004929879EDEC6A9463CB65F1117E19322394491244602C5362"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "8E31995689359D5F8DD1F23FC7A894C07AC8BBB3C08EF2B87651E6E3E8B1086A"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "5445CD4A9C9515A8732446DA397D0FF0BB66E657A17C14BEDC374CCC745CDF76"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "B7CBFA388BDD50F60CD5EEF88A63B62D357475925A0A3AA6D7DCA1A191607815"
)

# Frozen after the selector-730 closure becomes final.
EXPECTED_CLOSURE_BUILDER_SHA256: str | None = (
    "36203E94751006C6AD2E03642C448A235AE9C1EFB08B274A050F8E6A84E01F61"
)
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "A56DA1B7C3465EF9CA1640A059F7EE46EC73B0C4C95B2849551CDA34A91A8DDE"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256: str | None = (
    "070FA56F5F230A46B0A1A9BC1544FE676A5D93886A94686A5D2463D134399BDD"
)
EXPECTED_CLOSURE_COVERAGE_SHA256: str | None = (
    "E10A7B7E20F3259966F10B9787907124E3F72D910AA1D9E5FDCDC57616898186"
)
EXPECTED_CLOSURE_PROMOTION_SHA256: str | None = (
    "55B523C11A66EB8BB393FD562C22DE1F1DE80F723E84FF128EC14EC858A05FBD"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "5D4CDF1CEB8C733B0E22C7AA6185D9FF6C5C4C500176E99A6AACB3D89F7E0140"
)
EXPECTED_DECISION_COORDINATE_SHA256: str | None = (
    "A7AA97F0E5BE83EF88CE8F20387BBE589AC4AA3D2D08ED3A5260F2ED528B8D0E"
)
EXPECTED_PROMOTION_COORDINATE_SHA256: str | None = (
    "A7AA97F0E5BE83EF88CE8F20387BBE589AC4AA3D2D08ED3A5260F2ED528B8D0E"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256: str | None = (
    "EF6126175171237F1995DB709FD27ABFC7FB7583D1F250F6011CDB9AD094BC95"
)
EXPECTED_REVIEWED_SITE_SHA256: str | None = (
    "97C3B98B672FF969B99680AB35AA80D77A82726196BC53C1C02BD1813BC3C877"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256: str | None = (
    "AFF05F3C748B8B3A4044013477DAEC82615EAAC0CBF4526450BA0F38B3D0A586"
)
EXPECTED_OVERRIDES: int | None = 1
EXPECTED_ACTION_COUNTS: dict[str, int] | None = {
    "runtime_promotion": 2,
    "translation_override_and_runtime_promotion": 1,
}
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "9F6BD587F6EC92CD00A2E2AF9FD9E07A8B6A71405272F0D79A515C3405617C5C"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "311DD27E8C260B7438EDF90FFB944EAEC25C3462C2C8E6BDA196BCF89DEDF362"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 3
EXPECTED_UNAFFECTED_ROWS = 52_800
EXPECTED_OWNER_ROWS = 3
EXPECTED_PROMOTIONS = 3
EXPECTED_RENEWALS = 0
EXPECTED_OWNER_CHUNK_COUNTS = {1: 3}
EXPECTED_PREDECESSOR_PENDING = 6_181
EXPECTED_FINAL_PENDING = 6_178
EXPECTED_PREDECESSOR_ELIGIBLE = 46_622
EXPECTED_FINAL_ELIGIBLE = 46_625
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_502
EXPECTED_FINAL_PK_PROMOTIONS = 14_505
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_153
EXPECTED_FINAL_PROMOTED_TOTAL = 30_156
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES = 41
EXPECTED_SOURCE_ONLY_SITES = 5
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
UPDATE_ACTION_FIELD = "selector730_consolidated_update_action"

PIN_NAMES = (
    "EXPECTED_CLOSURE_BUILDER_SHA256",
    "EXPECTED_CLOSURE_DECISIONS_SHA256",
    "EXPECTED_CLOSURE_EVIDENCE_SHA256",
    "EXPECTED_CLOSURE_COVERAGE_SHA256",
    "EXPECTED_CLOSURE_PROMOTION_SHA256",
    "EXPECTED_FINAL_CANDIDATE_SHA256",
    "EXPECTED_DECISION_COORDINATE_SHA256",
    "EXPECTED_PROMOTION_COORDINATE_SHA256",
    "EXPECTED_OVERRIDE_COORDINATE_SHA256",
    "EXPECTED_REVIEWED_SITE_SHA256",
    "EXPECTED_SOURCE_ONLY_SITE_SHA256",
    "EXPECTED_OVERRIDES",
    "EXPECTED_ACTION_COUNTS",
    "EXPECTED_PRIVATE_OUTPUT_SHA256",
    "EXPECTED_PUBLIC_OUTPUT_SHA256",
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
    PREDECESSOR_BUILDER_PATH, "selector730_checkpoint_base"
)
UPSTREAM = PREDECESSOR.UPSTREAM
BASE = PREDECESSOR.BASE
ORIGINAL_PATCH_PREDECESSOR_ROW = PREDECESSOR.patch_predecessor_row


def unresolved_pins() -> list[str]:
    return [name for name in PIN_NAMES if globals()[name] is None]


def blocking_pins() -> list[str]:
    return [
        name
        for name in unresolved_pins()
        if name not in {
            "EXPECTED_PRIVATE_OUTPUT_SHA256",
            "EXPECTED_PUBLIC_OUTPUT_SHA256",
        }
    ]


def is_frozen() -> bool:
    return not unresolved_pins()


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
        "nobu16.kr.pc-dialogue-runtime-vm-selector730-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector730-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector562_selector730_single_coordinate_union_"
        "targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = (
        "selector730_consolidated_exact_override_evidence"
    )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector730-consolidated-row-verification.v1"
    )
    verification["method"] = (
        "reversed_vm_pk_selector730_consolidated_closure"
    )
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    report = PREDECESSOR.build_public_report(private_sha256, stream_result)
    report["selector730_consolidated"] = report.pop(
        "selector562_consolidated"
    )
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
        not blocking_pins(),
        "selector730 targeted checkpoint input pins unresolved: "
        + ",".join(blocking_pins()),
    )
    BASE.require(
        BASE.sha256_file(PREDECESSOR_BUILDER_PATH)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "selector562 targeted checkpoint base drifted",
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
