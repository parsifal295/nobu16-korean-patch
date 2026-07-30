#!/usr/bin/env python3
"""Build the selector-760 two-chunk closure on frozen post-selector1090."""

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

BASE_WRAPPER_PATH = (
    WORKSTREAM / "build_pk_selector1090_consolidated_closure_v1.py"
)
EXPECTED_BASE_WRAPPER_SHA256 = (
    "46449314582CFBEFCBCB4BA00EB7B36C83056B8EA0F223E26795350B6A1EDDAE"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector760_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector760_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector760_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1090_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector1090_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector760_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector760_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector760_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector760_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector760_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector760_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector760_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector760_consolidated_closure_promotion.v1.json"
)

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "FBE5625F1480AB8FD5C65E349F961F6336A1EA9A4F7C2C74E9579F092B2ACE5B",
    "assignment_private":
        "2D14D2E186E8E4A23B0BC1591B669E76B701071CDFB1A8ACBF93FA15B018C6AB",
    "assignment_public":
        "7DBCAF6DF39C482E6958390A944BF3941576B69F469361129FD46715E89648F5",
    "official_ledger":
        "CDF7539F8E6A6F0D024A7357854A0AFE45E91F3CBD144822E1DEF8730A9A373F",
    "predecessor_decisions":
        "059A2A0FCC04036A4FECDC00D8C9437623E4CC1B9B1DDC63867C882D3147DD50",
    "chunk0_builder":
        "527BA454D3C30EC5DF541D69A49657C45686FABB2EE88260A99FF83D26EC068E",
    "chunk0_public":
        "F1D9F23621BF784FDF6EBC19EAC14BE88910FA18252F7D7150E2252E2812C90A",
    "chunk0_decisions":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "chunk0_evidence":
        "0C8F07C1421E03A04441C7E65BB03BF40AEEE50D1E78254725D59558980EF43B",
    "chunk1_builder":
        "1F9DCCC3EA4E93DB0634B735BD72AC35396C0BD6252782C8D6E5EB38962D41AF",
    "chunk1_public":
        "59081F5586BC4F9B5DA57363071A40677AACF449100F15BF74833079ACCF67E4",
    "chunk1_decisions":
        "0C4A803CF5776E39953CC7983B4F91C0E728EF91C0E3C488FF7C9C62B376C51D",
    "chunk1_evidence":
        "D5C8D20A7F79036C8836EB11762C9E77EBC21AC8B2C57CB7AD2327DEE772B667",
}

