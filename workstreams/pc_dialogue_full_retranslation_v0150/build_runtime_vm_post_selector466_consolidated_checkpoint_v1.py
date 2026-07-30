#!/usr/bin/env python3
"""Scaffold selector-466 as a targeted immutable ledger delta."""

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
    WORKSTREAM / "build_runtime_vm_post_selector1078_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1078_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector1078_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector466_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector466_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector466_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector466_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector466_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector466_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector466_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "D3555F7C9CBE95B188C478D8D1AAEFD0F50EEB8C68A28F7D69819F77323D6D38"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "71ADE7F33FC40A817E60F429DE0A0B329E05BF37BD1E03E1671A019783E800F6"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "395C8B600B1AED634FA199602CBBB9F2DCA5691D9E5850688E2107966A8A77E3"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "1A931E023A5248626AE90094772657D91B4270D0F530B48ABC613FDA84BB508D"
)

# Frozen after the selector-466 closure became final.
EXPECTED_CLOSURE_BUILDER_SHA256: str | None = (
    "6AE6125177516E5B8533C49358EF5DD345EF9916E26D1B9F2FCB1078BFD794FF"
)
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "9460D51503D9B204E0D6AEC2BD152439137A38C2961D9C4D9464F7B5ABCE87DF"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256: str | None = (
    "C1D6BB02064E522E22C5667155184EBA7B7218206647ED9B0A2EC4B9BAF8B525"
)
EXPECTED_CLOSURE_COVERAGE_SHA256: str | None = (
    "CBE4FCFD4AFC24914BF57CF086D83D7EA55775ACD2223444AFA2624DB94CD6AE"
)
EXPECTED_CLOSURE_PROMOTION_SHA256: str | None = (
    "ABBDC09953748C70696E84F7681D47DD9AD5C8A2EC82BF403D1CB2E08054B5F1"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "E2283160520383E455C9C26112E80E5DB5EDB89161A9842FF3BD8F4C7FFCAD45"
)
EXPECTED_DECISION_COORDINATE_SHA256: str | None = (
    "3C41921A18094C62C9D1B9A98CC5D043C016B30651E4AD292CA1E756ECC18FEB"
)
EXPECTED_PROMOTION_COORDINATE_SHA256: str | None = (
    "3C41921A18094C62C9D1B9A98CC5D043C016B30651E4AD292CA1E756ECC18FEB"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256: str | None = (
    "032A9FA05D4C92FFF92930C780C3DE706B35E610E19519BEB750C1AD21F523BD"
)
EXPECTED_REVIEWED_SITE_SHA256: str | None = (
    "DD69F2428FD90984E29419091FEB764ACBEA21317C049AC746410F89AAA9A778"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256: str | None = (
    "5E6C7A981B5AEF2CA6903171CEB43062862E63B24B114FCD8CF3337CEDF57AEE"
)
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "99450F568D8EDED40C7A7332F52DADA184EE6F11FB129CFDBCC758C7880DC197"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "D3824B5CF7A8DE02626FF06CE40816086F7DFB8EF6A0A9E06686756A9B69EA5E"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 24
EXPECTED_UNAFFECTED_ROWS = 52_779
EXPECTED_OWNER_ROWS = 24
EXPECTED_PROMOTIONS = 24
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 13
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 11,
    "translation_override_and_runtime_promotion": 13,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 3, 1: 21}
EXPECTED_PREDECESSOR_PENDING = 6_215
EXPECTED_FINAL_PENDING = 6_191
EXPECTED_PREDECESSOR_ELIGIBLE = 46_588
EXPECTED_FINAL_ELIGIBLE = 46_612
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_468
EXPECTED_FINAL_PK_PROMOTIONS = 14_492
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_119
EXPECTED_FINAL_PROMOTED_TOTAL = 30_143
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES = 79
EXPECTED_SOURCE_ONLY_SITES = 15
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
UPDATE_ACTION_FIELD = "selector466_consolidated_update_action"

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
    PREDECESSOR_BUILDER_PATH, "selector466_checkpoint_base"
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
        "nobu16.kr.pc-dialogue-runtime-vm-selector466-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector466-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector1078_selector466_single_coordinate_union_"
        "targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = (
        "selector466_consolidated_exact_override_evidence"
    )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector466-consolidated-row-verification.v1"
    )
    verification["method"] = (
        "reversed_vm_pk_selector466_consolidated_closure"
    )
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    report = PREDECESSOR.build_public_report(private_sha256, stream_result)
    report["selector466_consolidated"] = report.pop(
        "selector1078_consolidated"
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
        "selector466 targeted checkpoint input pins unresolved: "
        + ",".join(blocking_pins()),
    )
    BASE.require(
        BASE.sha256_file(PREDECESSOR_BUILDER_PATH)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "selector1078 targeted checkpoint base drifted",
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
