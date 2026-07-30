#!/usr/bin/env python3
"""Apply selector-322 as a targeted immutable ledger delta."""

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
    WORKSTREAM / "build_runtime_vm_post_selector742_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector742_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector742_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector322_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector322_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector322_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector322_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector322_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector322_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector322_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "13A1467320BABDE88F9DC57DBB0B6C0366907AF6502E38521076D65CED9EB65D"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "4AC2CD8969958AA254D0F70F7302E1BC3D273229DBB59A0512FEB27E1786D90B"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "D9A52A500BD6E60D3B35574E1890BFC128151A9328A5CAE8B1C4CFBEAB087E9B"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "BCA693F86DEE850F95996243CB5FFA3DBA56A4F58750800FFE8253F9FC2ACFBB"
)
EXPECTED_CLOSURE_BUILDER_SHA256 = (
    "6DB6F858D716E9F77B5FAE46A60C9D4AE679B055BF5EB6432971EC4694B2BA70"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "F7992DD09D0955EC49B2CFD4419D1B53F29857E58510F4382C0514DEA83AF80B"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    "9642374CCA6ECEC2D478AFD8970A6106F576431C44705E095FAE1D8F04E4883F"
)
EXPECTED_CLOSURE_COVERAGE_SHA256 = (
    "2DE91D13ECE1E9AA8C47FE79C3BBBA9C1653131C9F56E1A517B86A8315F1885E"
)
EXPECTED_CLOSURE_PROMOTION_SHA256 = (
    "4F2DBE92BE6ADBA9EFA80A0A00A7C12E165EE61A1C31616E369FCBACC2EE1930"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 28
EXPECTED_UNAFFECTED_ROWS = 52_775
EXPECTED_OWNER_ROWS = 28
EXPECTED_PROMOTIONS = 25
EXPECTED_RENEWALS = 3
EXPECTED_OVERRIDES = 12
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 16,
    "translation_override_and_runtime_promotion": 9,
    "translation_override_and_verification_renewal": 3,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 17, 1: 11}
EXPECTED_PREDECESSOR_PENDING = 6_335
EXPECTED_FINAL_PENDING = 6_310
EXPECTED_PREDECESSOR_ELIGIBLE = 46_468
EXPECTED_FINAL_ELIGIBLE = 46_493
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_348
EXPECTED_FINAL_PK_PROMOTIONS = 14_373
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 29_999
EXPECTED_FINAL_PROMOTED_TOTAL = 30_024
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES = 85
EXPECTED_SOURCE_ONLY_SITES = 9
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "1169E96A368BD9E0362D4370CE828D65140ECB0189B99F2B667D771EE89282EB"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "5F971848A7D1BB9D1197BA0D1C13B71F01F02D023E27EC5CAD8E88150C073AED"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "BF7195E809B3E53F4E18E35CF7C9D282CC2D242E03AC8D803ACAEDD034549701"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "39AC2461307157E7B837CC457B33B00BDA7FF54C8638BD945807E46F86008B51"
)
EXPECTED_REVIEWED_SITE_SHA256 = (
    "E2E30CDE0A542E9265C4FAB36BE0C2701B74D84EF588EE52A8DA2CE5E3A3177F"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "93CE5ED3ED53ACF06FEDA71F84A2F24F86A4E419112BC68AFD5D37E80264EC7A"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "D0739EBB2E00B9034071165D00CA0D5E08D5F30A6400C8FF38CDA2867BA0203E"
)
UPDATE_ACTION_FIELD = "selector322_consolidated_update_action"
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "9A7E135544FA2F2A02A0D2B4941159CB92A3E4A495AF72B6CB335DE371351343"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "3C245CE82733F50F08E61B05A165B1038C4D5BBA5D3DAD38D46933B392101642"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR = load_module(PREDECESSOR_BUILDER_PATH, "selector322_checkpoint_base")
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
        "nobu16.kr.pc-dialogue-runtime-vm-selector322-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector322-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector742_selector322_single_coordinate_union_targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = (
        "selector322_consolidated_exact_override_evidence"
    )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector322-consolidated-row-verification.v1"
    )
    verification["method"] = "reversed_vm_pk_selector322_consolidated_closure"
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    report = PREDECESSOR.build_public_report(private_sha256, stream_result)
    report["selector322_consolidated"] = report.pop("selector742_consolidated")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        BASE.sha256_file(PREDECESSOR_BUILDER_PATH)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "selector742 targeted checkpoint base drifted",
    )
    configure_base()
    BASE.validate_closure_reports = UPSTREAM.validate_closure_reports
    BASE.patch_predecessor_row = patch_predecessor_row
    BASE.build_public_report = build_public_report
    decisions = BASE.load_closure_decisions()
    PREDECESSOR.validate_confirmed_non_display(decisions)
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
