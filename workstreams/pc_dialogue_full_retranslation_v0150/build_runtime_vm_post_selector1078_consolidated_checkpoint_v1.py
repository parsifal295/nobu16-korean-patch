#!/usr/bin/env python3
"""Scaffold selector-1078 as a targeted immutable ledger delta."""

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
    WORKSTREAM / "build_runtime_vm_post_selector268_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector268_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector268_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector1078_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1078_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1078_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector1078_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector1078_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1078_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector1078_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "6E4FEFF52329BA9A4A6AACB74910FC0DB05C0659F02277680102C4447BFA5B3A"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "0936BD050D1BB529848AD861B951D178A3521C086BC41027C4ED4A5B4FBC79C3"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "FD8A708ED92756AB2024861A1B97550F8229889282E7B58CDEFAEEDFC0C2ECE3"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "92B86808931C1FD34320BC5A9BFD05B7AD704FA9392534FF8DE8F6293F413DAD"
)

# Frozen after the selector-1078 consolidated closure became final.
EXPECTED_CLOSURE_BUILDER_SHA256: str | None = (
    "9836C4EC91F9E310E66DAF95A355554CC539F26F3DBC5D1C25A00B6A6B9860A9"
)
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "82196010FD6EF8C06B186FE8BA3A48DFAC684ABA7A3ADEDFCA66D7F843A34B70"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256: str | None = (
    "928D92973E6A83E5AECB59339A20E6750C7080447E4A3CA5D82207E9DD4A2422"
)
EXPECTED_CLOSURE_COVERAGE_SHA256: str | None = (
    "0EE007EF829401A0ECF4C2FF23708FD4E5BC4BEAE211CAE25CB371B523C9AC81"
)
EXPECTED_CLOSURE_PROMOTION_SHA256: str | None = (
    "0A8479EB633541824D59E73F2C75335E2C265A369E6C7535A1D7C1EE6B15C02A"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "1A931E023A5248626AE90094772657D91B4270D0F530B48ABC613FDA84BB508D"
)
EXPECTED_DECISION_COORDINATE_SHA256: str | None = (
    "06206391F470EF8CC73379D59CBB64D2E18460A4980B9B79709941DBC65E5AE4"
)
EXPECTED_PROMOTION_COORDINATE_SHA256: str | None = (
    "06206391F470EF8CC73379D59CBB64D2E18460A4980B9B79709941DBC65E5AE4"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256: str | None = (
    "76D3B7655FC64EA69FF1F822639F0B332025B9729FDD5F2706F8303C91B3819E"
)
EXPECTED_REVIEWED_SITE_SHA256: str | None = (
    "1D977FB6545FEB31EB452406B631B2730F77D5B7E07F29C3702F906200D461FB"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256: str | None = (
    "930A41B073B7144918A618D15D9E8181F53AAF6862408379527C993CC8CB24FA"
)
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "71ADE7F33FC40A817E60F429DE0A0B329E05BF37BD1E03E1671A019783E800F6"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "395C8B600B1AED634FA199602CBBB9F2DCA5691D9E5850688E2107966A8A77E3"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 17
EXPECTED_UNAFFECTED_ROWS = 52_786
EXPECTED_OWNER_ROWS = 17
EXPECTED_PROMOTIONS = 17
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 7
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 10,
    "translation_override_and_runtime_promotion": 7,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 7, 1: 10}
EXPECTED_PREDECESSOR_PENDING = 6_232
EXPECTED_FINAL_PENDING = 6_215
EXPECTED_PREDECESSOR_ELIGIBLE = 46_571
EXPECTED_FINAL_ELIGIBLE = 46_588
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_451
EXPECTED_FINAL_PK_PROMOTIONS = 14_468
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_102
EXPECTED_FINAL_PROMOTED_TOTAL = 30_119
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES = 43
EXPECTED_SOURCE_ONLY_SITES = 1
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
UPDATE_ACTION_FIELD = "selector1078_consolidated_update_action"

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
    PREDECESSOR_BUILDER_PATH, "selector1078_checkpoint_base"
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
        "nobu16.kr.pc-dialogue-runtime-vm-selector1078-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector1078-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector268_selector1078_single_coordinate_union_"
        "targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = (
        "selector1078_consolidated_exact_override_evidence"
    )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector1078-consolidated-row-verification.v1"
    )
    verification["method"] = (
        "reversed_vm_pk_selector1078_consolidated_closure"
    )
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    report = PREDECESSOR.build_public_report(private_sha256, stream_result)
    report["selector1078_consolidated"] = report.pop(
        "selector268_consolidated"
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
        "selector1078 targeted checkpoint input pins unresolved: "
        + ",".join(blocking_pins()),
    )
    BASE.require(
        BASE.sha256_file(PREDECESSOR_BUILDER_PATH)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "selector268 targeted checkpoint base drifted",
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
