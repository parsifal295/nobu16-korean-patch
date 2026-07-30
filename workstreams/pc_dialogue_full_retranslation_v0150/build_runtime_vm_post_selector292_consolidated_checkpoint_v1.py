#!/usr/bin/env python3
"""Apply selector-292 as a targeted immutable ledger delta."""

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
    WORKSTREAM / "build_runtime_vm_post_selector238_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector238_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector238_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector292_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector292_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector292_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector292_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector292_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector292_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector292_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "503A8500AFDB5A1041FA497A62634B3C30772DCE79628168C4208A898B45738B"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "AC10F7E71CFAD259ABBC08139BE0DB848CF5309578045532A48991F40E0035AB"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "0CAE7231474FBAE0BCE8E1E98D44225DCC5445EEEA435378E0D56BD1F83A5384"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "9E5C60A451DB7CCA7B046AFD8CFF199CB3665E003CB0C751120478F693D20C24"
)

# Frozen only after the consolidated closure lands.
EXPECTED_CLOSURE_BUILDER_SHA256: str | None = (
    "086C966B48F3B6CA6854C94E1B48C508F5084D05353712F464908C7C64A73B22"
)
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "F90AD78BF19BE129BFEF08FFF47C81CAFCD90ADBA7B6DDC0B1DF89039E47F004"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256: str | None = (
    "6BAF6AC32B0EEE03E8933BA65F9A56145758ECE72506DCF57FCCA068843839A9"
)
EXPECTED_CLOSURE_COVERAGE_SHA256: str | None = (
    "29244DDABD88277D8D6957E43D41B6FAABDD895EF857F34DCA42DC0B76DA0572"
)
EXPECTED_CLOSURE_PROMOTION_SHA256: str | None = (
    "B22953FA1215D16531370F931EAAC722B244D7A60914AEED19E240ABDF61870A"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "723589D4CC42165F93FF60F0711E96DAB6E84737C75954FA36819F780CD57A2C"
)
EXPECTED_DECISION_COORDINATE_SHA256: str | None = (
    "6FBF66819BF084FD16F156D28FEE233F964A882C02AE4E8A38119ACDA25643DD"
)
EXPECTED_PROMOTION_COORDINATE_SHA256: str | None = (
    "B6675351E0E5A7827561F5DC81569ED42E9B02C0C633DFC0CD18551207322618"
)
EXPECTED_RENEWAL_COORDINATE_SHA256: str | None = (
    "EFEB3EE59FE890CF7BEFC7386887D725948CD105CC8E64DB4C4CBE6D794B579F"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256: str | None = (
    "AD41BE18540EE1160AA2B21670D11FA84D0ABBD25CE2724D8A61FF699C03565E"
)
EXPECTED_REVIEWED_SITE_SHA256: str | None = (
    "9F320371558647FF01DD2F0F30F1B65DB068120C6922AC8D3223584738C5FA0E"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256: str | None = (
    "4B5C5E8AAF5AA1D14BAABFF35200E062154343CC777503EE652DC1D5D3B324D0"
)
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "90644EA8E6F2EF99CA2020993930E551536F00E9BF4DFD244ED46640123E8725"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "E76C849DFB6589B7C48B830D227C368ACA98B80F18FBBC2DD8CF146D455F9652"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 22
EXPECTED_UNAFFECTED_ROWS = 52_781
EXPECTED_OWNER_ROWS = 22
EXPECTED_PROMOTIONS = 21
EXPECTED_RENEWALS = 1
EXPECTED_OVERRIDES = 8
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 14,
    "translation_override_and_runtime_promotion": 7,
    "translation_override_and_verification_renewal": 1,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 12, 1: 10}
EXPECTED_PREDECESSOR_PENDING = 6_151
EXPECTED_FINAL_PENDING = 6_130
EXPECTED_PREDECESSOR_ELIGIBLE = 46_652
EXPECTED_FINAL_ELIGIBLE = 46_673
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_532
EXPECTED_FINAL_PK_PROMOTIONS = 14_553
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_183
EXPECTED_FINAL_PROMOTED_TOTAL = 30_204
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES = 26
EXPECTED_SOURCE_ONLY_SITES = 5
UPDATE_ACTION_FIELD = "selector292_consolidated_update_action"

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
    PREDECESSOR_BUILDER_PATH, "selector292_checkpoint_predecessor"
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
        "nobu16.kr.pc-dialogue-runtime-vm-selector292-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector292-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector238_selector292_single_coordinate_union_"
        "targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = (
        "selector292_consolidated_exact_override_evidence"
    )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector292-consolidated-row-verification.v1"
    )
    verification["method"] = (
        "reversed_vm_pk_selector292_consolidated_closure"
    )
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    report = ORIGINAL_BUILD_PUBLIC_REPORT(private_sha256, stream_result)
    report["selector292_consolidated"] = report.pop(
        "selector238_consolidated"
    )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        not blocking_pins(),
        "selector292 targeted checkpoint input pins unresolved: "
        + ",".join(blocking_pins()),
    )
    BASE.require(
        BASE.sha256_file(PREDECESSOR_BUILDER_PATH)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "selector238 targeted checkpoint predecessor drifted",
    )
    configure_predecessor()
    PREDECESSOR.configure_predecessor = configure_predecessor
    PREDECESSOR.patch_predecessor_row = patch_predecessor_row
    PREDECESSOR.build_public_report = build_public_report
    return PREDECESSOR.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
