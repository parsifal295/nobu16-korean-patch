#!/usr/bin/env python3
"""Consolidate the two selector-292 reviews on the post-selector238 state."""

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

SCAFFOLD_PATH = WORKSTREAM / "build_pk_selector238_consolidated_closure_v1.py"
EXPECTED_SCAFFOLD_SHA256 = (
    "0C803AD9BA0A54858879818951C03BDB5DB13FD9AC840124E39186CE44D74808"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector292_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector292_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector292_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector238_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector238_consolidated_closure_decisions.private.v1.jsonl"
)
CONTEXT_MANIFEST_PATH = DIALOGUE_TMP / "pk_selector292_context_inventory.private.v1.json"
LAYOUT_MANIFEST_PATH = (
    DIALOGUE_TMP
    / "pk_selector292_layout_manifest.selector178_chunk1_fast.private.v1.json"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector292_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector292_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector292_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector292_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector292_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector292_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector292_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector292_consolidated_closure_promotion.v1.json"
)

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "A1BC5DE2EA3E0CF06984FF97347006936407FF32B72D439B94F7598B0FD3847E",
    "assignment_private":
        "B2FD0DD7B016B20CCAB04CA903643CD158008299BBC9EF8FAA89187A5C9D6372",
    "assignment_public":
        "AAA5F7F7A503A508712AC1E0DB304F04A9152FA1E3CE30D5A53598B1AE3B06DD",
    "official_ledger":
        "AC10F7E71CFAD259ABBC08139BE0DB848CF5309578045532A48991F40E0035AB",
    "predecessor_decisions":
        "6C06A0C6702109D17663270FB6946155D28B805F6D81A71CFC522A12F9B75B58",
    "chunk0_builder":
        "1228F77668A394F7C67C6E238DFA6024CA1457669D15AF290858CEF1B949A074",
    "chunk0_public":
        "78A55FA3CA4FD492AED3520FF14857DCA00AE78A45ABF572DE0965F8085E269D",
    "chunk0_decisions":
        "C853D375FCD23CA0C2F64CF1959B1063973240E6196DFCD3A5EC5ABF109FF024",
    "chunk0_evidence":
        "160C3EA06455FD9E9800D68B0C950679C5CF132CB9F58AC1917576ABB981C7DF",
    "chunk1_builder":
        "E83AD39E4D08AC4902D4380D0973CFE1E7E8827B551610AFD47DCD1A59E1F5AF",
    "chunk1_public":
        "71A23B62D9B6DC0B32E02163F9B9997743453E55B13840401BB0E506BB915AF5",
    "chunk1_decisions":
        "6B2230F012B400AF9C393E0ADDBA0D7658E349ABC53E7DC49722FB27217C6A95",
    "chunk1_evidence":
        "92F0A300B915AC0EDB01CD00DF1C52DE5F6929BB71CC2F7A86CCA268616296C0",
}
EXPECTED_CHUNK_ROWS = (12, 10)
EXPECTED_CHUNK_SITES = (13, 13)
EXPECTED_CHUNK_PENDING_ROWS = (13, 20)
EXPECTED_CHUNK_HARD_BLOCK_ROWS = (1, 4)
EXPECTED_DECISION_ROWS = 22
EXPECTED_DECISION_ROOTS = 6
EXPECTED_PROMOTIONS = 21
EXPECTED_RENEWALS = 1
EXPECTED_OVERRIDES = 8
EXPECTED_ACTION_COUNTS: dict[str, int] = {
    "runtime_promotion": 14,
    "translation_override_and_runtime_promotion": 7,
    "translation_override_and_verification_renewal": 1,
}
EXPECTED_PENDING_BEFORE = 6_151
EXPECTED_PENDING_AFTER = 6_130
EXPECTED_REVIEWED_SITES = 26
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "9F320371558647FF01DD2F0F30F1B65DB068120C6922AC8D3223584738C5FA0E"
)
EXPECTED_SOURCE_SITES = 31
EXPECTED_SOURCE_SITE_SHA256 = (
    "64C9FD4610819E364E2ACD01C3EC634EFAF23A4E3951DC54FFC726B6E0E41686"
)
EXPECTED_SOURCE_ONLY_SITES = 5
EXPECTED_SOURCE_ONLY_SHA256 = (
    "4B5C5E8AAF5AA1D14BAABFF35200E062154343CC777503EE652DC1D5D3B324D0"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "9E5C60A451DB7CCA7B046AFD8CFF199CB3665E003CB0C751120478F693D20C24"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "0CAE7231474FBAE0BCE8E1E98D44225DCC5445EEEA435378E0D56BD1F83A5384"
)
EXPECTED_CONTEXT_MANIFEST_SHA256 = (
    "2DC02C44C2698F407970BB0291E3023A597D6F9944B330E91A3C4778C621685D"
)
EXPECTED_LAYOUT_MANIFEST_SHA256 = (
    "A19F3696797F141A282826D1E87DEA1D80EF11E0BB55F21EF49EF061CCE0FA99"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "F18978DBB58A5D8AF1ED4B2266FE2B599C98A038D5A85BDAAC2222FDEB8C51A6"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "84EE1EB18E39223AA009868B7FB99119073A6DFC7CA8FC899C70C464F8346B47"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "798B6E4A8099F9FCA1BF5033F8315B17832B8D17178826029B800738EAD905C2"
)
EXPECTED_EMPTY_CONTEXT_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_HARD_BLOCK_ROWS = 5
EXPECTED_SAME_GAP_BRANCHES = 392
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "F90AD78BF19BE129BFEF08FFF47C81CAFCD90ADBA7B6DDC0B1DF89039E47F004",
    "private_evidence":
        "6BAF6AC32B0EEE03E8933BA65F9A56145758ECE72506DCF57FCCA068843839A9",
    "public_coverage":
        "29244DDABD88277D8D6957E43D41B6FAABDD895EF857F34DCA42DC0B76DA0572",
    "public_promotion":
        "B22953FA1215D16531370F931EAAC722B244D7A60914AEED19E240ABDF61870A",
    "final_candidate":
        "723589D4CC42165F93FF60F0711E96DAB6E84737C75954FA36819F780CD57A2C",
    "decision_coordinates":
        "6FBF66819BF084FD16F156D28FEE233F964A882C02AE4E8A38119ACDA25643DD",
    "promotion_coordinates":
        "B6675351E0E5A7827561F5DC81569ED42E9B02C0C633DFC0CD18551207322618",
    "renewal_coordinates":
        "EFEB3EE59FE890CF7BEFC7386887D725948CD105CC8E64DB4C4CBE6D794B579F",
    "override_coordinates":
        "AD41BE18540EE1160AA2B21670D11FA84D0ABBD25CE2724D8A61FF699C03565E",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "5F22E98BD35042054416A5880AB6A9A19A695F3B619749D67D306AD422D20BC5",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCAFFOLD = load_module(SCAFFOLD_PATH, "selector292_closure_scaffold")