EXPECTED_CHUNK_ROWS = (0, 30)
EXPECTED_CHUNK_SITES = (16, 16)
EXPECTED_DECISION_ROWS = 30
EXPECTED_DECISION_ROOTS = 9
EXPECTED_PROMOTIONS = 27
EXPECTED_RENEWALS = 3
EXPECTED_OVERRIDES = 14
EXPECTED_ACTION_COUNTS: dict[str, int] = {
    "runtime_promotion": 16,
    "translation_override_and_runtime_promotion": 11,
    "translation_override_and_verification_renewal": 3,
}
EXPECTED_PENDING_BEFORE = 6_368
EXPECTED_PENDING_AFTER = 6_341
EXPECTED_REVIEWED_SITES = 32
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "1226CF6A1892998D892C15480708068D21ADA054D21BDA982DF0D0B51E05131D"
)
EXPECTED_SOURCE_SITES = 35
EXPECTED_SOURCE_SITE_SHA256 = (
    "54BF3A71CCC45F8DD56283FDB93F597A52E4D70BF3EBE9BDF201C36CDBFCF416"
)
EXPECTED_SOURCE_ONLY_SITES = 3
EXPECTED_SOURCE_ONLY_SHA256 = (
    "D6C6A092B570F9846E422D7063FEFD47342351DB248E6EDE52DE1BB8880188A5"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "396A8DF109A0693C439F990049477F5DE6E10720854D73057F3DFA1702002CCF"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "C01950D1B342D45FF8C6FBEB3D7EFD0B5087592D0585EC1A60A668FE0C0B0D93"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "959DD7C8607CBB4F5FCB1DF769914ABF03331A1F7C3CDB75EFD073303BB05FB3",
    "private_evidence":
        "FD4A436CEDF6C51B61C3CBF42275C70FC56DD2C7D43F5A6C1CC563EB45B554AC",
    "public_coverage":
        "089ECED1B842375BB0B33FF5AAD08ED35EDD32B1DE142ECD9F3EB9AB277458F4",
    "public_promotion":
        "04A6157CBAB6D9546F74C0CEF1266076BF5F87048642F3833872BF240F3B68C8",
    "final_candidate":
        "03D128438A4A79F1C4C59D46996D93E8DBD10ECAF707E18E0A46A0B3AF29A2F5",
    "decision_coordinates":
        "C14B5FC0FFFD08997BCAA1685B98015C8EB7207AE7290DB16059A3D27C1E3EDD",
    "promotion_coordinates":
        "FBB11BF3A69947409A9E443A15F4E1773981565EAB42326E6AA58D0F3D23C020",
    "renewal_coordinates":
        "24FAC46E2722AFD0994829AAF0B1C206DC88445DEC12AED4AF00DA11C52C4CE9",
    "override_coordinates":
        "3247C83C4288BA33BF53007BEA758BDF6A9004268B678F389148B4B3BA7E1EC5",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "E1B17F92F6D1C66D1A139E5471D3BB0350C24A30390FE283CC01BF32FA6386CD",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


WRAPPER = load_module(BASE_WRAPPER_PATH, "selector760_closure_base_wrapper")
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector760_closure_input")
BASE = WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = WRAPPER.configure_base


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.METHOD = (
        "post_selector1090_selector760_two_chunk_single_coordinate_union_"
        "with_targeted_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector760-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector760-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector760-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector760-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector760_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = "nobu16.kr.pk-selector760-assignment.private.v1"


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
        and tuple(row["target"]) == (0, 760)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-760 site drifted: {site}")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("utf-8"))
    proof = coverage["proof"]
    proof.pop("all_230_candidate_sites_reviewed", None)
    proof.pop("source_only_13_absent_from_current_and_candidate", None)
    proof["all_32_candidate_sites_reviewed"] = True
    proof["confirmed_non_display_rows_untouched"] = True
    proof["seven_terminal_records_unchanged"] = True
    proof["source_only_3_absent_from_current_and_candidate"] = True
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
    terminal_roots = {(0, record_id) for record_id in range(2175, 2182)}
    decision_roots = {
        tuple(map(int, coordinate.split(":")[:2]))
        for _resource, coordinate in decision_keys
    }
    BASE.require(
        len(official) == 52_803
        and len(confirmed) == EXPECTED_CONFIRMED_NON_DISPLAY
        and not decision_keys & confirmed,
        "selector760 touched the confirmed-non-display universe",
    )
    BASE.require(
        not decision_roots & terminal_roots,
        "selector760 decision union changed one of its seven terminals",
    )


for _name, _value in {
    "ASSIGNMENT": ASSIGNMENT,
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
    "EXPECTED_CONFIRMED_NON_DISPLAY": EXPECTED_CONFIRMED_NON_DISPLAY,
    "EXPECTED_OFFICIAL_CANDIDATE_SHA256": EXPECTED_OFFICIAL_CANDIDATE_SHA256,
    "EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256":
        EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256,
    "EXPECTED_OUTPUT_SHA256": EXPECTED_OUTPUT_SHA256,
    "configure_base": configure_base,
    "validate_site_call": validate_site_call,
    "transform_outputs": transform_outputs,
    "validate_wrapper_invariants": validate_wrapper_invariants,
}.items():
    setattr(WRAPPER, _name, _value)


def build_outputs() -> dict[Path, bytes]:
    BASE.require(
        BASE.sha256_file(BASE_WRAPPER_PATH) == EXPECTED_BASE_WRAPPER_SHA256,
        "selector1090 closure wrapper drifted",
    )
    return WRAPPER.build_outputs()


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
                f"selector760 closure output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(json.dumps({
        "decision_rows": EXPECTED_DECISION_ROWS,
        "pending_after": EXPECTED_PENDING_AFTER,
        "promotions": EXPECTED_PROMOTIONS,
        "source_only_actions": 0,
        "status": "PASS",
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
