#!/usr/bin/env python3
"""Scaffold the selector-1168 two-chunk closure on post-selector364 state."""

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

SCAFFOLD_BASE_PATH = (
    WORKSTREAM / "build_pk_selector364_consolidated_closure_v1.py"
)
EXPECTED_SCAFFOLD_BASE_SHA256 = (
    "024A7A1946808584EB9C52F28A80F6804CDF727D2A50636C6541485A4AD64596"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector1168_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector1168_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector1168_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector364_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector364_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector1168_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector1168_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector1168_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector1168_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector1168_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector1168_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector1168_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector1168_consolidated_closure_promotion.v1.json"
)

# Both bounded reviews and their single-coordinate union are frozen below.
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "48D0F8AB64F8F5FA9A2953A6B277519C724A838EF41CB83DB49D3FC8512B25F5",
    "assignment_private":
        "F2256EDB63FAD8148C6C8C1CDA8CF8E51C2BB47E2218812C34D921C3A8A8546B",
    "assignment_public":
        "33FF21CFE153B280B0F365573529B5BBA77B77BFB149623584C9B75237A13A2F",
    "official_ledger":
        "B776FEF076BC8A466D02F7A8C3624A2BC1EF52012306715A7FF083CF1F53FBD5",
    "predecessor_decisions":
        "19FB86E3D7B129344B42F391F9F8B72CC6ED0D3AFE61A86031A8BFD6EC9E5106",
    "chunk0_builder":
        "DCDDC1230496E6698CB5F39D15B77CEE660DCA6D4F06834A6D740FCC2E633A33",
    "chunk0_public":
        "775A5AB4238F45ECDC0DBA5467E4EEA21EFE698C0A2E9BFF621EDA9DFD5BFF64",
    "chunk0_decisions":
        "585C20C50BB22B709D03C7F6766E34C69B66E989ED7FADF28300B9BA810C5CCC",
    "chunk0_evidence":
        "19C318217E21CD7B7B1F64C01E3FA464BA8A0CF410085DC338E7C813B66B68DD",
    "chunk1_builder":
        "97DAEE691FC06B0107183394E848E4707DEE9A521EA573A81B9C3D1F448339C1",
    "chunk1_public":
        "5DA0977A9D46AE08273047A4185032D6EE60A0792C0BD38B56946AD49877F8B8",
    "chunk1_decisions":
        "C19E154059B94BE562ABEC3E174D7455DA657FDEB60DB9B569F4F7013797CF25",
    "chunk1_evidence":
        "6503637FC758A09AB11A1A8BF98BE7F0E160E6363A12CDEECCE44F827965CF0D",
}

