#!/usr/bin/env python3
"""Consolidate the two selector-562 reviews on the post-selector466 state."""

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

SCAFFOLD_PATH = WORKSTREAM / "build_pk_selector466_consolidated_closure_v1.py"
EXPECTED_SCAFFOLD_SHA256 = (
    "6AE6125177516E5B8533C49358EF5DD345EF9916E26D1B9F2FCB1078BFD794FF"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector562_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector562_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector562_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector466_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector466_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector562_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector562_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector562_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector562_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector562_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector562_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector562_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector562_consolidated_closure_promotion.v1.json"
)

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "FEBE7891BE6CA37EF8C2708F7E73F3F8647E2A1BCD55B85CD00F87FEF08F7395",
    "assignment_private":
        "9F0DF230231732B1345B80FC6F159F9D18DAD56F87D707971193658C895B1067",
    "assignment_public":
        "42AC1603E4F599BC36BF9B58BB766390388660050650101EC22DF41C043EED3A",
    "official_ledger":
        "99450F568D8EDED40C7A7332F52DADA184EE6F11FB129CFDBCC758C7880DC197",
    "predecessor_decisions":
        "9460D51503D9B204E0D6AEC2BD152439137A38C2961D9C4D9464F7B5ABCE87DF",
    "chunk0_builder":
        "3C755BBF00411FDF9FC6449C98D969A59E27CA2DAF052C1A8247B8185DDA2DFA",
    "chunk0_public":
        "673BBA243E381ED0579FB0CEE2688181087D7FBBA49095F4FDA6F46DFB05BDFC",
    "chunk0_decisions":
        "773B63D3427CDF9D0DA9246FB1618CBAABED46BC90CF53B8EBDC863E9631C911",
    "chunk0_evidence":
        "29E569E3BD5ADA74A6EBCE6448FDCC5E0F1C28FCDF4FDCCAEEBCAFED0D650BFF",
    "chunk1_builder":
        "4897BB2FC0028D0101D8701D9319C41D4256FB79D1844F28AE3D34C01080A040",
    "chunk1_public":
        "BFACB9361C7C6765504B691FF4DA6DE12807D409A0E26E648FEBCBC9DC359985",
    "chunk1_decisions":
        "4DB881B2DEC037241F3092B292D485695D2B3842982F91E6DCED249D156CE240",
    "chunk1_evidence":
        "C341085B60E72385F376819BD1F8D89651F4A5BAEC33AB5645CA4887631F60D9",
}
EXPECTED_CHUNK_ROWS = (5, 5)
EXPECTED_CHUNK_SITES = (28, 26)
EXPECTED_DECISION_ROWS = 10
EXPECTED_DECISION_ROOTS = 4
EXPECTED_PROMOTIONS = 10
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 7
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 3,
    "translation_override_and_runtime_promotion": 7,
}
EXPECTED_PENDING_BEFORE = 6_191
EXPECTED_PENDING_AFTER = 6_181
EXPECTED_REVIEWED_SITES = 54
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "D31C4A78FC7FA6713F04DBAF2DE0CB1C20DDBC856C3C25B43815850F3C682974"
)
EXPECTED_SOURCE_SITES = 60
EXPECTED_SOURCE_SITE_SHA256 = (
    "3CFDAA54625661224DB877A00B9AB9C947015492354C5E0D146ED65917FD7EB2"
)
EXPECTED_SOURCE_ONLY_SITES = 6
EXPECTED_SOURCE_ONLY_SHA256 = (
    "01AC741CD6E35AB30D8D0291D1B4B2110202B73AF4DD69DC4D4E53476ECC7128"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "E2283160520383E455C9C26112E80E5DB5EDB89161A9842FF3BD8F4C7FFCAD45"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "D3824B5CF7A8DE02626FF06CE40816086F7DFB8EF6A0A9E06686756A9B69EA5E"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "31F899387108821947571F9085D8A7FD9919BD52B8BA349DC831E138740343D6"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "31F899387108821947571F9085D8A7FD9919BD52B8BA349DC831E138740343D6"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "DD32A4A1CB88CDA98B9B37CDC21CB43A7D2C5B00B7EE374A10A0F774FD26C073"
)
EXPECTED_EMPTY_CONTEXT_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "51CA681BCE819F41B1D7B69BE6AD906BFCD519BC463BF8EEBAA08DACA5C5BD26",
    "private_evidence":
        "D1A8008699F36458A2F84D5FC731C37337177E41712A53A809513238CB4B212D",
    "public_coverage":
        "6357E5A97416AD056DC201BF3FE08ABF3969ADD790F9FBDD27AACBA249B19AA3",
    "public_promotion":
        "9AE738D3A1729D8876757CBA1BC2E8CE9290A62A8C235AA8B1A27C5984A24173",
    "final_candidate":
        "B7CBFA388BDD50F60CD5EEF88A63B62D357475925A0A3AA6D7DCA1A191607815",
    "decision_coordinates":
        "1FE88942F1B906361BD7F2E1361809DBE85E664FC0CD44834FF3CEDFF1CE8ACD",
    "promotion_coordinates":
        "1FE88942F1B906361BD7F2E1361809DBE85E664FC0CD44834FF3CEDFF1CE8ACD",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "340DD655AF4C272087695F4110B0DFB4A177A96F96F1E34EB9687C2B6969620E",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "F6116EC0DEDBB81E2D0D6B7CEDDEE36562AB23306D90D2AB8B02D74639866AF5",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCAFFOLD = load_module(SCAFFOLD_PATH, "selector562_closure_scaffold")
