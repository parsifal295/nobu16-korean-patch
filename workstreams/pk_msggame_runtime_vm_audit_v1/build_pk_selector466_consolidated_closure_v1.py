#!/usr/bin/env python3
"""Consolidate the two selector-466 reviews on the post-selector1078 state."""

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
    WORKSTREAM / "build_pk_selector1078_consolidated_closure_v1.py"
)
EXPECTED_SCAFFOLD_SHA256 = (
    "9836C4EC91F9E310E66DAF95A355554CC539F26F3DBC5D1C25A00B6A6B9860A9"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector466_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector466_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector466_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1078_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector1078_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector466_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector466_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector466_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector466_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector466_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector466_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector466_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector466_consolidated_closure_promotion.v1.json"
)

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "729E1778540A1E5FB5BF48CACE9309B83CFE0A021FDA294049FEC91104387F71",
    "assignment_private":
        "8C7350F94A08894C5B88A4E6BD335DA96877EEE55902B4E9110186FE0E8C7507",
    "assignment_public":
        "457C7C0D368269F69C391E6A981CF6AA5D4FB905C99B327C2DAEE9C4F137BA5E",
    "official_ledger":
        "71ADE7F33FC40A817E60F429DE0A0B329E05BF37BD1E03E1671A019783E800F6",
    "predecessor_decisions":
        "82196010FD6EF8C06B186FE8BA3A48DFAC684ABA7A3ADEDFCA66D7F843A34B70",
    "chunk0_builder":
        "996347B2D89CCD34200912D95D6E906C1A806F114A47B47C622E8EBAED1516B9",
    "chunk0_public":
        "D9F17A13C69FA8C5885D9BF048A98271ABA7B733D68C9F9AD3D6469198C418AE",
    "chunk0_decisions":
        "159087FAF3C33589CFCEA9447ECAA8074908F2AF2B5C962C67B85AC572CB5F86",
    "chunk0_evidence":
        "33C957C6B6F4B64874A27859900B8DCCD6B6052969DB9CA48EB8AB985A4D93AC",
    "chunk1_builder":
        "122AFABFDB86FC3235BF9CA52A7260753EFB16739816757E079B9476404738FC",
    "chunk1_public":
        "CA8571E73E15A9CFA4DECF83D3E8095EC9C0B5E56194D949604BF987237C1A5F",
    "chunk1_decisions":
        "DE6E32948B02FB7B19EB300C600B9732C9B3C27B4D30C9B00338F59C5FD61704",
    "chunk1_evidence":
        "3E4F2CCD6E06769A76A4BBC17CAA61EF0CA70A2ACC20AFB3FDF69A0F4EEDC22B",
}
EXPECTED_CHUNK_ROWS = (3, 21)
EXPECTED_CHUNK_SITES = (38, 41)
EXPECTED_DECISION_ROWS = 24
EXPECTED_DECISION_ROOTS = 12
EXPECTED_PROMOTIONS = 24
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 13
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 11,
    "translation_override_and_runtime_promotion": 13,
}
EXPECTED_PENDING_BEFORE = 6_215
EXPECTED_PENDING_AFTER = 6_191
EXPECTED_REVIEWED_SITES = 79
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "DD69F2428FD90984E29419091FEB764ACBEA21317C049AC746410F89AAA9A778"
)
EXPECTED_SOURCE_SITES = 94
EXPECTED_SOURCE_SITE_SHA256 = (
    "9E24FDF911F6DCBC2FAC75503DFB12766D5353826052F8C27289857B78FD26B7"
)
EXPECTED_SOURCE_ONLY_SITES = 15
EXPECTED_SOURCE_ONLY_SHA256 = (
    "5E6C7A981B5AEF2CA6903171CEB43062862E63B24B114FCD8CF3337CEDF57AEE"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "1A931E023A5248626AE90094772657D91B4270D0F530B48ABC613FDA84BB508D"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "395C8B600B1AED634FA199602CBBB9F2DCA5691D9E5850688E2107966A8A77E3"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "43B346EA667D710BDFC6A84D958602CCB68DB95CA78D204C1D8F2C43B7336483"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "EE25924A3F5EB5008D1EC7C3EE6506E11821B2969EF7E1AE76935E69CA64F9B3"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "47ABF41C98D2DF16C3C5A572EE31139D0C457B04C131D164FE69494332C4FBA3"
)
EXPECTED_EMPTY_CONTEXT_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "9460D51503D9B204E0D6AEC2BD152439137A38C2961D9C4D9464F7B5ABCE87DF",
    "private_evidence":
        "C1D6BB02064E522E22C5667155184EBA7B7218206647ED9B0A2EC4B9BAF8B525",
    "public_coverage":
        "CBE4FCFD4AFC24914BF57CF086D83D7EA55775ACD2223444AFA2624DB94CD6AE",
    "public_promotion":
        "ABBDC09953748C70696E84F7681D47DD9AD5C8A2EC82BF403D1CB2E08054B5F1",
    "final_candidate":
        "E2283160520383E455C9C26112E80E5DB5EDB89161A9842FF3BD8F4C7FFCAD45",
    "decision_coordinates":
        "3C41921A18094C62C9D1B9A98CC5D043C016B30651E4AD292CA1E756ECC18FEB",
    "promotion_coordinates":
        "3C41921A18094C62C9D1B9A98CC5D043C016B30651E4AD292CA1E756ECC18FEB",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "032A9FA05D4C92FFF92930C780C3DE706B35E610E19519BEB750C1AD21F523BD",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "75D0F6AFBFB8650021AB4560A3ED5694DDE713313258B5FE28AA29E55B347252",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCAFFOLD = load_module(SCAFFOLD_PATH, "selector466_closure_scaffold")
WRAPPER = SCAFFOLD.WRAPPER
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector466_closure_input")
BASE = WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = SCAFFOLD.configure_base


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.METHOD = (
        "post_selector1078_selector466_two_chunk_single_coordinate_union_"
        "with_read_only_terminal_and_same_gap_block_guards"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector466-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector466-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector466-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector466-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector466_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = (
        "nobu16.kr.pk-selector466-assignment.private.v1"
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
        and tuple(row["target"]) == (0, 466)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-466 site drifted: {site}")


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
        "all_79_candidate_sites_reviewed": True,
        "completed_selector_overlaps_freshly_reviewed": True,
        "confirmed_non_display_rows_untouched": True,
        "non_display_candidate_action_count_zero": True,
        "pending_assembly_evidence_did_not_auto_promote": True,
        "same_gap_atoms_blocked_as_one_unit": True,
        "seven_terminal_records_unchanged": True,
        "source_only_15_absent_from_current_and_candidate": True,
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
    for record_id in range(1839, 1846):
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
        f"0:{record_id}" for record_id in range(1839, 1846)
    }
    same_gap_roots = set(assignment["same_gap_control_atom"]["atom_roots"])
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
        "selector466 terminal contract drifted",
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
        and chunk_evidence[1]["proof"][
            "multi_control_partial_pass_authorized"
        ] is False
        and chunk_evidence[1]["counts"]["same_gap_atoms"] == 2
        and chunk_evidence[1]["counts"]["multi_control_blocked_sites"] == 2
        and chunk_evidence[1]["counts"]["source_only_actions"] == 0,
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
        "selector1078 closure scaffold drifted",
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
                f"selector466 closure output drifted: {path}",
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