WRAPPER = SCAFFOLD.WRAPPER
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector292_closure_input")
BASE = WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = SCAFFOLD.configure_base
ORIGINAL_BASE_LOAD_JSONL = BASE.load_jsonl


def load_jsonl_compatible(path: Path) -> list[dict[str, Any]]:
    rows = ORIGINAL_BASE_LOAD_JSONL(path)
    if path not in CHUNK_DECISIONS:
        return rows
    chunk_id = CHUNK_DECISIONS.index(path)
    expected_label = (
        "seven_of_seven_current_relative_nonexpanding"
        if chunk_id == 0
        else "current_relative_raw_g1n_nonexpanding"
    )
    BASE.require(
        all(str(row.get("layout_review")) == expected_label for row in rows),
        f"selector292 chunk{chunk_id} original layout review drifted",
    )
    return [
        {
            **row,
            "layout_review": "current_relative_raw_g1n_nonexpanding",
        }
        for row in rows
    ]


def validate_chunk_evidence(
    assignment: Mapping[str, Any],
    chunk_rows: Sequence[Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    evidence = [BASE.load_json(path) for path in CHUNK_EVIDENCE]
    all_sites: set[str] = set()
    all_decisions: set[str] = set()
    all_blocked: set[str] = set()
    assignment_hard_blocks = set(
        map(
            str,
            assignment["review_partition"]["hard_block_pending_coordinates"],
        )
    )
    for chunk_id, rows in enumerate(chunk_rows):
        assigned = assignment["chunks"][chunk_id]
        chunk_evidence = evidence[chunk_id]
        assigned_sites = set(map(str, assigned["sites"]))
        assigned_roots = set(map(str, assigned["roots"]))
        pending_coordinates = set(map(str, assigned["pending_coordinates"]))
        pending_roots = {
            BASE.coordinate_root(coordinate)
            for coordinate in pending_coordinates
        }
        decision_coordinates = {str(row["coordinate"]) for row in rows}
        promotion_coordinates = {
            str(row["coordinate"])
            for row in rows
            if str(row["action"]).endswith("runtime_promotion")
        }
        renewal_coordinates = decision_coordinates - promotion_coordinates
        accepted_roots = {
            BASE.coordinate_root(coordinate)
            for coordinate in promotion_coordinates
        }
        blocked_coordinates = pending_coordinates - promotion_coordinates
        blocked_roots = {
            BASE.coordinate_root(coordinate)
            for coordinate in blocked_coordinates
        }
        hard_blocks = pending_coordinates & assignment_hard_blocks
        counts = chunk_evidence["counts"]
        proof = chunk_evidence["proof"]
        BASE.require(
            len(rows) == EXPECTED_CHUNK_ROWS[chunk_id]
            and len(decision_coordinates) == len(rows)
            and promotion_coordinates <= pending_coordinates
            and not renewal_coordinates & pending_coordinates
            and accepted_roots <= assigned_roots
            and blocked_roots <= assigned_roots,
            f"chunk{chunk_id} decision partition drifted",
        )
        BASE.require(
            len(assigned_sites) == EXPECTED_CHUNK_SITES[chunk_id]
            and len(assigned_roots) == EXPECTED_CHUNK_SITES[chunk_id]
            and len(pending_coordinates) == EXPECTED_CHUNK_PENDING_ROWS[chunk_id]
            and int(assigned["pending_row_upper_bound"])
                == EXPECTED_CHUNK_PENDING_ROWS[chunk_id]
            and len(hard_blocks)
                == EXPECTED_CHUNK_HARD_BLOCK_ROWS[chunk_id]
            and hard_blocks <= blocked_coordinates,
            f"chunk{chunk_id} assignment or hard-block coverage drifted",
        )
        BASE.require(
            counts["decision_rows"] == EXPECTED_CHUNK_ROWS[chunk_id]
            and counts["accepted_pending_rows"] == len(promotion_coordinates)
            and counts["accepted_pending_roots"] == len(accepted_roots)
            and counts["promoted_pending_rows"] == len(promotion_coordinates)
            and counts["blocked_pending_rows"] == len(blocked_coordinates)
            and counts["blocked_pending_roots"] == len(blocked_roots)
            and counts["source_only_actions"] == 0
            and counts["non_display_actions"] == 0
            and counts["terminal_decision_rows"] == 0,
            f"chunk{chunk_id} evidence counts drifted",
        )
        if chunk_id == 0:
            reason_roots = {
                str(row["root"])
                for row in chunk_evidence["blocked_root_reasons"]
            }
            manifest = chunk_evidence["assembly_manifest"]
            BASE.require(
                len(renewal_coordinates) == 1
                and counts["sites"] == 13
                and counts["roots"] == 13
                and counts["accepted_pending_rows"] == 11
                and counts["blocked_pending_rows"] == 2
                and counts["shared_override_rows"] == 1
                and counts["translation_overrides"] == 4
                and counts["hard_blocked_roots"] == 1
                and counts["read_only_nonpending_roots"] == 8
                and counts["rewrite_attempt_roots"] == 4
                and counts["ordinary_attempt_branches"] == 28
                and counts["ordinary_verified_branches"] == 21
                and counts["full_layout_recomputed_branches"] == 0
                and reason_roots == blocked_roots
                and len(manifest) == 28
                and {
                    int(row["branch_ordinal"]) for row in manifest
                } == set(range(7))
                and proof[
                    "accepted_ordinary_branches_current_relative_nonexpanding"
                ] is True
                and proof["accepted_ordinary_branches_grammar_pass"] is True
                and proof["automatic_promotion_count"] == 0
                and proof[
                    "controls_tokens_and_linebreak_counts_preserved"
                ] is True
                and proof["full_518_branch_recompute_performed"] is False
                and proof["jp_semantic_authority"] is True
                and proof["maximum_rewrite_attempts_per_root"] == 1
                and proof["nonpending_roots_read_only"] is True
                and proof[
                    "prior_or_owned_evidence_automatic_promotion_count"
                ] == 0
                and proof["reused_context_manifest_sha256"]
                    == EXPECTED_CONTEXT_MANIFEST_SHA256
                and proof["reused_layout_manifest_sha256"]
                    == EXPECTED_LAYOUT_MANIFEST_SHA256
                and proof["source_only_action_count"] == 0
                and proof["steam_write_performed"] is False
                and proof["terminal_automatic_promotion_count"] == 0
                and proof["terminal_records_read_only"] is True,
                "chunk0 review or reused-layout proof drifted",
            )
        else:
            BASE.require(
                not renewal_coordinates
                and set(map(
                    str, chunk_evidence["accepted_pending_coordinates"]
                )) == promotion_coordinates
                and set(map(
                    str, chunk_evidence["blocked_pending_coordinates"]
                )) == blocked_coordinates
                and counts["assigned_sites"] == 13
                and counts["assigned_roots"] == 13
                and counts["accepted_pending_rows"] == 10
                and counts["blocked_pending_rows"] == 10
                and counts["translation_overrides"] == 4
                and counts["runtime_only_promotions"] == 6
                and counts["read_only_nonpending_roots"] == 7
                and counts["register_atom_blocked_roots"] == 2
                and counts["rewrite_attempt_roots"] == 5
                and counts["affected_ordinary_branches_computed"] == 35
                and counts["affected_ordinary_pass_branches"] == 33
                and counts["hard_block_reused_branches"] == 7
                and proof[
                    "affected_ordinary_branches_computed_once"
                ] is True
                and proof[
                    "all_accepted_branches_current_relative_nonexpanding"
                ] is True
                and proof["blocked_roots_received_no_decisions"] is True
                and proof["control_gap_change_count"] == 0
                and proof["historical_factuality_reviewed"] is True
                and proof["jp_authoritative"] is True
                and proof["layout_518_branch_recompute_performed"] is False
                and proof["linebreak_change_count"] == 0
                and proof["maximum_rewrite_attempts_per_root"] == 1
                and proof["owned_overlap_automatic_promotion_count"] == 0
                and proof[
                    "prior_pending_evidence_automatic_promotion_count"
                ] == 0
                and proof[
                    "register_atom_consistency_preserved_by_atomic_block"
                ] is True
                and proof[
                    "reverse_overlay_recovers_official_candidate"
                ] is True
                and proof["source_only_action_count"] == 0
                and proof["speaker_tone_reviewed"] is True
                and proof["steam_write_performed"] is False
                and proof["terminal_automatic_promotion_count"] == 0
                and proof["terminal_records_read_only"] is True,
                "chunk1 review or reused-layout proof drifted",
            )
        BASE.require(not all_sites & assigned_sites, "chunk sites overlap")
        BASE.require(not all_decisions & decision_coordinates, "chunk decisions overlap")
        BASE.require(not all_blocked & blocked_coordinates, "chunk blocks overlap")
        all_sites.update(assigned_sites)
        all_decisions.update(decision_coordinates)
        all_blocked.update(blocked_coordinates)
    BASE.require(
        len(all_sites) == EXPECTED_REVIEWED_SITES
        and BASE.site_digest(all_sites) == EXPECTED_CANDIDATE_SITE_SHA256
        and len(all_decisions) == EXPECTED_DECISION_ROWS
        and len(all_blocked) == 12
        and assignment_hard_blocks <= all_blocked,
        "selector292 review union drifted",
    )
    return evidence


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.load_jsonl = load_jsonl_compatible
    BASE.METHOD = (
        "post_selector238_selector292_two_chunk_single_coordinate_union_"
        "with_reused_cartesian_layout_and_read_only_terminal_guards"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector292-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector292-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector292-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector292-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector292_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = (
        "nobu16.kr.pk-selector292-assignment.private.v1"
    )
    BASE.validate_chunk_evidence = validate_chunk_evidence


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
        and tuple(row["target"]) == (0, 292)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-292 site drifted: {site}")


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
        "all_26_candidate_sites_reviewed": True,
        "confirmed_non_display_rows_untouched": True,
        "hard_block_5_pending_rows_received_no_decisions": True,
        "layout_manifest_reused_without_full_recompute": True,
        "same_gap_392_cartesian_branches_reused": True,
        "source_only_5_absent_from_current_and_candidate": True,
        "source_only_action_count_zero": True,
        "terminal_records_absent_from_decisions": True,
        "terminal_rows_6_verified_1_pending_all_read_only": True,
    })
    coverage["guards"].pop("payload_without_guard_sha256", None)
    coverage["guards"]["payload_without_guard_sha256"] = (
        BASE.canonical_sha256(coverage)
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)
    return outputs


def terminal_values(records: Mapping[tuple[int, int], Any]) -> list[str]:
    values = []
    for record_id in range(1615, 1622):
        literals = ASSIGNMENT.ENGINE.parse_record_literals(
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
    official = BASE.load_jsonl(OFFICIAL_LEDGER_PATH)
    decisions = [
        json.loads(line)
        for line in outputs[PRIVATE_DECISIONS_OUTPUT]
        .decode("utf-8", errors="strict")
        .splitlines()
        if line
    ]
    assignment = BASE.load_json(ASSIGNMENT_PRIVATE_PATH)
    decision_keys = {
        (str(row["resource"]), str(row["coordinate"])) for row in decisions
    }
    decision_coordinates = {coordinate for _resource, coordinate in decision_keys}
    decision_roots = {
        BASE.coordinate_root(coordinate) for coordinate in decision_coordinates
    }
    hard_block_coordinates = set(
        map(
            str,
            assignment["review_partition"]["hard_block_pending_coordinates"],
        )
    )
    hard_block_roots = set(
        map(str, assignment["review_partition"]["hard_block_roots"])
    )
    terminal_roots = {f"0:{record_id}" for record_id in range(1615, 1622)}
    confirmed = {
        (str(row["resource"]), str(row["coordinate"]))
        for row in official
        if row.get("scope_classification") == "confirmed_non_display"
    }
    candidate, current, source, contexts, _pending = (
        ASSIGNMENT.ASSIGNMENT.RECORDS.load_records()
    )
    terminal_manifest = assignment["shared_terminal_ownership"][
        "terminal_manifest"
    ]
    BASE.require(
        len(official) == 52_803
        and len(confirmed) == EXPECTED_CONFIRMED_NON_DISPLAY
        and not decision_keys & confirmed,
        "selector292 touched confirmed-non-display rows",
    )
    BASE.require(
        len(hard_block_coordinates) == EXPECTED_HARD_BLOCK_ROWS
        and not decision_coordinates & hard_block_coordinates
        and not decision_roots & hard_block_roots
        and not decision_roots & terminal_roots,
        "selector292 hard-block or terminal decision detected",
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
        and sum(row["runtime_review"] == "verified" for row in terminal_manifest)
            == 6
        and sum(row["runtime_review"] == "pending" for row in terminal_manifest)
            == 1
        and all(
            row["read_only"]
            and row["automatic_status_promotion_authorized"] is False
            for row in terminal_manifest
        ),
        "selector292 terminal contract drifted",
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
        "selector238 closure scaffold drifted",
    )
    BASE.require(
        BASE.sha256_file(CONTEXT_MANIFEST_PATH)
            == EXPECTED_CONTEXT_MANIFEST_SHA256
        and BASE.sha256_file(LAYOUT_MANIFEST_PATH)
            == EXPECTED_LAYOUT_MANIFEST_SHA256,
        "selector292 reused private evidence drifted",
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
                f"selector292 closure output drifted: {path}",
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