WRAPPER = SCAFFOLD.WRAPPER
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector562_closure_input")
BASE = WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = SCAFFOLD.configure_base


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.METHOD = (
        "post_selector466_selector562_two_chunk_single_coordinate_union_"
        "with_read_only_terminal_and_atomic_template_guards"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector562-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector562-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector562-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector562-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector562_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = (
        "nobu16.kr.pk-selector562-assignment.private.v1"
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
        and tuple(row["target"]) == (0, 562)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-562 site drifted: {site}")


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
        "all_54_candidate_sites_reviewed": True,
        "completed_selector_overlaps_freshly_reviewed": True,
        "confirmed_non_display_rows_untouched": True,
        "non_display_candidate_action_count_zero": True,
        "pending_assembly_evidence_did_not_auto_promote": True,
        "atomic_template_roots_reviewed_as_one_unit": True,
        "seven_terminal_records_unchanged": True,
        "source_only_6_absent_from_current_and_candidate": True,
        "source_only_action_count_zero": True,
        "terminal_records_absent_from_decisions": True,
        "terminal_register_order_preserved": True,
        "terminal_rows_verified_read_only": True,
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
    for record_id in range(1944, 1951):
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
        f"0:{record_id}" for record_id in range(1944, 1951)
    }
    candidate, current, source, contexts, _pending = (
        ASSIGNMENT.ASSIGNMENT.RECORDS.load_records()
    )
    BASE.require(
        not decision_roots & terminal_roots,
        "shared terminal entered decision union",
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
        and sorted(Counter(terminal_values(candidate)).values()) == [1, 2, 2, 2],
        "selector562 terminal contract drifted",
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
        and chunk_evidence[0]["exclusions"]["source_only_action_count"] == 0
        and chunk_evidence[0]["terminal_register_review"]["shared_read_only"]
        and chunk_evidence[1]["proof"][
            "prior_pending_evidence_automatic_promotion_count"
        ] == 0
        and chunk_evidence[0]["counts"]["same_gap_branches"] == 0
        and chunk_evidence[1]["counts"]["same_gap_branches"] == 0
        and chunk_evidence[1]["counts"]["source_only_actions"] == 0
        and chunk_evidence[1]["proof"]["shared_terminal_modified"] is False,
        "prior-evidence, terminal, source-only, or same-gap guard drifted",
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
        "selector466 closure scaffold drifted",
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
                f"selector562 closure output drifted: {path}",
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