EXPECTED_CHUNK_ROWS: tuple[int | None, int | None] = (15, 4)
EXPECTED_CHUNK_SITES = (26, 27)
EXPECTED_DECISION_ROWS: int | None = 19
EXPECTED_DECISION_ROOTS: int | None = 5
EXPECTED_PROMOTIONS: int | None = 19
EXPECTED_RENEWALS: int | None = 0
EXPECTED_OVERRIDES: int | None = 5
EXPECTED_ACTION_COUNTS: dict[str, int] | None = {
    "runtime_promotion": 14,
    "translation_override_and_runtime_promotion": 5,
}
EXPECTED_PENDING_BEFORE = 6_302
EXPECTED_PENDING_AFTER: int | None = 6_283
EXPECTED_REVIEWED_SITES = 53
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "5B250420F71B3E9A0BEBB3476A7BAF45BA7B99D913F783148D753D5A2676EF3B"
)
EXPECTED_SOURCE_SITES = 58
EXPECTED_SOURCE_SITE_SHA256 = (
    "D65A8E5D411413BFE6DAB0A57EC756A67C04F612F82022175703B30237D3DF1C"
)
EXPECTED_SOURCE_ONLY_SITES = 5
EXPECTED_SOURCE_ONLY_SHA256 = (
    "D4362787134108F376BAF902DD0FE5ED45FA36DA10ACEA74CBE2D8941620868D"
)
EXPECTED_PREDECESSOR_OVERLAPS: int | None = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS: int | None = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "6F3880DF9105F47402378E89E9C1ADE9599C052CAEC6EE3D7CC795333C04C7DE"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "6FBC581903028C5DE82B53368310D730F47CF408F59685BAA6310F6E62663680"
)
EXPECTED_EMPTY_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_SOURCE_TERMINAL_SHA256 = (
    "5D3D3A6C696F698638360E90EA204BE98C7B986199D29BB06AB10850039D10E9"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "37402EE773B331D48C957C8C2AA3EED55FA582726BC98EA5F9BECBF87AD153AE",
    "private_evidence":
        "D16D23F204D82F926CB0E6304928BD8F852FE2F6AB8B8437F80130A1889C2CEF",
    "public_coverage":
        "F929792EEA4C3B1B7F4F65C5F498C01437DA24A7812AC2B41B29B13806D53E38",
    "public_promotion":
        "D6BEC8BFCD19B0E75FFD0BDC491980528EF6FDBF92C7CD061D19093E1A782F2F",
    "final_candidate":
        "EF84A8B8A18C1F2F1F72D3A650C01DC7B058F32A3536C130809C4FCB31C837C7",
    "decision_coordinates":
        "9EAE219F77866334A2B88A574EA5928735DE735CED27046DD9114B232ABE6C0B",
    "promotion_coordinates":
        "9EAE219F77866334A2B88A574EA5928735DE735CED27046DD9114B232ABE6C0B",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "6B1B9A5804093507073303CF67C69FC3ECA09F1F828EF199002615B6D6B0977A",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "DEEC978994C9C4000C92D11F76979DBD09ECB818663993D68C82FC27008EF2EE",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCAFFOLD_BASE = load_module(
    SCAFFOLD_BASE_PATH, "selector1168_closure_scaffold_base"
)
WRAPPER = SCAFFOLD_BASE.WRAPPER
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector1168_closure_input")
BASE = WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = SCAFFOLD_BASE.ORIGINAL_CONFIGURE_BASE


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.METHOD = (
        "post_selector364_selector1168_two_chunk_single_coordinate_union_"
        "with_targeted_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector1168-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector1168-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector1168-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector1168-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector1168_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = (
        "nobu16.kr.pk-selector1168-assignment.private.v1"
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
        and tuple(row["target"]) == (0, 1168)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-1168 site drifted: {site}")


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
    proof["all_53_candidate_sites_reviewed"] = True
    proof["confirmed_non_display_rows_untouched"] = True
    proof["seven_terminal_records_unchanged"] = True
    proof["honorific_prefix_terminals_all_empty_in_candidate"] = True
    proof["honorific_prefix_terminals_absent_from_decisions"] = True
    proof["source_only_5_absent_from_current_and_candidate"] = True
    proof["owned_overlap_rows_require_fresh_exact_review"] = True
    coverage["guards"].pop("payload_without_guard_sha256", None)
    coverage["guards"]["payload_without_guard_sha256"] = BASE.canonical_sha256(
        coverage
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)
    return outputs


def terminal_digest(records: Mapping[tuple[int, int], Any]) -> str:
    values = []
    for record_id in range(2637, 2644):
        literals = ASSIGNMENT.ASSIGNMENT.ENGINE.parse_record_literals(
            records[(0, record_id)]
        )
        BASE.require(
            len(literals) == 1,
            f"selector1168 terminal literal shape drifted: {record_id}",
        )
        values.append(literals[0].text)
    return BASE.sha256_bytes("\0".join(values).encode("utf-8"))


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
    chunk_decisions = [
        json.loads(line)
        for path in CHUNK_DECISIONS
        for line in path.read_text(encoding="utf-8").splitlines()
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
    terminal_roots = {(0, record_id) for record_id in range(2637, 2644)}
    decision_roots = {
        tuple(map(int, coordinate.split(":")[:2]))
        for _resource, coordinate in decision_keys
    }
    candidate, _current, source, contexts, _pending = (
        ASSIGNMENT.ASSIGNMENT.RECORDS.load_records()
    )
    BASE.require(
        len(official) == 52_803
        and len(confirmed) == EXPECTED_CONFIRMED_NON_DISPLAY
        and not decision_keys & confirmed,
        "selector1168 touched the confirmed-non-display universe",
    )
    BASE.require(
        not decision_roots & terminal_roots,
        "selector1168 decision union changed a shared terminal",
    )
    BASE.require(
        terminal_digest(candidate) == EXPECTED_EMPTY_TERMINAL_SHA256
        and terminal_digest(source) == EXPECTED_SOURCE_TERMINAL_SHA256
        and all(
            terminal_digest(contexts[language])
            == EXPECTED_EMPTY_TERMINAL_SHA256
            for language in ("en", "sc", "tc")
        ),
        "selector1168 honorific-prefix terminal contract drifted",
    )
    BASE.require(
        all(
            row.get("fresh_semantic_review") == "approved"
            and row.get("runtime_review") == "verified"
            for row in decisions
        ),
        "selector1168 closure decisions lack fresh exact review",
    )
    BASE.require(
        all(
            row.get("fresh_semantic_review") == "approved"
            and row.get("runtime_review") == "verified"
            and row.get("predecessor_candidate_sha256")
            == EXPECTED_OFFICIAL_CANDIDATE_SHA256
            and "auto" not in str(row.get("action", "")).lower()
            for row in chunk_decisions
        ),
        "selector1168 chunk decisions lack exact predecessor-state review",
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


def unresolved_placeholders() -> list[str]:
    result = [
        key for key, value in EXPECTED_INPUT_SHA256.items() if value is None
    ]
    result.extend(
        f"chunk_rows[{index}]"
        for index, value in enumerate(EXPECTED_CHUNK_ROWS)
        if value is None
    )
    for name in (
        "EXPECTED_DECISION_ROWS",
        "EXPECTED_DECISION_ROOTS",
        "EXPECTED_PROMOTIONS",
        "EXPECTED_RENEWALS",
        "EXPECTED_OVERRIDES",
        "EXPECTED_ACTION_COUNTS",
        "EXPECTED_PENDING_AFTER",
        "EXPECTED_PREDECESSOR_OVERLAPS",
        "EXPECTED_PREDECESSOR_SUPERSESSIONS",
    ):
        if globals()[name] is None:
            result.append(name)
    result.extend(
        key for key, value in EXPECTED_OUTPUT_SHA256.items() if value is None
    )
    return result


def is_frozen() -> bool:
    return not unresolved_placeholders()


def build_outputs() -> dict[Path, bytes]:
    BASE.require(
        BASE.sha256_file(SCAFFOLD_BASE_PATH) == EXPECTED_SCAFFOLD_BASE_SHA256,
        "selector364 closure scaffold base drifted",
    )
    BASE.require(
        is_frozen(),
        "selector1168 closure scaffold is intentionally blocked: "
        + ",".join(unresolved_placeholders()),
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
                f"selector1168 closure output drifted: {path}",
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
