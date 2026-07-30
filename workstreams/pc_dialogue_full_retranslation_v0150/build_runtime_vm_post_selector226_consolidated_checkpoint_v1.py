#!/usr/bin/env python3
"""Scaffold selector-226 as a targeted immutable ledger delta."""

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
    WORKSTREAM / "build_runtime_vm_post_selector1168_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1168_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector1168_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector226_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector226_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector226_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector226_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector226_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector226_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector226_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "D9CECDD83B6197C8EAFD4154A0CD8B503842D5600E0E46E31E4ED25A6990FF31"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "56FBAF8FB54CCFA7EAF10355F66FE6A730374804F48FB4CD9F8F15A99AEE9A91"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "9A04C999B850A1024BBB9AE57F509CA1C879A5DC4D59BF717873FD17E609545F"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "EF84A8B8A18C1F2F1F72D3A650C01DC7B058F32A3536C130809C4FCB31C837C7"
)

# Frozen from the selector-226 consolidated closure.
EXPECTED_CLOSURE_BUILDER_SHA256: str | None = (
    "2925F268AC098096F94F4E4D91F14EC89C6CF06C14E8F7DF9CD85153DC2523C3"
)
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "C01523FE952E960CEF95DB8F9469BA388211C2B8F228CA269C9C32127599D5EB"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256: str | None = (
    "822B75980067F6D9BCA1D575021350727B5067C3D647B30581F2D3FF3AD47322"
)
EXPECTED_CLOSURE_COVERAGE_SHA256: str | None = (
    "3213267FFB7624FEA010B69A3542C542BFC906FA1DB8646CE3197015069CA246"
)
EXPECTED_CLOSURE_PROMOTION_SHA256: str | None = (
    "EDCAA78F69EE1BB844F2543BB4F9BCFE5A204816DD596B56691130FC269349E4"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "FEE99844339C291F6950BEB2193AB5FDD8D25B6F6117AD52F81DCBF7F0CC9B66"
)
EXPECTED_DECISION_COORDINATE_SHA256: str | None = (
    "428270DFDCFCB67D700B397D5DB3E903B1FE0545A0DBE7F452A878A7D95A1BE4"
)
EXPECTED_PROMOTION_COORDINATE_SHA256: str | None = (
    "428270DFDCFCB67D700B397D5DB3E903B1FE0545A0DBE7F452A878A7D95A1BE4"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256: str | None = (
    "ECF77DD71638F1E0EF1892C63A1530590D4ABC48CF5C67106C53ED49EC8C75BC"
)
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "33B635E1409B290202A98719A9CD58F356551BB54703B7F287FC45250134623D"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "8526C4C53B87ED529D6C9EC44FF00FC9B77703EB6D4369DB83F4B916BAE37337"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 37
EXPECTED_UNAFFECTED_ROWS = 52_766
EXPECTED_OWNER_ROWS = 37
EXPECTED_PROMOTIONS = 37
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 3
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 34,
    "translation_override_and_runtime_promotion": 3,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 20, 1: 17}
EXPECTED_PREDECESSOR_PENDING = 6_283
EXPECTED_FINAL_PENDING = 6_246
EXPECTED_PREDECESSOR_ELIGIBLE = 46_520
EXPECTED_FINAL_ELIGIBLE = 46_557
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_400
EXPECTED_FINAL_PK_PROMOTIONS = 14_437
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_051
EXPECTED_FINAL_PROMOTED_TOTAL = 30_088
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES = 70
EXPECTED_SOURCE_ONLY_SITES = 5
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_REVIEWED_SITE_SHA256 = (
    "CE5792EDBBE944E7FBF687177F65DEE5D3158123C4E291D5BA6A80EB33C9F391"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "AD94EB5D6589B6F0004C623B08D526C37E30AA4A62B83D1FD1772F92FC185AD6"
)
UPDATE_ACTION_FIELD = "selector226_consolidated_update_action"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR = load_module(
    PREDECESSOR_BUILDER_PATH, "selector226_checkpoint_base"
)
UPSTREAM = PREDECESSOR.UPSTREAM
BASE = PREDECESSOR.BASE
ORIGINAL_PATCH_PREDECESSOR_ROW = PREDECESSOR.ORIGINAL_PATCH_PREDECESSOR_ROW


def unresolved_pins() -> list[str]:
    names = (
        "EXPECTED_CLOSURE_BUILDER_SHA256",
        "EXPECTED_CLOSURE_DECISIONS_SHA256",
        "EXPECTED_CLOSURE_EVIDENCE_SHA256",
        "EXPECTED_CLOSURE_COVERAGE_SHA256",
        "EXPECTED_CLOSURE_PROMOTION_SHA256",
        "EXPECTED_FINAL_CANDIDATE_SHA256",
        "EXPECTED_DECISION_COORDINATE_SHA256",
        "EXPECTED_PROMOTION_COORDINATE_SHA256",
        "EXPECTED_OVERRIDE_COORDINATE_SHA256",
        "EXPECTED_PRIVATE_OUTPUT_SHA256",
        "EXPECTED_PUBLIC_OUTPUT_SHA256",
    )
    return [name for name in names if globals()[name] is None]


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
        "nobu16.kr.pc-dialogue-runtime-vm-selector226-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector226-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector1168_selector226_single_coordinate_union_"
        "targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = (
        "selector226_consolidated_exact_override_evidence"
    )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector226-consolidated-row-verification.v1"
    )
    verification["method"] = "reversed_vm_pk_selector226_consolidated_closure"
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    report = PREDECESSOR.build_public_report(private_sha256, stream_result)
    report["selector226_consolidated"] = report.pop(
        "selector1168_consolidated"
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
        "selector226 targeted checkpoint input pins unresolved: "
        + ",".join(blocking_pins()),
    )
    BASE.require(
        BASE.sha256_file(PREDECESSOR_BUILDER_PATH)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "selector1168 targeted checkpoint base drifted",
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
