#!/usr/bin/env python3
"""Build the selector-1090 two-chunk closure on frozen post-selector178."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
SEMANTIC_TMP = DIALOGUE_TMP / "semantic_overrides"
PUBLIC_DIR = WORKSTREAM / "public"

BASE_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector514_consolidated_closure_core_v1.py"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector1090_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector1090_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector1090_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector178_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector178_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector1090_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector1090_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector1090_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector1090_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector1090_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector1090_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector1090_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector1090_consolidated_closure_promotion.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "AE64FFC67F3B8424E78026DE82D32D8A176051A4FF8B45C1FDDBB750155DE4A3"
)
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "3E1D9AC82DB1BF6CA842AD47C2C5227A6F63BC80DCEA6C8553B1267DB1F15061",
    "assignment_private":
        "B256F67F1A584D8895BA7BDCCA764338A9F9A08B12C78F00579703035AC090FA",
    "assignment_public":
        "917E3C6087EE4593EEEA0529A2FE88E6D68FE16A69CBC61A0476113EE719EE9B",
    "official_ledger":
        "A11DC8F5F0BAA9532DCB7737AFAFC8732506AC2F4E4B6479B44056CF9958015D",
    "predecessor_decisions":
        "2F81E5E455F613A8B6550787FFB278282002B7BC487B60B29E05DCB09CB4C093",
    "chunk0_builder":
        "F0E889354EE4434F4B2E6DFD7EBE7A15D1A21053894CEFD6A30173BA7AF12103",
    "chunk0_public":
        "C390C034B0C115E60440616B8DABC289F65CB28D7F32410F4C774A34E7949833",
    "chunk0_decisions":
        "86180B30A40AF71F3C4D417DEED2D4184167003A45C215BFA262722F478D0789",
    "chunk0_evidence":
        "4664A9C4B009C6DF3EE52AE8B9D6881CB795B3E46987ED669306EFC006D1D7D3",
    "chunk1_builder":
        "F980540767D3E329966A7608DFD12C1DEDF611402382B7BCA4BC0C8DE10CAE61",
    "chunk1_public":
        "29A3743CD7EAB0C3C4927A378615D6BB89103753608948E76E1766F3FD0E10B3",
    "chunk1_decisions":
        "D567CBD70E2491D4FE4B90678F441C7C8168830199F9088AFCB85A75F7E42857",
    "chunk1_evidence":
        "BA0B228198517C8B9207A699356E8E9C890E58EA76F41CDF28424BCA21129835",
}

EXPECTED_CHUNK_ROWS = (49, 40)
EXPECTED_CHUNK_SITES = (47, 49)
EXPECTED_DECISION_ROWS = 89
EXPECTED_DECISION_ROOTS = 47
EXPECTED_PROMOTIONS = 64
EXPECTED_RENEWALS = 25
EXPECTED_OVERRIDES = 33
EXPECTED_ACTION_COUNTS: dict[str, int] = {
    "runtime_promotion": 56,
    "translation_override_and_runtime_promotion": 8,
    "translation_override_and_verification_renewal": 25,
}
EXPECTED_PENDING_BEFORE = 6_432
EXPECTED_PENDING_AFTER = 6_368
EXPECTED_REVIEWED_SITES = 96
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "CA5CA7CB645EBAB0E58629C4F05D435AF7EDDC8889C217F16F245B565E73965C"
)
EXPECTED_SOURCE_SITES = 104
EXPECTED_SOURCE_SITE_SHA256 = (
    "492E028A752B106F3A56160ED47B1430815BC2F9110ADC9256E8857E1F6CFE53"
)
EXPECTED_SOURCE_ONLY_SITES = 8
EXPECTED_SOURCE_ONLY_SHA256 = (
    "70EA10F83D5E591BF8FF0691A9AA7616E42A06CFCF73476AEA98672C1194F84A"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "D89D47866F7FA9D34F68814219A00840921C130E062EA5DE80F95063B9E96E7F"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "8850CDFFDEF13076DF8402F68AA4F72528C9ACEE8145F4A65B4FAF64C7A27742"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "059A2A0FCC04036A4FECDC00D8C9437623E4CC1B9B1DDC63867C882D3147DD50",
    "private_evidence":
        "FB0A5C409C8DE15FB63CA99185B2CDD7F64D79A14D23EFD45C6CDF818E3AD31A",
    "public_coverage":
        "14FE39742FF3BC069A7DED2B23F72AD772905FDBA8AFC26AE652A638B5E9BCC5",
    "public_promotion":
        "DEEDA41871B5711E4C9A30CCE0F65F046ECAF8B26F44F76CC3B2598078180CE6",
    "final_candidate":
        "396A8DF109A0693C439F990049477F5DE6E10720854D73057F3DFA1702002CCF",
    "decision_coordinates":
        "C630D3687B1337FC7BFE5366366C18C6A8381D22DEFA9EC9817840C26DB9E8C5",
    "promotion_coordinates":
        "60532C3BC0080546F27503110557929B9487F3F21E0FC9BABEE5896F2714B40F",
    "renewal_coordinates":
        "6DF4F642C48AB2704BEB52C937B99BF7FD59FD40C3BE907A66093458E672C6E4",
    "override_coordinates":
        "BCB6C6401010D51DD24A0A0065F718B2FC17A2E93E4317AC473156136D91B0A7",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "643478BD8D20FD1F078264B8CDC0C0B1E03832370036DEBDCD325A285D90207C",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_BUILDER_PATH, "selector1090_closure_base")
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector1090_closure_input")


def configure_base() -> None:
    ASSIGNMENT.coordinate_digest = ASSIGNMENT.ASSIGNMENT.coordinate_digest
    ASSIGNMENT.site_digest = ASSIGNMENT.ASSIGNMENT.site_digest
    values = {
        "ASSIGNMENT": ASSIGNMENT,
        "ENGINE": ASSIGNMENT.ENGINE,
        "RANKING": ASSIGNMENT.RANKING,
        "ASSIGNMENT_BUILDER_PATH": ASSIGNMENT_BUILDER_PATH,
        "ASSIGNMENT_PRIVATE_PATH": ASSIGNMENT_PRIVATE_PATH,
        "ASSIGNMENT_PUBLIC_PATH": ASSIGNMENT_PUBLIC_PATH,
        "OFFICIAL_LEDGER_PATH": OFFICIAL_LEDGER_PATH,
        "PREDECESSOR_DECISIONS_PATH": PREDECESSOR_DECISIONS_PATH,
        "CHUNK_BUILDERS": CHUNK_BUILDERS,
        "CHUNK_PUBLIC": CHUNK_PUBLIC,
        "CHUNK_DECISIONS": CHUNK_DECISIONS,
        "CHUNK_EVIDENCE": CHUNK_EVIDENCE,
        "PRIVATE_DECISIONS_OUTPUT": PRIVATE_DECISIONS_OUTPUT,
        "PRIVATE_EVIDENCE_OUTPUT": PRIVATE_EVIDENCE_OUTPUT,
        "PUBLIC_COVERAGE_OUTPUT": PUBLIC_COVERAGE_OUTPUT,
        "PUBLIC_PROMOTION_OUTPUT": PUBLIC_PROMOTION_OUTPUT,
        "EXPECTED_INPUT_SHA256": EXPECTED_INPUT_SHA256,
        "EXPECTED_CHUNK_ROWS": EXPECTED_CHUNK_ROWS,
        "EXPECTED_CHUNK_SITES": EXPECTED_CHUNK_SITES,
        "EXPECTED_DECISION_ROWS": EXPECTED_DECISION_ROWS,
        "EXPECTED_DECISION_ROOTS": EXPECTED_DECISION_ROOTS,
        "EXPECTED_PROMOTIONS": EXPECTED_PROMOTIONS,
        "EXPECTED_RENEWALS": EXPECTED_RENEWALS,
        "EXPECTED_OVERRIDES": EXPECTED_OVERRIDES,
        "EXPECTED_ACTION_COUNTS": EXPECTED_ACTION_COUNTS,
        "EXPECTED_PENDING_BEFORE": EXPECTED_PENDING_BEFORE,
        "EXPECTED_PENDING_AFTER": EXPECTED_PENDING_AFTER,
        "EXPECTED_REVIEWED_SITES": EXPECTED_REVIEWED_SITES,
        "EXPECTED_CANDIDATE_SITE_SHA256": EXPECTED_CANDIDATE_SITE_SHA256,
        "EXPECTED_SOURCE_SITES": EXPECTED_SOURCE_SITES,
        "EXPECTED_SOURCE_SITE_SHA256": EXPECTED_SOURCE_SITE_SHA256,
        "EXPECTED_SOURCE_ONLY_SITES": EXPECTED_SOURCE_ONLY_SITES,
        "EXPECTED_SOURCE_ONLY_SHA256": EXPECTED_SOURCE_ONLY_SHA256,
        "EXPECTED_PREDECESSOR_OVERLAPS": EXPECTED_PREDECESSOR_OVERLAPS,
        "EXPECTED_PREDECESSOR_SUPERSESSIONS":
            EXPECTED_PREDECESSOR_SUPERSESSIONS,
        "EXPECTED_OFFICIAL_CANDIDATE_SHA256":
            EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        "EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256":
            EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256,
        "EXPECTED_OUTPUT_SHA256": {
            key: (
                None
                if key in {"public_coverage", "public_promotion"}
                else value
            )
            for key, value in EXPECTED_OUTPUT_SHA256.items()
        },
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    BASE.METHOD = (
        "post_selector178_selector1090_two_chunk_single_coordinate_union_"
        "with_targeted_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector1090-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector1090-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector1090-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector1090-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector1090_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = "nobu16.kr.pk-selector1090-assignment.private.v1"


def validate_site_call(
    records: Mapping[tuple[int, int], Any],
    site: str,
    *,
    expected: bool,
) -> None:
    block_id, record_id, gap_id, offset = map(int, site.split(":"))
    rows = [
        row
        for row in BASE.RANKING.LEGACY.record_edges(records[(block_id, record_id)])
        if row["kind"] == "C"
        and tuple(row["target"]) == (0, 1090)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-1090 site drifted: {site}")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("utf-8"))
    proof = coverage["proof"]
    proof.pop("all_230_candidate_sites_reviewed", None)
    proof.pop("source_only_13_absent_from_current_and_candidate", None)
    proof["all_96_candidate_sites_reviewed"] = True
    proof["confirmed_non_display_rows_untouched"] = True
    proof["seven_terminal_records_unchanged"] = True
    proof["source_only_8_absent_from_current_and_candidate"] = True
    coverage["guards"].pop("payload_without_guard_sha256")
    coverage["guards"]["payload_without_guard_sha256"] = BASE.canonical_sha256(
        coverage
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)
    return outputs


def validate_wrapper_invariants(outputs: Mapping[Path, bytes]) -> None:
    official = [
        json.loads(line)
        for line in OFFICIAL_LEDGER_PATH.read_text(encoding="utf-8").splitlines()
        if line
    ]
    decisions = [
        json.loads(line)
        for line in outputs[PRIVATE_DECISIONS_OUTPUT]
        .decode("utf-8", errors="strict")
        .splitlines()
        if line
    ]
    confirmed = {
        (str(row["resource"]), str(row["coordinate"]))
        for row in official
        if row.get("scope_classification") == "confirmed_non_display"
    }
    decision_keys = {
        (str(row["resource"]), str(row["coordinate"])) for row in decisions
    }
    terminal_roots = {(0, record_id) for record_id in range(2574, 2581)}
    decision_roots = {
        tuple(map(int, coordinate.split(":")[:2]))
        for _resource, coordinate in decision_keys
    }
    BASE.require(
        len(official) == 52_803
        and len(confirmed) == EXPECTED_CONFIRMED_NON_DISPLAY
        and not decision_keys & confirmed,
        "selector1090 touched the confirmed-non-display universe",
    )
    BASE.require(
        not decision_roots & terminal_roots,
        "selector1090 decision union changed one of its seven terminals",
    )


def build_outputs() -> dict[Path, bytes]:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector closure base drifted",
    )
    BASE.require(
        all(value is not None for value in EXPECTED_INPUT_SHA256.values()),
        "selector1090 chunk inputs are not frozen yet",
    )
    BASE.require(
        EXPECTED_DECISION_ROWS >= 0
        and EXPECTED_DECISION_ROOTS >= 0
        and EXPECTED_PROMOTIONS >= 0
        and EXPECTED_RENEWALS >= 0
        and EXPECTED_OVERRIDES >= 0
        and EXPECTED_PENDING_AFTER >= 0
        and EXPECTED_PREDECESSOR_OVERLAPS >= 0
        and EXPECTED_PREDECESSOR_SUPERSESSIONS >= 0,
        "selector1090 exact union constants are not frozen yet",
    )
    configure_base()
    BASE.validate_site_call = validate_site_call
    outputs = BASE.build_outputs()
    validate_wrapper_invariants(outputs)
    outputs = transform_outputs(outputs)
    labels = {
        PRIVATE_DECISIONS_OUTPUT: "private_decisions",
        PRIVATE_EVIDENCE_OUTPUT: "private_evidence",
        PUBLIC_COVERAGE_OUTPUT: "public_coverage",
        PUBLIC_PROMOTION_OUTPUT: "public_promotion",
    }
    for path, label in labels.items():
        expected = EXPECTED_OUTPUT_SHA256[label]
        BASE.require(
            expected is None or BASE.sha256_bytes(outputs[path]) == expected,
            f"frozen {label} drifted",
        )
    return outputs


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    outputs = build_outputs()
    if args.check:
        for path, content in outputs.items():
            BASE.require(
                path.is_file() and path.read_bytes() == content,
                f"selector1090 closure output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(
        json.dumps(
            {
                "decision_rows": EXPECTED_DECISION_ROWS,
                "pending_after": EXPECTED_PENDING_AFTER,
                "promotions": EXPECTED_PROMOTIONS,
                "source_only_actions": 0,
                "status": "PASS",
                "steam_write_performed": False,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
