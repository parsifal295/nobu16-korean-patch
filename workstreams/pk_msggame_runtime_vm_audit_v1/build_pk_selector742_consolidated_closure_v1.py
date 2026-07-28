#!/usr/bin/env python3
"""Build the selector-742 two-chunk closure on frozen post760 state."""

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
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector742_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector742_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector742_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector760_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector508_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector742_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector742_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector742_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector742_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector742_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector742_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector742_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector742_consolidated_closure_promotion.v1.json"
)

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "615941B31D7251AF6F27BC8B801CFBA130C09D5A18662763DD09C09850CC3B91",
    "assignment_private":
        "155ADFBB8BB8F4267743B54A0085FCBA91B546F345D0CE08BF6CAE30A9065BD7",
    "assignment_public":
        "B6686C33345A4990FA8DADAE5FA59DE3A97B15497D6AF4133CB524123506C6B9",
    "official_ledger":
        "797D27314E8E168E1F2BACF9174E7246B83BF6DEDB0AC3B6C925D6D076CAC8C3",
    "predecessor_decisions":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "chunk0_builder":
        "C30F05FBD0A56883191B494DD61AB9AB007D336576C554B0A9CB2972A66972CE",
    "chunk0_public":
        "C1077A83B36731331529F19F89D8BB2606A811D98C18F2999278F92C0E160E87",
    "chunk0_decisions":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "chunk0_evidence":
        "F700D9CC9CE0C238EA9E462B81AA7629BC9779CFFA3256E2C442EEDD47F33F3B",
    "chunk1_builder":
        "30E2E246434F251BF3E3F288B4D3B4B1B39231D5108EF04EB30BFF994C55CE52",
    "chunk1_public":
        "26C62F210BFE7EC9D2A253E58AFF72269F6F392390B5B5CD34D616FE24D570B3",
    "chunk1_decisions":
        "6544C936F5DFDF362EED2C5F8B7E3DF4F4A23CC0B97B8B96AB65612E2AE65901",
    "chunk1_evidence":
        "101CEC8C42CDAB15688FD2592E363352A972A9DB6403888B0FAAC35A4A1837F8",
}

EXPECTED_CHUNK_ROWS = (0, 6)
EXPECTED_CHUNK_SITES = (30, 29)
EXPECTED_DECISION_ROWS = 6
EXPECTED_DECISION_ROOTS = 2
EXPECTED_PROMOTIONS = 6
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 3
EXPECTED_ACTION_COUNTS: dict[str, int] = {
    "runtime_promotion": 3,
    "translation_override_and_runtime_promotion": 3,
}
EXPECTED_PENDING_BEFORE = 6_341
EXPECTED_PENDING_AFTER = 6_335
EXPECTED_REVIEWED_SITES = 59
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "0E2C823877679AFA9F30F45C201B700B2B1D46ED1341164933943D59156E3371"
)
EXPECTED_SOURCE_SITES = 80
EXPECTED_SOURCE_SITE_SHA256 = (
    "5C9E701BE36BF4CD43DC3BFC0244A4CA32EB631FFA4FD7357EF0E8C7E574737F"
)
EXPECTED_SOURCE_ONLY_SITES = 21
EXPECTED_SOURCE_ONLY_SHA256 = (
    "2395475C05879CC553B6D7D87001B3494E3A850CCDBD2AC2E7896475CAE59DDA"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "03D128438A4A79F1C4C59D46996D93E8DBD10ECAF707E18E0A46A0B3AF29A2F5"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "3B67EC38FCECCD9B9592A39C426EC14F64EF9354C608C176730460E2C37D8B6D"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "F0EBDA5FC1154F9568CD802D1AA65BAD4FED0A082A41CC8E20959C3A9C263881",
    "private_evidence":
        "9351D0782BC5CB2D0E473FC860B8081D9ADBC48BEDA3E82771D8AB5CBBFC500F",
    "public_coverage":
        "BA906DBF87D4CD07505DDCA10211D5644AA965919BB7E0B34927A88FCBFDC79C",
    "public_promotion":
        "078A00B34D17ACAB0C7B50D0215982769641A82E6D400E8BA4B47C9D8FD38323",
    "final_candidate":
        "BCA693F86DEE850F95996243CB5FFA3DBA56A4F58750800FFE8253F9FC2ACFBB",
    "decision_coordinates":
        "A6B026FA44E087F4166F09660CA8B997A282A783FDD18FE9702D8D6A1E88FE67",
    "promotion_coordinates":
        "A6B026FA44E087F4166F09660CA8B997A282A783FDD18FE9702D8D6A1E88FE67",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "65B241E90B7268B91760D8907C50BD6BFDEFCECF0C811289703AD46AE5BCCA5B",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "9E618E639D1B135CA8F3D92B23BB1A14F0ED60D3FC351880ECFBA310556EEAE7",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


WRAPPER = load_module(BASE_WRAPPER_PATH, "selector742_closure_base_wrapper")
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector742_closure_input")
BASE = WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = WRAPPER.configure_base


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.METHOD = (
        "post_selector508_owned_post760_selector742_two_chunk_single_"
        "coordinate_union_with_targeted_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector742-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector742-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector742-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector742-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector742_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = "nobu16.kr.pk-selector742-assignment.private.v1"


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
        and tuple(row["target"]) == (0, 742)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-742 site drifted: {site}")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("utf-8"))
    proof = coverage["proof"]
    proof.pop("all_230_candidate_sites_reviewed", None)
    proof.pop("source_only_13_absent_from_current_and_candidate", None)
    proof["all_59_candidate_sites_reviewed"] = True
    proof["confirmed_non_display_rows_untouched"] = True
    proof["seven_terminal_records_unchanged"] = True
    proof["source_only_21_absent_from_current_and_candidate"] = True
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
    terminal_roots = {(0, record_id) for record_id in range(2154, 2161)}
    decision_roots = {
        tuple(map(int, coordinate.split(":")[:2]))
        for _resource, coordinate in decision_keys
    }
    BASE.require(
        len(official) == 52_803
        and len(confirmed) == EXPECTED_CONFIRMED_NON_DISPLAY
        and not decision_keys & confirmed,
        "selector742 touched the confirmed-non-display universe",
    )
    BASE.require(
        not decision_roots & terminal_roots,
        "selector742 decision union changed one of its seven terminals",
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
                f"selector742 closure output drifted: {path}",
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
