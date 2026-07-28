#!/usr/bin/env python3
"""Consolidate the two selector-1078 reviews on the post-selector268 state."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
SEMANTIC_TMP = DIALOGUE_TMP / "semantic_overrides"
PUBLIC_DIR = WORKSTREAM / "public"

SCAFFOLD_PATH = (
    WORKSTREAM / "build_pk_selector268_consolidated_closure_v1.py"
)
EXPECTED_SCAFFOLD_SHA256 = (
    "B7BBE790594D06F5962755462467575FA75663D72A180FE694D79F59E3C81914"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector1078_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector1078_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector1078_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector268_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector268_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector1078_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector1078_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector1078_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector1078_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector1078_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector1078_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector1078_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector1078_consolidated_closure_promotion.v1.json"
)

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "3D8332E789CD35560E78A68B153F25E20E500FF681E6DB38515240204DBE8551",
    "assignment_private":
        "6637FE722BF183489E8BE32473A67C5B40FDD2BB25DB080D6C5B429111A90F4D",
    "assignment_public":
        "0B01BDE88CE6CF091E07720FB5C83772F2C7EA7E9139C85EEFF7788F92864EA3",
    "official_ledger":
        "0936BD050D1BB529848AD861B951D178A3521C086BC41027C4ED4A5B4FBC79C3",
    "predecessor_decisions":
        "127BA2D9B9F443AA4DF5030643F476CBB943C971300020F249461A3745F6D93F",
    "chunk0_builder":
        "43D22C72260B478FA6FFB495DC3BB1F087E48A33CB0990B8F8D871C9AED6257F",
    "chunk0_public":
        "9976EE272E2F83FF93CAFE341AD3CBE5865D41918777288DF012F1D1BD5F98AE",
    "chunk0_decisions":
        "E29B1FE509F18C48189B5D532EEA7F47D711FF8FF8298283D46AA1CDA9D57D02",
    "chunk0_evidence":
        "56362E38B394EAB7739DC6497BEE5711A9600DAB30BB02A062C5820E4C9DD0CA",
    "chunk1_builder":
        "C81B80795C6F42F2913873B624AF088419F89B95ACBA77CA8F3A2D25BC26D1D8",
    "chunk1_public":
        "8844E5A29E3FD00735CE26A2FE2EE226A4C732F765D524613391040DC2CDE45D",
    "chunk1_decisions":
        "3FA2BF9BE3D62F980CF6BB90558999C921D68BDC97E470103050BEE3703C3429",
    "chunk1_evidence":
        "8D3C1A367AC82F23EBEAA05F4DEB973D3C5FD453437EBB3B3E1CB64CA732B99C",
}
EXPECTED_CHUNK_ROWS = (7, 10)
EXPECTED_CHUNK_SITES = (21, 22)
EXPECTED_DECISION_ROWS = 17
EXPECTED_DECISION_ROOTS = 7
EXPECTED_PROMOTIONS = 17
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 7
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 10,
    "translation_override_and_runtime_promotion": 7,
}
EXPECTED_PENDING_BEFORE = 6_232
EXPECTED_PENDING_AFTER = 6_215
EXPECTED_REVIEWED_SITES = 43
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "1D977FB6545FEB31EB452406B631B2730F77D5B7E07F29C3702F906200D461FB"
)
EXPECTED_SOURCE_SITES = 44
EXPECTED_SOURCE_SITE_SHA256 = (
    "A38C16555B9317E926627F2A9C2DD0C4C5ABC591EE23DCA4BAFB8CBB19C115BB"
)
EXPECTED_SOURCE_ONLY_SITES = 1
EXPECTED_SOURCE_ONLY_SHA256 = (
    "930A41B073B7144918A618D15D9E8181F53AAF6862408379527C993CC8CB24FA"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "92B86808931C1FD34320BC5A9BFD05B7AD704FA9392534FF8DE8F6293F413DAD"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "FD8A708ED92756AB2024861A1B97550F8229889282E7B58CDEFAEEDFC0C2ECE3"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "51C604DD377D15C87B104D243917530C2F1FBB2956C4770AC77451C9ED249219"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "D530A0A4D56E02144371B1A8299A42438CC4372773D1D0A23B9688E18E560AA9"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "2CFD3803511E2C4BCDDDFC25768645ED2E90CB8CACB750FC27F82742E9CA3793"
)
EXPECTED_EMPTY_CONTEXT_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "82196010FD6EF8C06B186FE8BA3A48DFAC684ABA7A3ADEDFCA66D7F843A34B70",
    "private_evidence":
        "928D92973E6A83E5AECB59339A20E6750C7080447E4A3CA5D82207E9DD4A2422",
    "public_coverage":
        "0EE007EF829401A0ECF4C2FF23708FD4E5BC4BEAE211CAE25CB371B523C9AC81",
    "public_promotion":
        "0A8479EB633541824D59E73F2C75335E2C265A369E6C7535A1D7C1EE6B15C02A",
    "final_candidate":
        "1A931E023A5248626AE90094772657D91B4270D0F530B48ABC613FDA84BB508D",
    "decision_coordinates":
        "06206391F470EF8CC73379D59CBB64D2E18460A4980B9B79709941DBC65E5AE4",
    "promotion_coordinates":
        "06206391F470EF8CC73379D59CBB64D2E18460A4980B9B79709941DBC65E5AE4",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "76D3B7655FC64EA69FF1F822639F0B332025B9729FDD5F2706F8303C91B3819E",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "E34022257593E9AC6379C74CF4AB5CE8BD51D71247442DC1A6AF59C9DA0087B0",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCAFFOLD = load_module(SCAFFOLD_PATH, "selector1078_closure_scaffold")
WRAPPER = SCAFFOLD.WRAPPER
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector1078_closure_input")
BASE = WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = SCAFFOLD.ORIGINAL_CONFIGURE_BASE


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.METHOD = (
        "post_selector268_selector1078_two_chunk_single_coordinate_union_"
        "with_bound_negative_and_same_gap_block_guards"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector1078-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector1078-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector1078-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector1078-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector1078_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = (
        "nobu16.kr.pk-selector1078-assignment.private.v1"
    )


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
        and tuple(row["target"]) == (0, 1078)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-1078 site drifted: {site}")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("utf-8"))
    proof = coverage["proof"]
    for key in tuple(proof):
        if key.startswith("all_") and key.endswith("_candidate_sites_reviewed"):
            proof.pop(key)
        if key.startswith("source_only_") and key.endswith(
            "_absent_from_current_and_candidate"
        ):
            proof.pop(key)
    proof.update({
        "all_43_candidate_sites_reviewed": True,
        "completed_selector_overlaps_freshly_reviewed": True,
        "confirmed_non_display_rows_untouched": True,
        "non_display_candidate_action_count_zero": True,
        "pending_assembly_evidence_did_not_auto_promote": True,
        "same_gap_atoms_blocked_as_one_unit": True,
        "seven_terminal_records_unchanged": True,
        "source_only_1_absent_from_current_and_candidate": True,
        "source_only_action_count_zero": True,
        "terminal_records_absent_from_decisions": True,
        "terminal_register_multiplicity_preserved": True,
    })
    coverage["guards"].pop("payload_without_guard_sha256", None)
    coverage["guards"]["payload_without_guard_sha256"] = BASE.canonical_sha256(
        coverage
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)
    return outputs


def terminal_values(records: Mapping[tuple[int, int], Any]) -> list[str]:
    values = []
    for record_id in range(2560, 2567):
        literals = ASSIGNMENT.ASSIGNMENT.ENGINE.parse_record_literals(
            records[(0, record_id)]
        )
        BASE.require(len(literals) == 1, "terminal literal shape drifted")
        values.append(literals[0].text)
    return values


def terminal_digest(records: Mapping[tuple[int, int], Any]) -> str:
    return BASE.sha256_bytes(
        "\0".join(terminal_values(records)).encode("utf-8")
    )


def validate_wrapper_invariants(outputs: Mapping[Path, bytes]) -> None:
    decisions = [
        json.loads(line)
        for line in outputs[PRIVATE_DECISIONS_OUTPUT]
        .decode("utf-8", errors="strict")
        .splitlines()
        if line
    ]
    assignment = json.loads(
        ASSIGNMENT_PRIVATE_PATH.read_text(encoding="utf-8")
    )
    decision_roots = {
        ":".join(str(row["coordinate"]).split(":")[:2])
        for row in decisions
    }
    terminal_roots = {
        f"0:{record_id}" for record_id in range(2560, 2567)
    }
    same_gap_roots = set(assignment["same_gap_control_atom"]["roots"])
    candidate, current, source, contexts, _pending = (
        ASSIGNMENT.ASSIGNMENT.RECORDS.load_records()
    )
    BASE.require(
        not decision_roots & terminal_roots
        and not decision_roots & same_gap_roots,
        "shared terminal or same-gap atom entered decision union",
    )
    BASE.require(
        terminal_digest(candidate) == EXPECTED_TERMINAL_CANDIDATE_SHA256
        and terminal_digest(current) == EXPECTED_TERMINAL_CURRENT_SHA256
        and terminal_digest(source) == EXPECTED_TERMINAL_SOURCE_SHA256
        and all(
            terminal_digest(contexts[language])
                == EXPECTED_EMPTY_CONTEXT_TERMINAL_SHA256
            for language in ("en", "sc", "tc")
        )
        and sorted(Counter(terminal_values(candidate)).values()) == [2, 2, 3],
        "selector1078 terminal contract drifted",
    )
    BASE.require(
        len(decisions) == EXPECTED_DECISION_ROWS
        and all(
            row.get("fresh_semantic_review") == "approved"
            and row.get("runtime_review") == "verified"
            and "auto" not in str(row.get("action", "")).lower()
            for row in decisions
        ),
        "union contains an inherited or automatic decision",
    )
    chunk_evidence = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in CHUNK_EVIDENCE
    ]
    BASE.require(
        chunk_evidence[0]["prior_evidence"][
            "automatic_status_promotion_authorized"
        ] is False
        and chunk_evidence[1]["proof"][
            "prior_pending_evidence_automatic_promotion_count"
        ] == 0
        and chunk_evidence[1]["proof"][
            "multi_control_partial_pass_authorized"
        ] is False,
        "prior-evidence or same-gap rejection drifted",
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
        BASE.sha256_file(SCAFFOLD_PATH) == EXPECTED_SCAFFOLD_SHA256,
        "selector268 closure scaffold drifted",
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
                f"selector1078 closure output drifted: {path}",
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
